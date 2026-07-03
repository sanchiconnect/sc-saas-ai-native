# ControlPlane

The financial and security governor of the production AI system. Enforces hard monthly cost ceilings per agent and per feature, right-sizes compute allocations based on observed usage, and monitors access patterns for security anomalies. Blocks further consumption at 100% of a monthly ceiling — protecting against unbounded AI billing events.

---

## When to Use

Run during the Operate phase to set up cost governance and security posture monitoring for the production system.

**Trigger phrases:** `run ControlPlane`, `set up cost governance`, `configure cost ceilings`, `monitor AI costs`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `artifacts/roi-brief.md` | Mandatory |
| `specs/design.md` | Mandatory |
| Monthly cost ceiling per agent (elicited) | Mandatory |
| Alert threshold % (elicited) | Mandatory |
| Observability/billing data source (elicited) | Mandatory |

## Outputs

- `operate/control-plane/cost-config.yaml` — cost ceiling configuration consumed by RuntimeIQ
- `operate/control-plane/security-event-log.md` — access pattern anomaly log

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Deployment (deploy-manifest available) | RuntimeIQ (provides cost-config.yaml) |
| | IncidentLens (provides security-event-log) |
