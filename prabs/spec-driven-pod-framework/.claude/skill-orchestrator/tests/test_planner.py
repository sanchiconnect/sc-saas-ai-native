"""Tests for plan mode (think first, act later)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_orchestrator import (
    PriceBook,
    build_state,
    is_complete,
    make_plan,
    next_wave,
    record_wave,
    render_report,
    write_plan,
)
from skill_orchestrator.models import TaskResult, TaskKind

SpecPod = Path(__file__).parent.parent / "examples" / "SpecPod"


def _spec():
    return {
        "name": "demo", "config": {"max_parallelism": 3, "default_rework_budget": 1},
        "tasks": [
            {"id": "g0", "name": "lock", "phase": "planning", "kind": "gate",
             "reviewer": "POD Lead", "produces": ["openspec.yaml"]},
            {"id": "plan-a", "name": "A", "phase": "planning", "kind": "skill", "skill": "a",
             "model": "claude-sonnet-4", "token_budget": 40000,
             "consumes": ["openspec.yaml"], "produces": ["a.yaml"]},
            {"id": "opt", "name": "Opt", "phase": "planning", "kind": "skill", "skill": "opt",
             "model": "claude-haiku-4-5", "token_budget": 20000, "optional": True,
             "consumes": ["openspec.yaml"], "produces": ["opt.md"]},
            {"id": "build-b", "name": "B", "phase": "build", "kind": "skill", "skill": "b",
             "model": "claude-opus-4", "token_budget": 100000, "consumes": ["a.yaml"],
             "produces": ["b.bundle"]},
        ],
    }


# --------------------------------------------------------------------------- #
def test_plan_estimates_tokens_and_cost():
    plan = make_plan(_spec(), requirements="build something")
    # tokens = 40k + 20k + 100k = 160k (gates cost nothing)
    assert plan.total_tokens == 160000
    assert plan.base_cost > 0
    assert plan.max_cost >= plan.base_cost  # rework ceiling >= base


def test_plan_pricebook_is_applied():
    cheap = PriceBook.from_dict({"prices": {}, "default": {"input_per_mtok": 0, "output_per_mtok": 0}})
    plan = make_plan(_spec(), pricebook=cheap)
    assert plan.base_cost == 0.0


def test_plan_dry_run_orders_waves_by_dependency():
    plan = make_plan(_spec())
    order = [w.task_ids for w in plan.waves]
    flat = [t for w in order for t in w]
    # gate first, then plan-a/opt, then build-b last
    assert flat[0] == "g0"
    assert flat.index("plan-a") < flat.index("build-b")


def test_optional_task_is_recommended_for_exclusion():
    plan = make_plan(_spec(), requirements="no special needs")
    exclude_recs = {(r.task_id, r.action) for r in plan.recommendations}
    assert ("opt", "exclude") in exclude_recs


def test_answer_drives_exclusion_and_reduces_cost():
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    base = make_plan(spec, requirements="plain CRUD service")
    # Answer the AI/diff questions 'no' -> drop optional AI/diff skills.
    answers = {"spec_diff": "no", "ai_features": "no"}
    pruned = make_plan(spec, requirements="plain CRUD service", answers=answers)
    assert "spec-impact-analyzer" in pruned.excluded_ids
    assert "prompt-bench" in pruned.excluded_ids
    assert pruned.base_cost < base.base_cost
    assert len(pruned.included_ids) < len(base.included_ids)


def test_status_needs_input_until_questions_answered():
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    p = make_plan(spec, requirements="x")
    assert p.status == "needs_input"
    assert p.questions  # at least one open question
    # answer them all
    answers = {q.id: (q.options[0] if q.options else "n/a") for q in p.questions}
    p2 = make_plan(spec, requirements="x", answers=answers)
    assert p2.status == "ready"
    assert p2.questions == []


def test_exclusion_orphan_guard_warns():
    # excluding plan-a strands build-b (which consumes a.yaml)
    plan = make_plan(_spec(), exclude={"plan-a"})
    assert any("build-b" in n and "plan-a" in n for n in plan.notes)


def test_explicit_include_overrides_answer_exclusion():
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    plan = make_plan(spec, requirements="x", answers={"ai_features": "no"}, include={"prompt-bench"})
    assert "prompt-bench" not in plan.excluded_ids


def test_finalized_config_is_runnable_by_engine(tmp_path):
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    answers = {q.id: (q.options[0] if q.options else "n/a")
               for q in make_plan(spec, requirements="x").questions}
    plan = make_plan(spec, requirements="x", answers=answers, include={"red-team-x"})
    assert plan.status == "ready"
    cfg_path = tmp_path / "run.json"
    written = write_plan(plan, spec, report_path=str(tmp_path / "r.md"), config_path=str(cfg_path))
    assert written["config"] is not None
    cfg = json.loads(cfg_path.read_text())
    assert "plan" in cfg  # provenance block
    # the persisted config builds and drives to completion
    state = build_state(cfg)
    guard = 0
    while True:
        guard += 1
        assert guard < 500
        wave = next_wave(state)
        if wave is None:
            break
        record_wave(state, [
            TaskResult(task_id=a.task_id, approved=True, duration_seconds=0) if a.kind is TaskKind.GATE
            else TaskResult(task_id=a.task_id, success=True, score=0.95, duration_seconds=1)
            for a in wave.actions
        ])
    assert is_complete(state)


def test_config_not_persisted_when_needs_input(tmp_path):
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    plan = make_plan(spec, requirements="x")  # questions unanswered
    cfg_path = tmp_path / "run.json"
    written = write_plan(plan, spec, report_path=str(tmp_path / "r.md"), config_path=str(cfg_path))
    assert written["config"] is None
    assert not cfg_path.exists()


def test_report_renders_key_sections():
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    md = render_report(make_plan(spec, requirements="x"))
    for heading in ("Implementation Plan", "Cost & effort estimate", "Execution plan",
                    "Required input specifications", "Price book in effect"):
        assert heading in md


def test_required_inputs_and_deliverables_detected():
    plan = make_plan(_spec())
    # openspec.yaml is produced by the gate -> not an external input
    assert "openspec.yaml" not in plan.required_input_specs
    assert "a.yaml" in plan.deliverables and "b.bundle" in plan.deliverables


def test_keyword_matching_ignores_substrings():
    # 'email'/'detail' contain 'ai' but must not trigger AI detection;
    # an explicit 'AI' mention should keep red-team-x recommended for inclusion.
    spec = json.loads((SpecPod / "SpecPod-sprint.workflow.json").read_text())
    no_ai = make_plan(spec, requirements="send email receipts with order detail")
    assert any(q.id == "ai_features" for q in no_ai.questions)  # not suppressed by 'email'/'detail'
    with_ai = make_plan(spec, requirements="an LLM extraction agent for documents")
    assert any(r.task_id == "red-team-x" and r.action == "include" for r in with_ai.recommendations)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
