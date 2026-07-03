---
name: value-modeler
description: "ValueModeler quantifies the expected business value of each sprint requirement before a single line of code is written. It calculates a per-requirement value forecast (time saved, error reduction, revenue impact) and a sprint-level ROI estimate with a confidence range."
---

# SKILL: ValueModeler
**SpecPod Framework v2.1.0 · Planning · 10 — Proposed**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~40K tokens
**Role:** Sprint ROI forecasting and per-requirement value quantification

> ⬡ **Proposed** — integration with ValueTracker (Operate phase) requires further design. Baseline metric inputs must be agreed with the business before first use. Accuracy improves across 3–5 sprints.

---

## Purpose
ValueModeler quantifies the expected business value of each sprint requirement before a single line of code is written. It calculates a per-requirement value forecast (time saved, error reduction, revenue impact) and a sprint-level ROI estimate with a confidence range. Low-value requirements are flagged for PortfolioPrioritizer's defer consideration. The output makes ROI accountability visible at the spec level — business leads can challenge weak-value requirements Monday morning rather than after delivery.

---

## Trigger
Invoke after SpecFlow produces `task-breakdown.yaml` (Step 5 of Monday planning).

**Activation phrase:** `Run ValueModeler` or `Forecast sprint ROI`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `artifacts/task-breakdown.yaml` | SpecFlow | REQUIRED |
| `specs/features.md` | spec-generation (prior phase) | REQUIRED |
| `specs/program.md` | program-charter (prior phase) | REQUIRED |
| `references/opportunity-catalogue.yaml` | TransformIQ references | REQUIRED |
| Prior sprint ValueTracker actuals | User (upload) | IF AVAILABLE |

---

## User Inputs Required

1. **Value dimensions:** "Which value dimensions apply to this sprint? Select all: [a] time saved (process automation) [b] error rate reduction [c] revenue enablement [d] cost avoidance [e] user experience / NPS [f] compliance risk reduction [g] technical debt reduction"
2. **Baseline metrics:** For each selected dimension, provide current state:
   - Time saved: "Current process time (minutes per occurrence) and daily frequency?"
   - Error rate: "Current error rate (%) and cost per error ($)?"
   - Revenue: "What revenue is blocked or at risk without this requirement?"
   - Cost avoidance: "What is the cost of NOT building this? ($/month)"
3. **Effort actuals:** "What is the actual builder-hour estimate per cluster? (Accept SpecFlow estimates or override)"
4. **Confidence modifier:** "Rate your confidence in these baseline metrics: (high / medium / low)"

---

## Processing Instructions

### Phase 1 — Requirement Value Classification
For each requirement, identify the value category:
- **Direct value:** Automates a manual process → time/cost savings calculable
- **Enabling value:** Unlocks a downstream capability → revenue or risk reduction
- **Quality value:** Improves reliability or compliance → cost avoidance
- **Experience value:** Improves user satisfaction → NPS / retention impact
- **Technical value:** Reduces debt or improves maintainability → future velocity gain

### Phase 2 — Per-Requirement Value Quantification
For Direct value requirements:
```
Annual Value = (time_saved_min / 60) × hourly_rate × daily_frequency × 250 working_days
```

For Enabling value requirements:
```
Annual Value = revenue_at_risk × probability_of_capture (from opportunity catalogue score / 10)
```

For Quality value (error reduction):
```
Annual Value = (current_error_rate - target_error_rate) × daily_occurrences × cost_per_error × 250
```

For Experience / Technical value:
Apply qualitative scoring (1–5) × $5K multiplier as a conservative proxy when hard data is unavailable.

### Phase 3 — Sprint ROI Calculation
```
Sprint_Investment = total_builder_hours × loaded_hourly_rate (default: $150/h)
Sprint_Annual_Value = sum of per-requirement annual values
Sprint_ROI = (Sprint_Annual_Value - Sprint_Investment) / Sprint_Investment × 100%
Payback_Period = Sprint_Investment / (Sprint_Annual_Value / 12) months
```

Apply confidence range: high confidence → ±15% / medium → ±30% / low → ±50%

### Phase 4 — Low-Value Flagging
Flag requirements where:
- Estimated annual value < 2× sprint investment allocated to that requirement → `DEFER_CANDIDATE`
- Value category is Technical/Experience only with qualitative scoring → `LOW_CONFIDENCE_VALUE`

### Phase 5 — Baseline Record
Produce a value baseline record for ValueTracker comparison post-deploy:
- Forecast values locked at planning time
- Actual values to be filled in during Operate phase

---

## Output Files

### `artifacts/roi-brief.md`
```markdown
# ROI Brief — Sprint [ID]
Generated: [Timestamp] · Confidence Level: [high/medium/low]

## Sprint ROI Summary
| Metric | Value |
|--------|-------|
| Builder Investment | N hours × $150 = $N |
| Estimated Annual Value | $N (range: $N – $N) |
| Sprint ROI | N% |
| Payback Period | N months |

## Per-Requirement Value Forecast
| REQ-ID | Description | Value Category | Annual Value | Builder Hours | Value/Hour | Flag |
|--------|-------------|----------------|-------------|---------------|------------|------|
| REQ-001 | Login flow | Direct | $24,000 | 3h | $8,000/h | — |
| REQ-007 | Bulk export | Enabling | $2,400 | 6h | $400/h | DEFER_CANDIDATE |

## Defer Candidates
Requirements flagged for PortfolioPrioritizer consideration:
- REQ-007: value/hour ratio below threshold ($400/h vs $2,000/h average)

## Assumptions & Confidence Notes
- Baseline process time: [source and date]
- Hourly rate used: $150 (loaded)
- First sprint — no actuals available for calibration

## Value Baseline Record (For ValueTracker)
[Forecast values locked for post-sprint comparison]
```

---

## Limitations
- Forecasts are estimates. Accuracy improves over 3–5 sprints as ValueTracker actuals accumulate.
- Requires consistent baseline metric inputs from the business — garbage in, garbage out.
- Technical and Experience value use qualitative proxies; treat these as directional, not accountable figures.
