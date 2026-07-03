# RunbookSynth

Generates complete, step-by-step operational runbooks per deployed feature and integration. On each new deployment, automatically diffs the previous runbook against the new system state and updates only the sections that changed. As IncidentLens surfaces root causes and verified fixes, enriches runbooks with "Known Issue" and "Verified Fix" sections.

---

## When to Use

Run during the Operate phase after each deployment to generate or update operational runbooks.

**Trigger phrases:** `run RunbookSynth`, `generate runbooks`, `update runbooks after deployment`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `artifacts/decision-ledger.md` | Mandatory |
| `operate/incident-lens/incident-log.md` | Optional |
| `operate/drift-guard/drift-report.md` | Optional |

## Outputs

- `operate/runbook-synth/runbooks/<feature>.md` — per-feature operational runbooks
- `operate/runbook-synth/rollback-runbook.md` — rollback-specific runbook (if requested)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Deployment (deploy-manifest available) | Incident response |
| IncidentLens (enriches runbooks with fixes) | |
