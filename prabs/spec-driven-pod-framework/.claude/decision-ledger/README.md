# DecisionLedger

Captures every scope, spec, and HITL gate decision during the sprint in a structured, append-only log. Each entry is timestamped, linked to the affected requirement ID, and attributed to a named approver. Superseded decisions are marked but never deleted.

---

## When to Use

Invoked on-demand throughout Monday and the rest of the sprint — every time a decision is made, a gate is cleared, a defer is logged, or a spec change is approved. Never batched.

**Trigger phrases:** `Log decision:`, `Record HITL gate clearance`, `Log defer:`, `Log spec change approved:`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/decision-ledger.md` (prior run) | Optional (append mode) |
| `artifacts/openspec.yaml` | For REQ-ID validation |
| `artifacts/impact-analysis.md` | For spec change entries |
| `artifacts/sprint-scope-ranked.md` | For defer entries |

## Outputs

- `artifacts/decision-ledger.md` — immutable append-only decision log with gate attestations

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Any decision, gate clearance, or scope change | Conductor (reads ledger before dispatch) |
| | SpecImpactAnalyzer (reads ledger for context) |
