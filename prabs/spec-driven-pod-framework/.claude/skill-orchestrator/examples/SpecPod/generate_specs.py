"""Generate SpecPod workflow specs from the three phase readmes.

Encodes the skill tables, models, token budgets, artifact (produces/consumes)
contracts, and HITL gates described in:
  - readme-planning.md   (13 planning skills + Gates 0, 0.5, 1)
  - readme-build.md      (9 build skills + Gate 2)
  - readme-validate.md   (6 validate skills + feature sign-off + Gate 3)

Writes four specs into this directory:
  planning.workflow.json, build.workflow.json, validate.workflow.json,
  and SpecPod-sprint.workflow.json (all three phases chained by gates).

Run:  python generate_specs.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent

SONNET, HAIKU, OPUS = "claude-sonnet-4", "claude-haiku-4-5", "claude-opus-4"


def est(token_budget: int) -> int:
    """Rough per-skill seconds estimate, proportional to token budget."""
    return max(10, token_budget // 1000)


def skill(id, name, phase, skill_name, model, tok, consumes=(), produces=(),
          depends_on=(), optional=False, exclusive=False, rework_budget=1, threshold=0.8, note=None):
    return {
        "id": id, "name": name, "phase": phase, "kind": "skill", "skill": skill_name,
        "model": model, "token_budget": tok * 1000, "estimated_seconds": est(tok * 1000),
        "consumes": list(consumes), "produces": list(produces), "depends_on": list(depends_on),
        "optional": optional, "exclusive": exclusive, "rework_budget": rework_budget,
        "accept_threshold": threshold, "note": note,
    }


def gate(id, name, phase, reviewer, consumes=(), depends_on=(), note=None):
    return {
        "id": id, "name": name, "phase": phase, "kind": "gate", "reviewer": reviewer,
        "estimated_seconds": 0, "consumes": list(consumes), "depends_on": list(depends_on),
        "note": note,
    }


# --------------------------------------------------------------------------- #
# PLANNING PHASE (Monday) — 13 skills + Gate 0 / 0.5 / 1
# --------------------------------------------------------------------------- #
def planning_tasks() -> list[dict]:
    return [
        gate("gate-0", "Gate 0 — openspec lock", "planning", "POD Lead",
             depends_on=[], note="Locking openspec.yaml triggers all planning skills"),
        # produced by the lock so downstream can wire on it:
        {**gate("gate-0", "x", "planning", "x"), "produces": ["openspec.yaml"]},

        skill("context-fabric", "ContextFabric", "planning", "context-fabric", SONNET, 80,
              consumes=["openspec.yaml"], produces=["context.yaml"]),
        skill("policy-catalog", "PolicyCatalog", "planning", "policy-catalog", HAIKU, 25,
              consumes=["openspec.yaml"], produces=["policy-catalogue.yaml"]),
        skill("research-copilot", "ResearchCopilot", "planning", "research-copilot", SONNET, 80,
              consumes=["openspec.yaml"], produces=["evidence-map.md"]),
        skill("transform-iq", "TransformIQ", "planning", "transform-iq", SONNET, 40,
              consumes=["openspec.yaml"], produces=["opportunity-backlog-rescored.md"]),

        skill("assumption-tracker", "AssumptionTracker", "planning", "assumption-tracker", HAIKU, 20,
              consumes=["evidence-map.md"], produces=["assumption-log.md"]),
        gate("gate-0_5", "Gate 0.5 — Assumption sign-off", "planning", "POD Lead",
             consumes=["assumption-log.md"], note="HITL blocker review; blocks SpecFlow dispatch"),

        skill("spec-flow", "SpecFlow", "planning", "spec-flow", OPUS, 120,
              consumes=["openspec.yaml", "context.yaml", "policy-catalogue.yaml"],
              produces=["task-breakdown.yaml", "ai-manifest.json"],
              depends_on=["gate-0_5"]),

        skill("trace-graph", "TraceGraph", "planning", "trace-graph", HAIKU, 30,
              consumes=["openspec.yaml", "ai-manifest.json"], produces=["traceability-report.md"]),
        skill("spec-impact-analyzer", "SpecImpactAnalyzer", "planning", "spec-impact-analyzer", SONNET, 50,
              consumes=["ai-manifest.json", "traceability-report.md"],
              produces=["impact-analysis.md", "rework-scope-patch.yaml"], optional=True),

        skill("value-modeler", "ValueModeler", "planning", "value-modeler", SONNET, 40,
              consumes=["openspec.yaml", "opportunity-backlog-rescored.md"], produces=["roi-brief.md"]),
        skill("portfolio-prioritizer", "PortfolioPrioritizer", "planning", "portfolio-prioritizer", SONNET, 35,
              consumes=["roi-brief.md", "task-breakdown.yaml", "opportunity-backlog-rescored.md"],
              produces=["sprint-scope-ranked.md"]),
        skill("scenario-planner", "ScenarioPlanner", "planning", "scenario-planner", SONNET, 30,
              consumes=["roi-brief.md", "sprint-scope-ranked.md"], produces=["scenario-matrix.md"]),

        skill("decision-ledger", "DecisionLedger", "planning", "decision-ledger", HAIKU, 20,
              consumes=["evidence-map.md", "assumption-log.md", "scenario-matrix.md"],
              produces=["decision-ledger.md"]),

        skill("conductor", "Conductor", "planning", "conductor", SONNET, 60,
              consumes=["task-breakdown.yaml", "context.yaml", "policy-catalogue.yaml",
                        "sprint-scope-ranked.md", "scenario-matrix.md", "traceability-report.md",
                        "decision-ledger.md"],
              produces=["sprint-board.md"]),

        gate("gate-1", "Gate 1 — Plan sign-off", "planning", "POD Lead + Business Lead",
             consumes=["sprint-board.md", "scenario-matrix.md"],
             note="Clears the sprint board for the Build phase"),
    ]


# --------------------------------------------------------------------------- #
# BUILD PHASE (Tue–Thu) — 9 skills + Gate 2
# --------------------------------------------------------------------------- #
def build_tasks(*, gate_into: list[str] | None = None) -> list[dict]:
    entry = list(gate_into or [])
    return [
        skill("secret-shield", "SecretShield", "build", "secret-shield", HAIKU, 15,
              produces=["secret-shield-redaction.log"], depends_on=entry,
              note="Runs on all context payloads"),
        skill("performance-optimizer", "PerformanceOptimizer", "build", "performance-optimizer", HAIKU, 20,
              consumes=["sprint-capacity.yaml"], produces=["token-consumption-report.yaml"],
              depends_on=entry),
        skill("experience-studio", "ExperienceStudio", "build", "experience-studio", SONNET, 45,
              consumes=["ui-ux.md", "openspec.yaml"], produces=["experience-conformance-report.md"],
              depends_on=entry),
        skill("trust-fabric", "TrustFabric", "build", "trust-fabric", HAIKU, 30,
              consumes=["database.md", "api.md", "openspec.yaml", "policy-catalogue.yaml"],
              produces=["data-contract-compliance-report.md", "data-contract-violations.yaml",
                        "unclassified-fields-report.md"],
              depends_on=entry),
        skill("knowledge-mesh", "KnowledgeMesh", "build", "knowledge-mesh", HAIKU, 60,
              consumes=["openspec.yaml", "task-breakdown.yaml", "decision-ledger.md",
                        "secret-shield-redaction.log"],
              produces=["knowledge-mesh-index.md"]),

        gate("gate-2", "Gate 2 — Design sign-off", "build", "POD Lead",
             consumes=["experience-conformance-report.md"],
             note="Builders may not start UI coding until this clears"),

        skill("dev-copilot", "DevCopilot", "build", "dev-copilot", SONNET, 50,
              consumes=["knowledge-mesh-index.md", "data-contract-compliance-report.md",
                        "token-consumption-report.yaml", "policy-catalogue.yaml",
                        "task-breakdown.yaml", "ai-manifest.json"],
              produces=["spec-ambiguity-escalation.log", "implementation.bundle"],
              depends_on=["gate-2"], rework_budget=2),
        skill("review-pilot", "ReviewPilot", "build", "review-pilot", SONNET, 70,
              consumes=["implementation.bundle", "openspec.yaml"], produces=["review-verdict.yaml"],
              rework_budget=2),
        skill("prompt-bench", "PromptBench", "build", "prompt-bench", HAIKU, 40,
              consumes=["knowledge-mesh-index.md"],
              produces=["prompt-bench-report.md", "prompt-bench-nfr-evidence.yaml"], optional=True),

        skill("nexus-deploy", "NexusDeploy", "build", "nexus-deploy", HAIKU, 25,
              consumes=["review-verdict.yaml", "data-contract-violations.yaml",
                        "task-breakdown.yaml", "ai-manifest.json"],
              produces=["deploy-manifest.yaml", "ai-manifest.updated.json"]),
    ]


# --------------------------------------------------------------------------- #
# VALIDATE PHASE (Tue–Fri) — 6 skills + feature sign-off + Gate 3
# --------------------------------------------------------------------------- #
def validate_tasks(*, gate_into: list[str] | None = None) -> list[dict]:
    entry = list(gate_into or [])
    # Tuesday pre-gate: rubric + feature generation (need only the locked spec).
    return [
        skill("eval-harness", "EvalHarness", "validate", "eval-harness", SONNET, 50,
              consumes=["openspec.yaml"], produces=["eval-rubric.yaml"], depends_on=entry),
        skill("guardian-gen", "Guardian (Generation)", "validate", "guardian", SONNET, 70,
              consumes=["openspec.yaml"], produces=["guardian-feature-files"], depends_on=entry),
        gate("gate-feature", "Gate 2 — Feature sign-off", "validate", "POD Lead",
             consumes=["guardian-feature-files"], note="POD Lead reviews .feature files"),
        # Wednesday–Thursday continuous: every agent waits on the feature sign-off.
        skill("guardian-exec", "Guardian (Execution)", "validate", "guardian", SONNET, 40,
              consumes=["eval-rubric.yaml", "guardian-feature-files"],
              produces=["test-results.json", "coverage-report.md"],
              depends_on=["gate-feature"], rework_budget=2),
        skill("red-team-x", "RedTeamX", "validate", "red-team-x", SONNET, 60,
              consumes=["eval-rubric.yaml", "ai-manifest.json"],
              produces=["adversarial-test-suite.json", "vulnerability-report.md", "redteam-summary.md"],
              depends_on=["gate-feature"], rework_budget=2),
        skill("sim-lab", "SimLab", "validate", "sim-lab", HAIKU, 30,
              consumes=["openspec.yaml", "task-breakdown.yaml", "deploy-manifest.yaml"],
              produces=["simlab-results.json", "nfr-verdict.md"],
              depends_on=["gate-feature"]),
        skill("policy-enforcer", "PolicyEnforcer", "validate", "policy-enforcer", HAIKU, 25,
              consumes=["policy-catalogue.yaml"],
              produces=["policy-scan-report.md", "policy-scan-results.json", "compliance-attestation.md"],
              depends_on=["gate-feature"]),

        skill("insight-ops", "InsightOps", "validate", "insight-ops", SONNET, 50,
              consumes=["coverage-report.md", "redteam-summary.md", "nfr-verdict.md",
                        "compliance-attestation.md", "eval-rubric.yaml"],
              produces=["validation-report.md", "spec-amendments.md", "action-list.md"]),
        gate("gate-3", "Gate 3 — Release sign-off", "validate", "POD Lead",
             consumes=["validation-report.md"], note="Primary release gate document"),
    ]


def _merge_gate0(tasks: list[dict]) -> list[dict]:
    """Fold the two gate-0 fragments (definition + produces) into one task."""
    out, seen = [], {}
    for t in tasks:
        if t["id"] in seen:
            seen[t["id"]].setdefault("produces", [])
            seen[t["id"]]["produces"] = sorted(set(seen[t["id"]].get("produces", []) + t.get("produces", [])))
            continue
        seen[t["id"]] = t
        out.append(t)
    return out


def write(name: str, config: dict, tasks: list[dict]) -> None:
    spec = {"name": name, "config": config, "tasks": _merge_gate0(tasks)}
    path = HERE / f"{name}.workflow.json"
    path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.name}  ({sum(1 for t in spec['tasks'] if t.get('kind','skill')=='skill')} skills, "
          f"{sum(1 for t in spec['tasks'] if t.get('kind')=='gate')} gates)")


def main() -> None:
    planning_cfg = {"time_budget_seconds": 0, "max_parallelism": 4, "default_rework_budget": 1}
    build_cfg = {"time_budget_seconds": 0, "max_parallelism": 4, "default_rework_budget": 1}
    validate_cfg = {"time_budget_seconds": 0, "max_parallelism": 4, "default_rework_budget": 1}
    sprint_cfg = {"time_budget_seconds": 0, "max_parallelism": 5, "default_rework_budget": 1}

    write("planning", planning_cfg, planning_tasks())
    write("build", build_cfg, build_tasks())
    write("validate", validate_cfg, validate_tasks())

    # Combined sprint: planning -> (Gate 1) -> build + validate, wired by artifacts + gates.
    # Validate's pre-gate work (rubric + feature generation) also waits on plan sign-off;
    # its later agents stagger naturally behind the build artifacts they consume
    # (ai-manifest.json, task-breakdown.yaml, deploy-manifest.yaml).
    combined = (
        planning_tasks()
        + build_tasks(gate_into=["gate-1"])
        + validate_tasks(gate_into=["gate-1"])
    )
    write("SpecPod-sprint", sprint_cfg, combined)


if __name__ == "__main__":
    main()
