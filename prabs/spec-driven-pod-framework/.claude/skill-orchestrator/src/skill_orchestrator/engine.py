"""The iterative state machine: build state, record waves, apply transitions.

Wave-based and resumable (dispatch mode):

    state = build_state(spec_dict)
    while True:
        wave = next_wave(state)      # from scheduler
        if wave is None: break
        # agent runs wave.actions, returns TaskResult list
        record_wave(state, results)  # transitions + clock advance + persist
"""

from __future__ import annotations

from .analysis import analyze
from .models import (
    Action,
    Decision,
    PHASE_INDEX,
    Phase,
    TaskAttempt,
    TaskKind,
    TaskResult,
    TaskRuntime,
    TaskSpec,
    TaskState,
    WorkflowConfig,
    WorkflowState,
)
from .scheduler import compute_critical_paths

try:
    from skill_governor import SkillGovernor
except Exception:  # pragma: no cover
    SkillGovernor = None  # type: ignore


# --------------------------------------------------------------------------- #
def build_state(spec: dict) -> WorkflowState:
    """Construct a workflow from a spec dict.

    Steps: parse config + tasks, validate kinds/skills, wire artifact-derived
    dependencies (consumer-of-file depends on producer-of-file), reject unknown deps
    and cycles, then annotate critical paths for scheduling.
    """
    cfg = WorkflowConfig.from_dict(spec.get("config", {}))
    specs: dict[str, TaskSpec] = {}
    for raw in spec["tasks"]:
        ts = TaskSpec.from_dict(raw, default_rework=cfg.default_rework_budget, default_threshold=cfg.default_accept_threshold)
        if ts.id in specs:
            raise ValueError(f"duplicate task id: {ts.id}")
        specs[ts.id] = ts

    _wire_artifact_dependencies(specs)

    for ts in specs.values():
        for dep in ts.depends_on:
            if dep not in specs:
                raise ValueError(f"task '{ts.id}' depends on unknown task '{dep}'")
        if cfg.enforce_phase_order:
            for dep in ts.depends_on:
                if PHASE_INDEX[specs[dep].phase] > PHASE_INDEX[ts.phase]:
                    raise ValueError(
                        f"task '{ts.id}' ({ts.phase.value}) depends on later-phase "
                        f"task '{dep}' ({specs[dep].phase.value})"
                    )

    _assert_acyclic(specs)

    tasks = {tid: TaskRuntime(spec=ts) for tid, ts in specs.items()}
    state = WorkflowState(name=spec.get("name", "workflow"), config=cfg, tasks=tasks)
    compute_critical_paths(state)
    return state


def _wire_artifact_dependencies(specs: dict[str, TaskSpec]) -> None:
    """Add a dependency from every consumer of a file to its in-workflow producer.

    Files with no producer task are treated as external preconditions and ignored
    (e.g. ``specs/*.md`` from a prior phase). A file produced by more than one task is
    an authoring error.
    """
    producers: dict[str, str] = {}
    for ts in specs.values():
        for artifact in ts.produces:
            if artifact in producers and producers[artifact] != ts.id:
                raise ValueError(
                    f"artifact '{artifact}' is produced by both "
                    f"'{producers[artifact]}' and '{ts.id}'"
                )
            producers[artifact] = ts.id

    for ts in specs.values():
        for artifact in ts.consumes:
            producer = producers.get(artifact)
            if producer and producer != ts.id and producer not in ts.depends_on:
                ts.depends_on.append(producer)


def _assert_acyclic(specs: dict[str, TaskSpec]) -> None:
    WHITE, GREY, BLACK = 0, 1, 2
    color = {tid: WHITE for tid in specs}

    def visit(tid: str, trail: list[str]) -> None:
        color[tid] = GREY
        for dep in specs[tid].depends_on:
            if color[dep] == GREY:
                raise ValueError("dependency cycle detected: " + " -> ".join(trail + [tid, dep]))
            if color[dep] == WHITE:
                visit(dep, trail + [tid])
        color[tid] = BLACK

    for tid in specs:
        if color[tid] == WHITE:
            visit(tid, [])


# --------------------------------------------------------------------------- #
def record_wave(state: WorkflowState, results: list[TaskResult], *, governor: "SkillGovernor | None" = None) -> list[str]:
    """Ingest results for the in-flight wave and advance state.

    The clock advances by the longest action in the wave (wave actions run
    concurrently). Returns human-readable transition notes. Raises ``ValueError`` if a
    result does not match an in-flight action.
    """
    by_task = {r.task_id: r for r in results}
    in_flight = [t for t in state.tasks.values() if t.in_flight is not None]

    missing = [t.spec.id for t in in_flight if t.spec.id not in by_task]
    if missing:
        raise ValueError(f"missing results for in-flight tasks: {', '.join(missing)}")
    extra = [tid for tid in by_task if tid not in {t.spec.id for t in in_flight}]
    if extra:
        raise ValueError(f"results for tasks not in flight: {', '.join(extra)}")

    wave_duration = max((by_task[t.spec.id].duration_seconds for t in in_flight), default=0.0)
    notes: list[str] = []

    for task in in_flight:
        action = task.in_flight
        result = by_task[task.spec.id]
        _record_attempt(task, action, result)
        note = _transition(state, task, action, result, governor=governor)
        notes.append(f"[{task.spec.id}] {note}")
        task.in_flight = None

    state.clock_seconds += wave_duration
    state.wave_log.append(
        {"wave_index": state.wave_index, "duration_seconds": wave_duration,
         "clock_after": state.clock_seconds, "notes": notes}
    )
    return notes


