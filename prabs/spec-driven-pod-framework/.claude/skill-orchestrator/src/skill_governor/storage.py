"""Pluggable persistence backends.

A backend only needs to do two things: persist a finalized :class:`TaskRecord`
(with its attempts) and read records back for aggregation. Backends are written
to be append/upsert friendly so a long-running governor can flush incrementally.
"""

from __future__ import annotations

import abc
import json
import sqlite3
import threading
from pathlib import Path
from typing import Iterable

from .exceptions import StorageError
from .models import RunStatus, SkillRun, TaskRecord, TaskStatus, TokenUsage


class StorageBackend(abc.ABC):
    """Interface every backend implements."""

    @abc.abstractmethod
    def save_task(self, task: TaskRecord) -> None:
        """Persist (insert or replace) a complete task and its attempts."""

    @abc.abstractmethod
    def load_tasks(self) -> list[TaskRecord]:
        """Return all stored tasks. Used by the metrics layer and CLI."""

    def close(self) -> None:  # pragma: no cover - optional override
        """Release any held resources. No-op by default."""


# --------------------------------------------------------------------------- #
class InMemoryStorage(StorageBackend):
    """Keeps records in a process-local dict. Ideal for tests and short jobs."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._lock = threading.Lock()

    def save_task(self, task: TaskRecord) -> None:
        with self._lock:
            self._tasks[task.task_id] = task

    def load_tasks(self) -> list[TaskRecord]:
        with self._lock:
            return list(self._tasks.values())


# --------------------------------------------------------------------------- #
class JSONLStorage(StorageBackend):
    """Newline-delimited JSON, one task per line.

    Cheap to append to and trivially greppable. On ``save_task`` the full file is
    rewritten so repeated saves of the same task id stay deduplicated -- fine for
    moderate volumes; switch to SQLite for high-throughput workloads.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_task(self, task: TaskRecord) -> None:
        with self._lock:
            existing = {t.task_id: t for t in self._read_unlocked()}
            existing[task.task_id] = task
            try:
                with self.path.open("w", encoding="utf-8") as fh:
                    for record in existing.values():
                        fh.write(json.dumps(record.to_dict()) + "\n")
            except OSError as exc:  # pragma: no cover - filesystem dependent
                raise StorageError(f"failed to write {self.path}: {exc}") from exc

    def load_tasks(self) -> list[TaskRecord]:
        with self._lock:
            return self._read_unlocked()

    def _read_unlocked(self) -> list[TaskRecord]:
        if not self.path.exists():
            return []
        tasks: list[TaskRecord] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    tasks.append(_task_from_dict(json.loads(line)))
        return tasks


