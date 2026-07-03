---
name: experiment-ops
description: "> ⬡ PROPOSED STATUS — Experiment design and guardrail thresholds require stakeholder alignment. > Statistical significance requirements must be defined BEFORE production experiments run."
---

# SKILL.md — ExperimentOps

```yaml
skill_id:      experiment-ops
display_name:  ExperimentOps
phase:         Operate
agent_ref:     O-07
version:       1.0.0
model:         claude-sonnet-4-20250514
token_budget:  ~35K
status:        proposed
```

> ⬡ **PROPOSED STATUS** — Experiment design and guardrail thresholds require stakeholder alignment.
> Statistical significance requirements must be defined BEFORE production experiments run.
> POD Lead sign-off is mandatory before any experiment goes live.

---

## Skill Purpose

ExperimentOps enables a 1 POD Lead + 2 builder team to run statistically rigorous A/B and multi-armed experiments in production without a dedicated data science team or experimentation infrastructure. It generates a complete experiment configuration — traffic routing rules, variant definitions, guardrail metric monitors, statistical significance calculators, and auto-stop logic — from the POD Lead's hypothesis and parameters. The critical safety guarantee is the guardrail system: if any experiment variant causes a monitored metric to degrade beyond the defined guardrail threshold, ExperimentOps automatically stops the experiment and routes all traffic back to the control variant, preventing an experiment from becoming an incident.

---

## Trigger Phrases

```
"run ExperimentOps"
"set up A/B test"
"create experiment"
"configure production experiment"
"run multi-armed bandit"
"design feature experiment"
"set up traffic split"
"experiment configuration"
"start production A/B"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/openspec.yaml` | Phase 3 — Planning | Feature definitions — identifies which features are candidates for experimentation |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | Deployed variants, service endpoints, routing layer details |
| `operate/runtime-iq/thresholds.yaml` | Operate — RuntimeIQ | Existing SLA thresholds — used as guardrail defaults |
| `operate/value-tracker/value-tracker-config.yaml` | Operate — ValueTracker | Business metric mappings — used to select primary experiment metric |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| Experiment hypothesis | Elicitation Q1 | Yes | What is being tested and expected outcome |
| Variants definition | Elicitation Q2 | Yes | Control + 1–3 treatment variants |
| Traffic allocation | Elicitation Q3 | Yes | % split across variants |
| Primary metric | Elicitation Q4 | Yes | The one metric this experiment is designed to move |
| Guardrail metrics | Elicitation Q5 | Yes | Metrics that must NOT degrade for any variant |
| Statistical significance threshold | Elicitation Q6 | Yes | Default: 95% confidence |
| Minimum runtime | Elicitation Q7 | Yes | Minimum days before results are evaluated |
| Maximum runtime | Elicitation Q8 | Yes | Auto-stop if no significance by this date |

---

## Elicitation Protocol

> ExperimentOps will warn if expected minimum runtime exceeds the current sprint cycle.
> POD Lead must acknowledge this before proceeding.

### Q&A Sequence

