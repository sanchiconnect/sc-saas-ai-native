"""Data models that encode the three governance dimensions.

The model layer is deliberately storage-agnostic and side-effect free. It captures:

1. **Tokens** -- via :class:`TokenUsage`, attached to each attempt and rolled up to the task.
2. **First-time-right** -- derived from the attempt sequence on :class:`TaskRecord`.
3. **Lifecycle** -- status plus ``start_time`` / ``end_time`` on both runs and tasks.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


# --------------------------------------------------------------------------- #
# Status enumerations
# --------------------------------------------------------------------------- #
class RunStatus(str, Enum):
    """Lifecycle state of a single execution attempt."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        return self in (RunStatus.SUCCEEDED, RunStatus.FAILED)


class TaskStatus(str, Enum):
    """Lifecycle state of a task (one or more attempts of a single skill)."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        return self in (TaskStatus.SUCCEEDED, TaskStatus.FAILED)


# --------------------------------------------------------------------------- #
# Token accounting
# --------------------------------------------------------------------------- #
@dataclass
class TokenUsage:
    """Token accounting for a single LLM round-trip or an aggregate.

    Cache tokens are tracked separately because they are billed differently and
    materially change the cost interpretation of a run; ``total_tokens`` sums all
    four buckets so downstream cost models can apply their own per-bucket pricing.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_read_tokens
            + self.cache_creation_tokens
        )

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        if not isinstance(other, TokenUsage):
            return NotImplemented
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_creation_tokens=self.cache_creation_tokens + other.cache_creation_tokens,
        )

    @classmethod
    def from_anthropic(cls, usage: Any) -> "TokenUsage":
        """Build from an Anthropic ``Usage`` object or an equivalent mapping.

        Accepts both the SDK object (attribute access) and a plain ``dict`` so it
        works whether the caller passes ``response.usage`` or ``response["usage"]``.
        """
        get = (
            usage.get
            if isinstance(usage, Mapping)
            else lambda k, d=0: getattr(usage, k, d)
        )
        return cls(
            input_tokens=int(get("input_tokens", 0) or 0),
            output_tokens=int(get("output_tokens", 0) or 0),
            cache_read_tokens=int(get("cache_read_input_tokens", 0) or 0),
            cache_creation_tokens=int(get("cache_creation_input_tokens", 0) or 0),
        )

    def to_dict(self) -> dict[str, int]:
        d = asdict(self)
        d["total_tokens"] = self.total_tokens
        return d


# --------------------------------------------------------------------------- #
# Single attempt
# --------------------------------------------------------------------------- #
@dataclass
class SkillRun:
    """One execution attempt of a skill within a task."""

    skill_name: str
    task_id: str
    attempt_number: int
    run_id: str = field(default_factory=lambda: _new_id("run"))
    status: RunStatus = RunStatus.PENDING
    start_time: datetime = field(default_factory=_utcnow)
    end_time: datetime | None = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds() * 1000.0

    @property
    def succeeded(self) -> bool:
        return self.status is RunStatus.SUCCEEDED

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "skill_name": self.skill_name,
            "attempt_number": self.attempt_number,
            "status": self.status.value,
            "start_time": _iso(self.start_time),
            "end_time": _iso(self.end_time),
            "duration_ms": self.duration_ms,
            "token_usage": self.token_usage.to_dict(),
            "error": self.error,
            "metadata": self.metadata,
        }


# --------------------------------------------------------------------------- #
# Task (groups attempts; this is where FTR lives)
# --------------------------------------------------------------------------- #
@dataclass
class TaskRecord:
    """A task is a single logical unit of work, executed via >=1 attempts.

    First-time-right is a property of the *task*, not the run: a task is FTR when
    its first and only terminal outcome was a success on attempt 1.
    """

    skill_name: str
    task_id: str = field(default_factory=lambda: _new_id("task"))
    status: TaskStatus = TaskStatus.PENDING
    start_time: datetime = field(default_factory=_utcnow)
    end_time: datetime | None = None
    attempts: list[SkillRun] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- lifecycle ------------------------------------------------------- #
    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds() * 1000.0

    # --- governance dimension 1: tokens ---------------------------------- #
    @property
    def total_token_usage(self) -> TokenUsage:
        total = TokenUsage()
        for attempt in self.attempts:
            total = total + attempt.token_usage
        return total

    # --- governance dimension 2: first-time-right ------------------------ #
    @property
    def first_time_right(self) -> bool:
        """True iff the task succeeded on its first attempt with no reruns."""
        return (
            self.status is TaskStatus.SUCCEEDED
            and self.attempt_count == 1
            and self.attempts[0].succeeded
        )

    @property
    def rerun_count(self) -> int:
        """Number of *additional* attempts beyond the first (0 when FTR)."""
        return max(self.attempt_count - 1, 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "skill_name": self.skill_name,
            "status": self.status.value,
            "start_time": _iso(self.start_time),
            "end_time": _iso(self.end_time),
            "duration_ms": self.duration_ms,
            "attempt_count": self.attempt_count,
            "rerun_count": self.rerun_count,
            "first_time_right": self.first_time_right,
            "total_token_usage": self.total_token_usage.to_dict(),
            "metadata": self.metadata,
            "attempts": [a.to_dict() for a in self.attempts],
        }
