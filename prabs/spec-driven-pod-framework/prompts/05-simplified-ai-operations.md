# Simplified AI Operations

> **Execution Gate:** Before executing any prompt in this file, read `skillflow_skip.md`.
> If the skill name for that prompt appears in `skillflow_skip.md`, skip it and log: `Skipped: <skill-name>`

---

## Output Policy — STRICT

The only content you may present inline in the chat is:

1. **Pre-generation summary** — 3–5 bullet points presented before the NEXT gate.
2. **Post-generation report** — A concise list of what was created or updated, presented after artifact generation.
3. **Phase completion summary** — At the end of each multi-phase skill, a maximum of 8 bullet points summarizing what was done across all phases. Nothing more.
4. **Blocker notice** — If a required input file is missing or a DESIGN BLOCKER is unresolved, state what is needed and stop.
5. **Confirmation** - After generation, wait for CONFIRM before proceeding to the next prompt.

Do NOT display any other content inline — no section content, no checklists, no intermediate findings, no context summaries, no per-step or per-domain output. All reading, analysis, and assessment runs internally before the pre-generation summary.

---

Execute the prompts in this file sequentially, in the order they appear.

For each prompt:

Execute the prompt exactly as written.

Wait for the user to reply NEXT before generating artifacts.

After generation, wait for CONFIRM before proceeding to the next prompt.

Do not skip, reorder, merge, or modify prompts.

After the final prompt has been executed, display:

Simplified AI Operations Complete

---

## Prompt 1

Run the `control-plane` skill.

### Inputs
- Skill definition: `.claude/control-plane/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
  - `artifacts/roi-brief.md`
  - `specs/design.md`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Conduct the required elicitation sequence to collect missing runtime configuration.
- Present the collected values in a confirmation summary.
- Wait for explicit confirmation before generating artifacts.
- Do not assume values that require user approval.

### Required Elicitation
Collect only the following:

1. Currency for cost tracking.
2. Monthly cost ceilings per deployed agent/service.
3. Warning alert threshold percentage.
4. Billing or cost data source.
5. Security anomaly detection sensitivity.
6. Alert notification channel.

### Confirmation Gate
Present a concise configuration summary including:
- Currency
- Governed agents/services
- Cost ceilings
- Warning threshold
- Billing source
- Security sensitivity
- Alert channel

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <question>` → update the specified value and re-display the summary.

### Outputs
After confirmation, generate:

- `operate/control-plane/cost-config.yaml`
- `operate/control-plane/control-plane-monitor.py`
- `operate/control-plane/cost-gate.py`
- `operate/control-plane/cost-limit-networkpolicy.yaml` (if applicable)
- `operate/control-plane/security-monitor.py`
- `operate/control-plane/cost-dashboard.json`
- `operate/control-plane/cost-event-log.md`
- `operate/control-plane/security-event-log.md`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 2

Run the `runtime-iq` skill.

### Inputs
- Skill definition: `.claude/runtime-iq/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
  - `specs/design.md`
  - `operate/control-plane/cost-config.yaml`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Conduct the required elicitation sequence to collect missing runtime configuration.
- Parse NFR targets from `artifacts/openspec.yaml` after confirmation.
- Generate only the artifacts applicable to the selected observability stack and deployment target.
- Do not assume values that require user approval.

### Required Elicitation
Collect only the following:

1. Observability stack in use.
2. Metrics endpoint or connection string.
3. Alert notification channel.
4. Monitoring polling interval.
5. Auto-scaling bounds.
6. SLA dimensions to monitor.

If `artifacts/deploy-manifest.yaml` is unavailable, collect deployment target details before continuing.

### Confirmation Gate
Present a concise configuration summary including:
- Deployment target
- Observability stack
- Metrics endpoint
- Alert channel
- Polling interval
- Auto-scaling bounds
- SLA dimensions
- Confirmation that NFR targets will be derived from `artifacts/openspec.yaml`

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <question>` → update the specified value and re-display the summary.

### Outputs
After confirmation, generate the applicable artifacts under `operate/runtime-iq/`:

- `sla-dashboard.json`
- Stack-specific monitoring configuration:
  - `prometheus-rules.yaml`, or
  - `datadog-monitors.json`, or
  - `cloudwatch-alarms.json`, or
  - `otel-collector-config.yaml`, or
  - `polling-script.py`
- `hpa.yaml` or `autoscaling-policy.json`
- `alert-config.yaml`
- `runtime-iq-monitor.py`
- `thresholds.yaml`
- `sla-breach-log.md`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 3

Run the `drift-guard` skill.

### Inputs
- Skill definition: `.claude/drift-guard/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
  - `artifacts/traceability-report.md`
  - `specs/features.md`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Conduct the required elicitation sequence to collect missing drift monitoring configuration.
- Parse the behavioural baseline from `artifacts/openspec.yaml` after confirmation.
- Load the EvalHarness baseline if available, or generate the required baseline template when absent.
- Generate only the artifacts applicable to the selected observability stack and notification method.
- Do not assume values that require user approval.

### Required Elicitation
Collect only the following:

1. EvalHarness baseline location.
2. Production traffic sampling rate.
3. Drift alert threshold.
4. Drift evaluation interval.
5. Observability stack.
6. Revalidation notification target.
7. Drift dimensions to monitor.

### Confirmation Gate
Present a concise configuration summary including:
- Baseline source
- Traffic sampling rate
- Drift threshold
- Evaluation interval
- Observability stack
- Revalidation target
- Drift dimensions
- Confirmation that the spec baseline will be derived from `artifacts/openspec.yaml`

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <question>` → update the specified value and re-display the summary.

### Outputs
After confirmation, generate the applicable artifacts under `operate/drift-guard/`:

- `drift-config.yaml`
- `drift-scorer.py`
- `sampling-config.yaml`
- `drift-report.md`
- `revalidation-trigger.yaml`
- `eval-baseline/baseline-manifest.yaml` (if baseline does not already exist)
- `drift-dashboard.json`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 4

Run the `incident-lens` skill.

### Inputs
- Skill definition: `.claude/incident-lens/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
  - `operate/runtime-iq/sla-breach-log.md`
  - `operate/runtime-iq/thresholds.yaml`
  - `operate/control-plane/security-event-log.md`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Ask the mode selection question first and do not assume the operating mode.
- Follow only the elicitation path applicable to the selected mode.
- Cross-reference RuntimeIQ and ControlPlane artifacts where available.
- Classify incidents and root causes strictly from available evidence.
- Do not invent incident history, recurrence patterns, or remediation details.

### Required Elicitation

**Q0 — Mode Selection**
Choose one:
- **Mode A:** Log and analyse a new incident
- **Mode B:** Analyse patterns in existing incident history

#### If Mode A:
Collect only:
1. Incident timestamp
2. Affected services/features
3. Observable symptom
4. Error type/category
5. Resolution steps taken
6. Known root cause (or `unknown`)
7. Resolution status

#### If Mode B:
Collect only:
1. Lookback window (sprints)
2. Pattern/systemic classification thresholds
3. Backlog item output format

### Confirmation Gate

#### Mode A
Present a concise summary including:
- Timestamp
- Affected services
- Symptom
- Error type
- Resolution steps
- Root cause
- Status

Wait for:
- `CONFIRM` → proceed.
- `EDIT <question>` → revise and re-display.

#### Mode B
Present a concise summary including:
- Lookback window
- Pattern threshold
- Systemic threshold
- Backlog format

Wait for:
- `CONFIRM` → proceed.
- `EDIT <question>` → revise and re-display.

### Outputs
After confirmation, generate only the applicable artifacts under `operate/incident-lens/`:

- `incident-log.md`
- `incident-pattern-report.md`
- `backlog-items.md`
- `backlog-items.yaml`
- `runbook-enrichments.yaml`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 5

Run the `runbook-synth` skill.

### Inputs
- Skill definition: `.claude/runbook-synth/SKILL.md`
- Authoritative inputs:
  - `artifacts/deploy-manifest.yaml`
  - `artifacts/openspec.yaml`
  - `specs/design.md`
  - `specs/api.md`
  - `artifacts/decision-ledger.md`
  - `operate/incident-lens/incident-log.md`
  - `operate/drift-guard/drift-report.md`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Conduct the required elicitation sequence before generating any runbooks.
- Generate only the sections explicitly selected by the user.
- Tailor the level of detail to the chosen audience.
- Incorporate incident-derived fixes and drift insights only when the corresponding artifacts exist.
- Do not assume rollback requirements, update triggers, or output preferences.

### Required Elicitation
Collect only the following:

1. Target audience level.
2. Runbook sections to generate.
3. Auto-update triggers.
4. Output format.
5. Whether a rollback runbook is required.
6. Deployment version identifier.

### Confirmation Gate
Present a concise configuration summary including:
- Target audience
- Selected sections
- Auto-update triggers
- Output format
- Rollback runbook requirement
- Version identifier
- Source artifacts that will be used

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <question>` → revise and re-display the summary.

