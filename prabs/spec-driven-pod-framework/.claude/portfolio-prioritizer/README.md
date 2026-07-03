# PortfolioPrioritizer

Ranks all backlog items using a composite score of value, urgency, and dependencies, then draws a capacity cut line — above it: this sprint; below it: deferred. Ensures a small team always builds the highest-value items within their capacity. Every defer decision is documented with a rationale.

> ⬡ **Proposed** — scoring model and weighting criteria require stakeholder alignment before production use.

---

## When to Use

Invoke after ValueModeler produces `roi-brief.md` (Step 5 of Monday planning).

**Trigger phrases:** `Run PortfolioPrioritizer`, `Rank sprint backlog`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/roi-brief.md` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| `artifacts/opportunity-backlog-rescored.md` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/program.md` | Mandatory |

## Outputs

- `artifacts/sprint-scope-ranked.md` — ranked backlog with PROCEED / DEFER / DESCOPE per item and rationale

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ValueModeler | ScenarioPlanner |
| TransformIQ | Conductor |
