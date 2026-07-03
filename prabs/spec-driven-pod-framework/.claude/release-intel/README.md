# ReleaseIntel

Release-readiness synthesis and blast-radius risk quantification. Aggregates planning artifacts into a single synthesised verdict — binary release decision with a structured blast-radius table. Eliminates the POD Lead's need to manually cross-reference five separate reports. Friday QA review time target: 30–45 minutes.

---

## When to Use

Run on Friday of any sprint to generate Gate 3 evidence before deployment decision.

**Trigger phrases:** `run release intel`, `are we ready to deploy`, `release readiness check`, `blast radius assessment`, `Gate 3 readiness`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/release/deploy-manifest.yaml` | Optional (priority 1) |
| `artifacts/sprint-board.md` | Fallback |
| `artifacts/task-breakdown.yaml` | Fallback |
| `artifacts/traceability-report.md` | Strongly recommended |
| `artifacts/scenario-matrix.md` | Strongly recommended |
| `artifacts/assumption-log.md` | Recommended |
| `artifacts/decision-ledger.md` | Recommended |
| `specs/spec.md` | Recommended |

## Outputs

- `artifacts/release/release-intel-report.md` — binary release verdict, blast-radius table, open items

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| NexusDeploy (deploy-manifest available) | ParityChecker |
| Validate phase complete | RolloutAdvisor |
