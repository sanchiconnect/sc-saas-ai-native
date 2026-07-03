---
name: assumption-tracker
description: "AssumptionTracker ingests weak-evidence flags from ResearchCopilot and explicit assumptions in openspec.yaml. It assigns a confidence score (0–1) to each assumption, flags low-confidence items as HITL gate blockers, tracks resolution throughout the sprint lifecycle, and escalates unresolved items to DecisionLedger for explicit risk acc..."
---

# SKILL: AssumptionTracker
**SpecPod Framework v2.1.0 · Planning · 09 — Proposed**
**Model:** claude-haiku-4-5-20251001 · **Context Budget:** ~20K tokens
**Role:** Sprint assumption confidence and HITL blocker management

> ⬡ **Proposed** — confidence threshold definition and escalation rules need stakeholder alignment before production use. First 2–3 sprints require manual POD Lead tuning of threshold values.

---

## Purpose
AssumptionTracker ingests weak-evidence flags from ResearchCopilot and explicit assumptions in `openspec.yaml`. It assigns a confidence score (0–1) to each assumption, flags low-confidence items as HITL gate blockers, tracks resolution throughout the sprint lifecycle, and escalates unresolved items to DecisionLedger for explicit risk acceptance. One unresolved low-confidence assumption can invalidate an entire sprint — this skill makes hidden risks visible before code is written.

---

## Trigger
Invoke after ResearchCopilot produces `evidence-map.md` (Step 2 of Monday planning).

**Activation phrase:** `Run AssumptionTracker` or `Score sprint assumptions`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/evidence-map.md` | ResearchCopilot | REQUIRED |
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `specs/knowledge.md` | spec-knowledge (prior phase) | REQUIRED |
| `references/assumption-history.yaml` | AssumptionTracker references | IF AVAILABLE |

---

## User Inputs Required

1. **Confidence threshold:** "What confidence score (0–1) should trigger a HITL blocker? (default: 0.4 — items below this require explicit POD Lead risk acceptance before dispatch)"
2. **Resolution deadline:** "When must all HITL blockers be resolved for Gate-1 to clear? (default: 2h before Gate-1)"
3. **Prior sprint context:** "Were any of these assumptions present in prior sprints? If yes, how were they resolved? (paste resolution notes or type NONE)"
4. **Risk posture:** "What is the sprint risk tolerance for unresolved assumptions? (conservative: block all below threshold / balanced: block below 0.3, warn 0.3–0.5 / aggressive: warn only, no blocks)"

---

## Processing Instructions

### Phase 1 — Assumption Inventory
1. Extract explicit assumptions from `artifacts/openspec.yaml` — any requirement tagged `assumption: true` or containing assumption language ("assumes", "requires", "depends on availability of", "provided that")
2. Import weak-evidence escalations from `artifacts/evidence-map.md` — all items flagged as WEAK, CONTRADICTED, or NO-EVIDENCE become tracked assumptions
3. Load `specs/knowledge.md` for domain-level assumption context
4. Deduplicate: if the same assumption appears in both openspec and evidence-map, merge into a single entry

### Phase 2 — Confidence Scoring
For each assumption, compute a confidence score (0–1) using the following heuristics:

| Factor | Score Modifier |
|--------|---------------|
| Evidence strength: CONFIRMED | +0.4 |
| Evidence strength: PARTIAL | +0.2 |
| Evidence strength: WEAK | +0.0 |
| Evidence strength: NO-EVIDENCE | -0.2 |
| Evidence strength: CONTRADICTED | -0.4 |
| Prior sprint: resolved successfully | +0.2 |
| Prior sprint: unresolved / wrong | -0.2 |
| Dependency on external system/team | -0.1 |
| POD Lead domain expertise available | +0.1 |

Base score: 0.5. Clamp result to [0.0, 1.0].

### Phase 3 — HITL Blocker Classification
- Score < confidence_threshold AND risk_posture != aggressive → `HITL_BLOCKER`
- Score between threshold and 0.6 AND risk_posture == conservative → `HITL_BLOCKER`
- Score between threshold and 0.6 AND risk_posture == balanced → `WARNING`
- Score ≥ 0.6 → `TRACKED` (monitor but do not block)

### Phase 4 — Resolution Tracking
For each HITL_BLOCKER, recommend one of:
- **VALIDATE:** Gather specific evidence before proceeding (specify what evidence would resolve it)
- **ACCEPT_RISK:** POD Lead explicitly accepts the assumption risk and logs in DecisionLedger
- **DEFER:** Move the dependent requirement to the next sprint
- **DESCOPE:** Remove the requirement from scope

### Phase 5 — Escalation to DecisionLedger
For each HITL_BLOCKER resolved via ACCEPT_RISK:
Generate a DecisionLedger entry payload:
```
Type: risk-acceptance
Decision: "[Assumption text] — risk accepted, proceeding with confidence [score]"
Rationale: [POD Lead's stated rationale]
Affected Requirements: [REQ-IDs]
```

---

## Output Files

### `artifacts/assumption-log.md`
```markdown
# Assumption Log — Sprint [ID]
Generated: [Timestamp] · Confidence Threshold: [N]

## Summary
- Total Assumptions: N
- HITL_BLOCKERS: N ← Gate-0.5 cannot clear until all resolved
- WARNINGS: N
- TRACKED: N
- RESOLVED: N

## HITL Blockers (Gate Blockers — Must Resolve Before Gate-0.5)

### ASM-001 — [Assumption Description]
- **Source:** openspec.yaml / evidence-map.md
- **Affected Requirements:** REQ-007, REQ-012
- **Confidence Score:** 0.25
- **Scoring Factors:** No evidence (−0.2), external dependency (−0.1), partial domain expertise (+0.1)
- **Status:** OPEN
- **Recommended Resolution:** VALIDATE — obtain confirmation from [specific team/source]
- **Resolution Deadline:** [Time]

## Warnings (Non-blocking — Monitor)
| ASM-ID | Description | Score | REQ-IDs | Recommended Action |
|--------|-------------|-------|---------|-------------------|

## Tracked Assumptions (Low Risk)
| ASM-ID | Description | Score | Status |
|--------|-------------|-------|--------|

## Resolved Assumptions
| ASM-ID | Description | Resolution | DecisionLedger Ref |
|--------|-------------|------------|-------------------|
```

---

## Limitations
- Confidence thresholds are subjective until calibrated across 2–3 sprints
- First sprint: scoring is approximation — treat all HITL_BLOCKERS as requiring manual POD Lead review regardless of score
- AssumptionTracker identifies risks; it does not resolve them — resolution requires human judgment
