"""JSON persistence for :class:`WorkflowState`.

Dispatch mode runs across many agent turns, so state must survive between the
``next`` (emit a wave) and ``record`` (ingest results) CLI calls. Writes are atomic
(temp file + rename) to avoid a half-written state file on interruption.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import WorkflowState


def save_state(state: WorkflowState, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(state.to_dict(), indent=2)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_state(path: str | Path) -> WorkflowState:
    with Path(path).open("r", encoding="utf-8") as fh:
        return WorkflowState.from_dict(json.load(fh))