```yaml
questions:
  - id: Q1
    required: true
    prompt: |
      State the experiment hypothesis in this format:
      "We believe that [CHANGE] will cause [PRIMARY METRIC] to [DIRECTION] by [EXPECTED MAGNITUDE]
       for [USER SEGMENT] because [RATIONALE]."
      Enter hypothesis:
    type: free_text
    validation: "Minimum 30 characters"
    depends_on: null

  - id: Q2
    required: true
    prompt: |
      Define the experiment variants. You need at least a control and one treatment.
      Format: variant_id=description, one per line. Example:
        control=Current summarisation prompt (baseline)
        treatment_a=Concise prompt variant (≤150 words output)
        treatment_b=Structured prompt variant (bullet-point output)
      Enter variants (maximum 4 including control):
    type: free_text
    validation: "Must include a 'control' variant. Maximum 4 lines."
    depends_on: null

  - id: Q3
    required: true
    prompt: |
      Define traffic allocation across variants. Must sum to 100%.
      Format: variant_id=pct, one per line. Example:
        control=50
        treatment_a=25
        treatment_b=25
      Enter allocation:
    type: free_text
    validation: "Values must sum to 100. Each value must be a positive integer."
    depends_on: null

  - id: Q4
    required: true
    prompt: |
      What is the PRIMARY metric this experiment is designed to improve?
      This is the metric whose change determines the winning variant.
      Examples: average_handle_time_seconds, conversion_rate_pct, user_satisfaction_score
      Enter metric name:
    type: free_text
    validation: "Non-empty string, no spaces (use underscores)"
    depends_on: null

  - id: Q4b
    required: true
    prompt: |
      What is the expected direction and minimum detectable effect for [Q4 metric]?
      Format: direction,minimum_effect_size (e.g. decrease,0.10 means 10% decrease expected)
      Direction options: increase | decrease
    type: free_text
    validation: "Format: increase|decrease,float (0.01–0.99)"
    depends_on: null

  - id: Q5
    required: true
    prompt: |
      Define GUARDRAIL metrics — metrics that must NOT degrade for any variant.
      If any guardrail is breached, the experiment auto-stops immediately.
      Format: metric_name=max_degradation_pct, one per line. Example:
        error_rate_5xx_pct=10
        latency_p99_ms=20
        user_satisfaction_score=5
      (Values are maximum allowed degradation %; auto-stops if exceeded)
      Press ENTER twice when done:
    type: free_text
    validation: "Each line: string=positive_integer"
    depends_on: null

  - id: Q6
    required: true
    prompt: |
      What statistical significance level is required to declare a winner?
      (Standard: 95%, Conservative: 99%, Lenient: 90%):
    type: single_select
    options:
      - 95% confidence (recommended)
      - 99% confidence (conservative)
      - 90% confidence (lenient — lower traffic requirements)
    default: "95% confidence (recommended)"
    depends_on: null

  - id: Q7
    required: true
    prompt: |
      What is the MINIMUM runtime in days before results are evaluated?
      (Prevents peeking bias. Recommended: 7 days minimum for most features):
    type: numeric
    validation: "Integer between 3 and 90"
    default: "7"
    depends_on: null

  - id: Q8
    required: true
    prompt: |
      What is the MAXIMUM runtime in days? (Experiment auto-stops after this date
      regardless of significance — prevents runaway experiments):
    type: numeric
    validation: "Integer greater than Q7 value, maximum 90"
    default: "30"
    depends_on: null

  - id: Q9
    required: true
    prompt: |
      How should ExperimentOps route traffic to variants?
    type: single_select
    options:
      - HTTP header-based routing (X-Experiment-Variant header)
      - User ID hash-based routing (consistent assignment per user)
      - Random per-request routing (no sticky sessions)
      - Feature flag system (describe your flag system below)
      - A/B routing at API gateway level
    depends_on: null

  - id: Q10
    required: true
    prompt: |
      Should the winning variant be automatically promoted to 100% traffic after
      statistical significance is reached and POD Lead approves?
      (yes / no — if yes, a HITL confirmation step is added before promotion):
    type: single_select
    options: [yes, no]
    depends_on: null
```

### Confirmation Gate

