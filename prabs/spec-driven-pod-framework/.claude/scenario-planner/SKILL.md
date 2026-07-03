---
name: scenario-planner
description: "ScenarioPlanner runs a 3-scenario (best / expected / worst) analysis per major scope choice, identifies which assumptions most heavily influence ROI outcomes, calculates minimum viable scope, and flags scope items with high variance between best and worst case. It gives the POD Lead a 5-minute stress-test of scope choices instead of an..."
---

# SKILL: ScenarioPlanner
**SpecPod Framework v2.1.0 · Planning · 12 — Proposed**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~30K tokens
**Role:** ROI sensitivity and scope stress-testing

> ⬡ **Proposed** — scenario parameters and sensitivity ranges require definition from the business before meaningful outputs can be generated. Quality is directly bounded by the accuracy of ValueModeler inputs and POD Lead's best/worst case estimates.

---

## Purpose
ScenarioPlanner runs a 3-scenario (best / expected / worst) analysis per major scope choice, identifies which assumptions most heavily influence ROI outcomes, calculates minimum viable scope, and flags scope items with high variance between best and worst case. It gives the POD Lead a 5-minute stress-test of scope choices instead of an intuition-based decision, preventing commitment to scope that looks viable in the expected case but fails in the likely case.

---

## Trigger
Invoke after PortfolioPrioritizer produces `sprint-scope-ranked.md` (Step 5 of Monday planning, final step before Conductor dispatch).

**Activation phrase:** `Run ScenarioPlanner` or `Stress-test sprint scope`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/roi-brief.md` | ValueModeler | REQUIRED |
| `artifacts/sprint-scope-ranked.md` | PortfolioPrioritizer | REQUIRED |
| `artifacts/assumption-log.md` | AssumptionTracker | REQUIRED |
| `artifacts/task-breakdown.yaml` | SpecFlow | REQUIRED |
| `specs/program.md` | program-charter (prior phase) | REQUIRED |

---

## User Inputs Required

1. **Scenario parameters — Best case:**
   - "Best case: What % faster than estimated could builders deliver? (e.g., 20% faster)"
   - "Best case: What % higher than forecast could business value be? (e.g., 30% higher)"
   - "Best case: Probability estimate? (e.g., 20% likely)"

2. **Scenario parameters — Worst case:**
   - "Worst case: What % slower than estimated could delivery be? (e.g., 40% slower)"
   - "Worst case: What % lower than forecast could business value be? (e.g., 50% lower)"
   - "Worst case: Probability estimate? (e.g., 30% likely)"

3. **Expected case:** Confirm whether to use ValueModeler's base estimates as expected (yes/no — default yes)

4. **Scope options to stress-test:** "Which scope configurations should I model?
   - [A] Full PROCEED list from PortfolioPrioritizer
   - [B] Full PROCEED minus BORDERLINE items
   - [C] Must-ship items only (minimum viable scope)
   - [D] Custom scope — provide REQ-ID list"

5. **Minimum value threshold:** "What is the minimum acceptable sprint ROI for the expected scenario? (e.g., 150%)"

---

## Processing Instructions

### Phase 1 — Assumption Sensitivity Analysis
From `artifacts/assumption-log.md`:
1. Identify all HITL_BLOCKERS and WARNINGS — these are the high-sensitivity assumptions
2. For each, estimate the ROI swing if the assumption fails:
   - How much of the sprint value depends on this assumption being true?
   - What is the effort cost of rework if the assumption fails mid-sprint?
3. Rank assumptions by ROI sensitivity: `sensitivity_score = value_at_risk × (1 - confidence_score)`
4. Report the top 3 highest-sensitivity assumptions

### Phase 2 — 3-Scenario ROI Matrix
For each scope option selected by the POD Lead, compute three scenarios:

**Best Case:**
```
Delivery_Hours = estimated_hours × (1 - speed_improvement)
Value_Realised = forecast_value × (1 + value_uplift)
ROI = (Value_Realised - Investment) / Investment × 100%
```

**Expected Case:**
```
Delivery_Hours = estimated_hours (ValueModeler base)
Value_Realised = forecast_value (ValueModeler base)
ROI = roi_brief.md sprint ROI
```

**Worst Case:**
```
Delivery_Hours = estimated_hours × (1 + delivery_slowdown)
Value_Realised = forecast_value × (1 - value_reduction)
ROI = (Value_Realised - Investment_worst) / Investment_worst × 100%
```

### Phase 3 — Minimum Viable Scope
1. Start with must-ship items only
2. Add items from the ranked list in order until ROI threshold is met in the expected scenario
3. Verify this minimum viable scope still delivers positive ROI in the worst case
4. If worst-case ROI is negative even for minimum viable scope → escalate to POD Lead

### Phase 4 — Variance Flagging
For each scope item, compute variance ratio: `best_case_value / worst_case_value`
- Ratio > 3× → `HIGH_VARIANCE` — flag for POD Lead awareness
- Ratio 2–3× → `MEDIUM_VARIANCE`
- Ratio < 2× → `LOW_VARIANCE`

High-variance items are the scope choices that matter most for sprint outcome — POD Lead attention required.

---

## Output Files

### `artifacts/scenario-matrix.md`
```markdown
# Scenario Matrix — Sprint [ID]
Generated: [Timestamp]

## Scenario Parameters
| Parameter | Best Case | Expected | Worst Case | Probability |
|-----------|-----------|----------|------------|-------------|
| Delivery speed | +20% | base | −40% | 20% / 50% / 30% |
| Value realisation | +30% | base | −50% | 20% / 50% / 30% |

## ROI Scenario Matrix

### Option A: Full PROCEED Scope
| Scenario | Investment | Value (Annual) | ROI | Payback |
|----------|------------|---------------|-----|---------|
| Best | $N | $N | N% | N months |
| Expected | $N | $N | N% | N months |
| Worst | $N | $N | N% | N months |

**Verdict:** Expected ROI (N%) [ABOVE / BELOW] threshold (N%). Worst-case ROI (N%) is [POSITIVE / NEGATIVE].

---

### Option C: Minimum Viable Scope (Must-Ship Only)
[Same matrix format]

**Minimum viable scope REQ-IDs:** REQ-001, REQ-002, REQ-003
**Rationale:** These 3 requirements deliver N% of the total sprint value at N% of the effort.

---

## Top-3 Assumption Sensitivities (POD Lead Awareness)
| Rank | Assumption | Confidence | Value at Risk | Sensitivity Score |
|------|-----------|-----------|--------------|------------------|
| 1 | [ASM-ID description] | 0.3 | $N | N |

## High-Variance Scope Items (Outcomes Highly Uncertain)
| REQ-ID | Description | Best Value | Worst Value | Variance Ratio | Recommendation |
|--------|-------------|------------|-------------|---------------|----------------|

## Recommendation
[Concise 2–3 sentence recommendation for POD Lead on which scope option to proceed with and why]
```

---

## Limitations
- Scenario quality is entirely dependent on the accuracy of ValueModeler inputs and the realism of best/worst parameters provided by the POD Lead
- Probability estimates are illustrative — they inform intuition, not statistical prediction
- ScenarioPlanner does not make the decision — it informs the POD Lead's judgment