# --------------------------------------------------------------------------- #
class SQLiteStorage(StorageBackend):
    """Durable, queryable backend. Recommended for production telemetry.

    Two tables (``tasks`` and ``runs``) with a foreign-key relationship. Writes are
    wrapped in a transaction so a task and its attempts persist atomically.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # check_same_thread=False + an explicit lock lets the governor be shared.
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id          TEXT PRIMARY KEY,
                    skill_name       TEXT NOT NULL,
                    status           TEXT NOT NULL,
                    start_time       TEXT NOT NULL,
                    end_time         TEXT,
                    duration_ms      REAL,
                    attempt_count    INTEGER NOT NULL,
                    rerun_count      INTEGER NOT NULL,
                    first_time_right INTEGER NOT NULL,
                    total_tokens     INTEGER NOT NULL,
                    metadata         TEXT
                );
                CREATE TABLE IF NOT EXISTS runs (
                    run_id                TEXT PRIMARY KEY,
                    task_id               TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
                    skill_name            TEXT NOT NULL,
                    attempt_number        INTEGER NOT NULL,
                    status                TEXT NOT NULL,
                    start_time            TEXT NOT NULL,
                    end_time              TEXT,
                    duration_ms           REAL,
                    input_tokens          INTEGER NOT NULL,
                    output_tokens         INTEGER NOT NULL,
                    cache_read_tokens     INTEGER NOT NULL,
                    cache_creation_tokens INTEGER NOT NULL,
                    error                 TEXT,
                    metadata              TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_skill ON tasks(skill_name);
                """
            )

    def save_task(self, task: TaskRecord) -> None:
        usage = task.total_token_usage
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO tasks
                (task_id, skill_name, status, start_time, end_time, duration_ms,
                 attempt_count, rerun_count, first_time_right, total_tokens, metadata)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    task.task_id,
                    task.skill_name,
                    task.status.value,
                    task.start_time.isoformat(),
                    task.end_time.isoformat() if task.end_time else None,
                    task.duration_ms,
                    task.attempt_count,
                    task.rerun_count,
                    int(task.first_time_right),
                    usage.total_tokens,
                    json.dumps(task.metadata),
                ),
            )
            # Replace the attempt rows wholesale to keep them in sync.
            self._conn.execute("DELETE FROM runs WHERE task_id = ?", (task.task_id,))
            self._conn.executemany(
                """
                INSERT INTO runs
                (run_id, task_id, skill_name, attempt_number, status, start_time,
                 end_time, duration_ms, input_tokens, output_tokens,
                 cache_read_tokens, cache_creation_tokens, error, metadata)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                [
                    (
                        r.run_id,
                        r.task_id,
                        r.skill_name,
                        r.attempt_number,
                        r.status.value,
                        r.start_time.isoformat(),
                        r.end_time.isoformat() if r.end_time else None,
                        r.duration_ms,
                        r.token_usage.input_tokens,
                        r.token_usage.output_tokens,
                        r.token_usage.cache_read_tokens,
                        r.token_usage.cache_creation_tokens,
                        r.error,
                        json.dumps(r.metadata),
                    )
                    for r in task.attempts
                ],
            )

    def load_tasks(self) -> list[TaskRecord]:
        with self._lock:
            task_rows = self._conn.execute(
                "SELECT * FROM tasks ORDER BY start_time"
            ).fetchall()
            run_rows = self._conn.execute(
                "SELECT * FROM runs ORDER BY task_id, attempt_number"
            ).fetchall()

        runs_by_task: dict[str, list[SkillRun]] = {}
        for row in run_rows:
            runs_by_task.setdefault(row["task_id"], []).append(_run_from_row(row))

        return [_task_from_row(row, runs_by_task.get(row["task_id"], [])) for row in task_rows]

    def close(self) -> None:
        with self._lock:
            self._conn.close()


# --------------------------------------------------------------------------- #
# Deserialization helpers
# --------------------------------------------------------------------------- #
from datetime import datetime  # noqa: E402  (kept local to deserialization helpers)


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _run_from_row(row: sqlite3.Row) -> SkillRun:
    run = SkillRun(
        skill_name=row["skill_name"],
        task_id=row["task_id"],
        attempt_number=row["attempt_number"],
        run_id=row["run_id"],
        status=RunStatus(row["status"]),
        start_time=_parse_dt(row["start_time"]),
        end_time=_parse_dt(row["end_time"]),
        token_usage=TokenUsage(
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            cache_read_tokens=row["cache_read_tokens"],
            cache_creation_tokens=row["cache_creation_tokens"],
        ),
        error=row["error"],
        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
    )
    return run


def _task_from_row(row: sqlite3.Row, attempts: Iterable[SkillRun]) -> TaskRecord:
    return TaskRecord(
        skill_name=row["skill_name"],
        task_id=row["task_id"],
        status=TaskStatus(row["status"]),
        start_time=_parse_dt(row["start_time"]),
        end_time=_parse_dt(row["end_time"]),
        attempts=list(attempts),
        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
    )


def _task_from_dict(data: dict) -> TaskRecord:
    attempts = []
    for a in data.get("attempts", []):
        tu = a.get("token_usage", {})
        attempts.append(
            SkillRun(
                skill_name=a["skill_name"],
                task_id=a["task_id"],
                attempt_number=a["attempt_number"],
                run_id=a["run_id"],
                status=RunStatus(a["status"]),
                start_time=_parse_dt(a["start_time"]),
                end_time=_parse_dt(a["end_time"]),
                token_usage=TokenUsage(
                    input_tokens=tu.get("input_tokens", 0),
                    output_tokens=tu.get("output_tokens", 0),
                    cache_read_tokens=tu.get("cache_read_tokens", 0),
                    cache_creation_tokens=tu.get("cache_creation_tokens", 0),
                ),
                error=a.get("error"),
                metadata=a.get("metadata", {}),
            )
        )
    return TaskRecord(
        skill_name=data["skill_name"],
        task_id=data["task_id"],
        status=TaskStatus(data["status"]),
        start_time=_parse_dt(data["start_time"]),
        end_time=_parse_dt(data["end_time"]),
        attempts=attempts,
        metadata=data.get("metadata", {}),
    )
