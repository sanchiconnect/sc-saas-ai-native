# PerformanceOptimizer

Enforces intelligent model routing and sprint token budget compliance. Routes each generation task to the optimal model by matching task complexity to model capability, and monitors cumulative token spend in real time — alerting at 80% threshold and recommending cost-reduction interventions before the budget is exhausted.

---

## When to Use

- Before any generation task is dispatched to a model (routing decision)
- When token budget threshold is crossed (80% alert)
- When POD Lead requests a sprint cost dashboard
- End-of-sprint token consumption report

**Trigger phrases:** `route this task`, `check budget status`, `run PerformanceOptimizer`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/sprint-capacity.yaml` | Mandatory |
| Live token consumption (per-agent tracking) | Mandatory |
| PromptBench results | Optional |

## Outputs

- Model routing recommendation per task
- Sprint token consumption dashboard
- End-of-sprint token consumption report

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Sprint planning artifacts available | Every generation task dispatch |
| | PromptBench (provides routing calibration data) |