### Outputs
After confirmation, generate the applicable artifacts under `operate/runbook-synth/`:

- `runbook-[feature-id]-[version].md`
- `runbook-rollback-[version].md` (if requested)
- `runbook-index.md`
- `runbook-update-trigger.sh`
- `runbook-config.yaml`
- `history/runbook-[feature]-[previous-version].md` (if prior versions exist)

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 6

Run the `value-tracker` skill.

### Inputs
- Skill definition: `.claude/value-tracker/SKILL.md`
- Authoritative inputs:
  - `artifacts/roi-brief.md`
  - `artifacts/openspec.yaml`
  - `artifacts/sprint-scope-ranked.md`
  - `artifacts/deploy-manifest.yaml`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- First determine whether pre-deployment baseline metrics were captured.
- Do not assume that a baseline exists.
- If no baseline exists:
  - Generate baseline setup artifacts only.
  - Stop after baseline setup generation.
- If a baseline exists:
  - Conduct the required elicitation sequence before generating measurement artifacts.
  - Parse ROI forecasts from `artifacts/roi-brief.md`.
  - Compare actual performance against forecasted outcomes.
  - Generate calibration outputs only if explicitly enabled.

### Baseline Decision Logic

- Check whether pre-deployment baseline metrics were captured.

If baseline metrics do **not** exist:
- Generate:
  - `operate/value-tracker/baseline-capture.py`
  - `operate/value-tracker/baseline-capture-guide.md`
- Explain that ValueTracker cannot perform actual vs. forecast analysis until baseline data has been collected.
- Stop execution after baseline setup artifacts are produced.

If baseline metrics **do** exist:
- Proceed with elicitation and active measurement mode.

### Required Elicitation (only if baseline exists)

Collect only the following:

1. Business metrics source.
2. Baseline metrics location.
3. Measurement window.
4. Feature-to-KPI mappings.
5. Reporting cadence.
6. Whether actuals should automatically feed back to ValueModeler.

### Confirmation Gate

Present a concise configuration summary including:
- Baseline availability
- Metrics source
- Baseline location
- Measurement window
- Feature-to-KPI mappings
- Reporting cadence
- Calibration feedback setting
- ROI forecast source

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <question>` → revise and re-display the summary.

### Outputs

If baseline is unavailable:
- `operate/value-tracker/baseline-capture.py`
- `operate/value-tracker/baseline-capture-guide.md`

If baseline exists, generate the applicable artifacts under `operate/value-tracker/`:

- `value-tracker-config.yaml`
- `value-tracker-fetcher.py`
- `value-comparator.py`
- `value-realization-report.md`
- `baseline-metrics.yaml`
- `value-modeler-calibration.yaml` (if enabled)

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin baseline verification and continue, or provide corrections, clarifications, or missing information before generation proceeds.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 7

Run the `experiment-ops` skill.

### Inputs
- Skill definition: `.claude/experiment-ops/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
  - `operate/runtime-iq/thresholds.yaml`
  - `operate/value-tracker/value-tracker-config.yaml`
- Use the skill specification exactly as defined. :contentReference[oaicite:0]{index=0}

### Execution
- Parse deployment and runtime context to identify experiment candidates and available routing mechanisms.
- Use RuntimeIQ thresholds as default guardrail references where applicable.
- Use ValueTracker metric mappings to help validate experiment metrics.
- Do not assume experiment details that have not been explicitly confirmed.

### Required Elicitation

Collect only the following:

1. Experiment hypothesis.
2. Variant definitions (control + treatments).
3. Traffic allocation.
4. Primary metric and expected effect.
5. Guardrail metrics with degradation thresholds.
6. Statistical significance level.
7. Minimum and maximum runtime.
8. Traffic routing method.
9. Whether the winning variant should be auto-promoted.

### Confirmation Gate

Present a concise configuration summary including:
- Hypothesis
- Variants
- Traffic allocation
- Primary metric and expected effect
- Guardrail metrics and thresholds
- Significance level
- Runtime window
- Routing method
- Auto-promotion setting

Include the stakeholder acknowledgement reminder:

> Stakeholder alignment is required before this experiment can run in production. Confirm that guardrail thresholds and significance requirements have been approved.

Wait for:

- `CONFIRM` → proceed with generation.
- `EDIT <Q-number>` → revise and re-display the summary.

### Outputs

Generate the following artifacts under `operate/experiment-ops/`:

- `experiment-[id]-manifest.yaml`
- Appropriate routing artifact (`traffic-router.py` or routing configuration)
- `guardrail-monitor.py`
- `significance-calculator.py`
- `auto-stop.sh`
- `experiment-dashboard.json`
- `experiment-results-report.md`

### Processing Requirements

- Validate that traffic allocation totals 100%; if not, re-prompt for correction.
- Select routing implementation based on the chosen routing method.
- Generate guardrail monitoring that automatically routes traffic back to control when thresholds are breached.
- Implement significance evaluation only after the minimum runtime has elapsed.
- Enforce automatic experiment termination at the maximum runtime.
- Never auto-promote a winner without explicit POD Lead approval, even if auto-promotion is enabled.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to begin the elicitation sequence, or provide corrections, clarifications, or missing information before generation proceeds.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 8

Run the `tool-surface-auditor` skill.

### Inputs
- Skill definition: `.claude/tool-surface-auditor/SKILL.md`
- Authoritative inputs:
  - `input/enabled-tools.json`
  - `input/usage-telemetry.json`
  - `input/audit-config.json`

### Execution
- Load the complete MCP server and tool inventory.
- Use telemetry from the 30-day window to calculate usage characteristics for every tool.
- Apply classification and recommendation rules exactly as defined.
- Treat all disable actions as recommendations requiring human review.

### Processing Requirements

#### Tool Inventory
- Record for each tool:
  - `server`
  - `name`
  - `description_tokens`
  - `param_schema_tokens`
  - `total_tokens`
- Compute:
  - Per-server token totals
  - Grand total token footprint
- Flag if ceilings from `audit-config.json` are exceeded:
  - MCP servers > configured ceiling
  - Total tools > configured ceiling

#### Telemetry Processing
For each tool extract:
- `calls_30d`
- `calls_7d`
- `last_called`
- `error_rate`
- `avg_latency_ms`

Calculate `recency_score`:
- Within 7 days → `1.0`
- Within 30 days → `0.5`
- Older than 30 days → `0.1`
- Never called → `0.0`

#### Usage Scoring

Calculate:

```text
usage_score =
    (calls_per_session × 0.5)
  + (recency_score × 0.3)
  + ((1 - error_rate) × 0.2)
```

Where:

```text
calls_per_session =
calls_30d ÷ maximum calls_30d observed
```

Requirements:
- Normalise to the range [0,1].
- Round usage scores to 4 decimal places.

#### Classification Rules

Apply exactly:

| Classification | Condition | Recommendation |
|---|---|---|
| active | score > 0.4 | KEEP |
| occasional | 0.1–0.4 inclusive | KEEP_MONITOR |
| dormant | 0.0–0.1 exclusive and calls > 0 | FLAG_FOR_REVIEW |
| never-used | calls_30d = 0 and last_called = null | RECOMMEND_DISABLE |

#### Safety Rule

Never auto-disable a tool when both conditions are true:

- `calls_30d == 0`
- `error_rate == 0.0`

Instead classify as:

```text
REVIEW_REQUIRED
reason: "zero-call-zero-error: possible emergency tool"
```

#### Server-Level Analysis

Generate recommendations:

- If all tools in a server are never-used → recommend disabling the server.
- If ≥80% of tools are never-used or dormant → recommend partial disable.
- Flag overlapping servers for consolidation review using heuristic tool-name similarity.

### Outputs

Generate:

- `tool-audit-report.json`
- `disabled-mcps-config.md`
- `token-impact-report.json`

### Output Requirements

#### tool-audit-report.json
Include:
- Tools sorted by descending `usage_score`
- Aggregate summary counts
- Per-server summaries
- Scores
- Classifications
- Recommendations
- Review reasons where applicable

#### disabled-mcps-config.md
Provide both formats:

Environment variables:

```text
ECC_DISABLED_MCPS=...
ECC_DISABLED_TOOLS=...
```

JSON config:

```json
{
  "disabled_servers": [],
  "disabled_tools": []
}
```

