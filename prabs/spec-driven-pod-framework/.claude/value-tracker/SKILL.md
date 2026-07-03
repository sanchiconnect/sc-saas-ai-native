---
name: value-tracker
description: "> ⬡ PROPOSED STATUS — Requires baseline metric collection to be in place before deployment. > Metrics integration with business systems needs further design with ValueModeler (Planning)."
---

# SKILL.md — ValueTracker

```yaml
skill_id:      value-tracker
display_name:  ValueTracker
phase:         Operate
agent_ref:     O-06
version:       1.0.0
model:         claude-sonnet-4-20250514
token_budget:  ~40K
status:        proposed
```

> ⬡ **PROPOSED STATUS** — Requires baseline metric collection to be in place before deployment.
> Metrics integration with business systems needs further design with ValueModeler (Planning).
> The POD Lead must instrument business metrics BEFORE deploying ValueTracker.

---

## Skill Purpose

ValueTracker closes the ROI accountability loop that most teams never close. It reads the sprint's ROI forecast from `roi-brief.md` (produced by ValueModeler during planning), ingests live business metrics from production, and compares actuals against forecasts per requirement. It identifies which features are over-performing, which are under-performing, and why — tracing variance to specific spec choices or deployment decisions. Critically, it feeds actuals back to ValueModeler as calibration data so that over 5–10 sprints, ROI forecasts become progressively more accurate, transforming ROI from a planning fiction into a reliable decision instrument.

---

## Trigger Phrases

```
"run ValueTracker"
"measure ROI"
"track value realisation"
"compare actual vs forecast"
"check ROI performance"
"measure feature value"
"close the ROI loop"
"value measurement setup"
"generate ROI report"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/roi-brief.md` | Phase 3 — ValueModeler | Sprint ROI forecast: predicted value per feature cluster, metrics, measurement period |
| `artifacts/openspec.yaml` | Phase 3 — Planning | Feature definitions and acceptance criteria |
| `artifacts/sprint-scope-ranked.md` | Phase 3 — PortfolioPrioritizer | Priority ranking — context for interpreting value performance |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | Deployment timestamp — start of measurement window |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| Business metrics source | Elicitation Q1 | Yes | Where live business metrics are stored |
| Baseline metrics (pre-deployment) | Elicitation Q2 | Yes | Must be captured BEFORE deployment |
| Measurement window | Elicitation Q3 | Yes | How long post-deployment before measuring |
| Business metrics to track | Elicitation Q4 | Yes | Which KPIs map to which features |
| Reporting cadence | Elicitation Q5 | Yes | How often to produce realisation report |

---

## Elicitation Protocol

> **PREREQUISITE CHECK**: Before running ValueTracker, confirm baseline metrics were captured pre-deployment.
> If no baseline exists, ValueTracker cannot produce meaningful comparisons.

### Q&A Sequence

```yaml
questions:
  - id: Q_PRE
    required: true
    prompt: |
      ⚠️  PREREQUISITE: ValueTracker requires pre-deployment baseline metrics.
      Were business metrics captured BEFORE this sprint was deployed?
      (yes / no — if no, ValueTracker will set up baseline capture for the NEXT deployment)
    type: single_select
    options: [yes, no]
    depends_on: null

  - id: Q_BASELINE_SETUP
    required: true
    prompt: |
      No baseline metrics exist yet. ValueTracker will generate a baseline capture script
      that must be run BEFORE the next deployment. Should I generate the baseline setup now?
      (yes / no)
    type: single_select
    options: [yes, no]
    depends_on: "Q_PRE == no"

  - id: Q1
    required: true
    prompt: |
      Where are live business metrics stored / accessible?
    type: single_select
    options:
      - Database (SQL — provide connection string reference)
      - REST API endpoint (provide URL)
      - CSV / Excel export (provide file path)
      - Google Analytics / GA4 (provide property ID)
      - Mixpanel (provide project token reference)
      - Amplitude (provide API key reference)
      - Custom data warehouse (describe below)
      - Not yet instrumented (generate instrumentation guide)
    depends_on: "Q_PRE == yes"

  - id: Q1b
    required: true
    prompt: |
      Provide the connection details (connection string reference, URL, or property ID):
      (Use env var names, not literal credentials — e.g. DB_CONNECTION_STRING)
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q1 not in ['Not yet instrumented (generate instrumentation guide)']"

  - id: Q2
    required: true
    prompt: |
      Where are the pre-deployment baseline metrics stored?
      (Path to file, or enter "captured" if stored in the same system as Q1):
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q_PRE == yes"

  - id: Q3
    required: true
    prompt: |
      What measurement window should ValueTracker use after deployment?
      The roi-brief.md may specify a period — check it first.
      Select:
    type: single_select
    options:
      - 7 days post-deployment
      - 14 days post-deployment
      - 30 days post-deployment (recommended for most features)
      - 60 days post-deployment
      - Sprint-end (fixed to next sprint cycle)
      - As defined in roi-brief.md
    depends_on: "Q_PRE == yes"

  - id: Q4
    required: true
    prompt: |
      Map business metrics to features. For each feature in the sprint, specify which
      business KPI measures its value.
      Format: feature_id=metric_name, one per line. Example:
        summarisation=average_handle_time_seconds
        classification=ticket_routing_accuracy_pct
        recommendation=conversion_rate_pct
      Enter mappings (reference roi-brief.md for the forecasted metrics):
    type: free_text
    validation: "Each line: string=string format"
    depends_on: "Q_PRE == yes"

  - id: Q5
    required: true
    prompt: |
      How often should ValueTracker generate a Value Realisation Report?
    type: single_select
    options:
      - Daily (track early post-deployment signals)
      - Weekly (standard — recommended)
      - At end of measurement window only
      - On-demand (manual trigger only)
    depends_on: "Q_PRE == yes"

  - id: Q6
    required: true
    prompt: |
      Should the realisation data be fed back to ValueModeler automatically to calibrate
      future forecasts? (yes / no)
    type: single_select
    options: [yes, no]
    default: yes
    depends_on: "Q_PRE == yes"
```

