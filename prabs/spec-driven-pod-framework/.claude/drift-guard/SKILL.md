---
name: drift-guard
description: "DriftGuard is the production behaviour watchdog. It continuously samples live AI model outputs from production traffic and evaluates them against two independent baselines: the locked openspec.yaml behavioural specification and the EvalHarness golden-set established at sprint validation."
---

# SKILL.md — DriftGuard

```yaml
skill_id:      drift-guard
display_name:  DriftGuard
phase:         Operate
agent_ref:     O-02
version:       1.0.0
model:         claude-sonnet-4-20250514
token_budget:  ~50K
status:        core
```

---

## Skill Purpose

DriftGuard is the production behaviour watchdog. It continuously samples live AI model outputs from production traffic and evaluates them against two independent baselines: the locked `openspec.yaml` behavioural specification and the EvalHarness golden-set established at sprint validation. Any divergence — whether in semantic quality, output format compliance, latency degradation, or accuracy — is scored, classified by direction (regression vs. improvement), and surfaced to the POD Lead before users notice. When cumulative drift exceeds the configured threshold, DriftGuard automatically triggers a revalidation workflow. This closes the gap that allows model degradation to silently compound over multiple sprint cycles.

---

## Trigger Phrases

```
"run DriftGuard"
"check for model drift"
"detect output drift"
"compare production vs spec baseline"
"start drift monitoring"
"evaluate semantic drift"
"drift detection setup"
"validate production behaviour"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/openspec.yaml` | Phase 3 — Planning | Behavioural spec: acceptance criteria, output format contracts, quality rubrics per feature |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | Deployed model versions, endpoints, feature identifiers |
| `artifacts/traceability-report.md` | Phase 3 — TraceGraph | Requirement-to-feature mapping; used to identify which spec sections govern each feature |
| `specs/features.md` | Phase 2 — Knowledge | Feature acceptance criteria and expected output patterns |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| EvalHarness baseline location | Elicitation Q1 | Yes | Path to golden output set from sprint validation |
| Production traffic sampling rate | Elicitation Q2 | Yes | % of traffic to sample; default 5% |
| Drift threshold (per-feature score) | Elicitation Q3 | Yes | Score below which alert triggers |
| Drift check interval | Elicitation Q4 | Yes | Default: every 6 hours |
| Observability stack | Elicitation Q5 | Yes | For performance drift dimension |
| Revalidation notification target | Elicitation Q6 | Yes | Who/where to send revalidation trigger |

---

## Elicitation Protocol

### Q&A Sequence

```yaml
questions:
  - id: Q1
    required: true
    prompt: |
      DriftGuard requires a baseline of golden outputs produced by EvalHarness during
      sprint validation. Where is the EvalHarness baseline stored?
      Options:
        a) operate/drift-guard/eval-baseline/ (default; I will create this if absent)
        b) Provide a custom path
        c) No baseline exists yet — I will use openspec.yaml acceptance criteria only
    type: single_select
    options:
      - "a) Use default: operate/drift-guard/eval-baseline/"
      - "b) Custom path (enter below)"
      - "c) No baseline — use openspec.yaml only"
    depends_on: null

  - id: Q1b
    required: true
    prompt: "Enter the custom baseline path:"
    type: free_text
    validation: "Must be a valid relative file path"
    depends_on: "Q1 == 'b) Custom path (enter below)'"

  - id: Q2
    required: true
    prompt: |
      What percentage of live production traffic should DriftGuard sample for evaluation?
      Recommended: 5% for high-traffic, 20% for low-traffic features.
      Enter an integer between 1 and 100:
    type: numeric
    validation: "Integer between 1 and 100"
    default: "5"
    depends_on: null

  - id: Q3
    required: true
    prompt: |
      Set the drift alert threshold. DriftGuard scores outputs 0.0–1.0 against the baseline.
      A score BELOW this threshold triggers an alert.
      Recommended: 0.80 (strict), 0.70 (moderate), 0.60 (lenient).
      Enter a decimal between 0.50 and 0.99:
    type: numeric
    validation: "Float between 0.50 and 0.99"
    default: "0.80"
    depends_on: null

  - id: Q4
    required: true
    prompt: |
      How frequently should DriftGuard run a full evaluation batch?
      Select interval:
    type: single_select
    options:
      - Every 1 hour
      - Every 6 hours (recommended)
      - Every 12 hours
      - Every 24 hours
      - Continuous (stream sampling — high token cost)
    default: "Every 6 hours (recommended)"
    depends_on: null

  - id: Q5
    required: true
    prompt: |
      What observability stack provides production traffic/log access for sampling?
    type: single_select
    options:
      - Prometheus + Grafana
      - Datadog
      - OpenTelemetry
      - AWS CloudWatch
      - Azure Monitor
      - ELK Stack
      - Application logs (file-based)
      - Custom / API endpoint
    depends_on: null

  - id: Q6
    required: true
    prompt: |
      When drift exceeds the threshold, who/where should the revalidation trigger be sent?
    type: single_select
    options:
      - Slack (provide webhook URL)
      - Email (provide address)
      - GitHub Issue (provide repo + token)
      - Jira (provide project key + API token)
      - Write to operate/drift-guard/revalidation-trigger.yaml only
    depends_on: null

  - id: Q6b
    required: true
    prompt: "Provide the revalidation notification destination value:"
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q6 != 'Write to operate/drift-guard/revalidation-trigger.yaml only'"

  - id: Q7
    required: true
    prompt: |
      Which drift dimensions should be evaluated? Select all that apply:
    type: multi_select
    options:
      - Semantic quality (output meaning vs. spec acceptance criteria)
      - Output format compliance (structure, schema, required fields)
      - Response length drift (significant change in output verbosity)
      - Accuracy / factual correctness (where ground truth is available)
      - Latency drift (performance degradation over time — requires observability stack)
      - Tone / safety drift (for customer-facing AI outputs)
    depends_on: null
```