Requirements:
- Human-review recommendations must remain commented.
- Prefix review-only entries with:

```text
# REVIEW:
```

#### token-impact-report.json

Calculate:

```text
total_tool_tokens_before
tokens_from_disabled
total_tool_tokens_after
savings
window_recovered_percentage
cost_per_session_saved
monthly_savings_at_1k_sessions_per_day
```

Where:

```text
window_recovered_percentage =
(savings / 200000) × 100
```

and cost calculations use:

```text
standing_context_per_token_cost
```

from `audit-config.json`.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 9

Run the `prompt-slimmer` skill.

### Inputs
- Skill definition: `.claude/prompt-slimmer/SKILL.md`
- Authoritative inputs:
  - `input/system-prompt.md`
  - `input/prompt-usage-log.json`
  - `input/slimmer-config.json`

### Execution
- Audit the current standing instructions before making any modifications.
- Preserve the original prompt and maintain a complete audit trail.
- Never silently rewrite directives.
- Do not apply critical changes without explicit human approval.

### Five-Phase Process

#### Phase 1 — Audit
- Parse the system prompt into discrete directives.
- Group directives into clusters (tone, formatting, tool use, escalation, compliance, etc.).
- Identify:
  - Exact duplicates
  - Semantic duplicates
  - Superseded rules
  - Contradictions
- Build an audit manifest including:
  - Directive text
  - Cluster
  - Duplicate references
  - Initial criticality classification

#### Phase 2 — Merge
- Consolidate directives with identical intent.
- Keep the most specific version.
- Remove superseded directives and document the reason.
- Preserve protected phrases exactly as written.
- Surface contradictions as:

```text
NEEDS_HUMAN_RESOLUTION
```

- Do not resolve contradictions automatically.

#### Phase 3 — Compress
- Rewrite only `safe` and `review` directives using concise phrasing.
- Remove filler and redundant qualifiers.
- Convert verbose prose into structured instructions where appropriate.
- Never compress `critical` directives.
- Leave critical directives unchanged pending approval.

#### Phase 4 — Classify
Classify every proposed change as:

| Classification | Action |
|---|---|
| safe | Auto-apply |
| review | Stage for human review |
| critical | Preserve original wording and require approval |

Apply these rules:
- Protected phrases automatically become `critical`.
- Removing directives is never `safe`.
- New consolidated directives inherit the highest classification of their source directives.

For all critical changes:
- Include:
  - Original text
  - Proposed text
  - Opus semantic-preservation review status
- Mark them:

```text
PENDING_APPROVAL
```

- Do not apply them.

#### Phase 5 — Diff
Generate a complete audit trail showing:
- Original directive
- Slimmed directive
- Change classification
- Estimated token savings
- Approval status where applicable

### Outputs

Generate:

- `system-prompt-slimmed.md`
- `prompt-diff.md`
- `slimming-report.json`

### Output Requirements

#### system-prompt-slimmed.md
- Apply all `safe` changes.
- Stage `review` changes.
- Leave `critical` directives unchanged until approved.
- Preserve protected phrases verbatim.

#### prompt-diff.md
Include:
- Summary counts by classification.
- Estimated aggregate token savings.
- Side-by-side entries:

```text
ORIGINAL
SLIMMED
CHANGE_TYPE
TOKENS_SAVED
STATUS
```

Requirements:
- Contradictions remain unresolved.
- Critical items show:
  - Opus review verdict
  - `PENDING_APPROVAL`

#### slimming-report.json
Include:
- Audit manifest
- Duplicate analysis
- Superseded directives
- Contradiction inventory
- Classification counts
- Estimated token savings
- Approval status summary

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 10

Run the `budget-governer` skill.

### Inputs
- Skill definition: `.claude/budget-governor/SKILL.md`
- Authoritative inputs:
  - `input/task-graph.json`
  - `input/pricing-table.json`
  - `input/budget-caps.json`

### Execution
- Perform deterministic cost accounting only. Do not use assumptions beyond the provided inputs.
- Use the pricing table supplied in the inputs. If required pricing data is missing, pause and request clarification before continuing.
- Preserve precision to 6 decimal places for calculations and use display rounding only in reports.

### Processing Steps

#### Step 1 — Load Task Graph
For each task step, extract:
- `step_id`
- `model`
- `estimated_input_tokens`
- `estimated_output_tokens`
- `is_optional`
- `depends_on`
- `estimated_iterations` (default to 1 if absent)

For looping steps:

```text
effective_input_tokens  = estimated_input_tokens × max(1, estimated_iterations)
effective_output_tokens = estimated_output_tokens × max(1, estimated_iterations)
```

#### Step 2 — Compute Per-Step Cost
Using `pricing-table.json`, calculate:

```text
input_cost_usd  = (effective_input_tokens / 1,000,000) × input_price
output_cost_usd = (effective_output_tokens / 1,000,000) × output_price
step_total_usd  = input_cost_usd + output_cost_usd
```

Round calculations to 6 decimal places.

#### Step 3 — Roll Up Totals
Calculate:

- Mandatory projection:
  - Include only `is_optional = false`
- Worst-case projection:
  - Include all steps

Generate:

```text
task_total_usd
task_worst_usd
session_total_usd
sprint_total_usd
```

using any prior spend values available in the budget inputs.

#### Step 4 — Budget Comparison
Load limits from `budget-caps.json`.

Calculate utilization percentages:

```text
task_utilization_pct
session_utilization_pct
sprint_utilization_pct
```

Also calculate:

```text
headroom = cap_usd − projected_total_usd
```

for each level.

#### Step 5 — Gate Decision
Use the highest utilization across all caps.

Apply:

```text
≤ 80%     → proceed
80–100%   → warn
> 100%    → block
```

The most constrained cap determines the final gate decision.

#### Step 6 — Remediation (Only if Blocked)
If the gate result is `block`:

- Identify the top 3 highest-cost steps.
- Evaluate the next cheaper model tier:
  - Opus → Sonnet
  - Sonnet → Haiku
- Recalculate projected costs.
- Estimate savings from model downgrades.
- Evaluate loop reduction opportunities using planned versus projected iterations.
- Rank remediation suggestions by estimated savings.

#### Step 7 — Ledger Update
Generate the forecast and append a ledger entry containing:

```json
{
  "session_id": "<uuid>",
  "timestamp_utc": "<iso8601>",
  "task_id": "<task_id>",
  "gate_decision": "<proceed|warn|block>",
  "projected_cost_usd": null,
  "actual_cost_usd": null
}
```

Populate `projected_cost_usd` from the forecast. Leave `actual_cost_usd` as `null`.

### Outputs

Generate:

- `cost-forecast.json`
- `spend-ledger.json`

### Output Requirements

#### cost-forecast.json
Include:
- Per-step breakdown
- Effective token counts
- Input/output costs
- Mandatory and worst-case totals
- Task/session/sprint projections
- Utilization percentages
- Headroom calculations
- Final gate decision

If blocked, also include:
- Highest-cost steps
- Downgrade analysis
- Iteration reduction opportunities
- Ordered remediation suggestions

#### spend-ledger.json
Append a new immutable ledger entry containing:
- Session identifier
- Timestamp
- Task identifier
- Gate decision
- Projected cost
- Actual cost placeholder

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 11

Run the `semantic-cache` skill.

### Inputs
- Skill definition: `SemanticCache/SKILL.md`
- Authoritative inputs:
  - `input/inbound-requests.json`
  - `input/cache-store.json`
  - `input/cache-config.json`

### Execution
- Follow the cache workflow exactly as defined.
- Do not assume missing values. If required cache configuration is absent, pause and request clarification before continuing.
- Respect all safety rules, especially never caching PII or personal account data.

### Processing Steps

#### Step 1 — Normalize and Hash
For each inbound request:

Normalize the input:

```text
trim whitespace
convert to lowercase
collapse repeated whitespace to a single space
remove special characters except standard punctuation
```

Generate:

```text
content_hash = SHA-256(normalized_input)
```

Use the normalized hash as the primary lookup key.

#### Step 2 — Never-Cache Validation
Before any cache lookup:

- Load `never_cache_patterns` from `cache-config.json`.
- Skip cache processing if the request matches any configured pattern.
- Also bypass caching for:
  - Email addresses
  - Queries containing 10+ digit numbers
  - Personal account references
  - Order-specific requests
  - Balance or account status queries
  - Any detected PII

For bypassed requests:
- Mark the request as `cache_bypassed`.
- Pass through normally without seeding the cache.

#### Step 3 — Exact Cache Lookup
Using `content_hash`:

- Search `cache-store.json`.
- Verify the entry exists and has not expired.
- Update:
  - `hit_count`
  - `last_accessed`

