"""Demonstrate plan mode end-to-end on the combined SpecPod sprint.

Pass 1 analyzes a thin requirements statement and surfaces clarifying questions.
Pass 2 supplies answers, finalizes the plan, prints the markdown report, and persists
a run config that `orchestrator init` can consume directly.

Run:  PYTHONPATH=../../src python plan_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from skill_orchestrator import make_plan, render_report, write_plan

HERE = Path(__file__).parent


def main() -> None:
    spec = json.loads((HERE / "SpecPod-sprint.workflow.json").read_text())
    requirements = (
        "Build an internal expense-approval service: a REST API plus a web UI, backed by "
        "Postgres. Standard CRUD and an approvals workflow, conventional application logic "
        "only. Must handle 1000 concurrent users with p95 latency under 300 ms."
    )

    print("=" * 74)
    print("PASS 1 — analyze requirements, surface questions")
    print("=" * 74)
    plan1 = make_plan(spec, requirements=requirements)
    print(f"status: {plan1.status}")
    print(f"estimate: {plan1.total_tokens:,} tokens, "
          f"{plan1.base_cost:.2f}-{plan1.max_cost:.2f} {plan1.currency}, "
          f"makespan ~{plan1.makespan_estimate_seconds:.0f}s")
    print("open questions:")
    for q in plan1.questions:
        print(f"  [{q.id}] {q.question}"
              + (f"  options={q.options}" if q.options else "  (free text)"))
    print("recommendations:")
    for r in plan1.recommendations:
        print(f"  {r.action.upper()} {r.task_id} — {r.reason}")

    print()
    print("=" * 74)
    print("PASS 2 — answer questions, finalize, persist run config")
    print("=" * 74)
    answers = {
        "spec_diff": "no",            # greenfield -> drop SpecImpactAnalyzer
        "ai_features": "no",          # no AI -> drop PromptBench
        "ai_facing": "no",            # no AI-facing components
        "nfr_targets": "1000 concurrent users, p95 < 300ms, error rate < 0.5%",
        "golden_refs": "will-provide-at-runtime",
    }
    # Keep red-team-x/insight-ops coherent: with no AI we still keep RedTeamX so the
    # InsightOps synthesis has all five inputs (excluding it would be flagged).
    plan2 = make_plan(spec, requirements=requirements, answers=answers, include={"red-team-x"})
    out = write_plan(plan2, spec,
                     report_path=str(HERE / "plan-report.md"),
                     config_path=str(HERE / "run-config.json"))
    print(f"status: {plan2.status}")
    print(f"excluded: {plan2.excluded_ids}")
    print(f"estimate: {plan2.total_tokens:,} tokens, {plan2.base_cost:.2f} {plan2.currency} "
          f"(max w/ rework {plan2.max_cost:.2f})")
    print(f"written: {out}")
    print()
    print(render_report(plan2))


if __name__ == "__main__":
    main()
