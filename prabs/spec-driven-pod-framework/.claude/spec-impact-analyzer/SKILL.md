---
name: spec-impact-analyzer
description: "SpecImpactAnalyzer is triggered whenever a change to openspec.yaml is proposed — either before sprint lock or mid-sprint. It traces the full downstream impact of the proposed change across all existing artifacts, estimates the regeneration and retest effort in builder-hours, classifies the change risk, and flags any closed HITL gates t..."
---

# SKILL: SpecImpactAnalyzer
**SpecPod Framework v2.1.0 · Planning · 04**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~50K tokens
**Role:** Change ripple detection across all sprint artifacts

---

## Purpose
SpecImpactAnalyzer is triggered whenever a change to `openspec.yaml` is proposed — either before sprint lock or mid-sprint. It traces the full downstream impact of the proposed change across all existing artifacts, estimates the regeneration and retest effort in builder-hours, classifies the change risk, and flags any closed HITL gates that would be invalidated. The output gives the POD Lead a data-driven proceed/defer/escalate decision in under 10 minutes.

---

## Trigger
Invoke whenever a spec change is proposed.

**Activation phrase:** `Run SpecImpactAnalyzer` or `Analyse spec change`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` (current) | POD Lead (locked) | REQUIRED |
| `artifacts/openspec-proposed.yaml` OR inline diff | POD Lead | REQUIRED |
| `artifacts/ai-manifest.json` | SpecFlow | REQUIRED |
| `artifacts/traceability-report.md` | TraceGraph | REQUIRED |
| `artifacts/task-breakdown.yaml` | SpecFlow | REQUIRED |
| `artifacts/decision-ledger.md` | DecisionLedger | REQUIRED |
| `specs/spec.md` | spec-generation (prior phase) | REQUIRED |
| `tests/*.feature` | Build phase | IF AVAILABLE |

---

## User Inputs Required

SpecImpactAnalyzer will ask the following before analysis:

1. **Change description:** "Describe the proposed change in one sentence. (Used as the Decision Ledger entry title)"
2. **Sprint timing:** "How many sprint days remain? (1–5)"
3. **Change source:** "Who is requesting this change? (business lead / POD Lead / technical discovery / external)"
4. **Risk tolerance:** "What is the current sprint risk posture? (low: defer anything > 2h / medium: accept up to 4h / high: accept any in-sprint-safe change)"

---

## Processing Instructions

### Phase 1 — Diff Parsing
1. If `openspec-proposed.yaml` is provided, compute the structural diff against `artifacts/openspec.yaml`
2. If an inline diff is provided in the message, parse it directly
3. Identify changed, added, and removed requirement IDs
4. Classify each change:
   - **ADDITIVE:** New requirement with no existing artifact dependencies → lower impact
   - **MODIFICATIVE:** Change to an existing requirement that has artifacts → may require regeneration
   - **DESTRUCTIVE:** Removal of a requirement that has artifacts → orphaned artifact risk
   - **NFR CHANGE:** Change to non-functional requirements → may require cross-cutting regeneration

### Phase 2 — Ripple Tracing
For each changed requirement ID:
1. Look up all downstream artifacts in `artifacts/traceability-report.md`
2. For each affected artifact, determine: regenerate / retest / redeploy required
3. Expand to transitive dependencies: if CLU-003 depends on CLU-001 and CLU-001 is affected, CLU-003 is also affected
4. Check `artifacts/decision-ledger.md` for any closed HITL gates that reference the affected requirements — flag if gate would be invalidated

### Phase 3 — Effort Estimation
For each affected artifact:
- Code file regeneration: 0.5h per file (heuristic baseline)
- Test scenario regeneration: 0.25h per scenario
- Integration retest: 1h per integration point
- Gate re-attestation: 0.5h per gate
- Total estimate: sum with ±30% variance range

### Phase 4 — Risk Classification
Classify the overall change:
- **IN-SPRINT SAFE:** Total effort ≤ risk tolerance threshold AND no closed gates invalidated
- **DEFER TO NEXT SPRINT:** Total effort > tolerance OR high-complexity regeneration required
- **SCOPE RISK:** Closed HITL gate would be invalidated OR critical path affected
- **ESCALATE:** Ambiguous impact, requires architectural judgment from POD Lead

### Phase 5 — Rework Scope Patch
If the change is classified IN-SPRINT SAFE and the POD Lead approves:
1. Generate `artifacts/rework-scope-patch.yaml` with the list of tasks to re-queue in Conductor
2. Mark affected artifacts in `ai-manifest.json` as `status: STALE`

---

## Output Files

### `artifacts/impact-analysis.md`
```markdown
# Impact Analysis — [Change Title]
Sprint: [ID] · Days Remaining: N · Generated: [Timestamp]

## Change Summary
- Type: MODIFICATIVE / ADDITIVE / DESTRUCTIVE / NFR
- Changed Requirements: [REQ-IDs]
- Requested By: [source]

## Affected Artifacts
| Artifact | Cluster | Impact Type | Est. Hours |
|----------|---------|-------------|------------|
| src/auth/login.ts | CLU-001 | REGENERATE | 0.5h |
| tests/auth.feature | CLU-001 | RETEST | 0.25h |

## HITL Gate Impact
| Gate | Status | Would Invalidate? |
|------|--------|-------------------|

## Effort Estimate
- Minimum: Nh · Expected: Nh · Maximum: Nh
- Available builder-hours remaining: Nh
- Capacity headroom: N%

## Risk Classification
**[IN-SPRINT SAFE / DEFER / SCOPE RISK / ESCALATE]**
Rationale: [one paragraph]

## Recommendation
[ ] PROCEED — approve change, dispatch rework-scope-patch.yaml to Conductor
[ ] DEFER — add to next sprint backlog with this analysis as context
[ ] ESCALATE — POD Lead architectural review required before decision
```

### `artifacts/rework-scope-patch.yaml`
Generated only if change is approved:
```yaml
sprint_id: SPRINT-XXX
change_id: CHANGE-NNN
approved_by: [approver]
approved_at: YYYY-MM-DDTHH:MM:SSZ
re_queue:
  - cluster_id: CLU-001
    reason: "REQ-001 modified: acceptance criteria changed"
    priority: HIGH
stale_artifacts:
  - src/auth/login.ts
  - tests/auth.feature
```

---

## Limitations
- Effort estimates are heuristic, not guaranteed. POD Lead makes the final proceed/defer call.
- Cannot detect semantic impact — a wording change that looks minor may have large architectural implications. Flag these for manual review.
- First sprint has no baseline for estimation accuracy. Estimates improve as historical sprint data accumulates.
