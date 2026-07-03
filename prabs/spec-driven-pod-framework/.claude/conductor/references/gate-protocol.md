# HITL Gate Protocol
**SpecPod Framework v2.1.0 · Conductor Reference**

## Gate Definitions

### Gate 0 — Spec Lock
- **Trigger:** POD Lead locks `artifacts/openspec.yaml`
- **Required for:** All Step 1 planning skills to start
- **Cleared by:** POD Lead confirming `openspec.yaml` is final
- **Cannot be bypassed:** All planning skills halt until this gate clears

### Gate 0.5 — Assumption Clearance
- **Trigger:** AssumptionTracker produces `assumption-log.md` with HITL_BLOCKERS
- **Required for:** SpecFlow to begin decomposition
- **Cleared by:** POD Lead resolving or accepting each HITL_BLOCKER
- **Blocked tasks:** SpecFlow, and all downstream skills

### Gate 1 — Plan Sign-off
- **Trigger:** All Monday planning artifacts complete
- **Required artifacts:** sprint-board.md, scenario-matrix.md, decision-ledger.md
- **Cleared by:** POD Lead AND Business Lead sign-off
- **Enables:** Build phase dispatch (Tue–Thu)

### Gate 2 — Build Complete (Reference — not Monday)
- **Trigger:** All clusters in sprint-board.md reach COMPLETE status
- **Required for:** Validate phase
- **Cleared by:** POD Lead review of TraceGraph Gate-2 attestation

## Gate Clearance Procedure
1. Conductor detects gate condition met
2. Conductor presents gate checklist to POD Lead
3. POD Lead reviews and types: `GATE [N] CLEARED — [name]`
4. DecisionLedger logs the gate clearance event
5. Conductor resumes dispatch for downstream tasks

## Gate Failure Procedure
1. Conductor identifies a gate blocker
2. Conductor lists specific blockers with required actions
3. POD Lead resolves blockers and re-triggers gate check
4. Conductor re-validates and clears if resolved

## Emergency Bypass Protocol
Gates cannot be bypassed automatically. If the POD Lead needs to proceed with unresolved blockers:
1. Type: `BYPASS GATE [N] — ACCEPT RISK — [rationale]`
2. DecisionLedger auto-logs a risk-acceptance entry
3. Conductor proceeds with a RISK-ACCEPTED flag on all affected tasks
4. All RISK-ACCEPTED tasks are flagged in sprint-board.md for end-of-sprint review
