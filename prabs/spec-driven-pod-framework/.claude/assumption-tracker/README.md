# AssumptionTracker

Scores sprint assumptions from ResearchCopilot evidence and `openspec.yaml`, flags low-confidence items as HITL gate blockers, and escalates unresolved items to DecisionLedger for explicit risk acceptance.

> ⬡ **Proposed** — confidence threshold definition and escalation rules need stakeholder alignment before production use.

---

## When to Use

Invoke after ResearchCopilot produces `evidence-map.md` (Step 2 of Monday planning).

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/evidence-map.md` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `specs/knowledge.md` | Mandatory |
| `references/assumption-history.yaml` | Optional |

## Outputs

- `artifacts/assumption-log.md` — scored assumptions with HITL blocker classification and resolution status

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ResearchCopilot | Conductor |
| | DecisionLedger (escalations) |
