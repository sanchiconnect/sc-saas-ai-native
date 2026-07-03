# InsightOps

The synthesis layer of the Validate phase. Aggregates outputs from all five preceding validation agents — Guardian, EvalHarness, RedTeamX, SimLab, and PolicyEnforcer — and identifies failure patterns that no individual agent can detect in isolation. Also traces failure patterns back to root causes in `openspec.yaml` and recommends specific amendments.

InsightOps is the last agent to run in the Validate phase. All other agents must have produced outputs before it runs.

---

## When to Use

Invoke after all five validation agents have completed their runs for the sprint.

**Trigger phrases:** `synthesise validation results`, `sprint quality summary`, `identify failure patterns`, `InsightOps report`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/test-results.json` (Guardian) | Mandatory |
| `artifacts/eval-results.json` (EvalHarness) | Mandatory |
| `artifacts/adversarial-test-suite.json` (RedTeamX) | Mandatory |
| `artifacts/simlab-results.json` (SimLab) | Mandatory |
| `artifacts/policy-scan-results.json` (PolicyEnforcer) | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| `artifacts/operate-metrics/` | Optional |

## Outputs

- `artifacts/insight-ops-report.md` — cross-agent failure patterns, root causes, POD Lead action list, spec amendment recommendations

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Guardian, EvalHarness, RedTeamX, SimLab, PolicyEnforcer | Release phase |