If valid:

Return:

```json
{
  "status": "hit",
  "cache_type": "exact",
  "similarity": 1.0
}
```

Do not continue to semantic search.

#### Step 4 — Semantic Lookup
Only if:

- Exact lookup misses or has expired, and
- Semantic caching is enabled.

Generate embeddings using the configured embedding model.

Search for the nearest stored embedding.

Calculate cosine similarity.

#### Step 5 — Semantic Hit Decision
If:

```text
cosine_similarity ≥ similarity_threshold
```

and the candidate entry is still valid:

Return a semantic hit.

Include the mandatory warning:

```text
semantic_match_verify_appropriateness
```

Populate:

```json
{
  "cache_type": "semantic",
  "similarity": "<score>",
  "warning": "semantic_match_verify_appropriateness"
}
```

If the threshold is not met, continue to Step 6.

#### Step 6 — Miss and Cache Seeding
For cache misses:

- Pass the original request through for downstream processing.
- Seed a new cache entry containing:
  - Cache UUID
  - Content hash
  - Embedding vector
  - Original request
  - Result
  - Created timestamp
  - TTL
  - Hit count
  - Last accessed timestamp

Determine TTL using the configured policy.

Do not seed requests excluded by never-cache rules.

### Cache Rules

Apply TTL and invalidation policies from configuration.

Support:
- Exact invalidation by hash
- Tag invalidation
- Query invalidation
- Full cache flush

Respect cache segmentation by model version where configured.

### Outputs

Generate the following:

- Cache decision for every inbound request
- `hit_metadata`
- `session_metrics`

### Output Requirements

#### hit_metadata
For every request include:

```json
{
  "cache_type": "exact | semantic | miss | bypassed",
  "similarity": 0.0,
  "tokens_saved": 0,
  "latency_ms": 0,
  "served_from_cache": false,
  "warning": null
}
```

Populate:
- Exact hits with similarity `1.0`
- Semantic hits with the mandatory warning
- Misses with `tokens_saved = 0`
- Bypassed requests with the bypass reason

#### session_metrics
Aggregate and report:

- Total requests processed
- Exact hit count
- Semantic hit count
- Miss count
- Bypassed request count
- Overall hit rate
- Tokens avoided
- Estimated latency avoided
- New cache entries seeded

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 12

Run the `model-router` skill.

### Inputs
- Skill definition: `ModelRouter/SKILL.md`
- Authoritative inputs:
  - `input/task-graph.json`
  - `input/budget-signal.json`
  - `input/routing-config.json`

### Execution
- Route each task to the least expensive model capable of meeting its quality requirements.
- Apply budget overrides and escalation rules exactly as defined.
- Do not assume missing complexity values. If required routing information is unavailable, pause and request clarification before continuing.

### Processing Steps

#### Step 1 — Load Tasks
For each task in `task-graph.json`, extract:
- `task_id`
- Task description
- Complexity hints (if provided)
- Existing model assignment (if any)
- Task type
- Quality gate information

Load:
- Budget utilization and remediation guidance from `budget-signal.json`
- Routing thresholds and scoring rules from `routing-config.json`

#### Step 2 — Score the Six Dimensions
Assign scores from 1–10 for:

| Dimension | Weight |
|---|---:|
| reasoning_depth | 0.30 |
| ambiguity_level | 0.15 |
| domain_expertise | 0.20 |
| multi_step_planning | 0.15 |
| safety_criticality | 0.10 |
| output_precision | 0.10 |

Use provided hints when available. Otherwise derive scores from the task description and record reduced confidence.

Calculate:

```text
weighted_composite =
(reasoning_depth × 0.30)
+ (ambiguity_level × 0.15)
+ (domain_expertise × 0.20)
+ (multi_step_planning × 0.15)
+ (safety_criticality × 0.10)
+ (output_precision × 0.10)
```

#### Step 3 — Baseline Tier Assignment
Apply routing thresholds:

```text
1.0–3.4   → claude-haiku-4-5
3.5–6.4   → claude-sonnet-4-5
6.5–10.0  → claude-opus-4-5
```

Record:
- Assigned model
- Tier label
- Composite score
- Routing rationale

#### Step 4 — Confidence Validation
Generate a classification confidence score.

If:

```text
classification_confidence < 0.70
```

then:

- Escalate to at least Sonnet.
- Append:

```text
[escalated: low-confidence classification]
```

to the rationale.

#### Step 5 — Budget Overrides
Use `budget-signal.json` utilization values.

Apply:

```text
budget ≥ 90%
```

- Force Haiku where possible.
- Do not downgrade tasks with:

```text
safety_criticality ≥ 7
```

below Sonnet.

Apply:

```text
budget 80–89%
```

- Downgrade one tier when permitted.

Downgrade ladder:

```text
Opus → Sonnet → Haiku
```

Update the rationale whenever a budget override is applied.

#### Step 6 — Safety Anchor
Enforce:

```text
safety_criticality ≥ 7
```

must never result in a model assignment lower than:

```text
claude-sonnet-4-5
```

regardless of budget pressure.

#### Step 7 — Escalation Evaluation
Where quality gates fail or escalation triggers exist:

- Escalate one tier:
  - Haiku → Sonnet
  - Sonnet → Opus
- Limit to a maximum of two escalations per task.
- Record:
  - Original model
  - Escalated model
  - Trigger reason
  - Additional projected cost
  - Escalation path

### Outputs

Generate:

- `routing-decisions.json`
- `escalation-log.json`

### Output Requirements

#### routing-decisions.json
For each task include:

```json
{
  "task_id": "",
  "dimension_scores": {},
  "weighted_composite_score": 0.0,
  "classification_confidence": 0.0,
  "tier": "",
  "assigned_model": "",
  "routing_rationale": "",
  "budget_override_applied": false,
  "safety_anchor_applied": false
}
```

Also include summary metrics:
- Tasks routed to Haiku
- Tasks routed to Sonnet
- Tasks routed to Opus
- Budget overrides applied
- Safety-anchor protections triggered

#### escalation-log.json
Include entries only for escalated tasks:

```json
{
  "task_id": "",
  "original_model": "",
  "escalated_model": "",
  "trigger": "",
  "additional_cost_usd": 0,
  "escalation_path": []
}
```

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 13

Run the `regex-llm-router` skill.

### Inputs
- Skill definition: `RegexLLMRouter/SKILL.md`
- Authoritative inputs:
  - `input/parsing-tasks.json`
  - `input/regex-patterns.json`
  - `input/routing-config.json`

### Execution
- Evaluate each parsing task to determine whether it should use deterministic parsing, a hybrid approach, or a full LLM solution.
- Follow the scoring rubric exactly.
- Do not assume missing task characteristics. If required information is unavailable, pause and request clarification before continuing.

### Processing Steps

#### Step 1 — Load Parsing Tasks
For each task in `parsing-tasks.json`, extract:
- `task_id`
- Task description
- Input examples or sample payloads
- Expected output fields
- Existing parsing approach (if any)
- Daily processing volume

Load:
- Existing regex library from `regex-patterns.json`
- Scoring thresholds and configuration from `routing-config.json`

#### Step 2 — Score the Five Dimensions
Assign integer scores from 1–5 for:

| Dimension | Description |
|---|---|
| Schema Consistency | Stability of input structure |
| Delimiter Reliability | Predictability of separators or anchors |
| Ambiguity Level | Need for semantic understanding |
| Error Tolerance | Impact of incorrect extraction |
| Volume | Expected daily execution frequency |

Document the rationale for every score.

Calculate:

```text
total_score =
schema_consistency
+ delimiter_reliability
+ ambiguity_level
+ error_tolerance
+ volume
```

#### Step 3 — Determine Routing Strategy
Apply routing thresholds:

```text
20–25 → regex
13–19 → hybrid
0–12  → llm
```

Record:
- Total score
- Selected route
- Routing justification
- Estimated economic impact

#### Step 4 — Regex Generation
For tasks routed to `regex`:

Generate starter patterns that:

- Compile successfully using Python `re`
- Use named capture groups where multiple fields exist
- Use non-capturing groups where extraction is unnecessary
- Include normalization guidance when required

For each generated pattern include:

- Pattern
- Flags
- At least 3 positive test cases
- At least 2 negative test cases
- Known limitations

Update `regex-patterns.json` accordingly.

#### Step 5 — Hybrid Strategy Definition
For tasks routed to `hybrid`:

Define:

1. Regex-first execution.
2. Lightweight validation checks:
   - Length checks
   - Character class checks
   - Checksum or format validation where applicable.
