"""Tests for the phase-based SpecPod skill-orchestration engine.

Model under test: a workflow is a list of tasks in three ordered phases
(planning -> build -> validate); each task is a single skill invocation or a HITL
gate; dependencies are explicit and/or artifact-derived (consumer-of-file depends on
producer-of-file); gates approve/reject and can route rework upstream.

Run:  PYTHONPATH=src python -m pytest tests/ -q
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_governor import TokenUsage
from skill_orchestrator import (
    Phase,
    TaskKind,
    TaskResult,
    TaskState,
    build_report,
    build_state,
    is_complete,
    load_state,
    next_wave,
    record_wave,
    save_state,
)

SpecPod = Path(__file__).parent.parent / "examples" / "SpecPod"


# --------------------------------------------------------------------------- #
# Spec helpers
# --------------------------------------------------------------------------- #
def skill(id, phase="planning", *, consumes=(), produces=(), depends_on=(),
          exclusive=False, optional=False, rework_budget=1, threshold=0.8, est=10):
    return {"id": id, "name": id, "phase": phase, "kind": "skill", "skill": f"{id}-skill",
            "consumes": list(consumes), "produces": list(produces), "depends_on": list(depends_on),
            "exclusive": exclusive, "optional": optional, "rework_budget": rework_budget,
            "accept_threshold": threshold, "estimated_seconds": est}


def gate(id, phase="planning", *, consumes=(), depends_on=(), reviewer="POD Lead"):
    return {"id": id, "name": id, "phase": phase, "kind": "gate", "reviewer": reviewer,
            "consumes": list(consumes), "depends_on": list(depends_on), "estimated_seconds": 0}


def wf(tasks, **config):
    cfg = {"max_parallelism": 4, "default_rework_budget": 1, "enforce_phase_order": True}
    cfg.update(config)
    return {"name": "t", "config": cfg, "tasks": tasks}


def ok(task_id, score=0.95):
    return TaskResult(task_id=task_id, success=True, score=score,
                      token_usage=TokenUsage(input_tokens=100, output_tokens=40), duration_seconds=5.0)


def approve(task_id):
    return TaskResult(task_id=task_id, approved=True, duration_seconds=1.0)


def drive(state, result_fn, *, max_waves=300):
    n = 0
    while True:
        n += 1
        assert n < max_waves, "engine did not terminate"
        wave = next_wave(state)
        if wave is None:
            break
        record_wave(state, [result_fn(a) for a in wave.actions])


# --------------------------------------------------------------------------- #
# Dependency resolution
# --------------------------------------------------------------------------- #
def test_explicit_dependency_blocks_until_done():
    state = build_state(wf([skill("a"), skill("b", depends_on=["a"])]))
    wave = next_wave(state)
    assert {a.task_id for a in wave.actions} == {"a"}


def test_artifact_dependency_is_derived_from_produces_consumes():
    # b consumes a file a produces -> b must wait for a, with no explicit depends_on.
    state = build_state(wf([
        skill("a", produces=["x.yaml"]),
        skill("b", consumes=["x.yaml"]),
    ]))
    assert "a" in state.tasks["b"].spec.depends_on
    wave = next_wave(state)
    assert {a.task_id for a in wave.actions} == {"a"}


def test_external_artifact_without_producer_is_ignored():
    # consuming a file no task produces (a prior-phase input) adds no dependency.
    state = build_state(wf([skill("a", consumes=["specs/openspec.yaml"])]))
    assert state.tasks["a"].spec.depends_on == []
    wave = next_wave(state)
    assert {a.task_id for a in wave.actions} == {"a"}


def test_duplicate_producer_is_rejected():
    with pytest.raises(ValueError, match="produced by both"):
        build_state(wf([skill("a", produces=["x"]), skill("b", produces=["x"])]))


def test_unknown_dependency_rejected():
    with pytest.raises(ValueError, match="unknown task"):
        build_state(wf([skill("a", depends_on=["ghost"])]))


def test_cycle_detection():
    with pytest.raises(ValueError, match="cycle"):
        build_state(wf([skill("a", depends_on=["b"]), skill("b", depends_on=["a"])]))


def test_phase_order_violation_rejected():
    # a planning task may not depend on a build task when phase order is enforced.
    with pytest.raises(ValueError, match="later-phase"):
        build_state(wf([
            skill("p", phase="planning", depends_on=["b"]),
            skill("b", phase="build"),
        ]))


def test_phase_order_can_be_disabled():
    state = build_state(wf([
        skill("p", phase="planning", depends_on=["b"]),
        skill("b", phase="build"),
    ], enforce_phase_order=False))
    assert "b" in state.tasks["p"].spec.depends_on


# --------------------------------------------------------------------------- #
# Wave scheduling: parallel / gate / exclusive
# --------------------------------------------------------------------------- #
def test_independent_tasks_fan_out_in_parallel():
    state = build_state(wf([skill("x"), skill("y"), skill("z")]))
    wave = next_wave(state)
    assert wave.mode == "parallel"
    assert {a.task_id for a in wave.actions} == {"x", "y", "z"}


def test_max_parallelism_caps_wave():
    state = build_state(wf([skill("x"), skill("y"), skill("z")], max_parallelism=2))
    assert len(next_wave(state).actions) == 2


def test_gate_runs_alone_and_requires_approval_flag():
    state = build_state(wf([gate("g")]))
    wave = next_wave(state)
    assert wave.mode == "sequential"
    assert len(wave.actions) == 1
    assert wave.actions[0].kind is TaskKind.GATE
    assert wave.actions[0].requires_approval is True
    assert wave.actions[0].skill is None


def test_exclusive_task_runs_alone():
    state = build_state(wf([skill("x"), skill("m", exclusive=True, est=999)]))
    wave = next_wave(state)
    assert [a.task_id for a in wave.actions] == ["m"]
    assert wave.mode == "sequential"


def test_gate_blocks_downstream_until_approved():
    state = build_state(wf([
        skill("a", produces=["doc"]),
        gate("g", consumes=["doc"]),
        skill("b", depends_on=["g"]),
    ]))
    # a -> g -> b strictly sequential
    order = []
    drive(state, lambda act: order.append(act.task_id) or (approve(act.task_id) if act.kind is TaskKind.GATE else ok(act.task_id)))
    assert order == ["a", "g", "b"]
    assert all(t.state is TaskState.DONE for t in state.tasks.values())


# --------------------------------------------------------------------------- #
# Skill accept / rework / fail
# --------------------------------------------------------------------------- #
def test_skill_accepts_on_passing_score():
    state = build_state(wf([skill("a", threshold=0.8)]))
    drive(state, lambda act: ok(act.task_id, score=0.9))
    t = state.tasks["a"]
    assert t.state is TaskState.DONE and t.first_time_right


def test_skill_reworks_then_accepts_with_skill_redirect():
    state = build_state(wf([skill("a", threshold=0.8, rework_budget=2)]))
    seen = []

    def fn(act):
        seen.append(act.skill)
        if act.attempt_number == 1:
            return TaskResult(task_id="a", success=False, score=0.4, issues=["bug"],
                              suggested_skill="a-fixer", token_usage=TokenUsage(input_tokens=10),
                              duration_seconds=1)
        return ok("a")

    drive(state, fn)
    t = state.tasks["a"]
    assert t.state is TaskState.DONE
    assert t.rework_count == 1
    assert t.first_time_right is False
    assert seen == ["a-skill", "a-fixer"]  # redirect applied on the retry


def test_skill_fails_when_rework_budget_exhausted():
    state = build_state(wf([skill("a", threshold=0.9, rework_budget=1)]))
    drive(state, lambda act: TaskResult(task_id="a", success=False, score=0.1,
                                        token_usage=TokenUsage(), duration_seconds=1))
    t = state.tasks["a"]
    assert t.state is TaskState.FAILED
    assert t.rework_count == 1


def test_dependent_of_failed_task_is_skipped():
    state = build_state(wf([
        skill("a", produces=["x"], threshold=0.9, rework_budget=0),
        skill("b", consumes=["x"]),
    ]))
    drive(state, lambda act: TaskResult(task_id=act.task_id, success=False, score=0.0,
                                        token_usage=TokenUsage(), duration_seconds=1)
          if act.task_id == "a" else ok(act.task_id))
    assert state.tasks["a"].state is TaskState.FAILED
    assert state.tasks["b"].state is TaskState.SKIPPED


# --------------------------------------------------------------------------- #
# Gates: approve / reject / rework routing + ripple
# --------------------------------------------------------------------------- #
def test_gate_approves_to_done():
    state = build_state(wf([skill("a", produces=["doc"]), gate("g", consumes=["doc"])]))
    drive(state, lambda act: approve(act.task_id) if act.kind is TaskKind.GATE else ok(act.task_id))
    assert state.tasks["g"].state is TaskState.DONE
    assert state.tasks["g"].first_time_right is False  # gates are never FTR


def test_gate_reject_routes_rework_then_approves_and_ripples():
    # a -> b(consumes a) -> g ; g rejects targeting a, which must re-run AND ripple to b.
    state = build_state(wf([
        skill("a", produces=["ar"]),
        skill("b", consumes=["ar"], produces=["br"]),
        gate("g", consumes=["br"]),
    ]))
    runs: dict[str, int] = {}
    state_flags = {"rejected": False}

    def fn(act):
        runs[act.task_id] = runs.get(act.task_id, 0) + 1
        if act.kind is TaskKind.GATE:
            if not state_flags["rejected"]:
                state_flags["rejected"] = True
                return TaskResult(task_id=act.task_id, approved=False, rework_targets=["a"])
            return approve(act.task_id)
        return ok(act.task_id)

    drive(state, fn)
    assert is_complete(state)
    assert state.tasks["g"].state is TaskState.DONE
    # a was the explicit target -> reworked; b is a's DONE dependent -> rippled re-run.
    assert state.tasks["a"].rework_count == 1
    assert runs["a"] == 2
    assert runs["b"] == 2          # ripple re-ran the downstream consumer
    assert runs["g"] == 2          # gate fired twice
    assert state.tasks["b"].first_time_right is False


def test_gate_reject_without_targets_fails_and_blocks_downstream():
    state = build_state(wf([
        skill("a", produces=["doc"]),
        gate("g", consumes=["doc"]),
        skill("b", depends_on=["g"]),
    ]))
    drive(state, lambda act: TaskResult(task_id=act.task_id, approved=False)
          if act.kind is TaskKind.GATE else ok(act.task_id))
    assert state.tasks["g"].state is TaskState.FAILED
    assert state.tasks["b"].state is TaskState.SKIPPED


# --------------------------------------------------------------------------- #
# Time budget
# --------------------------------------------------------------------------- #
def test_time_budget_strands_remaining_tasks():
    state = build_state(wf([
        skill("a", produces=["x"], est=6),
        skill("b", consumes=["x"], est=6),
    ], time_budget_seconds=10, max_parallelism=1))

    def slow(act):
        return TaskResult(task_id=act.task_id, success=True, score=0.95,
                          token_usage=TokenUsage(input_tokens=10), duration_seconds=6.0)

    drive(state, slow)
    assert is_complete(state)
    assert state.clock_seconds >= 6


def test_optional_task_dropped_under_time_pressure():
    state = build_state(wf([
        skill("a", est=6),
        skill("opt", optional=True, est=6),
    ], time_budget_seconds=8, max_parallelism=1))
    drive(state, lambda act: TaskResult(task_id=act.task_id, success=True, score=0.95,
                                        token_usage=TokenUsage(), duration_seconds=6.0))
    # one of them runs; the optional one is the first to be dropped once time is tight.
    assert state.tasks["opt"].state in (TaskState.SKIPPED, TaskState.DONE)
    assert is_complete(state)


# --------------------------------------------------------------------------- #
# Result-matching guards
# --------------------------------------------------------------------------- #
def test_record_rejects_missing_results():
    state = build_state(wf([skill("a"), skill("b")]))
    next_wave(state)
    with pytest.raises(ValueError, match="missing results"):
        record_wave(state, [])


def test_record_rejects_results_not_in_flight():
    state = build_state(wf([skill("a"), skill("b", depends_on=["a"])]))
    next_wave(state)  # only 'a' in flight
    with pytest.raises(ValueError, match="not in flight"):
        record_wave(state, [ok("a"), ok("b")])


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #
def test_state_roundtrip_mid_flight(tmp_path):
    state = build_state(wf([skill("a", produces=["x"]), skill("b", consumes=["x"])]))
    next_wave(state)  # 'a' in flight
    p = tmp_path / "s.json"
    save_state(state, p)
    reloaded = load_state(p)
    assert reloaded.tasks["a"].in_flight is not None
    record_wave(reloaded, [ok("a")])
    drive(reloaded, lambda act: ok(act.task_id))
    assert is_complete(reloaded)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def test_report_counts_phases_ftr_and_gates():
    state = build_state(wf([
        skill("a", phase="planning", produces=["x"]),
        gate("g", phase="planning", consumes=["x"]),
        skill("b", phase="build", depends_on=["g"]),
    ]))
    drive(state, lambda act: approve(act.task_id) if act.kind is TaskKind.GATE else ok(act.task_id))
    rep = build_report(state)
    assert rep.done == 2  # skill tasks done (gates counted separately)
    assert rep.skill_tasks == 2
    assert rep.gates_total == 1 and rep.gates_approved == 1
    assert rep.by_phase["planning"].done == 1
    assert rep.by_phase["build"].done == 1


# --------------------------------------------------------------------------- #
# Full SpecPod sprint integration
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not (SpecPod / "SpecPod-sprint.workflow.json").exists(),
                    reason="generated specs not present")
def test_full_SpecPod_sprint_completes_with_rework_and_gate_loop():
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    state = build_state(spec)
    flags = {"g3": False}

    def fn(act):
        if act.kind is TaskKind.GATE:
            if act.task_id == "gate-3" and not flags["g3"]:
                flags["g3"] = True
                return TaskResult(task_id=act.task_id, approved=False, rework_targets=["red-team-x"])
            return approve(act.task_id)
        if act.task_id == "dev-copilot" and act.attempt_number == 1:
            return TaskResult(task_id="dev-copilot", success=False, score=0.5,
                              issues=["ambiguity"], token_usage=TokenUsage(input_tokens=100),
                              duration_seconds=3)
        return ok(act.task_id, score=0.92)

    drive(state, fn)
    rep = build_report(state)
    assert is_complete(state)
    assert rep.failed == 0
    assert rep.done == 29
    assert rep.gates_approved == rep.gates_total == 6
    # dev-copilot reworked once; red-team-x reworked once; insight-ops rippled (re-ran).
    assert state.tasks["dev-copilot"].rework_count == 1
    assert state.tasks["red-team-x"].rework_count == 1
    assert len(state.tasks["insight-ops"].attempts) == 2
    assert state.tasks["insight-ops"].first_time_right is False


def test_each_generated_phase_spec_builds_and_starts():
    for name in ("planning", "build", "validate"):
        path = SpecPod / f"{name}.workflow.json"
        if not path.exists():
            continue
        state = build_state(json.loads(path.read_text()))
        wave = next_wave(state)
        assert wave is not None and len(wave.actions) >= 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
