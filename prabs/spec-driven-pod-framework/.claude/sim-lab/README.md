# SimLab

Validates that every built component meets its Non-Functional Requirements under realistic stress conditions before deployment. Generates load test scripts, injects failure scenarios, and validates that circuit-breakers and fallback behaviours match the spec. A component that passes functional tests but fails its p95 latency target or lacks a working circuit-breaker is not deployable.

---

## When to Use

Invoke during the Validate phase after build is complete to run NFR validation, load testing, and chaos engineering.

**Trigger phrases:** `load test`, `performance test`, `stress test`, `NFR validation`, `chaos engineering`, `SimLab`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `artifacts/task-breakdown.yaml` | Optional |
| `artifacts/context.yaml` | Optional |

## Outputs

- `artifacts/simlab-results.json` — load test results, chaos test outcomes, NFR pass/fail per component
- Generated load test scripts (k6 / Locust / Artillery)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Build phase complete (staging deployed) | InsightOps |
| EvalHarness rubric defined | Release phase |
