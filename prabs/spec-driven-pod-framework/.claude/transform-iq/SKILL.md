---
name: transform-iq
description: "TransformIQ rescores the AI opportunity backlog against the current sprint's requirements and operational signals from prior sprints. It surfaces unmapped value candidates that are not yet in scope but have high effort-to-value ratios for 1-week delivery."
---

# SKILL: TransformIQ
**SpecPod Framework v2.1.0 · Planning · 06**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~40K tokens
**Role:** AI opportunity backlog rescoring and surface

---

## Purpose
TransformIQ rescores the AI opportunity backlog against the current sprint's requirements and operational signals from prior sprints. It surfaces unmapped value candidates that are not yet in scope but have high effort-to-value ratios for 1-week delivery. The output feeds PortfolioPrioritizer for final ranking and ensures the business lead starts Monday with a current opportunity map, not stale scores.

---

## Trigger
Invoke in parallel with PolicyCatalog, ContextFabric, and ResearchCopilot at Step 1 of Monday planning.

**Activation phrase:** `Run TransformIQ` or `Rescore opportunity backlog`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `specs/features.md` | spec-generation (prior phase) | REQUIRED |
| `specs/program.md` | program-charter (prior phase) | REQUIRED |
| `references/opportunity-catalogue.yaml` | TransformIQ references | REQUIRED |
| `artifacts/feedback-loop-triggers.yaml` | Prior Operate phase | IF AVAILABLE |

---

## User Inputs Required

1. **Sprint strategic theme:** "What is the primary strategic objective for this sprint? (e.g., reduce handle time / improve data quality / enable new user segment)"
2. **Strategic weights:** "Rate the following dimensions 1–5 for this sprint's scoring: [Strategic fit / Speed to value / Risk / User impact / Technical debt reduction]"
3. **Candidate threshold:** "What is the minimum value-density score (0–10) to surface as a candidate addition? (default: 7)"
4. **First sprint check:** "Is this the first sprint? (yes/no) — If yes, prior actuals are unavailable and scores will be approximations."

---

## Processing Instructions

### Phase 1 — Current Backlog Scan
1. Load `references/opportunity-catalogue.yaml` — the full AI opportunity backlog with historical scores
2. Load `specs/features.md` — features already planned for this sprint
3. Identify which backlog items are already in sprint scope vs. unmapped

### Phase 2 — Signal Ingestion
If `artifacts/feedback-loop-triggers.yaml` is available:
1. Extract operational signals: which prior sprint items delivered value, which underdelivered
2. Extract pattern signals: recurring user pain points, repeated defect categories, process bottlenecks
3. Map signals to backlog items that address the same root cause

### Phase 3 — Rescoring
For each backlog item, compute a composite score:
```
Score = (Strategic_Fit × W1) + (Speed_to_Value × W2) + (Risk_Inverse × W3) + (User_Impact × W4) + (Tech_Debt × W5)
```
Where W1–W5 are the POD Lead's strategic weights normalised to sum to 1.

Calibrate against prior sprint actuals if available:
- Item scored high but underdelivered → reduce score by 20% with a calibration note
- Item scored medium but overdelivered → increase score by 10% with a calibration note

### Phase 4 — Candidate Surfacing
1. Filter items above the candidate threshold that are NOT in current sprint scope
2. For each candidate, compute effort-to-value ratio: `Value_Score / Estimated_Builder_Hours`
3. Rank by effort-to-value ratio descending — these are the quick wins

### Phase 5 — Value Density Summary
Produce a 1-table summary for the business lead: top 5 candidates by value density with a one-line rationale each.

---

## Output Files

### `artifacts/opportunity-backlog-rescored.md`
```markdown
# Opportunity Backlog — Rescored for Sprint [ID]
Generated: [Timestamp] · Sprint Theme: [theme]

## Scoring Weights Applied
| Dimension | Weight |
|-----------|--------|
| Strategic Fit | N% |
| Speed to Value | N% |
...

## Current Sprint Items (Already In Scope)
| REQ-ID | Backlog Ref | Prior Score | New Score | Δ | Calibration Note |
|--------|-------------|-------------|-----------|---|-----------------|

## Candidate Additions (Not In Scope — Above Threshold)
| OPP-ID | Title | Score | Effort (h) | Value Density | Evidence |
|--------|-------|-------|------------|---------------|---------|
| OPP-042 | Auto-classify inbound tickets | 8.4 | 4h | 2.1 | 3 prior feedback triggers |

## Value Density Summary — Top 5 Quick Wins
1. **[OPP-ID]** — [title]: [one-line rationale]
...

## Items Descored This Sprint
| OPP-ID | Prior Score | New Score | Reason |
```

---

## Limitations
- Scoring accuracy depends on the richness of operational feedback from prior sprints
- First sprint scores are approximations based on strategic weights alone — treat as directional, not precise
- TransformIQ surfaces candidates; it does not add them to scope. PortfolioPrioritizer and the POD Lead make the final inclusion decision.
