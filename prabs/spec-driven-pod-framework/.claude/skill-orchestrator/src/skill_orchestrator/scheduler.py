"""Scheduling: choose the next wave of actions.

- resolve dependencies; cascade SKIPPED through dependents of failed/skipped tasks;
- order ready work by phase (earlier phases first), then critical path, then
  required-before-optional;
- pack independent skill tasks up to ``max_parallelism`` into one parallel wave;
- give gates and ``exclusive`` tasks their own sequential wave;
- stop launching new work once the time budget is spent.
"""

from __future__ import annotations

from .models import (
    Action,
    PHASE_INDEX,
    Phase,
    TaskKind,
    TaskRuntime,
    TaskState,
    WaveDispatch,
    WorkflowState,
)


def compute_critical_paths(state: WorkflowState) -> None:
    tasks = state.tasks
    dependents: dict[str, list[str]] = {tid: [] for tid in tasks}
    for tid, t in tasks.items():
        for dep in t.spec.depends_on:
            if dep in dependents:
                dependents[dep].append(tid)

    memo: dict[str, float] = {}
    visiting: set[str] = set()

    def cp(tid: str) -> float:
        if tid in memo:
            return memo[tid]
        if tid in visiting:
            return tasks[tid].spec.estimated_seconds
        visiting.add(tid)
        own = tasks[tid].spec.estimated_seconds
        downstream = max((cp(d) for d in dependents[tid]), default=0.0)
        visiting.discard(tid)
        memo[tid] = own + downstream
        return memo[tid]

    for tid, t in tasks.items():
        t.critical_path = cp(tid)


def _deps_satisfied(task: TaskRuntime, state: WorkflowState) -> bool:
    return all(
        dep in state.tasks and state.tasks[dep].state is TaskState.DONE
        for dep in task.spec.depends_on
    )


def _dep_failed(task: TaskRuntime, state: WorkflowState) -> bool:
    return any(
        dep not in state.tasks or state.tasks[dep].state in (TaskState.FAILED, TaskState.SKIPPED)
        for dep in task.spec.depends_on
    )


def cascade_blocked(state: WorkflowState) -> None:
    changed = True
    while changed:
        changed = False
        for task in state.tasks.values():
            if task.state is TaskState.PENDING and task.in_flight is None and _dep_failed(task, state):
                task.state = TaskState.SKIPPED
                task.last_decision = "skipped: an upstream dependency did not complete"
                changed = True


def _ready(state: WorkflowState) -> list[TaskRuntime]:
    ready: list[TaskRuntime] = []
    for task in state.tasks.values():
        if task.in_flight is not None or task.state.is_terminal:
            continue
        if task.state is TaskState.PENDING and not _deps_satisfied(task, state):
            continue
        if task.state is TaskState.RUNNING and not _deps_satisfied(task, state):
            # a gate re-queued for rework waits for its targets to finish again
            continue
        ready.append(task)
    return ready


def _make_action(task: TaskRuntime) -> Action:
    is_gate = task.is_gate
    return Action(
        task_id=task.spec.id,
        task_name=task.spec.name,
        phase=task.spec.phase,
        kind=task.spec.kind,
        attempt_number=len(task.attempts) + 1,
        skill=(None if is_gate else task.skill_for()),
        model=task.spec.model,
        requires_approval=is_gate,
        reviewer=task.spec.reviewer,
        exclusive=task.spec.exclusive or is_gate,
        estimated_seconds=task.spec.estimated_seconds,
        token_budget=task.spec.token_budget,
        consumes=task.spec.consumes,
        produces=task.spec.produces,
        context={
            "rework_count": task.rework_count,
            "rework_budget": task.spec.rework_budget,
            "accept_threshold": task.spec.accept_threshold,
            "is_rework": (len(task.attempts) > 0),
            "depends_on": task.spec.depends_on,
            "note": task.spec.note,
        },
    )


def next_wave(state: WorkflowState) -> WaveDispatch | None:
    cascade_blocked(state)

    if state.config.time_budget_seconds > 0 and state.time_remaining <= 0:
        _strand_remaining(state, reason="time budget exhausted")
        return None

    ready = _ready(state)
    if not ready:
        if any(not t.state.is_terminal for t in state.tasks.values()):
            _strand_remaining(state, reason="no runnable tasks (dependency stall)")
        return None

    # phase first, then critical path, required-before-optional, larger estimate.
    ready.sort(key=lambda t: (
        PHASE_INDEX[t.spec.phase], -t.critical_path, t.spec.optional, -t.spec.estimated_seconds, t.spec.id
    ))

    max_par = max(1, state.config.max_parallelism)
    head = ready[0]
    chosen: list[TaskRuntime]

    if head.is_gate or head.spec.exclusive:
        chosen = [head]
        mode = "sequential"
    else:
        chosen = []
        for task in ready:
            if task.is_gate or task.spec.exclusive:
                continue
            if (
                state.config.time_budget_seconds > 0
                and task.state is TaskState.PENDING
                and task.spec.optional
                and state.time_remaining < task.spec.estimated_seconds
            ):
                task.state = TaskState.SKIPPED
                task.last_decision = "skipped: optional task dropped under time pressure"
                continue
            chosen.append(task)
            if len(chosen) >= max_par:
                break
        mode = "parallel" if len(chosen) > 1 else "sequential"

    if not chosen:
        if any(not t.state.is_terminal for t in state.tasks.values()):
            _strand_remaining(state, reason="no eligible tasks within time budget")
        return None

    actions: list[Action] = []
    for task in chosen:
        if task.state is TaskState.PENDING:
            task.state = TaskState.RUNNING
            if task.start_clock is None:
                task.start_clock = state.clock_seconds
        action = _make_action(task)
        task.in_flight = action
        actions.append(action)

    state.wave_index += 1
    wave_phase = chosen[0].spec.phase
    gate_note = "HITL gate: route to the reviewer for approval" if chosen[0].is_gate else None
    return WaveDispatch(
        wave_index=state.wave_index,
        mode=mode,
        phase=wave_phase,
        actions=actions,
        clock_seconds=state.clock_seconds,
        time_remaining_seconds=state.time_remaining,
        note=gate_note or ("run these actions concurrently" if mode == "parallel" else "run this action alone"),
    )


def _strand_remaining(state: WorkflowState, *, reason: str) -> None:
    for task in state.tasks.values():
        if not task.state.is_terminal:
            task.state = TaskState.SKIPPED
            task.end_clock = state.clock_seconds
            task.last_decision = f"skipped: {reason}"
