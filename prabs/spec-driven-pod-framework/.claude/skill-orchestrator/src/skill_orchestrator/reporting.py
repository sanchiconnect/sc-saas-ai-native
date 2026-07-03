"""Workflow-level governance report with per-phase rollups and gate outcomes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from skill_governor import TokenUsage

from .models import PHASE_ORDER, Phase, TaskKind, TaskState, WorkflowState


def _safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


@dataclass
class PhaseMetrics:
    phase: str
    skill_tasks: int = 0
    done: int = 0
    failed: int = 0
    skipped: int = 0
    first_time_right: int = 0
    rework_cycles: int = 0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    gates_total: int = 0
    gates_approved: int = 0

    @property
    def completion_rate(self) -> float:
        return _safe_div(self.done, self.skill_tasks)

    @property
    def ftr_rate(self) -> float:
        return _safe_div(self.first_time_right, self.skill_tasks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "skill_tasks": self.skill_tasks,
            "done": self.done, "failed": self.failed, "skipped": self.skipped,
            "completion_rate": round(self.completion_rate, 4),
            "first_time_right": self.first_time_right,
            "ftr_rate": round(self.ftr_rate, 4),
            "rework_cycles": self.rework_cycles,
            "tokens": self.token_usage.to_dict(),
            "gates": {"total": self.gates_total, "approved": self.gates_approved},
        }


@dataclass
class WorkflowReport:
    name: str
    skill_tasks: int = 0
    done: int = 0
    failed: int = 0
    skipped: int = 0
    first_time_right: int = 0
    total_rework_cycles: int = 0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    gates_total: int = 0
    gates_approved: int = 0
    makespan_seconds: float = 0.0
    time_budget_seconds: float = 0.0
    waves: int = 0
    dispatched_actions: int = 0
    by_phase: dict[str, PhaseMetrics] = field(default_factory=dict)
    task_rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def completion_rate(self) -> float:
        return _safe_div(self.done, self.skill_tasks)

    @property
    def ftr_rate(self) -> float:
        return _safe_div(self.first_time_right, self.skill_tasks)

    @property
    def avg_parallelism(self) -> float:
        return _safe_div(self.dispatched_actions, self.waves)

    @property
    def within_budget(self) -> bool | None:
        if self.time_budget_seconds <= 0:
            return None
        return self.makespan_seconds <= self.time_budget_seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "skill_tasks": {"total": self.skill_tasks, "done": self.done,
                            "failed": self.failed, "skipped": self.skipped,
                            "completion_rate": round(self.completion_rate, 4)},
            "first_time_right": {"count": self.first_time_right, "rate": round(self.ftr_rate, 4)},
            "rework": {"total_cycles": self.total_rework_cycles},
            "gates": {"total": self.gates_total, "approved": self.gates_approved},
            "tokens": self.token_usage.to_dict(),
            "schedule": {"makespan_seconds": round(self.makespan_seconds, 3),
                         "time_budget_seconds": self.time_budget_seconds,
                         "within_budget": self.within_budget,
                         "waves": self.waves, "dispatched_actions": self.dispatched_actions,
                         "avg_parallelism": round(self.avg_parallelism, 3)},
            "by_phase": {k: v.to_dict() for k, v in self.by_phase.items()},
            "tasks_detail": self.task_rows,
        }


def build_report(state: WorkflowState) -> WorkflowReport:
    rep = WorkflowReport(name=state.name, time_budget_seconds=state.config.time_budget_seconds,
                         makespan_seconds=state.clock_seconds, waves=len(state.wave_log))
    rep.by_phase = {p.value: PhaseMetrics(phase=p.value) for p in PHASE_ORDER}

    for task in state.tasks.values():
        pm = rep.by_phase[task.spec.phase.value]
        rep.dispatched_actions += len(task.attempts)

        if task.is_gate:
            rep.gates_total += 1
            pm.gates_total += 1
            if task.state is TaskState.DONE:
                rep.gates_approved += 1
                pm.gates_approved += 1
            rep.task_rows.append({
                "id": task.spec.id, "name": task.spec.name, "phase": task.spec.phase.value,
                "kind": "gate", "state": task.state.value, "reviewer": task.spec.reviewer,
                "attempts": len(task.attempts), "last_decision": task.last_decision,
            })
            continue

        rep.skill_tasks += 1
        pm.skill_tasks += 1
        if task.state is TaskState.DONE:
            rep.done += 1; pm.done += 1
        elif task.state is TaskState.FAILED:
            rep.failed += 1; pm.failed += 1
        elif task.state is TaskState.SKIPPED:
            rep.skipped += 1; pm.skipped += 1

        if task.first_time_right:
            rep.first_time_right += 1; pm.first_time_right += 1
        rep.total_rework_cycles += task.rework_count
        pm.rework_cycles += task.rework_count
        rep.token_usage = rep.token_usage + task.total_token_usage
        pm.token_usage = pm.token_usage + task.total_token_usage

        rep.task_rows.append({
            "id": task.spec.id, "name": task.spec.name, "phase": task.spec.phase.value,
            "kind": "skill", "skill": task.skill_for(), "model": task.spec.model,
            "state": task.state.value, "first_time_right": task.first_time_right,
            "rework_count": task.rework_count, "attempts": len(task.attempts),
            "tokens": task.total_token_usage.total_tokens, "last_decision": task.last_decision,
        })

    return rep


def format_report(rep: WorkflowReport) -> str:
    L: list[str] = []
    a = L.append
    a("=" * 74)
    a(f"SpecPod WORKFLOW GOVERNANCE REPORT : {rep.name}")
    a("=" * 74)
    a(f"skill tasks      : {rep.skill_tasks}  (done={rep.done}, failed={rep.failed}, "
      f"skipped={rep.skipped}, completion={rep.completion_rate*100:.1f}%)")
    a(f"first-time-right : {rep.first_time_right}/{rep.skill_tasks}  (rate={rep.ftr_rate*100:.1f}%)")
    a(f"rework           : {rep.total_rework_cycles} cycle(s)")
    a(f"HITL gates       : {rep.gates_approved}/{rep.gates_total} approved")
    tu = rep.token_usage
    a(f"tokens           : {tu.total_tokens:,}  (in={tu.input_tokens:,}, out={tu.output_tokens:,})")
    budget = f"{rep.time_budget_seconds:.0f}s" if rep.time_budget_seconds else "unbounded"
    wb = rep.within_budget
    wb_txt = "n/a" if wb is None else ("yes" if wb else "OVER")
    a(f"schedule         : makespan={rep.makespan_seconds:.1f}s / budget={budget} "
      f"(within={wb_txt}); waves={rep.waves}; avg parallelism={rep.avg_parallelism:.2f}")
    a("")
    a("BY PHASE")
    for p in PHASE_ORDER:
        pm = rep.by_phase[p.value]
        a(f"  {p.value:<9} tasks={pm.skill_tasks} done={pm.done} ftr={pm.first_time_right} "
          f"rework={pm.rework_cycles} tokens={pm.token_usage.total_tokens:,} "
          f"gates={pm.gates_approved}/{pm.gates_total}")
    a("")
    a("TASKS")
    for row in rep.task_rows:
        if row["kind"] == "gate":
            a(f"  - [{row['phase']:<8}] {row['id']:<22} GATE   {row['state']:<8} "
              f"reviewer={row.get('reviewer')}")
        else:
            ftr = "FTR" if row["first_time_right"] else f"rework={row['rework_count']}"
            a(f"  - [{row['phase']:<8}] {row['id']:<22} {row['state']:<8} {ftr:<10} "
              f"tokens={row['tokens']:,} ({row.get('skill')})")
    a("")
    return "\n".join(L)
