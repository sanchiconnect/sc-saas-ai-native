# IncidentLens

Converts repeated production incidents into product improvement signals. Classifies every incident as one-off, pattern, or systemic, traces root causes to spec gaps or infrastructure limits, and produces actionable sprint backlog items. Distinguishes between incidents requiring a hotfix and those requiring a spec change.

---

## When to Use

Run during the Operate phase to log new incidents, classify existing ones, or generate a post-incident analysis report.

**Trigger phrases:** `run IncidentLens`, `analyse incidents`, `log a new incident`, `post-incident analysis`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `operate/runtime-iq/sla-breach-log.md` | Mandatory |
| `operate/runtime-iq/thresholds.yaml` | Mandatory |
| `operate/control-plane/security-event-log.md` | Mandatory |
| New incident details (elicited) | Mandatory |

## Outputs

- `operate/incident-lens/incident-log.md` — classified incidents with root causes and sprint backlog items
- Sprint backlog additions (hotfix items or spec change requests)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| RuntimeIQ and ControlPlane configured | RunbookSynth (enriches runbooks with fixes) |
| Production incidents occur | Next sprint planning |
