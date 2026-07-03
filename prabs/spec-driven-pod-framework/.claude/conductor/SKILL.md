---
name: conductor
description: "Conductor is the central nervous system of the sprint. It reads all planning artifacts produced on Monday, maps every task to the correct AI Builder and accelerator skill, sequences dispatch respecting inter-agent dependencies, holds dispatch until HITL gates are cleared, and maintains the live sprint board throughout the week."
---

# SKILL: Conductor
**SpecPod Framework v2.1.0 · Planning · 01**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~60K tokens
**Role:** Cross-phase sprint orchestrator and task dispatcher

---

## Purpose
Conductor is the central nervous system of the sprint. It reads all planning artifacts produced on Monday, maps every task to the correct AI Builder and accelerator skill, sequences dispatch respecting inter-agent dependencies, holds dispatch until HITL gates are cleared, and maintains the live sprint board throughout the week. It never bypasses a HITL gate — it queues and waits.

---

## Trigger
Invoke Conductor after all Step 1–6 planning artifacts are produced and Gate 1 (Plan Sign-off) is cleared by the POD Lead.

**Activation phrase:** `Run Conductor` or `Dispatch sprint board`

---

## Required Input Files
All files must be present before Conductor runs. If any are missing, Conductor will list them and halt.

| File | Source Skill | Required? |
|------|-------------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `artifacts/task-breakdown.yaml` | SpecFlow | REQUIRED |
| `artifacts/ai-manifest.json` | SpecFlow | REQUIRED |
| `artifacts/policy-catalogue.yaml` | PolicyCatalog | REQUIRED |
| `artifacts/traceability-report.md` | TraceGraph | REQUIRED |
| `artifacts/sprint-scope-ranked.md` | PortfolioPrioritizer | REQUIRED |
| `artifacts/assumption-log.md` | AssumptionTracker | REQUIRED |
| `artifacts/decision-ledger.md` | DecisionLedger | REQUIRED |
| `artifacts/context.yaml` | ContextFabric | IF AVAILABLE |
| `artifacts/impact-analysis.md` | SpecImpactAnalyzer | IF SPEC CHANGED |
| `artifacts/rework-scope-patch.yaml` | SpecImpactAnalyzer | IF SPEC CHANGED |
| `specs/tasks.md` | spec-generation (prior phase) | REQUIRED |
| `specs/program.md` | program-charter (prior phase) | REQUIRED |

---

## User Inputs Required
Conductor will ask these questions before dispatching if the answers are not in the artifacts:

1. **Builder availability:** "How many AI Builders are active today? (default: 2)" 
2. **Capacity override:** "Has sprint capacity changed from what PortfolioPrioritizer was given? (yes/no)"
3. **Gate status:** "Has Gate 1 (Plan Sign-off) been cleared? Confirm with: YES, GATE 1 CLEARED"
4. **Priority override:** "Are there any manual task priority overrides from the POD Lead not captured in the ranked scope list?"

---

## Processing Instructions

### Phase 1 — Pre-flight Validation
1. Verify all REQUIRED input files are present. List any missing files and halt if any are absent.
2. Confirm Gate 1 is cleared. If not, output a pending gate notice and stop.
3. Check `assumption-log.md` for any OPEN HITL blockers. If blockers exist, list them and halt — do not dispatch.
4. Cross-reference `sprint-scope-ranked.md` against `task-breakdown.yaml` to confirm only PROCEED items are dispatched.

### Phase 2 — Task-to-Builder Mapping
For each task in `task-breakdown.yaml` with status PROCEED:
1. Assign to an AI Builder based on task type (use the capability matrix in `references/capability-matrix.md`)
2. Identify which accelerator skill the builder should invoke for that task type
3. Resolve inter-task dependencies from the dependency graph in `task-breakdown.yaml`
4. Flag tasks that cannot start until a predecessor completes — mark as BLOCKED with dependency ID

### Phase 3 — Sprint Board Generation
Produce `artifacts/sprint-board.md` in the format specified in the Output section.

### Phase 4 — Dispatch Log
Produce `artifacts/dispatch-log.md` with each dispatch event timestamped.

### Phase 5 — Completion Forecast
Calculate: tasks remaining × average task duration / available builder-hours = days remaining estimate.

---

## Output Files

### `artifacts/sprint-board.md`
```markdown
# Sprint Board — [Sprint ID] — [Date]

## Status Summary
- Total Tasks: N
- Dispatched: N
- Blocked (dependency): N
- Blocked (HITL): N
- Deferred: N

## Task Board

| Task ID | Description | Builder | Skill | Status | Depends On | ETA |
|---------|-------------|---------|-------|--------|------------|-----|
| T-001   | ...         | Builder-1 | spec-flow | DISPATCHED | — | Tue AM |
| T-002   | ...         | Builder-2 | spec-flow | DISPATCHED | — | Tue PM |
| T-003   | ...         | Builder-1 | — | BLOCKED | T-001 | Wed AM |

## HITL Gate Queue
(Tasks waiting for gate clearance)

## Escalation Queue
(Tasks that failed or require POD Lead input)

## Completion Forecast
- Builder-hours available: N
- Builder-hours consumed: N
- Estimated completion: [Day]
```

### `artifacts/dispatch-log.md`
Append-only log. Format per entry:
```
[TIMESTAMP] DISPATCHED | Task: [ID] | Builder: [N] | Skill: [name] | Trigger: [Gate/Auto]
[TIMESTAMP] BLOCKED    | Task: [ID] | Reason: [dependency/HITL] | Waiting on: [ID/Gate]
[TIMESTAMP] ESCALATED  | Task: [ID] | Reason: [description] | Action required: POD Lead
```

---

## Escalation Rules
- Task fails twice → escalate to POD Lead immediately
- HITL gate not cleared within 2 hours → send reminder to POD Lead
- Spec change detected mid-sprint → pause all affected tasks, trigger SpecImpactAnalyzer, await POD Lead decision
- Builder capacity drops to 0 → halt all dispatch, notify POD Lead

---

## Limitations
- Cannot resolve genuine resource contention without human input
- HITL gate release always requires POD Lead confirmation — Conductor queues but never bypasses
- Re-routing decisions on failed tasks are suggestions — POD Lead makes the final call

---

## References
- `references/capability-matrix.md` — AI Builder skill-to-task type mapping
- `references/gate-protocol.md` — HITL gate clearance procedures
