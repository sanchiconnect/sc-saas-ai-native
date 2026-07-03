# RolloutAdvisor

Rollout strategy, rollback plan, and go/no-go recommendation. Recommends rollout method (canary, blue-green, feature-flag toggle), generates a rollback plan with RTO target and trigger conditions, and defines the Monday smoke test checklist. Turns Monday deployment into mechanical execution of a pre-approved plan.

---

## When to Use

Run on Friday after ReleaseIntel and ParityChecker have both cleared.

**Trigger phrases:** `rollout advice`, `how should we deploy`, `rollout strategy`, `rollback plan`, `RolloutAdvisor`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/release/release-intel-report.md` | Mandatory |
| `artifacts/release/parity-check-report.md` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/sprint-board.md` | Mandatory (if no deploy-manifest) |
| `artifacts/scenario-matrix.md` | Strongly recommended |
| `artifacts/release/deploy-manifest.yaml` | Optional |

## Outputs

- `artifacts/release/rollout-strategy.md` — recommended rollout method with phasing and traffic split
- `artifacts/release/rollback-plan.md` — step-by-step rollback procedure with RTO target and trigger conditions

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ReleaseIntel | Gate 3 clearance |
| ParityChecker | Monday deployment execution |
