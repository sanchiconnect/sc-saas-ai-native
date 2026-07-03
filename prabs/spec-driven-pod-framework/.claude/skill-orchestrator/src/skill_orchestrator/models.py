"""Domain models for the phase-based skill-orchestration engine.

A **workflow** is a list of **tasks** grouped into three **phases** that run in order:
``planning -> build -> validate``. Each task is one of:

- a **skill** task -- a single AI-native skill invocation that *consumes* and *produces*
  artifact files and may be reworked if its result is rejected; or
- a **gate** task -- a Human-in-the-loop (HITL) checkpoint (e.g. SpecPod Gate 0/1/2/3)
  that must be *approved* before the tasks behind it may run, and can send specific
  upstream tasks back for rework when rejected.

Dependencies are explicit (``depends_on``) and/or derived from the artifact contract
(a task that consumes file X depends on the task that produces X). Telemetry
primitives (``TokenUsage``) come from the vendored ``skill_governor`` package, so the
governance dimensions -- tokens, first-time-right, lifecycle -- carry over unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from skill_governor import TokenUsage


# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #
class Phase(str, Enum):
    PLANNING = "planning"
    BUILD = "build"
    VALIDATE = "validate"


PHASE_ORDER: tuple[Phase, ...] = (Phase.PLANNING, Phase.BUILD, Phase.VALIDATE)
PHASE_INDEX: dict[Phase, int] = {p: i for i, p in enumerate(PHASE_ORDER)}


class TaskKind(str, Enum):
    SKILL = "skill"   # an AI skill invocation
    GATE = "gate"     # a HITL approval checkpoint


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"

    @property
    def is_terminal(self) -> bool:
        return self in (TaskState.DONE, TaskState.FAILED, TaskState.SKIPPED)


class Decision(str, Enum):
    ACCEPT = "accept"     # skill result good enough -> done
    RETRY = "retry"       # re-run the skill (optionally a different skill)
    FAIL = "fail"         # exhausted rework budget / time
    APPROVE = "approve"   # gate approved -> done
    REJECT = "reject"     # gate rejected -> rework targets or fail


# --------------------------------------------------------------------------- #
# Result reported by the agent for one dispatched action
# --------------------------------------------------------------------------- #
@dataclass
class TaskResult:
    """What Claude Code reports after running one action.

    For **skill** tasks, ``success`` / ``score`` / ``issues`` / ``suggested_skill`` drive
    the accept-or-rework decision. For **gate** tasks, ``approved`` (and optionally
    ``rework_targets``) drive the approve-or-reject decision.
    """

    task_id: str
    success: bool = True
    score: float | None = None
    issues: list[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    duration_seconds: float = 0.0
    suggested_skill: str | None = None
    # gate-specific
    approved: bool | None = None
    rework_targets: list[str] = field(default_factory=list)
    note: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TaskResult":
        tu = d.get("token_usage", {}) or {}
        return cls(
            task_id=d["task_id"],
            success=bool(d.get("success", True)),
            score=d.get("score"),
            issues=list(d.get("issues", [])),
            token_usage=TokenUsage(
                input_tokens=int(tu.get("input_tokens", 0) or 0),
                output_tokens=int(tu.get("output_tokens", 0) or 0),
                cache_read_tokens=int(tu.get("cache_read_tokens", 0) or 0),
                cache_creation_tokens=int(tu.get("cache_creation_tokens", 0) or 0),
            ),
            duration_seconds=float(d.get("duration_seconds", 0.0) or 0.0),
            suggested_skill=d.get("suggested_skill"),
            approved=d.get("approved"),
            rework_targets=list(d.get("rework_targets", [])),
            note=d.get("note"),
        )


@dataclass
class TaskAttempt:
    attempt_number: int
    skill: str                      # the skill name, or "<gate>" for gates
    success: bool
    score: float | None = None
    issues: list[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    duration_seconds: float = 0.0
    approved: bool | None = None
    started_clock: float = 0.0
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "skill": self.skill,
            "success": self.success,
            "score": self.score,
            "issues": self.issues,
            "token_usage": self.token_usage.to_dict(),
            "duration_seconds": self.duration_seconds,
            "approved": self.approved,
            "started_clock": self.started_clock,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TaskAttempt":
        tu = d.get("token_usage", {}) or {}
        return cls(
            attempt_number=d["attempt_number"],
            skill=d["skill"],
            success=d["success"],
            score=d.get("score"),
            issues=list(d.get("issues", [])),
            token_usage=TokenUsage(
                input_tokens=tu.get("input_tokens", 0),
                output_tokens=tu.get("output_tokens", 0),
                cache_read_tokens=tu.get("cache_read_tokens", 0),
                cache_creation_tokens=tu.get("cache_creation_tokens", 0),
            ),
            duration_seconds=d.get("duration_seconds", 0.0),
            approved=d.get("approved"),
            started_clock=d.get("started_clock", 0.0),
            note=d.get("note"),
        )


# --------------------------------------------------------------------------- #
# Static task configuration
# --------------------------------------------------------------------------- #
@dataclass
class TaskSpec:
    id: str
    name: str
    phase: Phase
    kind: TaskKind = TaskKind.SKILL
    skill: str | None = None
    model: str | None = None
    depends_on: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    exclusive: bool = False
    optional: bool = False
    rework_budget: int = 1
    accept_threshold: float = 0.8
    estimated_seconds: float = 60.0
    token_budget: int | None = None
    reviewer: str | None = None      # for gates
    note: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any], *, default_rework: int, default_threshold: float) -> "TaskSpec":
        kind = TaskKind(d.get("kind", "skill"))
        skill = d.get("skill")
        if kind is TaskKind.SKILL and not skill:
            raise ValueError(f"skill task '{d.get('id')}' must define 'skill'")
        return cls(
            id=d["id"],
            name=d.get("name", d["id"]),
            phase=Phase(d["phase"]),
            kind=kind,
            skill=skill,
            model=d.get("model"),
            depends_on=list(d.get("depends_on", [])),
            consumes=list(d.get("consumes", [])),
            produces=list(d.get("produces", [])),
            exclusive=bool(d.get("exclusive", kind is TaskKind.GATE)),
            optional=bool(d.get("optional", False)),
            rework_budget=int(d.get("rework_budget", default_rework)),
            accept_threshold=float(d.get("accept_threshold", default_threshold)),
            estimated_seconds=float(d.get("estimated_seconds", 60.0)),
            token_budget=(int(d["token_budget"]) if d.get("token_budget") is not None else None),
            reviewer=d.get("reviewer"),
            note=d.get("note"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase.value,
            "kind": self.kind.value,
            "skill": self.skill,
            "model": self.model,
            "depends_on": self.depends_on,
            "consumes": self.consumes,
            "produces": self.produces,
            "exclusive": self.exclusive,
            "optional": self.optional,
            "rework_budget": self.rework_budget,
            "accept_threshold": self.accept_threshold,
            "estimated_seconds": self.estimated_seconds,
            "token_budget": self.token_budget,
            "reviewer": self.reviewer,
            "note": self.note,
        }


# --------------------------------------------------------------------------- #
# Action + wave (engine output for the agent)
# --------------------------------------------------------------------------- #
@dataclass
class Action:
    task_id: str
    task_name: str
    phase: Phase
    kind: TaskKind
    attempt_number: int
    skill: str | None = None
    model: str | None = None
    requires_approval: bool = False
    reviewer: str | None = None
    exclusive: bool = False
    estimated_seconds: float = 20.0
    token_budget: int | None = None
    consumes: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "phase": self.phase.value,
            "kind": self.kind.value,
            "attempt_number": self.attempt_number,
            "skill": self.skill,
            "model": self.model,
            "requires_approval": self.requires_approval,
            "reviewer": self.reviewer,
            "exclusive": self.exclusive,
            "estimated_seconds": self.estimated_seconds,
            "token_budget": self.token_budget,
            "consumes": self.consumes,
            "produces": self.produces,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Action":
        return cls(
            task_id=d["task_id"], task_name=d["task_name"], phase=Phase(d["phase"]),
            kind=TaskKind(d["kind"]), attempt_number=d["attempt_number"], skill=d.get("skill"),
            model=d.get("model"), requires_approval=d.get("requires_approval", False),
            reviewer=d.get("reviewer"), exclusive=d.get("exclusive", False),
            estimated_seconds=d.get("estimated_seconds", 20.0), token_budget=d.get("token_budget"),
            consumes=d.get("consumes", []), produces=d.get("produces", []), context=d.get("context", {}),
        )


@dataclass
class WaveDispatch:
    wave_index: int
    mode: str  # "parallel" | "sequential"
    phase: Phase
    actions: list[Action]
    clock_seconds: float
    time_remaining_seconds: float
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "wave_index": self.wave_index,
            "mode": self.mode,
            "phase": self.phase.value,
            "actions": [a.to_dict() for a in self.actions],
            "clock_seconds": round(self.clock_seconds, 3),
            "time_remaining_seconds": round(self.time_remaining_seconds, 3),
            "note": self.note,
        }


# --------------------------------------------------------------------------- #
# Runtime state of one task
# --------------------------------------------------------------------------- #
@dataclass
class TaskRuntime:
    spec: TaskSpec
    state: TaskState = TaskState.PENDING
    attempts: list[TaskAttempt] = field(default_factory=list)
    rework_count: int = 0
    skill_override: str | None = None
    in_flight: Action | None = None
    start_clock: float | None = None
    end_clock: float | None = None
    critical_path: float = 0.0
    last_decision: str | None = None

    @property
    def is_gate(self) -> bool:
        return self.spec.kind is TaskKind.GATE

    def skill_for(self) -> str | None:
        return self.skill_override or self.spec.skill

    @property
    def total_token_usage(self) -> TokenUsage:
        total = TokenUsage()
        for a in self.attempts:
            total = total + a.token_usage
        return total

    @property
    def first_time_right(self) -> bool:
        """Skill tasks only: DONE on the first attempt with no rework."""
        if self.is_gate:
            return False
        return (
            self.state is TaskState.DONE
            and self.rework_count == 0
            and len(self.attempts) == 1
            and self.attempts[0].success
        )

    @property
    def duration_seconds(self) -> float | None:
        if self.start_clock is None or self.end_clock is None:
            return None
        return self.end_clock - self.start_clock

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec": self.spec.to_dict(),
            "state": self.state.value,
            "attempts": [a.to_dict() for a in self.attempts],
            "rework_count": self.rework_count,
            "skill_override": self.skill_override,
            "in_flight": self.in_flight.to_dict() if self.in_flight else None,
            "start_clock": self.start_clock,
            "end_clock": self.end_clock,
            "critical_path": self.critical_path,
            "last_decision": self.last_decision,
            "first_time_right": self.first_time_right,
            "total_token_usage": self.total_token_usage.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any], *, default_rework: int, default_threshold: float) -> "TaskRuntime":
        spec = TaskSpec.from_dict(d["spec"], default_rework=default_rework, default_threshold=default_threshold)
        rt = cls(spec=spec)
        rt.state = TaskState(d["state"])
        rt.attempts = [TaskAttempt.from_dict(a) for a in d.get("attempts", [])]
        rt.rework_count = d.get("rework_count", 0)
        rt.skill_override = d.get("skill_override")
        rt.in_flight = Action.from_dict(d["in_flight"]) if d.get("in_flight") else None
        rt.start_clock = d.get("start_clock")
        rt.end_clock = d.get("end_clock")
        rt.critical_path = d.get("critical_path", 0.0)
        rt.last_decision = d.get("last_decision")
        return rt


# --------------------------------------------------------------------------- #
# Whole-workflow state
# --------------------------------------------------------------------------- #
@dataclass
class WorkflowConfig:
    time_budget_seconds: float = 0.0  # 0 == unbounded
    max_parallelism: int = 4
    default_rework_budget: int = 1
    default_accept_threshold: float = 0.8
    tight_time_fraction: float = 0.3
    enforce_phase_order: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_budget_seconds": self.time_budget_seconds,
            "max_parallelism": self.max_parallelism,
            "default_rework_budget": self.default_rework_budget,
            "default_accept_threshold": self.default_accept_threshold,
            "tight_time_fraction": self.tight_time_fraction,
            "enforce_phase_order": self.enforce_phase_order,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WorkflowConfig":
        return cls(
            time_budget_seconds=float(d.get("time_budget_seconds", 0.0)),
            max_parallelism=int(d.get("max_parallelism", 4)),
            default_rework_budget=int(d.get("default_rework_budget", 1)),
            default_accept_threshold=float(d.get("default_accept_threshold", 0.8)),
            tight_time_fraction=float(d.get("tight_time_fraction", 0.3)),
            enforce_phase_order=bool(d.get("enforce_phase_order", True)),
        )


@dataclass
class WorkflowState:
    name: str
    config: WorkflowConfig
    tasks: dict[str, TaskRuntime]
    clock_seconds: float = 0.0
    wave_index: int = 0
    wave_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def time_remaining(self) -> float:
        if self.config.time_budget_seconds <= 0:
            return float("inf")
        return max(0.0, self.config.time_budget_seconds - self.clock_seconds)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "config": self.config.to_dict(),
            "clock_seconds": self.clock_seconds,
            "wave_index": self.wave_index,
            "wave_log": self.wave_log,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WorkflowState":
        cfg = WorkflowConfig.from_dict(d.get("config", {}))
        tasks = {
            tid: TaskRuntime.from_dict(
                td, default_rework=cfg.default_rework_budget, default_threshold=cfg.default_accept_threshold
            )
            for tid, td in d.get("tasks", {}).items()
        }
        return cls(
            name=d["name"], config=cfg, tasks=tasks,
            clock_seconds=d.get("clock_seconds", 0.0),
            wave_index=d.get("wave_index", 0), wave_log=d.get("wave_log", []),
        )