3. LLM fallback conditions.
4. Fallthrough logging requirements.
5. Promotion and demotion rules:

```text
Fallthrough < 10% → consider promotion to regex
Fallthrough > 60% → consider demotion to llm
```

#### Step 6 — LLM Routing
For tasks routed to `llm`:

Document why deterministic parsing is unsuitable, including:
- Sources of ambiguity
- Context requirements
- Risks of brittle parsing

Recommend periodic reassessment triggers.

### Outputs

Generate:

- `routing-decisions.json`
- `regex-patterns.json`
- `hybrid-strategy.json`

### Output Requirements

#### routing-decisions.json
Include for each task:

```json
{
  "task_id": "",
  "dimension_scores": {
    "schema_consistency": 0,
    "delimiter_reliability": 0,
    "ambiguity_level": 0,
    "error_tolerance": 0,
    "volume": 0
  },
  "total_score": 0,
  "route": "regex|hybrid|llm",
  "justification": "",
  "economic_impact": ""
}
```

Include summary metrics:
- Total tasks evaluated
- Regex decisions
- Hybrid decisions
- LLM decisions
- Estimated LLM spend avoided

#### regex-patterns.json
For every regex-routed task include:

```json
{
  "task_id": "",
  "pattern": "",
  "flags": [],
  "positive_tests": [],
  "negative_tests": [],
  "known_limitations": [],
  "normalization_function": null
}
```

#### hybrid-strategy.json
For every hybrid task include:

```json
{
  "task_id": "",
  "regex_strategy": "",
  "validation_rules": [],
  "llm_fallback_conditions": [],
  "fallthrough_logging": "",
  "promotion_rule": "",
  "demotion_rule": ""
}
```

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 14

Run the `context-profiler` skill.

### Inputs
- Skill definition: `ContextProfiler/SKILL.md`
- Authoritative inputs:
  - `input/session-window.md`
  - `input/profiler-config.json`

### Execution
- Profile the active context window deterministically.
- Measure context usage only. Do not summarize, rewrite, compact, or modify any segment.
- Treat missing inputs as zero-token segments and document them accordingly.

### Processing Steps

#### Step 1 — Load Inputs
Read:
- Session context from `session-window.md`
- Configuration from `profiler-config.json`

Extract:
- Model context window size (default to `200000` if absent)
- Alert thresholds
- Segment definitions

If the model window size is defaulted, add a note indicating this assumption.

#### Step 2 — Profile the Five Segments
Account for exactly these segments:

| Segment | Description |
|---|---|
| `system_prompt` | Static instructions loaded at session start |
| `conversation_history` | User turns, assistant turns, tool invocations, and tool outputs |
| `retrieved_context` | Retrieved documents, RAG inserts, and injected knowledge |
| `tool_schemas` | Loaded MCP/tool schemas and descriptors |
| `working_memory` | Active memory blocks, project instructions, and temporary reasoning aids |

If a segment source is unavailable:
- Set token count to `0`
- Mark its source as `"missing"`
- Add a corresponding note.

#### Step 3 — Estimate Tokens
Apply the deterministic heuristic independently to each segment:

```text
estimated_tokens = ceil(character_count / 3.8)
```

For JSON-heavy segments:

```text
estimated_tokens = ceil(character_count / 3.5)
```

Annotate all estimates with:

```json
"method": "char_heuristic"
```

Do not claim exact tokenizer counts.

#### Step 4 — Compute Budget Totals
Calculate:

```text
total_used = sum(segment_tokens)

utilization_percentage =
(total_used / model_window_size) × 100

headroom =
model_window_size − total_used

headroom_percentage =
(headroom / model_window_size) × 100
```

#### Step 5 — Apply Alert Thresholds
Use these thresholds:

| Utilization | Alert Level |
|---|---|
| < 70% | none |
| 70–84.9% | warn |
| 85–94.9% | critical |
| ≥ 95% | emergency |

Determine:
- `alert_level`
- `threshold_crossed`
- `recommended_action`

Recommended actions:

```text
none
invoke_strategic_compactor
invoke_strategic_compactor_immediately
invoke_relevance_pruner_then_compactor
```

If utilization exceeds the model window:

```text
status = overflow
alert_level = emergency
```

#### Step 6 — Build context-budget.json
Generate:

```text
output/context-budget.json
```

Include:

- Schema version
- Timestamp
- Model window size
- Estimation method
- Per-segment:
  - token count
  - percentage
  - character count
  - source
- Totals
- Utilization percentage
- Headroom
- Status
- Alert level
- Threshold status
- Recommended action
- Notes

#### Step 7 — Action Payload
If a recommendation exists, include:

```json
"action_payload": {
  "skill": "",
  "priority": "",
  "suggested_compaction_target_tokens": 0,
  "segments_to_compact": [],
  "rationale": ""
}
```

Use:

```text
suggested_compaction_target_tokens =
ceil(conversation_history_tokens × 0.40)
```

when compaction is recommended.

### Outputs

Generate:

- `output/context-budget.json`

### Output Requirements

Include summary metrics:

- Total tokens used
- Context utilization percentage
- Remaining headroom
- Alert level
- Recommended next action

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 15

Run the `relevance-pruner` skill.

### Inputs
- Skill definition: `RelevancePruner/SKILL.md`
- Authoritative inputs:
  - `input/candidate-chunks.json`
  - `input/task-query.md`
  - `input/pruning-config.json`

### Execution
- Prune candidate context deterministically before downstream reasoning.
- Do not summarize, rewrite, truncate, or modify chunk content.
- Score, retain, or reject complete chunks only.
- Pause and request clarification if required inputs are incomplete.

### Processing Steps

#### Step 1 — Load Inputs
Read:

- Candidate chunks from `candidate-chunks.json`
- Current task intent from `task-query.md`
- Configuration from `pruning-config.json`

Extract:

- Threshold (default `0.35`)
- Maximum token budget
- Scoring weights
- Protected patterns
- Embedding model

If configuration values are missing, apply documented defaults and record them.

#### Step 2 — Score Every Chunk
For each chunk calculate:

```text
relevance_score =
(semantic_similarity × 0.6)
+ (recency_weight × 0.2)
+ (source_authority × 0.2)
```

Document each component score.

##### Semantic Similarity
- Compute embeddings using the configured embedding model.
- Query embedding uses:
  - Primary intent
  - Secondary intent
  - Explicit keywords from `task-query.md`
- Chunk embedding uses:

```text
title + first 512 characters of content
```

Clamp cosine similarity:

```text
semantic_similarity = max(0, cosine_similarity)
```

##### Recency Weight

```text
days_old = (now − created_at).days

recency_weight = exp(-days_old / 365)
```

If `created_at` is missing:

```text
recency_weight = 0.5
```

##### Source Authority
Use explicit authority scores when present.

Otherwise apply defaults:

| Source | Authority |
|---|---:|
| knowledge_base | 0.90 |
| product_documentation | 0.85 |
| faq | 0.75 |
| crm_case_note | 0.70 |
| prior_turn | 0.65 |
| external_article | 0.50 |
| user_generated | 0.30 |
| unknown | 0.50 |

#### Step 3 — Protect Critical Chunks
Protect any chunk matching:

- `customer_id`
- `ticket_id`
- `commitment_made`

Protected chunks:

- Cannot be dropped by threshold checks.
- Must record:

```text
kept_reason = "protected_pattern"
```

Reserve their tokens before budget packing.

#### Step 4 — Apply Threshold
Drop non-protected chunks where:

```text
relevance_score < threshold
```

Log:

```text
drop_reason = "below_threshold"
```

#### Step 5 — Greedy Budget Packing
Sort survivors by:

```text
relevance_score descending
```

Pack chunks greedily:

```text
if token_count + chunk_tokens <= max_tokens:
    keep
else:
    drop
```

Over-budget drops use:

```text
drop_reason = "over_budget_after_threshold"
```

Protected chunks always take precedence.

If protected chunks alone exceed budget:

```text
budget_exceeded_by_protection = true
```

Keep them anyway.

#### Step 6 — Generate Outputs

Generate:

##### pruned-context.json

Include:

```json
{
  "id": "",
  "title": "",
  "source": "",
  "relevance_score": 0,
  "semantic_similarity": 0,
  "recency_weight": 0,
  "source_authority": 0,
  "tokens": 0,
  "kept_reason": "",
  "content": ""
}
```

##### dropped-chunks-log.json

Include:

```json
{
  "id": "",
  "title": "",
  "source": "",
  "relevance_score": 0,
  "tokens": 0,
  "drop_reason": ""
}
```

##### pruning-summary.json

Include:

