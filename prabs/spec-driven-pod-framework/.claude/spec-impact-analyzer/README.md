# SpecImpactAnalyzer

Traces the full downstream impact of a proposed `openspec.yaml` change across all existing sprint artifacts. Estimates regeneration and retest effort in builder-hours, classifies change risk, and flags any closed HITL gates that would be invalidated. Delivers a data-driven proceed/defer/escalate decision in under 10 minutes.

---

## When to Use

Invoke whenever a spec change is proposed — either before sprint lock or mid-sprint.

**Trigger phrases:** `Run SpecImpactAnalyzer`, `Analyse spec change`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` (current) | Mandatory |
| `artifacts/openspec-proposed.yaml` or inline diff | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/decision-ledger.md` | Mandatory |
| `specs/spec.md` | Mandatory |
| `tests/*.feature` | Optional |

## Outputs

- `artifacts/impact-analysis.md` — downstream impact map with affected artifacts and effort estimate
- `artifacts/rework-scope-patch.yaml` — regeneration scope for Conductor if change is approved

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Any proposed spec change | DecisionLedger (records the decision) |
| TraceGraph (traceability-report available) | Conductor (rework dispatch if approved) |