```
ExperimentOps Configuration Summary
─────────────────────────────────────────────
Hypothesis          : [Q1]
Variants            : [Q2 parsed — list]
Traffic allocation  : [Q3 parsed — list]
Primary metric      : [Q4] ([Q4b direction] by [Q4b effect])
Guardrail metrics   : [Q5 parsed — list with thresholds]
Significance level  : [Q6]
Runtime window      : [Q7] – [Q8] days
Routing method      : [Q9]
Auto-promotion      : [Q10]
─────────────────────────────────────────────
⚠️  STAKEHOLDER ALIGNMENT REQUIRED before running this experiment in production.
Confirm that guardrail thresholds and significance requirements are approved.

Type CONFIRM to generate experiment artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

1. **Parse deploy manifest** — Identify which services handle the feature under experiment. Determine where traffic routing can be injected (API gateway, service mesh, application layer).

2. **Generate experiment manifest** — Produce `experiment-[id]-manifest.yaml` with all experiment parameters: hypothesis, variants, allocation, metrics, guardrails, runtime bounds, significance level.

3. **Generate traffic router** — Based on Q9, generate the routing configuration:
   - Header-based: Nginx/Traefik routing rules
   - User ID hash: `traffic-router.py` with consistent hashing
   - API gateway: provider-specific routing rule (AWS API Gateway, Kong, etc.)
   - Feature flag: generic flag config and SDK snippet

4. **Generate guardrail monitor** — Produce `guardrail-monitor.py` that:
   - Polls each Q5 guardrail metric on a 60-second cycle
   - Calculates degradation % vs. control variant
   - Auto-stops experiment (sets all traffic to control) if any guardrail is breached
   - Alerts POD Lead immediately on auto-stop

5. **Generate significance calculator** — Produce `significance-calculator.py` that:
   - Runs daily after Q7 minimum runtime
   - Calculates statistical significance using two-proportion z-test or t-test based on metric type
   - Produces significance summary and winner recommendation when significance is reached

6. **Generate experiment dashboard** — Produce `experiment-dashboard.json` showing:
   - Real-time variant performance on primary metric
   - Guardrail metric status (green/red per variant)
   - Significance progress bar
   - Sample size and power calculations

7. **Generate auto-stop logic** — Produce `auto-stop.sh` that enforces maximum runtime: sets all traffic back to control at Q8 days regardless of results.

8. **Generate results reporter** — Produce `experiment-results-report.md` template that populates automatically when significance is reached or experiment ends.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `experiment-[id]-manifest.yaml` | `operate/experiment-ops/` | YAML | Complete experiment definition |
| `traffic-router.py` OR routing config | `operate/experiment-ops/` | Python / YAML | Variant traffic routing |
| `guardrail-monitor.py` | `operate/experiment-ops/` | Python | Continuous guardrail enforcement agent |
| `significance-calculator.py` | `operate/experiment-ops/` | Python | Statistical significance evaluator |
| `auto-stop.sh` | `operate/experiment-ops/` | Shell | Maximum runtime enforcement |
| `experiment-dashboard.json` | `operate/experiment-ops/` | JSON | Real-time experiment dashboard |
| `experiment-results-report.md` | `operate/experiment-ops/` | Markdown | Results: variant performance, significance, winner recommendation |

### Feedback Loop Contribution

```yaml
experiment_ops:
  generated_at: "ISO-8601"
  summary: "Experiment [id] status: [running|complete|auto-stopped]. Winner: [variant_id|none]."
  triggers:
    - experiment_id: string
      status: running | complete | auto-stopped | guardrail-breached
      primary_metric_delta: float | null
      winning_variant: string | null
      significance_reached: boolean
      recommendation: string
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `experiment-results-report.md` | ValueTracker | Experiment outcomes feed into value realisation |
| `experiment-results-report.md` | POD Lead | Winning variant becomes next sprint scope candidate |
| `feedback-loop-triggers.yaml` | Planning session | Experiment results inform feature promotion decisions |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `deploy-manifest.yaml` missing | Abort: routing config cannot be generated without deployment context |
| Traffic allocation does not sum to 100 | Reject at validation; re-prompt Q3 |
| Guardrail breach detected | Auto-stop immediately; alert POD Lead; write incident entry to IncidentLens |
| Experiment runtime exceeded without significance | Auto-stop; generate inconclusive results report; recommend larger sample size for re-run |
| Control variant performing significantly worse | Flag as anomaly; alert POD Lead; do NOT auto-promote any variant |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | All generation |
| Experiment go-live | Before any traffic routing activates | POD Lead + Stakeholder | Experiment activation |
| Winner promotion | Significance reached and winner identified | POD Lead | Traffic shift to 100% |
| Guardrail breach | Any guardrail metric degraded | POD Lead | Experiment auto-stopped; human reviews before any restart |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-07)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
