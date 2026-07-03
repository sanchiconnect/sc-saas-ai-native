"""CLI driver for the dispatch loop.

    orchestrator init   --spec planning.workflow.json --state state.json
    orchestrator next   --state state.json               # -> JSON wave of actions
    orchestrator record --state state.json --results results.json
    orchestrator status --state state.json
    orchestrator report --state state.json [--json]

`next` emits skill actions (run as parallel subagents) or a gate action (route to the
reviewer). `record` ingests TaskResults and advances the engine. Loop until complete.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import build_state, is_complete, record_wave
from .models import TaskResult
from .reporting import build_report, format_report
from .scheduler import next_wave
from .state_store import load_state, save_state

try:
    from skill_governor import SQLiteStorage, SkillGovernor
except Exception:  # pragma: no cover
    SkillGovernor = None  # type: ignore
    SQLiteStorage = None  # type: ignore


def _cmd_init(args: argparse.Namespace) -> int:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if args.time_budget is not None:
        spec.setdefault("config", {})["time_budget_seconds"] = args.time_budget
    if args.max_parallel is not None:
        spec.setdefault("config", {})["max_parallelism"] = args.max_parallel
    state = build_state(spec)
    save_state(state, args.state)
    skills = sum(1 for t in state.tasks.values() if not t.is_gate)
    gates = sum(1 for t in state.tasks.values() if t.is_gate)
    print(json.dumps({"initialized": True, "workflow": state.name,
                      "skill_tasks": skills, "gates": gates,
                      "max_parallelism": state.config.max_parallelism,
                      "time_budget_seconds": state.config.time_budget_seconds,
                      "state_path": str(args.state)}, indent=2))
    return 0


def _cmd_next(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    wave = next_wave(state)
    save_state(state, args.state)
    if wave is None:
        print(json.dumps({"complete": is_complete(state), "actions": [],
                          "note": "done" if is_complete(state) else "stalled or out of budget"}, indent=2))
        return 0
    payload = wave.to_dict()
    payload["complete"] = False
    payload["instructions"] = (
        "For each skill action, spawn a subagent that runs 'skill' for the task, "
        "consuming/producing the listed artifact files; return a TaskResult per action. "
        "For a gate action, route to 'reviewer' and report {approved: true/false, "
        "rework_targets: [...]}. If mode is 'parallel', dispatch concurrently."
    )
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_record(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    raw = json.loads(Path(args.results).read_text(encoding="utf-8"))
    items = raw["results"] if isinstance(raw, dict) and "results" in raw else raw
    results = [TaskResult.from_dict(r) for r in items]
    governor = None
    if args.governor_db and SkillGovernor and SQLiteStorage:
        governor = SkillGovernor(storage=SQLiteStorage(args.governor_db))
    notes = record_wave(state, results, governor=governor)
    save_state(state, args.state)
    print(json.dumps({"recorded": len(results), "clock_seconds": round(state.clock_seconds, 3),
                      "time_remaining_seconds": (None if state.config.time_budget_seconds <= 0
                                                 else round(state.time_remaining, 3)),
                      "complete": is_complete(state), "transitions": notes}, indent=2))
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    rows = [{"id": t.spec.id, "phase": t.spec.phase.value, "kind": t.spec.kind.value,
             "state": t.state.value, "in_flight": (t.in_flight.kind.value if t.in_flight else None),
             "rework_count": t.rework_count} for t in state.tasks.values()]
    print(json.dumps({"workflow": state.name, "clock_seconds": round(state.clock_seconds, 3),
                      "wave_index": state.wave_index, "complete": is_complete(state), "tasks": rows}, indent=2))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    rep = build_report(state)
    print(json.dumps(rep.to_dict(), indent=2) if args.json else format_report(rep))
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    from .planner import PriceBook, make_plan, render_report, write_plan

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    requirements = ""
    if args.requirements_file:
        requirements = Path(args.requirements_file).read_text(encoding="utf-8")
    elif args.requirements:
        requirements = args.requirements

    answers = {}
    if args.answers:
        answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    pricebook = PriceBook.from_dict(json.loads(Path(args.pricebook).read_text())) if args.pricebook else None
    exclude = set(s for s in (args.exclude or "").split(",") if s)
    include = set(s for s in (args.include or "").split(",") if s)

    plan = make_plan(spec, requirements=requirements, answers=answers,
                     pricebook=pricebook, exclude=exclude, include=include)
    written = write_plan(plan, spec, report_path=args.report, config_path=args.config)

    if args.markdown:
        print(render_report(plan))
        return 0
    summary = plan.to_dict()
    summary["written"] = written
    summary.pop("task_costs", None)  # keep stdout compact; full detail is in the report
    print(json.dumps(summary, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="orchestrator", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init"); pi.add_argument("--spec", required=True); pi.add_argument("--state", required=True)
    pi.add_argument("--time-budget", type=float, default=None); pi.add_argument("--max-parallel", type=int, default=None)
    pi.set_defaults(func=_cmd_init)

    pn = sub.add_parser("next"); pn.add_argument("--state", required=True); pn.set_defaults(func=_cmd_next)

    pr = sub.add_parser("record"); pr.add_argument("--state", required=True); pr.add_argument("--results", required=True)
    pr.add_argument("--governor-db", default=None); pr.set_defaults(func=_cmd_record)

    ps = sub.add_parser("status"); ps.add_argument("--state", required=True); ps.set_defaults(func=_cmd_status)

    prep = sub.add_parser("report"); prep.add_argument("--state", required=True); prep.add_argument("--json", action="store_true")
    prep.set_defaults(func=_cmd_report)

    pp = sub.add_parser("plan", help="plan mode: analyze, estimate cost, ask questions, persist a run config")
    pp.add_argument("--spec", required=True)
    pp.add_argument("--requirements", default=None, help="free-text requirements statement")
    pp.add_argument("--requirements-file", default=None)
    pp.add_argument("--answers", default=None, help="JSON file mapping question id -> answer")
    pp.add_argument("--exclude", default=None, help="comma-separated task ids to drop")
    pp.add_argument("--include", default=None, help="comma-separated task ids to force-keep")
    pp.add_argument("--pricebook", default=None, help="JSON price book to override defaults")
    pp.add_argument("--report", default=None, help="path to write the markdown plan report")
    pp.add_argument("--config", default=None, help="path to write the finalized run config (only when READY)")
    pp.add_argument("--markdown", action="store_true", help="print the markdown report instead of JSON")
    pp.set_defaults(func=_cmd_plan)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