- Task query summary
- Total candidate tokens
- Total kept tokens
- Tokens reclaimed
- Reduction percentage
- Chunks evaluated
- Chunks kept
- Chunks dropped
- Below-threshold count
- Over-budget count
- Protected chunks kept
- Budget exceeded by protection flag
- Threshold used
- Maximum token budget

### Outputs

Generate:

- `pruned-context.json`
- `dropped-chunks-log.json`
- `pruning-summary.json`

### Output Requirements

Include summary metrics:

- Total chunks evaluated
- Chunks retained
- Chunks dropped
- Tokens reclaimed
- Reduction percentage
- Protected chunks preserved
- Budget utilization after pruning

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt


---

## Prompt 16

Run the `rolling-summarizer` skill.

### Inputs
- Skill definition: `RollingSummarizer/SKILL.md`
- Authoritative inputs:
  - `input/recent-turns.md`
  - `input/prior-summary.md`
  - `input/summarizer-config.json`

### Execution
Maintain a bounded rolling session memory by folding recent turns into the existing structured summary. Preserve critical commitments and identifiers exactly as recorded.

### Processing Steps

#### Step 1 — Validate Trigger Conditions
Determine whether summarization should run.

Trigger if either condition is true:

```text
turns_since_last_summary >= 10
```

OR

```text
new_turns_token_count > 3000
```

If both conditions fire:

```text
trigger = "both"
```

Otherwise log:

```text
turns_trigger
```

or

```text
token_trigger
```

If neither trigger condition is met, stop and report that summarization was not required.

#### Step 2 — Select Model
Default model:

```text
claude-haiku-4-5
```

Escalate to:

```text
claude-sonnet-4-6
```

if any new turn contains:

- Legal language
- Formal commitments
- Regulatory references
- Dispute escalation content

Examples include:

- "per our SLA"
- "I can confirm..."
- "GDPR"
- "HIPAA"
- "chargeback"
- "attorney"
- "legal action"

If escalation occurs:

Record:

```text
escalation_triggered: true
escalation_reason: <detected signal>
model_used: claude-sonnet-4-6
```

Use Sonnet for the entire run.

#### Step 3 — Load Existing Summary
Read:

- Recent turns from `recent-turns.md`
- Previous rolling summary from `prior-summary.md`
- Summarizer configuration

If no prior summary exists:

Initialize an empty summary using the required six sections and note the session start context.

#### Step 4 — Extract New Facts
Identify information not already represented in the prior summary.

Capture:

- Identity/profile updates
- Issue developments
- Actions taken
- Status changes
- New commitments
- Pending items
- Root-cause findings
- Resolution updates

Do not duplicate facts already represented semantically.

#### Step 5 — Fold Into Existing Summary
For each summary section:

- Modify outdated information in place.
- Append additive information concisely.
- Preserve unchanged content exactly.

Apply section labels:

```text
[UPDATED]
```

```text
[NEW]
```

```text
[UNCHANGED]
```

Strictly avoid duplication.

#### Step 6 — Preserve Verbatim Fields
Never paraphrase or compress fields listed in:

```text
preserve_verbatim
```

At minimum preserve exactly:

- customer_id
- ticket_id
- commitment_text
- amounts

Copy character-for-character.

#### Step 7 — Enforce Token Budget
Maximum summary size:

```text
max_summary_tokens
```

(default: 800)

If exceeded:

1. Compress `Session Context`
2. Compress `Issue Summary`
3. Compress `Actions Taken`
4. Never compress:
   - Customer Profile
   - Commitments Made

Record if budget compression occurred.

#### Step 8 — Generate Updated Summary
Produce exactly these six sections in this order:

```markdown
## Session Context

## Customer Profile

## Issue Summary

## Actions Taken

## Pending Items

## Commitments Made
```

Requirements:

- Mark sections using `[UPDATED]`, `[NEW]`, or `[UNCHANGED]`
- Preserve commitments verbatim
- Remove resolved pending items
- Reflect the latest understanding of the issue

#### Step 9 — Generate Session State Metadata
Produce:

```json
{
  "last_summarized_at": {
    "turn_number": "",
    "timestamp": ""
  },
  "trigger_fired": "",
  "model_used": "",
  "summary_token_count": 0,
  "escalation_triggered": false,
  "escalation_reason": null
}
```

#### Step 10 — Context Replacement Instructions
After summary generation:

- Remove all raw turns included in this run from active context.
- Replace them with the updated rolling summary.
- Retain turns occurring after the summarization cutoff.
- Update session state metadata.

### Outputs

Generate:

- `updated-rolling-summary.md`
- `summary-run-log.json`
- `session-state.json`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 17

Run the `strategic-compactor` skill.

### Inputs
- Skill definition: `StrategicCompactor/SKILL.md` :contentReference[oaicite:0]{index=0}
- Authoritative inputs:
  - `input/full-session.md`
  - `input/keep-anchors.json`
  - `input/context-profiler-alert.json`

### Execution
Compact stale session history into a structured digest that preserves all actionable state while aggressively reclaiming context tokens. This is a lossy operation, but no actionable information may be lost.

### Processing Steps

#### Step 1 — Validate Inputs
Load and review all inputs before classification.

Read:

- `full-session.md`
- `keep-anchors.json`
- `context-profiler-alert.json`

Extract:

- Anchor values requiring verbatim preservation
- Alert level and utilization percentage
- Complete session history

Do not classify turns until the entire session has been reviewed.

#### Step 2 — Determine Compaction Aggression
Use the ContextProfiler alert to calibrate reduction targets.

| Alert Level | Reduction Target |
|---|---:|
| `warn` | 50–60% |
| `critical` | 65–75% |

Record:

```text
alert_level
utilization_percentage
target_reduction
```

#### Step 3 — Classify Every Turn
Assign each turn exactly one classification:

- `ANCHOR`
  - Contains values from `keep-anchors.json`
  - Final decisions still in force
  - Live error codes or API responses
  - Constraints or SLA boundaries
  - Latest unsuperseded status

- `LIVE`
  - Informs the current approach
  - Marks pivots between approaches
  - Contains unresolved customer information
  - Contributes to the active resolution path

- `STALE`
  - Abandoned explorations
  - Superseded attempts
  - Completed intermediate steps
  - Filler with minor informational value

- `DISCARD`
  - Pure acknowledgements
  - Duplicate content
  - Retry noise
  - Status chatter without current relevance

#### Step 4 — Preserve Anchors Verbatim
Every value from `keep-anchors.json` must appear unchanged.

Preserve exactly:

- Customer IDs
- Ticket IDs
- Transaction IDs
- Error codes
- Monetary amounts
- Current status
- Open decisions
- Constraints
- Customer-stated unresolved facts

No paraphrasing, rounding, or abbreviation is allowed.

#### Step 5 — Build the Structured Digest
Generate `compacted-context.md` using exactly these sections:

```markdown
# Compacted Session Context

## Task State

## Decisions Made

## Open Threads

## Key IDs & References

## Constraints

## Discarded Material
```

Requirements:

- Task State reflects the latest confirmed status.
- Include only active decisions.
- Include all unresolved blockers.
- Preserve all IDs and amounts verbatim.
- Summarize discarded exploration using counts rather than detail.

#### Step 6 — Collapse Noise
Apply compaction rules:

- Collapse exploration loops into counts.
- Remove intermediate tool-call chatter.
- Preserve final outcomes.
- Preserve customer-stated unresolved facts.
- Summarize escalation loops if applicable.
- Never discard the latest status.

#### Step 7 — Generate Anchor Manifest
Produce:

```text
retained-anchor-manifest.json
```

For each retained item include:

- Item description
- Retention reason
- Original token estimate
- Retained format:
  - verbatim
  - summarized
  - counted-only
- Source turns
- Destination section

Ensure every retained element in the digest has a corresponding manifest entry.

#### Step 8 — Generate Token Metrics
Produce:

```text
token-delta.json
```

Include:

- Pre-compaction tokens
- Post-compaction tokens
- Tokens saved
- Reduction percentage
- Compaction quality
- Anchors preserved
- Turns summarized
- Turns discarded
- Alert level
- Utilization at trigger
- Estimated new utilization
- Compaction timestamp

Assess quality honestly:

| Quality | Criteria |
|---|---|
| `high` | All anchors preserved and ≥40% reduction |
| `medium` | All anchors preserved and ≥30% reduction |
| `low` | Anchor loss or insufficient reduction |

### Outputs

Generate:

- `compacted-context.md`
- `retained-anchor-manifest.json`
- `token-delta.json`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 18

Run the `iterative-retrieval` skill.

