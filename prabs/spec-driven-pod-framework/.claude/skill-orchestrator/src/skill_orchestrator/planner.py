"""Plan mode -- think first, act later.

Given a workflow spec and a free-text requirements statement, plan mode:

1. *explores the specifications* -- the artifact graph (which input files the run
   needs, which deliverables it produces) and the skill/gate inventory;
2. *generates a structured implementation plan* -- the exact wave-by-wave execution
   order (by dry-running the real scheduler without invoking any skill), per phase;
3. *estimates cost* -- tokens and money from each task's token budget and a
   configurable price book, as a base figure and a worst-case-with-rework ceiling;
4. *asks for clarifications* -- heuristic questions (scope, AI features, NFR targets,
   golden references) whose answers can prune or keep skills;
5. *recommends skills to include/exclude* -- e.g. drop SpecImpactAnalyzer when there is
   no spec diff, or PromptBench when there are no AI features;
6. once no questions remain, *builds a detailed report and persists the finalized
   orchestrator configuration* (a pruned spec) ready for an actual `init` run.

Nothing here calls a model or mutates a live run; it operates on the spec only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .engine import build_state
from .models import PHASE_ORDER, Phase, TaskKind, TaskState, WorkflowState
from .scheduler import next_wave


# --------------------------------------------------------------------------- #
# Cost model (configurable; defaults are order-of-magnitude tier placeholders)
# --------------------------------------------------------------------------- #
@dataclass
class ModelPrice:
    input_per_mtok: float
    output_per_mtok: float
    input_fraction: float  # share of token_budget treated as input (rest is output)


@dataclass
class PriceBook:
    """USD per million tokens, per model. EDIT THESE to your contracted rates.

    The defaults reflect the usual Claude tier *structure* (Haiku < Sonnet < Opus) and
    are placeholders only -- they are not a quote and will drift. The report always
    prints the price book in effect so any estimate is reproducible and auditable.
    """

    prices: dict[str, ModelPrice]
    default: ModelPrice
    currency: str = "USD"

    @classmethod
    def default_book(cls) -> "PriceBook":
        return cls(
            prices={
                "claude-opus-4": ModelPrice(15.0, 75.0, 0.60),
                "claude-sonnet-4": ModelPrice(3.0, 15.0, 0.75),
                "claude-haiku-4-5": ModelPrice(1.0, 5.0, 0.85),
            },
            default=ModelPrice(3.0, 15.0, 0.75),
            currency="USD",
        )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PriceBook":
        prices = {
            m: ModelPrice(p["input_per_mtok"], p["output_per_mtok"], p.get("input_fraction", 0.75))
            for m, p in d.get("prices", {}).items()
        }
        dd = d.get("default", {"input_per_mtok": 3.0, "output_per_mtok": 15.0, "input_fraction": 0.75})
        return cls(prices=prices,
                   default=ModelPrice(dd["input_per_mtok"], dd["output_per_mtok"], dd.get("input_fraction", 0.75)),
                   currency=d.get("currency", "USD"))

    def _price(self, model: str | None) -> ModelPrice:
        if model and model in self.prices:
            return self.prices[model]
        # tier fallback by substring, then global default
        if model:
            for key, mp in self.prices.items():
                tier = key.split("-")[1] if "-" in key else key
                if tier and tier in model:
                    return mp
        return self.default

    def split(self, model: str | None, token_budget: int) -> tuple[int, int]:
        mp = self._price(model)
        inp = int(round(token_budget * mp.input_fraction))
        return inp, token_budget - inp

    def cost(self, model: str | None, token_budget: int) -> float:
        mp = self._price(model)
        inp, out = self.split(model, token_budget)
        return inp / 1e6 * mp.input_per_mtok + out / 1e6 * mp.output_per_mtok

    def summary(self) -> dict[str, Any]:
        return {
            "currency": self.currency,
            "prices": {m: {"input_per_mtok": p.input_per_mtok, "output_per_mtok": p.output_per_mtok,
                           "input_fraction": p.input_fraction} for m, p in self.prices.items()},
            "default": {"input_per_mtok": self.default.input_per_mtok,
                        "output_per_mtok": self.default.output_per_mtok,
                        "input_fraction": self.default.input_fraction},
        }


# --------------------------------------------------------------------------- #
# Plan data structures
# --------------------------------------------------------------------------- #
@dataclass
class TaskCost:
    task_id: str
    model: str | None
    token_budget: int
    input_tokens: int
    output_tokens: int
    base_cost: float
    max_cost: float  # with rework budget fully spent


@dataclass
class PhasePlan:
    phase: str
    skill_ids: list[str] = field(default_factory=list)
    gate_ids: list[str] = field(default_factory=list)
    tokens: int = 0
    base_cost: float = 0.0
    max_cost: float = 0.0


@dataclass
class PlannedWave:
    index: int
    phases: list[str]
    mode: str
    task_ids: list[str]


@dataclass
class PlanQuestion:
    id: str
    question: str
    kind: str  # "single_select" | "free_text"
    options: list[str] = field(default_factory=list)
    rationale: str = ""
    exclude_if: dict[str, list[str]] = field(default_factory=dict)  # answer -> task ids to drop

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "question": self.question, "kind": self.kind,
                "options": self.options, "rationale": self.rationale,
                "exclude_if": self.exclude_if}


@dataclass
class Recommendation:
    task_id: str
    action: str  # "include" | "exclude"
    reason: str
    safe: bool   # True when no in-workflow task depends on this one

    def to_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "action": self.action, "reason": self.reason, "safe": self.safe}


@dataclass
class ImplementationPlan:
    workflow_name: str
    requirements: str
    status: str  # "needs_input" | "ready"
    phases: list[PhasePlan]
    waves: list[PlannedWave]
    task_costs: list[TaskCost]
    total_tokens: int
    base_cost: float
    max_cost: float
    currency: str
    makespan_estimate_seconds: float
    gates: list[dict[str, Any]]
    questions: list[PlanQuestion]            # still open (unanswered)
    answered: dict[str, str]
    recommendations: list[Recommendation]
    included_ids: list[str]
    excluded_ids: list[str]
    required_input_specs: list[str]
    deliverables: list[str]
    hitl_prerequisites: list[str]
    notes: list[str]
    pricebook: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow_name,
            "status": self.status,
            "requirements": self.requirements,
            "totals": {"tokens": self.total_tokens, "base_cost": round(self.base_cost, 2),
                       "max_cost_with_rework": round(self.max_cost, 2), "currency": self.currency,
                       "makespan_estimate_seconds": round(self.makespan_estimate_seconds, 1)},
            "scope": {"included": self.included_ids, "excluded": self.excluded_ids},
            "phases": [{"phase": p.phase, "skills": p.skill_ids, "gates": p.gate_ids,
                        "tokens": p.tokens, "base_cost": round(p.base_cost, 2),
                        "max_cost": round(p.max_cost, 2)} for p in self.phases],
            "waves": [{"index": w.index, "phases": w.phases, "mode": w.mode,
                       "tasks": w.task_ids} for w in self.waves],
            "gates": self.gates,
            "open_questions": [q.to_dict() for q in self.questions],
            "answered": self.answered,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "required_input_specs": self.required_input_specs,
            "deliverables": self.deliverables,
            "hitl_prerequisites": self.hitl_prerequisites,
            "notes": self.notes,
            "task_costs": [{"task_id": c.task_id, "model": c.model, "token_budget": c.token_budget,
                            "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
                            "base_cost": round(c.base_cost, 4), "max_cost": round(c.max_cost, 4)}
                           for c in self.task_costs],
            "pricebook": self.pricebook,
        }


# --------------------------------------------------------------------------- #
# Spec helpers
# --------------------------------------------------------------------------- #
def _dependents_map(state: WorkflowState) -> dict[str, list[str]]:
    dep: dict[str, list[str]] = {tid: [] for tid in state.tasks}
    for tid, t in state.tasks.items():
        for d in t.spec.depends_on:
            if d in dep:
                dep[d].append(tid)
    return dep


def prune_spec(spec: dict, exclude_ids: set[str]) -> dict:
    """Return a copy of ``spec`` with excluded tasks removed and dangling explicit
    ``depends_on`` references cleaned. Artifact-derived dependencies on an excluded
    producer become external preconditions automatically (the engine ignores
    unproduced consumed files)."""
    kept = [dict(t) for t in spec["tasks"] if t["id"] not in exclude_ids]
    for t in kept:
        if t.get("depends_on"):
            t["depends_on"] = [d for d in t["depends_on"] if d not in exclude_ids]
    out = {k: v for k, v in spec.items() if k != "tasks"}
    out["tasks"] = kept
    return out


# --------------------------------------------------------------------------- #
# Dry-run schedule (no skills invoked)
# --------------------------------------------------------------------------- #
def dry_run_schedule(state: WorkflowState) -> tuple[list[PlannedWave], float]:
    """Drive the real scheduler with synthetic all-pass results to reveal the
    execution plan and an estimated makespan, without calling any skill."""
    from .engine import record_wave
    from .models import TaskResult

    waves: list[PlannedWave] = []
    guard = 0
    while True:
        guard += 1
        if guard > 1000:
            break
        wave = next_wave(state)
        if wave is None:
            break
        phases = sorted({a.phase.value for a in wave.actions})
        waves.append(PlannedWave(index=wave.wave_index, phases=phases, mode=wave.mode,
                                 task_ids=[a.task_id for a in wave.actions]))
        results = []
        for a in wave.actions:
            if a.kind is TaskKind.GATE:
                results.append(TaskResult(task_id=a.task_id, approved=True, duration_seconds=0.0))
            else:
                results.append(TaskResult(task_id=a.task_id, success=True, score=1.0,
                                          duration_seconds=a.estimated_seconds))
        record_wave(state, results)
    return waves, state.clock_seconds


# --------------------------------------------------------------------------- #
# Cost estimation
# --------------------------------------------------------------------------- #
def estimate_costs(spec: dict, pricebook: PriceBook) -> tuple[list[TaskCost], list[PhasePlan], int, float, float]:
    phases: dict[str, PhasePlan] = {p.value: PhasePlan(phase=p.value) for p in PHASE_ORDER}
    task_costs: list[TaskCost] = []
    total_tokens = 0
    base_total = 0.0
    max_total = 0.0

    for t in spec["tasks"]:
        phase = t["phase"]
        pp = phases[phase]
        if t.get("kind", "skill") == "gate":
            pp.gate_ids.append(t["id"])
            continue
        pp.skill_ids.append(t["id"])
        tb = int(t.get("token_budget") or 0)
        model = t.get("model")
        inp, out = pricebook.split(model, tb)
        base = pricebook.cost(model, tb)
        rb = int(t.get("rework_budget", 1))
        mx = base * (1 + rb)  # worst case: rework budget fully spent
        task_costs.append(TaskCost(t["id"], model, tb, inp, out, base, mx))
        pp.tokens += tb
        pp.base_cost += base
        pp.max_cost += mx
        total_tokens += tb
        base_total += base
        max_total += mx

    return task_costs, [phases[p.value] for p in PHASE_ORDER], total_tokens, base_total, max_total


# --------------------------------------------------------------------------- #
# Requirement analysis -> questions + recommendations
# --------------------------------------------------------------------------- #
_AI_TERMS = ("ai", "llm", "prompt", "rag", "model", "extraction", "agent", "ml", "genai", "chatbot")
_DIFF_TERMS = ("spec change", "diff", "amend", "modify existing", "rework", "changed requirement", "delta")
_NFR_TERMS = ("latency", "load", "throughput", "concurrent", "performance", "scale", "p95", "p99", "nfr", "rps")


def _mentions(text: str, terms) -> bool:
    """Word-boundary keyword match. Heuristic only -- it cannot read negation
    ('no AI' still matches 'ai'), which is precisely why plan mode asks the user to
    confirm rather than deciding silently."""
    t = (text or "").lower()
    for term in terms:
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", t):
            return True
    return False


def generate_questions(state: WorkflowState, requirements: str) -> list[PlanQuestion]:
    qs: list[PlanQuestion] = []
    ids = set(state.tasks)

    if not (requirements or "").strip():
        qs.append(PlanQuestion(
            id="scope", question="Describe the primary deliverable and scope for this sprint.",
            kind="free_text", rationale="No requirements text was supplied; scope drives every downstream decision."))

    if "spec-impact-analyzer" in ids and not _mentions(requirements, _DIFF_TERMS):
        qs.append(PlanQuestion(
            id="spec_diff",
            question="Is this sprint reacting to a change in an already-locked spec (an openspec diff)?",
            kind="single_select", options=["yes", "no"],
            rationale="SpecImpactAnalyzer runs only when a spec diff is present (readme-planning).",
            exclude_if={"no": ["spec-impact-analyzer"]}))

    if "prompt-bench" in ids and not _mentions(requirements, _AI_TERMS):
        qs.append(PlanQuestion(
            id="ai_features",
            question="Does this sprint build AI/LLM features that need prompt benchmarking?",
            kind="single_select", options=["yes", "no"],
            rationale="PromptBench applies to AI features only (readme-build).",
            exclude_if={"no": ["prompt-bench"]}))

    if "red-team-x" in ids and not _mentions(requirements, _AI_TERMS):
        qs.append(PlanQuestion(
            id="ai_facing",
            question="Are there AI-facing components that require adversarial / safety testing?",
            kind="single_select", options=["yes", "no"],
            rationale="RedTeamX targets AI-facing components; skipping it forgoes safety coverage (readme-validate).",
            exclude_if={"no": ["red-team-x"]}))

    if "sim-lab" in ids and not _mentions(requirements, _NFR_TERMS):
        qs.append(PlanQuestion(
            id="nfr_targets",
            question="Provide NFR targets for load/resilience testing (target & peak concurrent users, "
                     "p95 latency ms, error-rate ceiling %). Reply 'none' to skip SimLab.",
            kind="free_text",
            rationale="SimLab needs an NFR block in openspec; without targets it cannot produce a valid verdict.",
            exclude_if={"none": ["sim-lab"]}))

    if "eval-harness" in ids:
        qs.append(PlanQuestion(
            id="golden_refs",
            question="Will the POD Lead supply golden reference outputs / per-dimension score thresholds "
                     "for semantic evaluation? (required for EvalHarness)",
            kind="single_select", options=["yes", "will-provide-at-runtime"],
            rationale="EvalHarness cannot score without golden references (readme-validate)."))

    return qs


def recommend_skills(state: WorkflowState, requirements: str) -> list[Recommendation]:
    deps = _dependents_map(state)
    recs: list[Recommendation] = []

    def safe(tid: str) -> bool:
        return len(deps.get(tid, [])) == 0

    # Optional tasks default to "exclude unless justified".
    for tid, t in state.tasks.items():
        if t.is_gate:
            continue
        if t.spec.optional:
            recs.append(Recommendation(tid, "exclude",
                        "Marked optional; include only if its trigger condition applies.", safe(tid)))

    if "spec-impact-analyzer" in state.tasks and not _mentions(requirements, _DIFF_TERMS):
        recs.append(Recommendation("spec-impact-analyzer", "exclude",
                    "No spec-change/diff signal in requirements.", safe("spec-impact-analyzer")))
    if "prompt-bench" in state.tasks and not _mentions(requirements, _AI_TERMS):
        recs.append(Recommendation("prompt-bench", "exclude",
                    "No AI/LLM-feature signal in requirements.", safe("prompt-bench")))
    if "red-team-x" in state.tasks and _mentions(requirements, _AI_TERMS):
        recs.append(Recommendation("red-team-x", "include",
                    "AI-facing components detected; adversarial testing recommended.", safe("red-team-x")))

    # de-duplicate (task_id, action)
    seen, out = set(), []
    for r in recs:
        key = (r.task_id, r.action)
        if key not in seen:
            seen.add(key); out.append(r)
    return out


def _hitl_prerequisites(state: WorkflowState) -> list[str]:
    pre: list[str] = []
    if "eval-harness" in state.tasks:
        pre.append("EvalHarness: POD Lead must define golden reference outputs / per-dimension thresholds.")
    if "sim-lab" in state.tasks:
        pre.append("SimLab: openspec must carry an NFR block (targets), and staging<->prod equivalence must be confirmed.")
    if "policy-enforcer" in state.tasks or "policy-catalog" in state.tasks:
        pre.append("PolicyEnforcer: policy-catalogue.yaml must be current before the compliance gate.")
    gates = [t for t in state.tasks.values() if t.is_gate]
    if gates:
        pre.append(f"{len(gates)} HITL gate(s) require a reviewer sign-off: "
                   + ", ".join(f"{t.spec.id} ({t.spec.reviewer})" for t in gates) + ".")
    return pre


# --------------------------------------------------------------------------- #
# Top-level: make a plan
# --------------------------------------------------------------------------- #
def make_plan(spec: dict, *, requirements: str = "", answers: dict[str, str] | None = None,
              pricebook: PriceBook | None = None, exclude: set[str] | None = None,
              include: set[str] | None = None) -> ImplementationPlan:
    answers = dict(answers or {})
    pricebook = pricebook or PriceBook.default_book()
    explicit_exclude = set(exclude or set())
    explicit_include = set(include or set())
    notes: list[str] = []

    # Validate the *full* spec first so questions/recs see every task.
    full_state = build_state(spec)
    questions_all = generate_questions(full_state, requirements)
    recommendations = recommend_skills(full_state, requirements)

    # Resolve exclusions: explicit + answer-driven, minus explicit includes.
    excluded: set[str] = set(explicit_exclude)
    for q in questions_all:
        if q.id in answers:
            ans = str(answers[q.id]).strip().lower()
            for tid in q.exclude_if.get(ans, []):
                excluded.add(tid)
    excluded -= explicit_include
    excluded &= set(full_state.tasks)  # ignore unknown ids

    # Guard: don't orphan required consumers.
    deps = _dependents_map(full_state)
    for tid in sorted(excluded):
        live_dependents = [d for d in deps.get(tid, []) if d not in excluded]
        if live_dependents:
            notes.append(f"Excluding '{tid}' leaves consumers {live_dependents} relying on its artifacts as "
                         f"external inputs -- confirm those files are supplied another way.")

    effective_spec = prune_spec(spec, excluded)
    state = build_state(effective_spec)  # re-validate the pruned DAG

    waves, makespan = dry_run_schedule(build_state(effective_spec))
    task_costs, phase_plans, total_tokens, base_cost, max_cost = estimate_costs(effective_spec, pricebook)

    open_questions = [q for q in questions_all if q.id not in answers]
    status = "needs_input" if open_questions else "ready"

    all_consumed = {f for t in effective_spec["tasks"] for f in t.get("consumes", [])}
    all_produced = {f for t in effective_spec["tasks"] for f in t.get("produces", [])}
    required_inputs = sorted(all_consumed - all_produced)
    deliverables = sorted(all_produced)

    gates = [{"id": t.spec.id, "phase": t.spec.phase.value, "reviewer": t.spec.reviewer}
             for t in state.tasks.values() if t.is_gate]

    included_ids = sorted(t["id"] for t in effective_spec["tasks"])
    return ImplementationPlan(
        workflow_name=spec.get("name", "workflow"), requirements=requirements, status=status,
        phases=phase_plans, waves=waves, task_costs=task_costs, total_tokens=total_tokens,
        base_cost=base_cost, max_cost=max_cost, currency=pricebook.currency,
        makespan_estimate_seconds=makespan, gates=gates, questions=open_questions, answered=answers,
        recommendations=recommendations, included_ids=included_ids, excluded_ids=sorted(excluded),
        required_input_specs=required_inputs, deliverables=deliverables,
        hitl_prerequisites=_hitl_prerequisites(state), notes=notes, pricebook=pricebook.summary())


# --------------------------------------------------------------------------- #
# Report + persistence
# --------------------------------------------------------------------------- #
def render_report(plan: ImplementationPlan) -> str:
    L: list[str] = []
    a = L.append
    a(f"# Implementation Plan — {plan.workflow_name}")
    a("")
    a(f"**Status:** {'READY to run' if plan.status == 'ready' else 'NEEDS INPUT (open questions below)'}")
    if plan.requirements:
        a(f"\n**Requirements:** {plan.requirements}")
    a("")
    a("## Cost & effort estimate")
    a("")
    a(f"- Estimated tokens: **{plan.total_tokens:,}**")
    a(f"- Estimated cost (base, one pass): **{plan.base_cost:.2f} {plan.currency}**")
    a(f"- Worst case with full rework budgets: **{plan.max_cost:.2f} {plan.currency}**")
    a(f"- Estimated makespan (scheduled, parallelism-aware): **{plan.makespan_estimate_seconds:.0f}s**")
    a(f"- Skills included: **{len(plan.included_ids) - len(plan.gates)}**, gates: **{len(plan.gates)}**")
    a("")
    a("> Costs use the price book below and each task's token budget; they are estimates, "
      "not a quote. Token budgets and prices are both approximate — edit the price book "
      "with your contracted rates.")
    a("")
    a("### Per-phase")
    a("")
    a("| Phase | Skills | Gates | Tokens | Base cost | Max cost |")
    a("|-------|-------:|------:|-------:|----------:|---------:|")
    for p in plan.phases:
        a(f"| {p.phase} | {len(p.skill_ids)} | {len(p.gate_ids)} | {p.tokens:,} | "
          f"{p.base_cost:.2f} | {p.max_cost:.2f} |")
    a("")

    if plan.status == "needs_input":
        a("## Open questions (answer these to finalize)")
        a("")
        for q in plan.questions:
            opts = f"  _(options: {', '.join(q.options)})_" if q.options else "  _(free text)_"
            a(f"- **[{q.id}]** {q.question}{opts}")
            if q.rationale:
                a(f"  - _why:_ {q.rationale}")
        a("")

    if plan.recommendations:
        a("## Scope recommendations")
        a("")
        for r in plan.recommendations:
            tag = "EXCLUDE" if r.action == "exclude" else "INCLUDE"
            safe = "" if r.safe else "  ⚠ has dependents — review before excluding"
            a(f"- **{tag} {r.task_id}** — {r.reason}{safe}")
        a("")

    a("## Scope decisions")
    a("")
    a(f"- **Included ({len(plan.included_ids)}):** {', '.join(plan.included_ids)}")
    a(f"- **Excluded ({len(plan.excluded_ids)}):** {', '.join(plan.excluded_ids) or '(none)'}")
    if plan.answered:
        a(f"- **Answers applied:** " + "; ".join(f"{k}={v}" for k, v in plan.answered.items()))
    a("")

    a("## Required input specifications")
    a("")
    a(("- " + "\n- ".join(plan.required_input_specs)) if plan.required_input_specs
      else "- (none — the workflow is self-contained)")
    a("")
    a("## Deliverables (artifacts produced)")
    a("")
    a("- " + ", ".join(plan.deliverables) if plan.deliverables else "- (none)")
    a("")

    a("## Execution plan (waves)")
    a("")
    a("Each wave is dispatched together; `gate` waves pause for a human reviewer.")
    a("")
    for w in plan.waves:
        ph = "+".join(w.phases)
        a(f"- **Wave {w.index}** [{w.mode}, {ph}]: {', '.join(w.task_ids)}")
    a("")

    if plan.hitl_prerequisites:
        a("## HITL prerequisites")
        a("")
        for h in plan.hitl_prerequisites:
            a(f"- {h}")
        a("")

    if plan.notes:
        a("## Notes & risks")
        a("")
        for n in plan.notes:
            a(f"- {n}")
        a("")

    a("## Price book in effect")
    a("")
    pb = plan.pricebook
    a(f"Currency: {pb['currency']}  (USD per million tokens)")
    a("")
    a("| Model | Input | Output | Input share |")
    a("|-------|------:|-------:|------------:|")
    for m, p in pb["prices"].items():
        a(f"| {m} | {p['input_per_mtok']} | {p['output_per_mtok']} | {p['input_fraction']:.0%} |")
    d = pb["default"]
    a(f"| _(default)_ | {d['input_per_mtok']} | {d['output_per_mtok']} | {d['input_fraction']:.0%} |")
    a("")
    return "\n".join(L)


def finalize_config(spec: dict, plan: ImplementationPlan) -> dict:
    """Produce the persisted run configuration: the pruned spec plus a provenance
    ``plan`` block. Consumable directly by ``orchestrator init``."""
    cfg = prune_spec(spec, set(plan.excluded_ids))
    cfg["plan"] = {
        "requirements": plan.requirements,
        "answers": plan.answered,
        "excluded": plan.excluded_ids,
        "estimate": {"tokens": plan.total_tokens, "base_cost": round(plan.base_cost, 2),
                     "max_cost_with_rework": round(plan.max_cost, 2), "currency": plan.currency,
                     "makespan_estimate_seconds": round(plan.makespan_estimate_seconds, 1)},
        "pricebook": plan.pricebook,
    }
    return cfg


def write_plan(plan: ImplementationPlan, spec: dict, *, report_path: str | Path | None = None,
               config_path: str | Path | None = None) -> dict[str, str | None]:
    """Write the report (always, if a path is given) and -- only when the plan is
    READY -- the finalized run config. Returns the paths written."""
    written: dict[str, str | None] = {"report": None, "config": None}
    if report_path:
        Path(report_path).write_text(render_report(plan), encoding="utf-8")
        written["report"] = str(report_path)
    if config_path and plan.status == "ready":
        Path(config_path).write_text(json.dumps(finalize_config(spec, plan), indent=2) + "\n", encoding="utf-8")
        written["config"] = str(config_path)
    return written