def _record_attempt(task: TaskRuntime, action: Action, result: TaskResult) -> None:
    task.attempts.append(
        TaskAttempt(
            attempt_number=action.attempt_number,
            skill=(action.skill or "<gate>"),
            success=result.success if not task.is_gate else bool(result.approved),
            score=result.score,
            issues=list(result.issues),
            token_usage=result.token_usage,
            duration_seconds=result.duration_seconds,
            approved=result.approved,
            note=result.note,
        )
    )


def _transition(state: WorkflowState, task: TaskRuntime, action: Action, result: TaskResult, *, governor) -> str:
    outcome = analyze(result, task, time_remaining=state.time_remaining, cfg=state.config)
    task.last_decision = f"{outcome.decision.value}: {outcome.reason}"
    end_clock = state.clock_seconds + result.duration_seconds

    if outcome.decision in (Decision.ACCEPT, Decision.APPROVE):
        task.state = TaskState.DONE
        task.end_clock = end_clock
        _maybe_persist(task, governor)
        return outcome.reason

    if outcome.decision is Decision.FAIL:
        task.state = TaskState.FAILED
        task.end_clock = end_clock
        _maybe_persist(task, governor)
        return outcome.reason

    if outcome.decision is Decision.RETRY:
        task.rework_count += 1
        if outcome.skill_override:
            task.skill_override = outcome.skill_override
        # stays RUNNING; scheduler will re-dispatch its (overridden) skill
        return outcome.reason

    if outcome.decision is Decision.REJECT:
        if outcome.rework_targets:
            _route_rework(state, task, outcome.rework_targets)
            return outcome.reason
        task.state = TaskState.FAILED
        task.end_clock = end_clock
        return outcome.reason

    return outcome.reason  # pragma: no cover


def _route_rework(state: WorkflowState, gate: TaskRuntime, targets: list[str]) -> None:
    """Send specific upstream tasks back for rework and re-queue the gate.

    Reopening a task *ripples forward*: any already-DONE task that (transitively)
    depends on a reopened target is also reopened, so the gate re-fires against freshly
    regenerated inputs rather than stale downstream artifacts (e.g. rejecting the
    release gate over a RedTeamX vulnerability re-runs RedTeamX *and* the InsightOps
    synthesis that consumes its report). Only the explicitly named targets count as
    rework cycles; rippled dependents simply re-execute. The gate returns to PENDING so
    it fires only after the reopened subgraph completes again. Unknown ids are ignored.
    """
    dependents: dict[str, list[str]] = {tid: [] for tid in state.tasks}
    for tid, t in state.tasks.items():
        for dep in t.spec.depends_on:
            if dep in dependents:
                dependents[dep].append(tid)

    explicit = {tid for tid in targets if tid in state.tasks and not state.tasks[tid].is_gate}

    # Forward transitive closure of the explicit targets.
    closure: set[str] = set()
    stack = list(explicit)
    while stack:
        tid = stack.pop()
        if tid in closure:
            continue
        closure.add(tid)
        for d in dependents.get(tid, []):
            if d not in closure:
                stack.append(d)

    for tid in closure:
        target = state.tasks[tid]
        if target.is_gate:
            continue  # other gates re-fire via their own dependency logic
        if tid not in explicit and target.state is not TaskState.DONE:
            continue  # don't disturb work that hasn't completed yet
        if tid in explicit:
            target.rework_count += 1
            target.last_decision = f"reopened for rework by gate '{gate.spec.id}'"
        else:
            target.last_decision = f"re-run: upstream rework rippled from gate '{gate.spec.id}'"
        target.state = TaskState.RUNNING
        target.end_clock = None
        target.in_flight = None

    gate.state = TaskState.PENDING
    gate.end_clock = None


def _maybe_persist(task: TaskRuntime, governor) -> None:
    if governor is None or SkillGovernor is None or task.is_gate:
        return
    with governor.task(task.spec.id) as gtask:
        for att in task.attempts:
            with gtask.run() as run:
                run.add_token_usage(att.token_usage)
                if att.success:
                    run.succeed()
                else:
                    run.fail(("; ".join(att.issues)) or "rejected")


# --------------------------------------------------------------------------- #
def is_complete(state: WorkflowState) -> bool:
    return all(t.state.is_terminal for t in state.tasks.values())
