"""The governor: the public entry point that drives task/run lifecycles.

Three usage styles are supported, from lowest to highest level of abstraction:

1. **Manual context managers** -- ``with gov.task(...) as task:`` then ``with task.run() as run:``.
   Maximum control; you decide the retry loop.
2. **High-level executor** -- ``gov.execute(skill, fn, max_attempts=3, ...)``.
   The governor owns the retry loop and FTR accounting.
3. **Decorator** -- ``@gov.govern(skill, max_attempts=3)`` on a function returning a
   :class:`GovernedResult`.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Iterator

from .exceptions import SkillExecutionError, StateError
from .models import RunStatus, SkillRun, TaskRecord, TaskStatus, TokenUsage
from .storage import InMemoryStorage, StorageBackend

logger = logging.getLogger("skill_governor")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
@dataclass
class GovernedResult:
    """Return type for functions wrapped by :meth:`SkillGovernor.govern`.

    ``succeeded`` is what drives first-time-right and the retry loop. ``token_usage``
    is recorded against the attempt. ``output`` is handed back to the caller.
    """

    output: Any = None
    succeeded: bool = True
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
class RunHandle:
    """Live handle to a single attempt, exposed inside ``with task.run() as run``."""

    def __init__(self, run: SkillRun, task_ctx: "TaskHandle") -> None:
        self._run = run
        self._task = task_ctx
        self._finalized = False

    @property
    def record(self) -> SkillRun:
        return self._run

    @property
    def attempt_number(self) -> int:
        return self._run.attempt_number

    def add_token_usage(self, usage: TokenUsage) -> None:
        """Accumulate token usage (callable multiple times within one attempt)."""
        self._run.token_usage = self._run.token_usage + usage

    def add_tokens(
        self,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_creation_tokens: int = 0,
    ) -> None:
        """Convenience wrapper around :meth:`add_token_usage`."""
        self.add_token_usage(
            TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_read_tokens=cache_read_tokens,
                cache_creation_tokens=cache_creation_tokens,
            )
        )

    def set_metadata(self, **kwargs: Any) -> None:
        self._run.metadata.update(kwargs)

    def succeed(self) -> None:
        self._finalize(RunStatus.SUCCEEDED, error=None)

    def fail(self, error: str | None = None) -> None:
        self._finalize(RunStatus.FAILED, error=error)

    def _finalize(self, status: RunStatus, *, error: str | None) -> None:
        if self._finalized:
            raise StateError(f"run {self._run.run_id} already finalized")
        self._run.status = status
        self._run.error = error
        self._run.end_time = _utcnow()
        self._finalized = True


# --------------------------------------------------------------------------- #
class TaskHandle:
    """Live handle to a task, exposed inside ``with gov.task(...) as task``."""

    def __init__(self, governor: "SkillGovernor", record: TaskRecord) -> None:
        self._gov = governor
        self._task = record
        self._closed = False

    @property
    def record(self) -> TaskRecord:
        return self._task

    @property
    def task_id(self) -> str:
        return self._task.task_id

    @property
    def attempt_count(self) -> int:
        return self._task.attempt_count

    @contextmanager
    def run(self) -> Iterator[RunHandle]:
        """Open a new attempt. The attempt is appended to the task on entry.

        Outcome resolution on exit:
        - explicit ``succeed()``/``fail()`` wins;
        - an unhandled exception marks the attempt FAILED and re-raises;
        - a clean exit with no explicit outcome is treated as SUCCEEDED.
        """
        if self._closed:
            raise StateError("cannot start a run on a closed task")
        if self._task.status is TaskStatus.PENDING:
            self._task.status = TaskStatus.RUNNING

        run_record = SkillRun(
            skill_name=self._task.skill_name,
            task_id=self._task.task_id,
            attempt_number=self._task.attempt_count + 1,
            status=RunStatus.RUNNING,
        )
        self._task.attempts.append(run_record)
        handle = RunHandle(run_record, self)
        try:
            yield handle
        except Exception as exc:
            if not handle._finalized:
                handle.fail(error=f"{type(exc).__name__}: {exc}")
            raise
        else:
            if not handle._finalized:
                handle.succeed()

    def set_metadata(self, **kwargs: Any) -> None:
        self._task.metadata.update(kwargs)

    def _close(self) -> None:
        """Derive final task status from its attempts and persist."""
        if self._closed:
            return
        if any(a.succeeded for a in self._task.attempts):
            self._task.status = TaskStatus.SUCCEEDED
        elif self._task.attempts:
            self._task.status = TaskStatus.FAILED
        else:
            # No attempts were ever made; treat as failed-but-empty.
            self._task.status = TaskStatus.FAILED
        self._task.end_time = _utcnow()
        self._closed = True
        self._gov._persist(self._task)


# --------------------------------------------------------------------------- #
class SkillGovernor:
    """Coordinates governed skill execution and telemetry persistence.

    Parameters
    ----------
    storage:
        Backend used to persist finalized tasks. Defaults to in-memory.
    on_task_complete:
        Optional callback invoked with each finalized :class:`TaskRecord` -- handy
        for streaming metrics to an external observability system.
    """

    def __init__(
        self,
        storage: StorageBackend | None = None,
        *,
        on_task_complete: Callable[[TaskRecord], None] | None = None,
    ) -> None:
        self.storage = storage or InMemoryStorage()
        self._on_task_complete = on_task_complete

    # --- persistence hook ------------------------------------------------ #
    def _persist(self, task: TaskRecord) -> None:
        self.storage.save_task(task)
        if self._on_task_complete is not None:
            try:
                self._on_task_complete(task)
            except Exception:  # pragma: no cover - callback must not break runs
                logger.exception("on_task_complete callback raised")

    # --- style 1: manual context managers -------------------------------- #
    @contextmanager
    def task(
        self,
        skill_name: str,
        *,
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[TaskHandle]:
        record = TaskRecord(skill_name=skill_name, metadata=metadata or {})
        if task_id is not None:
            record.task_id = task_id
        handle = TaskHandle(self, record)
        try:
            yield handle
        finally:
            handle._close()

    # --- style 2: high-level executor ------------------------------------ #
    def execute(
        self,
        skill_name: str,
        fn: Callable[..., GovernedResult],
        *args: Any,
        max_attempts: int = 1,
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        pass_attempt: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run ``fn`` under governance with an automatic retry loop.

        ``fn`` must return a :class:`GovernedResult`. When ``pass_attempt`` is True,
        the current 1-based attempt number is injected as the ``attempt`` keyword.
        Returns the ``output`` of the first successful result, or raises
        :class:`SkillExecutionError` once ``max_attempts`` is exhausted.
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        last_error: str | None = None
        with self.task(skill_name, task_id=task_id, metadata=metadata) as task:
            for attempt in range(1, max_attempts + 1):
                with task.run() as run:
                    call_kwargs = dict(kwargs)
                    if pass_attempt:
                        call_kwargs["attempt"] = attempt
                    result = fn(*args, **call_kwargs)
                    if not isinstance(result, GovernedResult):
                        raise TypeError(
                            "governed function must return a GovernedResult, "
                            f"got {type(result).__name__}"
                        )
                    run.add_token_usage(result.token_usage)
                    if result.metadata:
                        run.set_metadata(**result.metadata)
                    if result.succeeded:
                        run.succeed()
                        return result.output
                    last_error = result.error or "skill reported failure"
                    run.fail(last_error)

        raise SkillExecutionError(
            f"skill '{skill_name}' failed after {max_attempts} attempt(s)",
            task_id=task.task_id,
            attempts=max_attempts,
            last_error=last_error,
        )

    # --- style 3: decorator ---------------------------------------------- #
    def govern(
        self,
        skill_name: str,
        *,
        max_attempts: int = 1,
        pass_attempt: bool = False,
    ) -> Callable[[Callable[..., GovernedResult]], Callable[..., Any]]:
        """Decorate a function returning :class:`GovernedResult` to govern it."""

        def decorator(fn: Callable[..., GovernedResult]) -> Callable[..., Any]:
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self.execute(
                    skill_name,
                    fn,
                    *args,
                    max_attempts=max_attempts,
                    pass_attempt=pass_attempt,
                    **kwargs,
                )

            return wrapper

        return decorator
