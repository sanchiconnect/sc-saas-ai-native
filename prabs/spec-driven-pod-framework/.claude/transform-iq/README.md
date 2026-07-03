# TransformIQ

Rescores the AI opportunity backlog against the current sprint's requirements and operational signals from prior sprints. Surfaces unmapped value candidates with high effort-to-value ratios for 1-week delivery. Ensures the business lead starts Monday with a current opportunity map, not stale scores.

---

## When to Use

Invoke in parallel with PolicyCatalog, ContextFabric, and ResearchCopilot at Step 1 of Monday planning.

**Trigger phrases:** `Run TransformIQ`, `Rescore opportunity backlog`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/program.md` | Mandatory |
| `references/opportunity-catalogue.yaml` | Mandatory |
| `artifacts/feedback-loop-triggers.yaml` | Optional |

## Outputs

- `artifacts/opportunity-backlog-rescored.md` — sprint-scored opportunity candidates with value-density scores above threshold

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Phase 01 spec completion | PortfolioPrioritizer |
| (parallel with PolicyCatalog, ContextFabric, ResearchCopilot) | |
