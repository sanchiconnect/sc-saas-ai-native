"""skill-governor: a governance/telemetry SDK for AI-native skill execution.

Captures, per skill task:
  1. Token usage (input/output/cache), rolled up from each attempt.
  2. First-time-right -- whether the skill succeeded on attempt 1 with no rerun.
  3. Task lifecycle -- status, start_time, end_time, and derived duration.

Quick start
-----------
    from skill_governor import SkillGovernor, SQLiteStorage, GovernedResult, TokenUsage

    gov = SkillGovernor(storage=SQLiteStorage("runs.db"))

    @gov.govern("pdf-extraction", max_attempts=3, pass_attempt=True)
    def extract(doc, attempt):
        resp = call_llm(doc)
        return GovernedResult(
            output=resp.text,
            succeeded=is_valid(resp.text),
            token_usage=TokenUsage.from_anthropic(resp.usage),
        )

    extract(my_doc)

    # later, anywhere:
    from skill_governor import aggregate
    report = aggregate(gov.storage.load_tasks())
    print(report.overall.first_time_right_rate)
"""

from __future__ import annotations

from .exceptions import (
    SkillExecutionError,
    SkillGovernorError,
    StateError,
    StorageError,
)
from .governor import GovernedResult, RunHandle, SkillGovernor, TaskHandle
from .metrics import GovernanceReport, SkillMetrics, aggregate
from .models import (
    RunStatus,
    SkillRun,
    TaskRecord,
    TaskStatus,
    TokenUsage,
)
from .storage import (
    InMemoryStorage,
    JSONLStorage,
    SQLiteStorage,
    StorageBackend,
)

__version__ = "0.1.0"

__all__ = [
    "SkillGovernor",
    "GovernedResult",
    "TaskHandle",
    "RunHandle",
    "TokenUsage",
    "SkillRun",
    "TaskRecord",
    "RunStatus",
    "TaskStatus",
    "StorageBackend",
    "InMemoryStorage",
    "JSONLStorage",
    "SQLiteStorage",
    "aggregate",
    "GovernanceReport",
    "SkillMetrics",
    "SkillGovernorError",
    "SkillExecutionError",
    "StorageError",
    "StateError",
    "__version__",
]