### Inputs
- Skill definition: `IterativeRetrieval/SKILL.md` :contentReference[oaicite:0]{index=0}
- Authoritative inputs:
  - `input/task-query.md`
  - `input/knowledge-base/`
  - `input/retrieval-config.json`

### Execution
Use progressive retrieval to answer the task using the minimum grounded context necessary. Start with a small slice, identify knowledge gaps, and retrieve additional evidence only when confidence remains below threshold.

### Processing Steps

#### Step 1 — Initialize Retrieval Context
Read `task-query.md` completely.

Extract:

- Primary question to resolve
- Key entities
- User intent
- Likely document domains
- Known facts already present
- Constraints affecting the answer
- Initial unresolved conditions

Initialize:

```text
confidence = 0.0
round = 0
tokens_loaded = 0
gaps = []
```

Do not retrieve documents yet.

#### Step 2 — First Retrieval Slice
Using the primary question and top entities:

- Query the knowledge base.
- Retrieve the top 3 highest-relevance chunks.
- Record:

```json
{
  "round": 1,
  "query": "",
  "docs_loaded": [],
  "tokens_this_round": 0,
  "cumulative_tokens": 0
}
```

Update cumulative token usage.

#### Step 3 — Assess Grounding and Confidence
Attempt to answer the task using only currently loaded context.

Evaluate for knowledge gaps, including:

- Missing eligibility conditions
- Unknown thresholds or dates
- Unloaded referenced sections
- Ambiguous policy scope
- Missing supporting evidence
- Unresolved reasoning branches

Assign confidence:

| Confidence | Interpretation |
|---|---|
| 0.00–0.40 | Major gaps remain |
| 0.41–0.60 | Partial answer |
| 0.61–0.84 | Likely answer with minor uncertainty |
| 0.85–1.00 | Fully grounded |

For every detected gap record:

```json
{
  "gap_id": "",
  "description": "",
  "target_query": "",
  "target_category": "",
  "severity": "blocking | supporting"
}
```

#### Step 4 — Evaluate Stop Conditions
Check stop criteria in this order:

1. Confidence ≥ 0.85
2. Maximum rounds reached
3. Maximum token budget reached
4. No gaps detected
5. Confidence ≥ 0.70 with only supporting gaps remaining

Apply defaults from configuration:

| Parameter | Default |
|---|---:|
| Confidence threshold | 0.85 |
| Maximum rounds | 5 |
| Token budget | 12,000 |
| Initial slice size | Top-3 |

If a stop condition is met:

Record the appropriate:

```text
stop_reason
```

Proceed to output generation.

#### Step 5 — Progressive Retrieval Loop
If blocking gaps remain:

- Select the highest-priority blocking gap.
- Formulate a targeted query.
- Retrieve the top 2 new chunks not already loaded.
- Update:

```text
round
tokens_loaded
retrieval_context
confidence
gaps
```

Repeat Steps 3–5 until a stop condition is satisfied.

#### Step 6 — Generate Grounded Answer
Produce:

```text
grounded-answer.md
```

Include:

```markdown
## Resolution

## Supporting Evidence

## Recommended Agent Actions

## Coverage Confidence
```

Requirements:

- Every factual claim must include inline citations.
- Recommended actions must be grounded in retrieved evidence.
- State the final confidence score and confidence band.

#### Step 7 — Generate Retrieval Trace
Produce:

```text
retrieval-trace.json
```

For each round record:

- Round number
- Query issued
- Documents loaded
- Tokens loaded this round
- Cumulative tokens
- Confidence after reasoning
- Gaps detected

Include `stop_reason` only in the final round.

#### Step 8 — Generate Coverage Metrics
Produce:

```text
coverage-report.json
```

Include:

- Final confidence
- Stop reason
- Total rounds
- Total tokens loaded
- Gaps identified
- Gaps resolved
- Gaps unresolved
- Efficiency versus full corpus load
- Percentage reduction achieved

### Outputs

Generate:

- `grounded-answer.md`
- `retrieval-trace.json`
- `coverage-report.json`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**  
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 19

Run the `memory-persistence` skill.

### Inputs
- Skill definition: `.claude/memory-persistence/SKILL.md`
- Authoritative inputs:
  - `input/session-state-raw.json`
  - `input/memory-config.json`

### Execution
Read all required inputs and execute the skill exactly as defined.

Execute the following phases in order:
- Phase 1: State Extraction
- Phase 2: Sensitive Data Exclusion
- Phase 3: State Prioritization
- Phase 4: Session State Serialization
- Phase 5: Rehydration Block Construction
- Phase 6: Character Cap Enforcement

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- State complexity classification
- Open thread count
- Interdependency count
- Escalation status
- Truncation decisions

### Phase 1 — State Extraction
Validate that all REQUIRED inputs are present.

Verify the existence of:
- `input/session-state-raw.json`
- `input/memory-config.json`

If any REQUIRED inputs are missing:
- List every missing input.
- Halt execution.
- Do not proceed further.

Extract and categorize session state from `input/session-state-raw.json`.

Identify and prioritize:
- Commitments
- Open decisions
- Active task
- Constraints
- Context notes

Capture any additional state required by the skill definition.

### Phase 2 — Sensitive Data Exclusion
Inspect the extracted state and apply exclusion rules from `input/memory-config.json`.

Verify that the following are NEVER persisted:
- Authentication tokens
- Session cookies
- Passwords
- API keys
- Credit card numbers
- Any prohibited sensitive fields defined by the configuration

Document all excluded items and reasons for exclusion.

### Phase 3 — State Prioritization
Prioritize extracted state using the following order:
1. Commitments
2. Open decisions
3. Active task
4. Constraints
5. Context notes

Determine:
- State complexity
- Open thread count
- Interdependency count

Apply all escalation rules defined in the skill.

If escalation conditions are met:
- Record the escalation reason.
- Document the selected model.

### Phase 4 — Session State Serialization
Generate the persistent session snapshot.

Ensure the serialized state:
- Conforms to the schema defined by the skill
- Includes all required metadata
- Preserves prioritized information accurately
- Excludes prohibited sensitive information

### Phase 5 — Rehydration Block Construction
Generate the rehydration block using the prioritized session state.

Ensure the block:
- Follows the priority ordering defined by the skill
- Is suitable for injection at the start of a future session
- Preserves higher-priority information before lower-priority information

### Phase 6 — Character Cap Enforcement
Apply the configured 6,000-character cap.

Trim lower-priority tiers first while preserving higher-priority information.

If truncation occurs:
- Record which items were truncated.
- Document the reason for truncation.
- Preserve the highest-priority content intact.

Follow all constraints, escalation rules, processing logic, and execution behavior defined in the `MemoryPersistence` skill.

### Outputs
Generate or update the following artifacts:
- `session-state.json`
- `rehydration-block.md`

Ensure `session-state.json` contains:
- Version and schema information
- Session metadata
- Sanitized and prioritized session state
- Complexity metadata
- Required fields defined by the skill

Ensure `rehydration-block.md`:
- Uses the prioritized ordering defined by the skill
- Respects the 6,000-character cap
- Documents any truncation decisions
- Is ready for future session restoration

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 20

Run the `eval-harness` skill.

### Inputs
- Skill definition: `.claude/eval-harness/SKILL.md`
- Authoritative inputs:
  - `input/eval-cases.json`
  - `input/golden-references/`
  - `input/eval-config.json`

### Execution
Read all required inputs and execute the skill exactly as defined.

Execute the following phases in order:
- Phase 1: Input Validation
- Phase 2: Evaluation Suite Preparation
- Phase 3: Exact Match Evaluation
- Phase 4: Rubric Evaluation
- Phase 5: Rubric + Regex Evaluation
- Phase 6: Functional Evaluation
- Phase 7: Adversarial Evaluation
- Phase 8: Quality Gate Assessment
- Phase 9: Failure Analysis
- Phase 10: Results Generation

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Evaluation execution mode
- Grader mix configuration
- Pass@k configuration
- Quality gate thresholds
- Overall gate status

### Phase 1 — Input Validation
Validate that all REQUIRED inputs are present.

Verify the existence of:
- `input/eval-cases.json`
- `input/golden-references/`
- `input/eval-config.json`

If any REQUIRED inputs are missing:
- List every missing input.
- Halt execution.
- Do not proceed further.

Inspect `input/eval-config.json` and determine:
- Checkpoint vs continuous execution mode
- Enabled grader types
- Pass@k settings
- Gate thresholds

Validate that every evaluation case contains:
- Case identifier
- Input
- Expected output
- Grader type

If malformed cases exist:
- List all affected case IDs.
- Halt execution.

### Phase 2 — Evaluation Suite Preparation
Load all evaluation cases.

