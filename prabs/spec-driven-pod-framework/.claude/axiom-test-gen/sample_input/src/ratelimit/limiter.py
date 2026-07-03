"""Fixed-window rate limiter (TASK-03.2).

Produced by DevCopilot. Time is injected via a `clock` callable so behaviour is
deterministic and testable. Single-threaded per spec §4.2.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Tuple


@dataclass
class Decision:
    """Result of a rate-limit check."""
    allowed: bool
    remaining: int
    retry_after: float = 0.0


class RateLimiter:
    def __init__(self, limit: int, window_seconds: float, clock: Callable[[], float]):
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.limit = limit
        self.window = window_seconds
        self.clock = clock
        # key -> (window_start, count)
        self._buckets: Dict[str, Tuple[float, int]] = {}

    def check(self, key: str) -> Decision:
        now = self.clock()
        start, count = self._buckets.get(key, (now, 0))

        # Window rollover: counter resets once the window has fully elapsed.
        if now - start >= self.window:
            start, count = now, 0

        if count < self.limit:
            count += 1
            self._buckets[key] = (start, count)
            return Decision(allowed=True, remaining=self.limit - count)

        retry_after = self.window - (now - start)
        self._buckets[key] = (start, count)
        return Decision(allowed=False, remaining=0, retry_after=retry_after)