### Confirmation Gate

```
DriftGuard Configuration Summary
─────────────────────────────────────────────
Baseline source      : [Q1 resolved path]
Traffic sample rate  : [Q2]%
Drift threshold      : [Q3] (alert if score < [Q3])
Evaluation interval  : [Q4]
Observability stack  : [Q5]
Revalidation target  : [Q6] → [Q6b]
Drift dimensions     : [Q7 selections]
Spec baseline from   : artifacts/openspec.yaml
─────────────────────────────────────────────
Type CONFIRM to generate all DriftGuard artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

1. **Parse spec baseline** — Extract all `acceptance_criteria`, `output_format`, and `quality_rubric` blocks from `artifacts/openspec.yaml`. Build a structured evaluation rubric per feature. Also read `specs/features.md` for supplementary acceptance criteria.

2. **Load or create EvalHarness baseline** — If Q1 path exists, load golden outputs. If not, create the directory and generate a baseline manifest template at `operate/drift-guard/eval-baseline/baseline-manifest.yaml` for the POD Lead to populate with golden samples.

3. **Configure sampling** — Based on Q5, generate the appropriate log/traffic sampler:
   - For Prometheus/OTel: generate a sampling sidecar config
   - For Datadog/CloudWatch: generate a log forwarder config
   - For file-based logs: generate a tail-and-sample script

4. **Generate scoring engine** — Produce `drift-scorer.py` — a Python script that:
   - Reads sampled production outputs
   - Scores each output against the rubric using the Claude Sonnet API (embedded prompt within the script)
   - Aggregates scores per feature per evaluation window
   - Identifies drift direction (regression vs. improvement) and severity

5. **Generate drift tracking config** — Produce `drift-config.yaml` with all elicited parameters and per-feature threshold overrides if present in openspec.yaml.

6. **Generate revalidation trigger** — When drift threshold is breached, write `operate/drift-guard/revalidation-trigger.yaml` and send notification per Q6 configuration.

7. **Write drift report** — After each evaluation batch, append to `operate/drift-guard/drift-report.md` with feature scores, trend direction, and breach flags.

8. **Contribute to feedback loop** — Append drift summary to `operate/feedback-loop-triggers.yaml`.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `drift-config.yaml` | `operate/drift-guard/` | YAML | All drift configuration: thresholds, intervals, dimensions, routing |
| `drift-scorer.py` | `operate/drift-guard/` | Python | Sampling, scoring, and reporting agent |
| `sampling-config.yaml` | `operate/drift-guard/` | YAML | Observability stack sampler configuration |
| `drift-report.md` | `operate/drift-guard/` | Markdown | Per-feature drift score history with direction and severity |
| `revalidation-trigger.yaml` | `operate/drift-guard/` | YAML | Written when drift threshold is exceeded; triggers revalidation workflow |
| `eval-baseline/baseline-manifest.yaml` | `operate/drift-guard/` | YAML | Golden output manifest for EvalHarness baseline management |
| `drift-dashboard.json` | `operate/drift-guard/` | JSON | Grafana/generic dashboard showing drift score trends per feature |

### Feedback Loop Contribution

```yaml
drift_guard:
  generated_at: "ISO-8601"
  summary: "Drift evaluation across N features. X features below threshold."
  triggers:
    - feature_id: string
      dimension: semantic | format | latency | accuracy | tone
      drift_score: float          # 0.0–1.0
      baseline_score: float
      delta: float
      direction: regression | improvement
      severity: info | warning | critical
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `drift-report.md` | RunbookSynth | Enriches runbooks with known drift patterns |
| `revalidation-trigger.yaml` | POD Lead (manual gate) | Triggers re-run of EvalHarness from Build/Test phase |
| `feedback-loop-triggers.yaml` | Next sprint planning | Drift evidence informs spec revision backlog |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `openspec.yaml` missing | Abort with message: `"openspec.yaml required"` |
| EvalHarness baseline empty | Warn: create baseline-manifest.yaml template; operate in spec-only mode |
| Sampling rate returns 0 outputs | Log warning; skip evaluation cycle; alert POD Lead if 3 consecutive empty cycles |
| Claude API unavailable for scoring | Fall back to regex/rule-based scoring; flag as `scored_by: fallback` in report |
| Drift score unavailable for a feature | Skip feature in batch; log as `insufficient_samples`; reduce interval temporarily |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | All generation |
| Revalidation trigger | Any feature drift score < threshold | POD Lead | Revalidation workflow execution |
| Critical drift | Score < 0.60 on customer-facing feature | POD Lead | Feature may require immediate rollback via RolloutAdvisor |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-02)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
