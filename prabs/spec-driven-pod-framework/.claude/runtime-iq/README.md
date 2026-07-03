# RuntimeIQ

The continuous SLA sentinel for the production environment. Ingests live telemetry (latency percentiles, error rates, token consumption, agent health) and compares them against NFR targets locked in `openspec.yaml`. Alerts the POD Lead on threshold breaches. Enforces auto-scaling within the cost ceiling approved by ControlPlane.

---

## When to Use

Run during the Operate phase to set up continuous production SLA monitoring and auto-scaling.

**Trigger phrases:** `run RuntimeIQ`, `start SLA monitoring`, `set up production monitoring`, `generate SLA dashboard`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `specs/design.md` | Mandatory |
| `operate/control-plane/cost-config.yaml` | Mandatory |
| Observability stack type (elicited) | Mandatory |
| Metrics endpoint / connection string (elicited) | Mandatory |
| Alert notification channel (elicited) | Mandatory |

## Outputs

- `operate/runtime-iq/thresholds.yaml` — configured SLA thresholds per feature
- `operate/runtime-iq/sla-breach-log.md` — running breach log
- `operate/runtime-iq/feedback-loop-triggers.yaml` — performance signals for next sprint planning

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ControlPlane configured (cost-config available) | IncidentLens (provides breach log) |
| Deployment | ExperimentOps (provides thresholds) |
