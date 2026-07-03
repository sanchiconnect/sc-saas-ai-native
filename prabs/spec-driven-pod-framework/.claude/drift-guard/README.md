# DriftGuard

The production behaviour watchdog. Continuously samples live AI model outputs from production traffic and evaluates them against the locked `openspec.yaml` spec and EvalHarness golden-set. Scores divergence, classifies direction (regression vs. improvement), and automatically triggers a revalidation workflow when cumulative drift exceeds the configured threshold.

---

## When to Use

Run during the Operate phase to set up continuous drift monitoring after deployment.

**Trigger phrases:** `run DriftGuard`, `check for model drift`, `detect output drift`, `start drift monitoring`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| `specs/features.md` | Mandatory |
| EvalHarness baseline location (elicited) | Mandatory |
| Production traffic sampling rate (elicited) | Mandatory |
| Drift threshold per feature (elicited) | Mandatory |

## Outputs

- `operate/drift-guard/drift-report.md` — per-feature drift scores and classification
- Revalidation trigger (when threshold exceeded)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Deployment + EvalHarness baseline established | RunbookSynth (provides drift-report) |
| | IncidentLens (cross-reference) |
