"""Aggregation of stored tasks into governance metrics.

This is where the three captured dimensions become decision-grade numbers:
token spend, first-time-right rate, and task throughput/latency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import TaskRecord, TaskStatus, TokenUsage


def _percentile(values: list[float], pct: float) -> float | None:
    """Nearest-rank percentile (no interpolation) -- robust for small samples."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = max(1, min(len(ordered), round(pct / 100.0 * len(ordered))))
    return ordered[rank - 1]


def _safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


@dataclass
class SkillMetrics:
    """Aggregated governance metrics for a single skill (or all skills)."""

    skill_name: str
    total_tasks: int = 0
    succeeded_tasks: int = 0
    failed_tasks: int = 0

    # Dimension 1: tokens
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    # Dimension 2: first-time-right
    first_time_right_count: int = 0
    rerun_count: int = 0  # total extra attempts across tasks

    # Dimension 3: lifecycle / timing
    total_attempts: int = 0
    duration_samples_ms: list[float] = field(default_factory=list)

    # --- derived rates --------------------------------------------------- #
    @property
    def success_rate(self) -> float:
        return _safe_div(self.succeeded_tasks, self.total_tasks)

    @property
    def first_time_right_rate(self) -> float:
        """FTR rate over *all* tasks (the headline governance KPI)."""
        return _safe_div(self.first_time_right_count, self.total_tasks)

    @property
    def first_time_right_rate_of_successful(self) -> float:
        """FTR rate measured only over tasks that eventually succeeded."""
        return _safe_div(self.first_time_right_count, self.succeeded_tasks)

    @property
    def avg_attempts_per_task(self) -> float:
        return _safe_div(self.total_attempts, self.total_tasks)

    @property
    def total_tokens(self) -> int:
        return self.token_usage.total_tokens

    @property
    def avg_tokens_per_task(self) -> float:
        return _safe_div(self.total_tokens, self.total_tasks)

    @property
    def total_duration_ms(self) -> float:
        return sum(self.duration_samples_ms)

    @property
    def avg_duration_ms(self) -> float:
        return _safe_div(self.total_duration_ms, len(self.duration_samples_ms))

    @property
    def p50_duration_ms(self) -> float | None:
        return _percentile(self.duration_samples_ms, 50)

    @property
    def p95_duration_ms(self) -> float | None:
        return _percentile(self.duration_samples_ms, 95)

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "total_tasks": self.total_tasks,
            "succeeded_tasks": self.succeeded_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": round(self.success_rate, 4),
            "first_time_right_count": self.first_time_right_count,
            "first_time_right_rate": round(self.first_time_right_rate, 4),
            "first_time_right_rate_of_successful": round(
                self.first_time_right_rate_of_successful, 4
            ),
            "rerun_count": self.rerun_count,
            "total_attempts": self.total_attempts,
            "avg_attempts_per_task": round(self.avg_attempts_per_task, 4),
            "tokens": {
                **self.token_usage.to_dict(),
                "avg_tokens_per_task": round(self.avg_tokens_per_task, 2),
            },
            "duration_ms": {
                "total": round(self.total_duration_ms, 2),
                "avg": round(self.avg_duration_ms, 2),
                "p50": (round(self.p50_duration_ms, 2) if self.p50_duration_ms else None),
                "p95": (round(self.p95_duration_ms, 2) if self.p95_duration_ms else None),
            },
        }

    def _ingest(self, task: TaskRecord) -> None:
        self.total_tasks += 1
        if task.status is TaskStatus.SUCCEEDED:
            self.succeeded_tasks += 1
        elif task.status is TaskStatus.FAILED:
            self.failed_tasks += 1
        self.token_usage = self.token_usage + task.total_token_usage
        if task.first_time_right:
            self.first_time_right_count += 1
        self.rerun_count += task.rerun_count
        self.total_attempts += task.attempt_count
        if task.duration_ms is not None:
            self.duration_samples_ms.append(task.duration_ms)


@dataclass
class GovernanceReport:
    """Top-level report: overall metrics plus a per-skill breakdown."""

    overall: SkillMetrics
    by_skill: dict[str, SkillMetrics]

    def to_dict(self) -> dict:
        return {
            "overall": self.overall.to_dict(),
            "by_skill": {name: m.to_dict() for name, m in self.by_skill.items()},
        }


def aggregate(tasks: Iterable[TaskRecord]) -> GovernanceReport:
    """Fold a collection of tasks into an overall + per-skill report."""
    overall = SkillMetrics(skill_name="__all__")
    by_skill: dict[str, SkillMetrics] = {}
    for task in tasks:
        overall._ingest(task)
        bucket = by_skill.setdefault(task.skill_name, SkillMetrics(skill_name=task.skill_name))
        bucket._ingest(task)
    return GovernanceReport(overall=overall, by_skill=by_skill)