### Confirmation Gate

```
ValueTracker Configuration Summary
─────────────────────────────────────────────
Baseline available    : [Q_PRE]
Metrics source        : [Q1] → [Q1b]
Baseline location     : [Q2]
Measurement window    : [Q3]
Feature-metric map    : [Q4 parsed]
Reporting cadence     : [Q5]
Calibration feedback  : [Q6]
ROI forecast from     : artifacts/roi-brief.md
─────────────────────────────────────────────
Type CONFIRM to generate all ValueTracker artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

### Baseline Setup Mode (Q_PRE = no)

1. Generate `baseline-capture.py` — a script that queries all Q4-mapped metrics and writes them to `operate/value-tracker/baseline-metrics.yaml` with a deployment timestamp.
2. Generate `baseline-capture-guide.md` — instructions for running baseline capture before next deployment.
3. Abort main ValueTracker generation until baseline is captured.

### Active Measurement Mode (Q_PRE = yes)

1. **Parse ROI forecast** — Read `artifacts/roi-brief.md`. Extract per-feature predicted value, metric names, baseline assumptions, and measurement period.

2. **Load baseline metrics** — Read pre-deployment baseline from Q2 location. Validate that all Q4-mapped metrics have baseline values.

3. **Generate metric fetcher** — Based on Q1, produce `value-tracker-fetcher.py` that pulls current business metric values for all Q4 mappings.

4. **Generate comparison engine** — Produce `value-comparator.py` that:
   - Computes delta: actual vs. baseline for each metric
   - Computes delta: actual vs. forecast from roi-brief.md
   - Classifies each feature as: over-performing | on-track | under-performing | insufficient-data
   - Calculates realised ROI % vs. forecasted ROI %

5. **Generate realisation report** — Produce `value-realization-report.md` with per-feature actual vs. forecast table, variance analysis, and plain-language explanation of variance drivers.

6. **Generate calibration output** — If Q6=yes, produce `value-modeler-calibration.yaml` containing the actual vs. forecast deltas and accuracy scores for ValueModeler to consume.

7. **Write feedback loop contribution**.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `value-tracker-config.yaml` | `operate/value-tracker/` | YAML | All configuration: metric mappings, window, cadence |
| `baseline-capture.py` | `operate/value-tracker/` | Python | Pre-deployment baseline capture script |
| `value-tracker-fetcher.py` | `operate/value-tracker/` | Python | Post-deployment metric fetcher |
| `value-comparator.py` | `operate/value-tracker/` | Python | Actual vs. forecast comparison engine |
| `value-realization-report.md` | `operate/value-tracker/` | Markdown | Actual vs. forecast ROI per requirement |
| `baseline-metrics.yaml` | `operate/value-tracker/` | YAML | Captured pre-deployment baseline values |
| `value-modeler-calibration.yaml` | `operate/value-tracker/` | YAML | Calibration data for ValueModeler (if Q6=yes) |

### Feedback Loop Contribution

```yaml
value_tracker:
  generated_at: "ISO-8601"
  summary: "ROI realisation: N features measured. X over-performing, Y under-performing."
  triggers:
    - feature_id: string
      metric: string
      forecasted_delta: float
      actual_delta: float
      variance_pct: float
      classification: over-performing | on-track | under-performing
      severity: info | warning | critical
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `value-realization-report.md` | POD Lead / Business Lead | Sprint accountability review |
| `value-modeler-calibration.yaml` | ValueModeler (next sprint planning) | Forecast model calibration |
| `feedback-loop-triggers.yaml` | Planning session | ROI actuals inform next sprint scope decisions |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `roi-brief.md` missing | Abort: `"roi-brief.md required. Run ValueModeler (Planning) first."` |
| Baseline metrics missing | Abort measurement; offer to generate baseline-capture.py instead |
| Business metrics API unreachable | Log warning; skip measurement cycle; retry on next cadence |
| Feature metric mapping incomplete | Warn for unmapped features; proceed with mapped ones; note gaps in report |
| Insufficient data (< 100 data points) | Mark feature as `insufficient-data`; do not classify as under-performing |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | All generation |
| Baseline not captured | Q_PRE = no | POD Lead | Must run baseline capture before deployment |
| Under-performing feature | Actual < 50% of forecast | POD Lead + Business Lead | Report distribution |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-06)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