Group cases by grader type:
- `exact_match`
- `rubric`
- `rubric_regex`
- `functional`
- `adversarial`

Resolve corresponding references from `input/golden-references/`.

Identify:
- Total evaluation count
- Grader distribution
- Missing references

If required references are unavailable:
- List all affected cases.
- Halt execution.

### Phase 3 — Exact Match Evaluation
Execute all `exact_match` cases.

Compare generated outputs against the corresponding golden references.

Record:
- Case ID
- Expected output
- Actual output
- Pass/fail result

Calculate aggregate exact match performance.

### Phase 4 — Rubric Evaluation
Execute all `rubric` cases.

Use Sonnet as specified by the skill.

Evaluate outputs against rubric criteria.

Record:
- Case ID
- Rubric score
- Evaluation rationale
- Pass/fail determination

Calculate aggregate rubric performance.

### Phase 5 — Rubric + Regex Evaluation
Execute all `rubric_regex` cases.

Apply:
- Regex validation
- Rubric assessment

Record:
- Case ID
- Regex outcome
- Rubric outcome
- Combined decision
- Pass/fail result

Identify all regex validation failures.

### Phase 6 — Functional Evaluation
Execute all `functional` cases.

Validate behavioral correctness according to the skill requirements.

Record:
- Case ID
- Functional outcome
- Validation evidence
- Pass/fail result

Calculate aggregate functional performance.

### Phase 7 — Adversarial Evaluation
Execute all `adversarial` cases.

Use Opus as specified by the skill.

Assess:
- Robustness
- Safety behavior
- Resistance to adversarial inputs

Record:
- Case ID
- Vulnerability findings
- Severity
- Pass/fail determination

Document all adversarial findings.

### Phase 8 — Quality Gate Assessment
Aggregate evaluation outcomes across all grader types.

Calculate:
- Overall pass rate
- Per-grader pass rates
- Pass@k metrics
- Threshold utilization

Apply the quality gate rules defined in `input/eval-config.json`.

If performance falls below threshold:
- Set gate status to `GATE_FAIL`.
- List every failing case ID.
- Document the reason for failure.

Otherwise:
- Set gate status to `GATE_PASS`.

### Phase 9 — Failure Analysis
Analyze all failing cases.

Identify:
- Failure categories
- Common failure patterns
- Repeated failure modes
- Cross-grader correlations

Generate actionable findings for remediation.

Prioritize failures by impact.

### Phase 10 — Results Generation
Finalize all output artifacts.

Ensure all findings, gate decisions, and analyses are consistent with the execution results.

Follow all constraints, grader behaviors, gate logic, and execution rules defined in the `EvalHarness` skill.

### Outputs
Generate or update the following artifacts:
- `eval-results.json`
- `adversarial-findings.json`
- `failure-analysis.json`
- `gate-attestation.md`

Ensure `eval-results.json` contains:
- Evaluation metadata
- Overall gate status
- Per-case outcomes
- Per-grader summaries
- Aggregate metrics
- Pass@k results

Ensure `adversarial-findings.json` contains:
- Adversarial case identifiers
- Findings
- Severity classifications
- Recommended mitigations

Ensure `failure-analysis.json` contains:
- Failing case IDs
- Failure categories
- Root-cause patterns
- Cross-grader insights
- Prioritized remediation guidance

Ensure `gate-attestation.md` contains:
- Evaluation mode
- Total evaluations executed
- Overall pass rates
- Threshold comparison
- Final gate decision
- Failing case identifiers when `GATE_FAIL`

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 21

Run the `pattern-extractor` skill.

### Inputs
- Skill definition: `.claude/pattern-extractor/SKILL.md`
- Authoritative inputs:
  - `input/session-traces/`
  - `input/existing-patterns.json`
  - `input/extractor-config.json`

### Execution
Read all required inputs and execute the skill exactly as defined.

Execute the following phases in order:
- Phase 1: Input Validation
- Phase 2: Mine
- Phase 3: Score
- Phase 4: Cluster
- Phase 5: Draft
- Phase 6: Queue
- Phase 7: Results Generation

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Total session traces analyzed
- Existing pattern catalogue size
- Confidence threshold applied
- Clustering parameters used
- Anti-pattern detection status
- Promotion queue summary

### Phase 1 — Input Validation
Validate that all REQUIRED inputs are present.

Verify the existence of:
- `input/session-traces/`
- `input/existing-patterns.json`
- `input/extractor-config.json`

If any REQUIRED inputs are missing:
- List every missing input.
- Halt execution.
- Do not proceed further.

Inspect `input/extractor-config.json` and determine:
- Confidence threshold
- Clustering parameters
- Anti-pattern detection rules

Validate that session traces are readable and suitable for extraction.

If malformed traces exist:
- List all affected trace identifiers.
- Halt execution.

### Phase 2 — Mine
Scan all session traces and accompanying artifacts for recurring patterns.

Identify and extract:

1. Recurring tool call sequences
2. Repeated reasoning chains
3. Consistent phrasing patterns
4. Decision heuristics
5. Artifact patterns

For each candidate pattern, record:
- `pattern_id`
- `pattern_type`
- `occurrences`
- `raw_evidence`

Limit raw evidence excerpts according to the skill definition.

Determine whether the session qualifies for extraction based on the execution criteria defined by the skill.

### Phase 3 — Score
Assign confidence scores to all extracted patterns.

Apply the scoring formula defined by the skill:

```
confidence = min(
    1.0,
    ((occurrences - 1) * 0.25)
    + (consistency_score * 0.5)
)
```

Calculate:
- Consistency scores
- Confidence scores
- Failure session counts
- Failure rates

Classify patterns as:
- High confidence (`>= 0.75`)
- Moderate confidence (`0.50–0.74`)
- Low confidence (`< 0.50`)

Identify all patterns eligible for promotion review.

### Phase 4 — Cluster
Group related patterns into candidate skills.

Evaluate:
- Trigger overlap
- Intent overlap
- Workflow similarity
- Keyword similarity using Jaccard thresholds

Compute cluster confidence using the method defined by the skill.

Cross-reference all clusters against `input/existing-patterns.json`.

Determine whether each cluster should be classified as:
- New candidate skill
- Existing skill enhancement (`OVERLAP`)
- Instinct requiring additional evidence

Document overlap findings.

### Phase 5 — Draft
Generate candidate skill drafts for all patterns or clusters with confidence `>= 0.50`.

For each draft, generate:

- Candidate metadata
- Trigger section
- Instructions section
- Examples section
- Caveats section

Ensure generated drafts conform to the structure defined by the skill.

Flag all drafts as requiring human review.

### Phase 6 — Queue
Generate the promotion queue.

Classify entries as:

#### Ready for Promotion
Requirements:
- Confidence `>= 0.75`
- No blocking anti-pattern designation

Include:
- Draft path
- Confidence score
- Evidence summary
- Overlap notes
- Reviewer checklist

#### Needs More Evidence
Requirements:
- Confidence `0.50–0.74`

Include:
- Instinct summary
- Required additional evidence
- Suggested re-evaluation timing

#### Instinct Only
Requirements:
- Confidence `< 0.50`

Record in the catalogue only.

Do not surface these in the promotion queue unless explicitly required by the skill.

Apply all anti-pattern detection rules.

If anti-patterns are identified:
- Flag them separately.
- Prevent automatic promotion.
- Include warning notes and reviewer guidance.

### Phase 7 — Results Generation
Finalize all output artifacts.

Ensure all findings, classifications, queues, and draft outputs are internally consistent.

Follow all constraints, scoring rules, clustering logic, anti-pattern safeguards, promotion thresholds, and execution behavior defined in the `PatternExtractor` skill.

### Outputs
Generate or update the following artifacts:
- `pattern-catalogue.json`
- `SKILL-*-candidate.md`
- `promotion-queue.json`
- `extraction-report.json`

Ensure `pattern-catalogue.json` contains:
- All extracted patterns
- Pattern classifications
- Confidence scores
- Occurrence counts
- Evidence excerpts
- Anti-pattern indicators

Ensure `SKILL-*-candidate.md` files contain:
- Candidate status
- Confidence metadata
- Evidence summaries
- Trigger definitions
- Step-by-step instructions
- Examples
- Caveats

Ensure `promotion-queue.json` contains:
- Ready-for-promotion entries
- Needs-more-evidence entries
- Overlap notes
- Reviewer checklists
- Anti-pattern warnings

Ensure `extraction-report.json` contains:
- Execution summary
- Session statistics
- Pattern counts by category
- Confidence distributions
- Promotion recommendations
- Anti-pattern findings
- Estimated reuse value

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

**Simplified AI Operations Complete**
