"""Drive the combined SpecPod sprint workflow end-to-end with simulated results.

Stands in for Claude Code's subagents: fabricates a TaskResult per dispatched action
and an approval per gate. Demonstrates phase ordering (planning -> build -> validate),
parallel fan-out within a phase, HITL gates, a skill rework (DevCopilot fails review
once), and a gate-driven remediation loop (Gate 3 rejects once and sends RedTeamX back).

Run:  PYTHONPATH=../../src python run_sprint.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from skill_governor import TokenUsage
from skill_orchestrator import (
    Phase,
    TaskResult,
    build_report,
    build_state,
    format_report,
    is_complete,
    next_wave,
    record_wave,
)

HERE = Path(__file__).parent


def simulate(action_dict: dict, *, rng: random.Random, memo: dict) -> TaskResult:
    tid = action_dict["task_id"]
    kind = action_dict["kind"]
    attempt = action_dict["attempt_number"]

    if kind == "gate":
        # Gate 3 rejects once, routing RedTeamX back for remediation; everything else approves.
        if tid == "gate-3" and not memo.get("gate3_rejected_once"):
            memo["gate3_rejected_once"] = True
            return TaskResult(task_id=tid, approved=False, rework_targets=["red-team-x"],
                              note="VULNERABLE finding in adversarial report; remediate before release")
        return TaskResult(task_id=tid, approved=True, note="approved by reviewer")

    # Skill action: budget-proportional token usage; DevCopilot fails its first review cycle.
    budget = action_dict.get("token_budget") or 30000
    usage = TokenUsage(input_tokens=int(budget * rng.uniform(0.45, 0.7)),
                       output_tokens=int(budget * rng.uniform(0.15, 0.3)))
    duration = max(1.0, budget / 6000 * rng.uniform(0.8, 1.2))

    if tid == "dev-copilot" and attempt == 1:
        return TaskResult(task_id=tid, success=False, score=0.55,
                          issues=["spec ambiguity in REQ-API-003"], suggested_skill="dev-copilot",
                          token_usage=usage, duration_seconds=duration, note="escalated ambiguity")

    score = rng.uniform(0.86, 0.99)
    return TaskResult(task_id=tid, success=True, score=score,
                      token_usage=usage, duration_seconds=duration, note="ok")


def main() -> None:
    rng = random.Random(7)
    memo: dict = {}
    spec = json.loads((HERE / "SpecPod-sprint.workflow.json").read_text())
    state = build_state(spec)

    print(f"SpecPod sprint '{state.name}': "
          f"{sum(1 for t in state.tasks.values() if not t.is_gate)} skills + "
          f"{sum(1 for t in state.tasks.values() if t.is_gate)} gates\n")

    seen_phases: set = set()
    wave_no = 0
    while True:
        wave = next_wave(state)
        if wave is None:
            break
        wave_no += 1
        phases_here = sorted({a.phase.value for a in wave.actions}, key=lambda p: p)
        new = [p for p in phases_here if p not in seen_phases]
        for p in new:
            print(f"\n===== PHASE BEGINS: {p.upper()} =====")
            seen_phases.add(p)
        kind_tag = "GATE" if wave.actions[0].kind.value == "gate" else wave.mode
        phase_tag = "+".join(p[:4] for p in phases_here)
        labels = ", ".join(a.task_id for a in wave.actions)
        print(f"  wave {wave_no:2} [{kind_tag:10}] ({phase_tag:>9}) {labels}")
        results = [simulate(a.to_dict(), rng=rng, memo=memo) for a in wave.actions]
        for n in record_wave(state, results):
            if "rework" in n or "reject" in n or "retry" in n:
                print(f"       ! {n}")

    print()
    print(format_report(build_report(state)))
    print("complete =", is_complete(state))


if __name__ == "__main__":
    main()
