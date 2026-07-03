# ValueTracker

Closes the ROI accountability loop. Compares actual post-deployment business metric performance against ValueModeler forecasts per requirement, identifies over/under-performing features, and feeds calibration data back to ValueModeler to improve future forecast accuracy.

> ⬡ **Proposed** — requires baseline metric collection to be in place before deployment. Business metrics must be instrumented BEFORE deploying ValueTracker.

---

## When to Use

Run during the Operate phase after sufficient production data has accumulated (recommended: 2+ weeks post-deployment).

**Trigger phrases:** `run ValueTracker`, `measure ROI`, `track value realisation`, `compare actual vs forecast`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/roi-brief.md` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/sprint-scope-ranked.md` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| Business metrics source (elicited) | Mandatory |
| Pre-deployment baseline metrics (elicited) | Mandatory |

## Outputs

- `operate/value-tracker/value-tracker-config.yaml` — metric mappings and measurement configuration
- `operate/value-tracker/value-realization-report.md` — per-feature actual vs. forecast ROI with variance classification
- `operate/value-tracker/value-modeler-calibration.yaml` — calibration data fed back to ValueModeler

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Deployment + measurement window elapsed | ValueModeler next sprint (calibration) |
| ValueModeler (provides roi-brief) | ExperimentOps (provides metric mappings) |
