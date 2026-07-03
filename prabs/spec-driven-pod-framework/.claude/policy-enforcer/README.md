# PolicyEnforcer

Scans generated source code and runtime behaviour against the project's compliance policy catalogue. Enforces a hard gate: zero critical violations and zero high violations are required before any artifact can enter the Release phase. Does not negotiate — classifies and blocks.

---

## When to Use

Invoke during the Validate phase to run the compliance gate before release.

**Trigger phrases:** `compliance scan`, `policy check`, `run the policy gate`, `GDPR scan`, `PolicyEnforcer`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/policy-catalogue.yaml` | Mandatory |
| Generated source code (`src/**`) | Mandatory |
| Configuration files | Mandatory |
| `artifacts/deploy-manifest.yaml` | Optional |
| Runtime request/response logs | Optional |
| `artifacts/trustfabric-classification.yaml` | Optional |

## Outputs

- `artifacts/policy-scan-results.json` — per-policy pass/fail with violation details
- Blocking gate report if critical or high violations found

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| DevCopilot code generation complete | InsightOps |
| TrustFabric classification available | Release phase |
