# ValueModeler

Quantifies the expected business value of each sprint requirement before a single line of code is written. Calculates per-requirement value forecasts (time saved, error reduction, revenue impact) and a sprint-level ROI estimate with a confidence range. Low-value requirements are flagged for PortfolioPrioritizer's defer consideration.

> ⬡ **Proposed** — baseline metric inputs must be agreed with the business before first use. Accuracy improves across 3–5 sprints.

---

## When to Use

Invoke after SpecFlow produces `task-breakdown.yaml` (Step 5 of Monday planning).

**Trigger phrases:** `Run ValueModeler`, `Forecast sprint ROI`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/program.md` | Mandatory |
| `references/opportunity-catalogue.yaml` | Mandatory |
| Prior sprint ValueTracker actuals | Optional |

## Outputs

- `artifacts/roi-brief.md` — per-requirement value forecast and sprint-level ROI estimate with confidence range

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| SpecFlow | PortfolioPrioritizer |
| | ValueTracker (provides forecast for comparison) |
