"""skill-orchestrator: a dynamic, dispatch-mode workflow engine for AI-native skills.

Organizes tasks into three ordered phases -- planning -> build -> validate -- where
each task is a single skill invocation or a HITL gate. Dependencies come from explicit
links and the artifact (produces/consumes) contract. The engine schedules tasks
sequentially or in parallel within a time budget, analyzes each result to accept or
rework, routes gate rejections back to specific upstream tasks, and tracks tokens,
first-time-right, and lifecycle via the vendored ``skill_governor``.
"""

from __future__ import annotations

from .analysis import AnalysisOutcome, analyze
from .engine import build_state, is_complete, record_wave
from .models import (
    Action,
    Decision,
    PHASE_ORDER,
    Phase,
    TaskAttempt,
    TaskKind,
    TaskResult,
    TaskRuntime,
    TaskSpec,
    TaskState,
    WaveDispatch,
    WorkflowConfig,
    WorkflowState,
)
from .reporting import PhaseMetrics, WorkflowReport, build_report, format_report
from .scheduler import compute_critical_paths, next_wave
from .planner import (
    ImplementationPlan,
    PlanQuestion,
    PriceBook,
    Recommendation,
    dry_run_schedule,
    estimate_costs,
    finalize_config,
    make_plan,
    render_report,
    write_plan,
)
from .state_store import load_state, save_state

__version__ = "0.3.0"

__all__ = [
    "build_state", "next_wave", "record_wave", "is_complete",
    "analyze", "AnalysisOutcome",
    "build_report", "format_report", "WorkflowReport", "PhaseMetrics",
    "make_plan", "render_report", "write_plan", "finalize_config", "dry_run_schedule",
    "estimate_costs", "PriceBook", "ImplementationPlan", "PlanQuestion", "Recommendation",
    "save_state", "load_state", "compute_critical_paths",
    "Phase", "PHASE_ORDER", "Decision", "TaskKind", "TaskState",
    "TaskSpec", "TaskRuntime", "TaskResult", "TaskAttempt",
    "Action", "WaveDispatch", "WorkflowConfig", "WorkflowState",
    "__version__",
]
