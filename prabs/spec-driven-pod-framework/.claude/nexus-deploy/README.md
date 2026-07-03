# NexusDeploy

The sprint close-out gate. Verifies that every requirement has a corresponding, verified artifact before the deploy manifest is issued. Also executes the deployment pipeline on release day and registers production artifacts in the production agent registry.

---

## When to Use

- Sprint build phase complete (Thursday EOD) — completeness check
- Release gate (Friday) — deploy manifest execution
- Mid-sprint completeness check at POD Lead request

**Trigger phrases:** `run NexusDeploy`, `check sprint completeness`, `generate deploy manifest`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `artifacts/review-verdict.yaml` | Mandatory |
| `data-contract-violations.yaml` | Mandatory |
| `prompt-bench-nfr-evidence.yaml` | Mandatory |
| Source code modules with provenance headers | Mandatory |
| Infrastructure config (Dockerfile, docker-compose) | Mandatory |

## Outputs

- `artifacts/deploy-manifest.yaml` — locked deployment scope for release execution
- `artifacts/completeness-report.md` — per-requirement completeness status

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ReviewPilot, TrustFabric, PromptBench complete | ReleaseIntel |
| Build phase (Thursday EOD) | ParityChecker |
