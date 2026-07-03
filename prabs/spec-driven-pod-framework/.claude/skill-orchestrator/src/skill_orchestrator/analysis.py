"""Decision logic for skill results and gate approvals.

Goal: complete each phase within the time budget with the least rework. Skill rework
is curbed when time is tight; gate rejections can route specific upstream tasks back
for rework (the SpecPod remediation loop, e.g. RedTeamX VULNERABLE -> builder fixes).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Decision, TaskResult, TaskRuntime, WorkflowConfig


@dataclass
class AnalysisOutcome:
    decision: Decision
    skill_override: str | None = None
    rework_targets: list[str] = field(default_factory=list)
    reason: str = ""


def _effective_rework_budget(task: TaskRuntime, time_remaining: float, cfg: WorkflowConfig) -> int:
    budget = task.spec.rework_budget
    if cfg.time_budget_seconds <= 0:
        return budget
    if time_remaining <= 0:
        return 0
    if time_remaining < cfg.tight_time_fraction * cfg.time_budget_seconds:
        return min(budget, 1)
    return budget


def analyze(result: TaskResult, task: TaskRuntime, *, time_remaining: float, cfg: WorkflowConfig) -> AnalysisOutcome:
    # ---- Gate tasks: approve / reject ---- #
    if task.is_gate:
        if result.approved:
            return AnalysisOutcome(Decision.APPROVE, reason="gate approved")
        if result.rework_targets:
            return AnalysisOutcome(
                Decision.REJECT, rework_targets=list(result.rework_targets),
                reason=f"gate rejected; sending {len(result.rework_targets)} task(s) back for rework",
            )
        return AnalysisOutcome(Decision.REJECT, reason="gate rejected; no remediation path -> downstream blocked")

    # ---- Skill tasks: accept / retry / fail ---- #
    threshold = task.spec.accept_threshold
    passing = result.success and (result.score is None or result.score >= threshold)
    if passing:
        return AnalysisOutcome(Decision.ACCEPT, reason="result accepted")

    if task.rework_count >= _effective_rework_budget(task, time_remaining, cfg):
        return AnalysisOutcome(Decision.FAIL, reason="rejected and rework budget/time exhausted")

    return AnalysisOutcome(
        Decision.RETRY,
        skill_override=result.suggested_skill,
        reason=(
            "result rejected; re-running"
            + (f" with '{result.suggested_skill}'" if result.suggested_skill else "")
        ),
    )
