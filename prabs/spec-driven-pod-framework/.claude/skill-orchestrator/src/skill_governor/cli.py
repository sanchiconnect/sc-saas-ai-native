"""Command-line reporting tool.

Usage:
    python -m skill_governor.cli report --sqlite runs.db
    python -m skill_governor.cli report --jsonl runs.jsonl --json
"""

from __future__ import annotations

import argparse
import json
import sys

from .metrics import GovernanceReport, SkillMetrics, aggregate
from .storage import JSONLStorage, SQLiteStorage


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _print_skill(m: SkillMetrics, *, indent: str = "") -> None:
    print(f"{indent}{m.skill_name}")
    print(f"{indent}  tasks            : {m.total_tasks}  "
          f"(ok={m.succeeded_tasks}, failed={m.failed_tasks}, "
          f"success={_fmt_pct(m.success_rate)})")
    print(f"{indent}  first-time-right : {m.first_time_right_count}/{m.total_tasks}  "
          f"(rate={_fmt_pct(m.first_time_right_rate)}, "
          f"of-successful={_fmt_pct(m.first_time_right_rate_of_successful)})")
    print(f"{indent}  reruns           : {m.rerun_count}  "
          f"(avg attempts/task={m.avg_attempts_per_task:.2f})")
    print(f"{indent}  tokens           : {m.total_tokens:,}  "
          f"(avg/task={m.avg_tokens_per_task:,.0f}; "
          f"in={m.token_usage.input_tokens:,}, out={m.token_usage.output_tokens:,})")
    p50 = m.p50_duration_ms or 0.0
    p95 = m.p95_duration_ms or 0.0
    print(f"{indent}  duration (ms)    : total={m.total_duration_ms:,.0f}, "
          f"avg={m.avg_duration_ms:,.0f}, p50={p50:,.0f}, p95={p95:,.0f}")


def _print_report(report: GovernanceReport) -> None:
    print("=" * 64)
    print("SKILL GOVERNANCE REPORT")
    print("=" * 64)
    print("\nOVERALL")
    _print_skill(report.overall, indent="  ")
    if report.by_skill:
        print("\nBY SKILL")
        for name in sorted(report.by_skill):
            print()
            _print_skill(report.by_skill[name], indent="  ")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill_governor", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rep = sub.add_parser("report", help="aggregate stored tasks into a report")
    src = rep.add_mutually_exclusive_group(required=True)
    src.add_argument("--sqlite", metavar="PATH", help="path to a SQLite store")
    src.add_argument("--jsonl", metavar="PATH", help="path to a JSONL store")
    rep.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    args = parser.parse_args(argv)

    if args.command == "report":
        backend = SQLiteStorage(args.sqlite) if args.sqlite else JSONLStorage(args.jsonl)
        try:
            report = aggregate(backend.load_tasks())
        finally:
            backend.close()
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            _print_report(report)
        return 0

    return 1  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())
