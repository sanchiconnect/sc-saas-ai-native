"""Exception hierarchy for the skill-governor SDK."""

from __future__ import annotations


class SkillGovernorError(Exception):
    """Base class for all SDK errors."""


class SkillExecutionError(SkillGovernorError):
    """Raised when a governed skill exhausts its retry budget without succeeding.

    Carries the underlying task identifier and the last recorded error so callers
    can inspect what went wrong without re-querying the store.
    """

    def __init__(self, message: str, *, task_id: str, attempts: int, last_error: str | None = None):
        super().__init__(message)
        self.task_id = task_id
        self.attempts = attempts
        self.last_error = last_error


class StorageError(SkillGovernorError):
    """Raised when a storage backend fails to persist or read a record."""


class StateError(SkillGovernorError):
    """Raised when the SDK is driven into an inconsistent lifecycle state.

    Example: calling ``succeed()`` on a run that was already finalized.
    """
