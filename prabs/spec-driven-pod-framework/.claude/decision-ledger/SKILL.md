---
name: decision-ledger
description: "DecisionLedger captures every scope, spec, and HITL gate decision made during the sprint in a structured, append-only log. Each entry is timestamped, linked to the affected requirement ID, and attributed to a named approver."
---

# SKILL: DecisionLedger
**SpecPod Framework v2.1.0 · Planning · 08**
**Model:** claude-haiku-4-5-20251001 · **Context Budget:** ~20K tokens
**Role:** Immutable audit trail for all scope and spec decisions

---

## Purpose
DecisionLedger captures every scope, spec, and HITL gate decision made during the sprint in a structured, append-only log. Each entry is timestamped, linked to the affected requirement ID, and attributed to a named approver. Superseded decisions are marked but never deleted. The ledger is queryable by requirement ID, date range, or approver, and produces the official attestation records for all HITL gates.

---

## Trigger
DecisionLedger is invoked on-demand throughout Monday and the rest of the sprint. It is never batched — every decision is logged as it happens.

**Activation phrases:**
- `Log decision: [description]`
- `Record HITL gate [N] clearance`
- `Log defer: [REQ-ID]`
- `Log spec change approved: [change description]`
- `Query ledger: [requirement ID / date / approver]`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/decision-ledger.md` | Prior DecisionLedger run | IF EXISTS (append mode) |
| `artifacts/openspec.yaml` | POD Lead | FOR REQ-ID VALIDATION |
| `artifacts/impact-analysis.md` | SpecImpactAnalyzer | FOR SPEC CHANGE ENTRIES |
| `artifacts/sprint-scope-ranked.md` | PortfolioPrioritizer | FOR DEFER ENTRIES |

---

## User Inputs Required

For every log entry, DecisionLedger collects:

1. **Decision type:** Prompt: "Decision type? (scope-change / spec-change / defer / descope / gate-clearance / risk-acceptance / assumption-resolution)"
2. **Decision text:** Prompt: "State the decision in one clear sentence."
3. **Rationale:** Prompt: "What is the rationale? (1–3 sentences)"
4. **Approver:** Prompt: "Who approved this decision? (name or role)"
5. **Affected requirement(s):** Prompt: "Which requirement IDs are affected? (comma-separated, or NONE)"
6. **Supersedes:** Prompt: "Does this supersede a prior decision? (enter prior decision ID, or NO)"

For HITL gate clearances, additionally:
7. **Gate ID:** "Which gate is being cleared? (Gate-0 / Gate-0.5 / Gate-1 / Gate-2)"
8. **Conditions:** "Are there any conditions or caveats on this clearance? (or NONE)"

---

## Processing Instructions

### Log Entry Mode
1. Collect all required inputs
2. Generate a unique decision ID: `DEC-[SPRINT-ID]-[NNN]` (auto-incrementing)
3. Timestamp the entry: `YYYY-MM-DDTHH:MM:SSZ`
4. If `supersedes` is specified, mark the prior decision as `STATUS: SUPERSEDED by [new DEC-ID]`
5. Append entry to `artifacts/decision-ledger.md` — never modify existing entries
6. Confirm to user: "Decision [DEC-ID] logged."

### Query Mode
When the user invokes a query:
- **By REQ-ID:** Return all decisions affecting the specified requirement, sorted by timestamp descending
- **By date range:** Return all decisions within the specified window
- **By approver:** Return all decisions attributed to the specified approver
- **By type:** Return all decisions of the specified type
- **Full log:** Return entire ledger formatted as a readable table

### Sprint Summary Mode
At the end of Monday (or when requested):
Produce `artifacts/decision-summary.md` — a condensed business-lead-ready summary of all decisions made, grouped by type.

---

## Output Files

### `artifacts/decision-ledger.md`
Append-only. Each entry formatted as:
```markdown
---
## DEC-SPRINT-XXX-001
- **Type:** gate-clearance
- **Timestamp:** 2026-05-27T09:45:00Z
- **Decision:** Gate 1 cleared — sprint plan approved for Build phase dispatch.
- **Rationale:** All traceability checks passed. Scenario matrix reviewed. No HITL blockers outstanding.
- **Approver:** [POD Lead Name]
- **Affected Requirements:** ALL (sprint-wide)
- **Gate:** Gate-1
- **Conditions:** NONE
- **Status:** ACTIVE
- **Supersedes:** N/A

---
## DEC-SPRINT-XXX-002
- **Type:** defer
- **Timestamp:** 2026-05-27T10:12:00Z
- **Decision:** REQ-007 deferred to Sprint [N+1].
- **Rationale:** CONTRADICTED by evidence (see evidence-map.md). Insufficient time to resolve stakeholder conflict before Gate-1.
- **Approver:** [POD Lead Name]
- **Affected Requirements:** REQ-007
- **Status:** ACTIVE
- **Supersedes:** N/A
```

### `artifacts/decision-summary.md`
Business-lead-ready sprint decision summary produced on-demand or at end-of-Monday:
```markdown
# Sprint [ID] — Decision Summary
Date: [Date] · Prepared By: DecisionLedger

## Gate Clearances
- Gate 1 cleared at 09:45 by [approver]

## Scope Decisions
- 2 requirements deferred: REQ-007, REQ-012
- 1 requirement descoped: REQ-015

## Spec Changes Approved
- 1 change approved: [change title] (DEC-XXX-003)

## Risk Acceptances
- 1 assumption risk accepted: [assumption title]

## Full Ledger
See artifacts/decision-ledger.md
```

---

## Limitations
- Only captures decisions that flow through defined channels. Verbal-only decisions that bypass the system leave no trace — POD Lead must log them manually.
- DecisionLedger never modifies or deletes entries. Corrections are new entries that supersede prior ones.
- Append-only integrity must be enforced by the POD Lead — the file should be treated as immutable outside of DecisionLedger invocations.
