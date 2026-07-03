# ParityChecker

Staging-to-production environment parity verification. Answers one question before any deployment: "Is production identical to staging in every dimension that could cause a test to pass in staging but fail in production?" Critical drift count must be zero for Gate 3 to clear.

---

## When to Use

Run on Friday of any sprint before Gate 3 sign-off, after ReleaseIntel has run.

**Trigger phrases:** `run parity check`, `check environment parity`, `staging vs production diff`, `Gate 3 parity`

---

## Inputs

**First run (Elicitation Mode):** Structured interview across infrastructure, dependencies, feature flags, secrets, and external services.

**Subsequent runs (Diff Mode):**

| Input | Required |
|---|---|
| `artifacts/release/env-config-staging.yaml` | Mandatory |
| `artifacts/release/env-config-production.yaml` | Mandatory |

## Outputs

- `artifacts/release/parity-check-report.md` — critical drift count and full environment diff
- `artifacts/release/env-config-staging.yaml` — generated on first run
- `artifacts/release/env-config-production.yaml` — generated on first run

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| NexusDeploy (deploy-manifest available) | RolloutAdvisor |
| ReleaseIntel | Gate 3 clearance |
