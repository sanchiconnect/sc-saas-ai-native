# BudgetGovernor

Per-task and per-sprint token and cost enforcement for AI agent pipelines.

BudgetGovernor performs deterministic cost accounting before any tokens are spent. It reads a task graph with per-step model and I/O token estimates, computes projected cost against a live pricing table, compares the projection to tiered budget caps, and returns a gate decision — `proceed`, `warn`, or `block` — with no LLM required.

---

## Directory Layout

```
BudgetGovernor/
  SKILL.md                         — full accounting algorithm and pricing table
  input/
    task-graph.json                — per-step model + token estimates + loop config
    pricing-table.json             — Claude API prices per MTok (update as pricing changes)
    budget-caps.json               — tiered caps + alert webhook + scaling profiles
  output/
    cost-forecast.json             — example: proceed at 68% task utilization
    cost-forecast-blocked.json     — example: block at 174% from runaway research_loop
    spend-ledger.json              — 5-session running ledger with daily/sprint rollups
```

---

## Setting Budget Caps for Different Deployment Scales

Three scaling profiles are defined in `input/budget-caps.json`. Choose based on traffic volume and quality requirements.

### Startup / MVP (pre-revenue, low traffic)

```json
{
  "task_cap_usd": 0.02,
  "session_cap_usd": 0.06,
  "daily_cap_usd": 10.00,
  "sprint_cap_usd": 100.00,
  "monthly_cap_usd": 400.00
}
```

At this cap level, the standard task graph ($0.034 estimated) will immediately trigger `warn` and frequently `block`. You must either downgrade `issue_analysis` and `response_generation` to Haiku, reduce token estimates to reflect simpler queries, or accept that complex cases will be gated to a human fallback.

Implied capacity: roughly 500 resolved sessions per day before the daily cap is hit.

### Growth Stage (current profile, 1K–2K sessions/day)

```json
{
  "task_cap_usd": 0.05,
  "session_cap_usd": 0.15,
  "daily_cap_usd": 50.00,
  "sprint_cap_usd": 500.00,
  "monthly_cap_usd": 2000.00
}
```

The standard task graph at $0.034 sits at 68% task utilization — comfortable headroom for variance while still catching runaway loops. This is the recommended starting point for production.

Implied capacity: roughly 1,470 sessions per day before the daily cap, or about 14,700 per sprint.

### Enterprise Scale (high volume, SLA-bound)

```json
{
  "task_cap_usd": 0.10,
  "session_cap_usd": 0.30,
  "daily_cap_usd": 500.00,
  "sprint_cap_usd": 5000.00,
  "monthly_cap_usd": 20000.00
}
```

Allows Sonnet to be used on more steps and accommodates research-heavy enterprise cases without hitting hard blocks. The monthly cap aligns with a finance-approved AI spend envelope at this scale. Implied capacity: 5,000+ sessions per day.

### Setting Caps in Practice

1. Start with the `growth_stage` profile.
2. Run for one sprint and observe `spend-ledger.json` — specifically `variance_analysis.mean_absolute_percentage_error`.
3. If MAPE is above 15%, your estimates are miscalibrated. Fix the task graph estimates before lowering caps.
4. Tighten `task_cap_usd` incrementally. The goal is a cap that catches genuine overruns without false-blocking normal sessions.
5. Always set `warn_threshold_percentage` at least 10 points below `block_threshold_percentage` to give operators time to intervene.

---

## Interpreting Gate Decisions

### `proceed`

Task utilization is at or below 80% across all cap levels. Execution may continue. No action required.

Check `budget_headroom.task.research_loop_iterations_affordable` if the task includes a research loop — this tells you how many additional iterations fit within remaining headroom before BudgetGovernor would block.

### `warn`

Task utilization is between 80% and 100%. Execution is allowed to continue, but:

- A webhook alert is fired to `alert_webhook` in `budget-caps.json`
- The session is flagged in `spend-ledger.json` with `gate_decision: "warn"`
- ModelRouter (if integrated) can optionally downgrade remaining steps automatically

Operator response: Review the current task's cost distribution in the `cost_forecast.json` output. If the warn is on `session` or `sprint` utilization (not `task`), no immediate action is needed — it is an informational signal for the POD Lead.

If the warn is on `task` utilization (projecting $0.04–$0.05 on a $0.05 cap), check whether `research_loop` is included in the execution path. If so, the loop guard will activate earlier — the headroom field in the forecast shows how many loop iterations remain before a hard block.

### `block`

Projected cost exceeds the cap at any tier. Execution is halted immediately. Downstream steps are not executed.

The forecast output includes:
- `block_reason`: a machine-readable string describing which cap was breached and by how much
- `halt_point`: the step and iteration where execution stopped
- `spend_at_halt_usd`: actual spend already incurred before the halt (this is real money spent)
- `remediation_suggestions`: ordered list of concrete actions to bring projected cost within cap

**What to do after a block:**

1. Read `remediation_suggestions` in priority order. Apply the highest-savings remediations first.
2. If the block is from a runaway loop (the most common case), apply remediation #1 (reduce iterations) and remediation #2 (downgrade loop model to Haiku) together — the combined saving typically resolves the breach.
3. Update `task-graph.json` to reflect the corrected iteration limit or model assignment. This prevents the same block from repeating.
4. If the block is a one-off (unusual task type), use the manual override flow in `budget-caps.json` under `overrides`. This requires POD Lead approval and is logged to the audit trail.

### Reading `remediation_suggestions`

Each suggestion has a `priority` (1 = highest savings), `type`, `savings_usd`, `feasibility`, and `quality_impact`.

| Type | What it does |
|---|---|
| `reduce_iterations` | Lower the loop's `estimated_iterations` or enforce a hard cap earlier in the loop guard |
| `model_downgrade` | Route a specific step to the next cheaper model tier via ModelRouter |
| `combined` | Apply multiple remediations simultaneously — shows the resulting utilization after all changes |

Always check `quality_impact` before applying a `model_downgrade` to a customer-facing step (`response_generation`). Downgrading that step from Sonnet to Haiku saves money but will produce noticeably lower-quality responses. Reserve this for last-resort scenarios.

---

## Integrating with ModelRouter for Automatic Downgrade on Budget Pressure

BudgetGovernor and ModelRouter are designed to work together. On a `warn` gate decision, BudgetGovernor passes `remediation_suggestions` to ModelRouter as routing hints. ModelRouter can act on these automatically without human intervention.

### Configuration

In your agent orchestrator, wire the two agents together:

```python
forecast = BudgetGovernor.evaluate(task_graph, pricing_table, budget_caps)

if forecast.gate_decision == "warn":
    # Pass downgrade hints to ModelRouter before executing remaining steps
    ModelRouter.apply_budget_pressure_hints(
        hints=forecast.remediation_suggestions,
        threshold="warn"  # Only apply model downgrades, not iteration changes
    )

elif forecast.gate_decision == "block":
    # Hard stop — do not execute any further steps
    raise BudgetBlockException(
        reason=forecast.block_reason,
        remediations=forecast.remediation_suggestions
    )
```

### Automatic Downgrade Priority

When ModelRouter receives `budget_pressure=true`, it uses the `downgrade_ladder` from `pricing-table.json`:

```
claude-opus-4-7 → claude-sonnet-4-6 → claude-haiku-4-5 → (no further downgrade)
```

ModelRouter only downgrades optional or non-customer-facing steps by default. To allow downgrading customer-facing steps (`response_generation`), set `allow_response_generation_downgrade: true` in ModelRouter's config. This is off by default because the quality impact is user-visible.

### Feedback Loop

After execution completes, the runtime writes `actual_cost_usd` back to the spend ledger. BudgetGovernor reads historical ledger entries during the next sprint review to compute `variance_analysis.mean_absolute_percentage_error`. If MAPE drifts above 15%, the system should flag that task graph estimates need recalibration.

---

## Calibrating Estimates for New Task Types

When you add a new step or task type to the task graph, the initial `estimated_input_tokens` and `estimated_output_tokens` values are guesses. Follow this process to calibrate them.

### Step 1 — Run Shadow Mode for One Sprint

Set `is_optional: true` for the new step initially so BudgetGovernor does not block on it. Let the step run and capture actual token counts in the ledger with no gate enforcement.

### Step 2 — Collect Actual Token Data

After 50–100 runs of the new step, compute:

```
p50_input_tokens  = median(actual input tokens across all runs)
p95_input_tokens  = 95th percentile
p50_output_tokens = median(actual output tokens)
p95_output_tokens = 95th percentile
```

### Step 3 — Set Estimates at P75

Use the 75th percentile as your estimate. This is slightly conservative, which means BudgetGovernor's forecasts will be above actual cost — giving you real headroom rather than false precision.

```python
estimated_input_tokens  = percentile(actual_input_values, 75)
estimated_output_tokens = percentile(actual_output_values, 75)
```

If the step is a loop, measure the distribution of iteration counts and set `estimated_iterations` at the P75 iteration count.

### Step 4 — Validate Against MAPE Target

After applying the calibrated estimates, run for another sprint and check `variance_analysis.mean_absolute_percentage_error` in the ledger. Target: below 15% MAPE. If it remains high, your task inputs are highly variable and you may need to stratify by customer tier or query complexity class.

### Calibration Notes for the Canonical Task Graph

Based on production data in `spend-ledger.json`:

- `issue_analysis` consistently runs over estimate for enterprise-tier customers because their account histories are longer. Consider using separate estimates per customer tier: standard (~3,500 input tokens), enterprise (~4,200 input tokens).
- `research_loop` has a 40% MAPE due to iteration unpredictability. The loop guard is the primary mitigation — do not rely on token estimate accuracy here. Instead, lower `estimated_iterations` conservatively and let the loop guard enforce the runtime ceiling.
- `context_load` and `account_lookup` are highly predictable (MAPE under 5%). Their estimates are well-calibrated.

---

## Webhook Alert Integration

BudgetGovernor posts to the `alert_webhook` in `budget-caps.json` on any warn or block decision. The payload is the gate decision object from `cost-forecast.json`.

Example payload:

```json
{
  "alert_id": "alert-20250603-114709-001",
  "session_id": "sess-d9e2f405-...",
  "condition": "task_utilization >= 100",
  "severity": "critical",
  "utilization_pct": 174.0,
  "projected_usd": 0.087,
  "cap_usd": 0.05,
  "block_reason": "projected_exceeds_cap_174_percent",
  "remediation_suggestions": [...],
  "timestamp_utc": "2025-06-03T11:47:09Z"
}
```

Configure your Slack integration to route `severity: critical` to `#ai-ops-alerts` (paging) and `severity: warn` to `#ai-ops-logs` (non-paging).

---

## Limitations

- BudgetGovernor does not observe mid-step token usage. It forecasts before and accounts after. A step that runs significantly over its token estimate will not be halted mid-step.
- Cache hit rates are assumed to be 0% in forecasts (conservative). Actual savings from prompt caching appear in the ledger as the difference between `projected_total_usd` and `actual_total_usd`.
- Novel tasks (first time a task type runs) can over- or under-shoot by 2–3x. Always run new task types in shadow mode for at least one sprint before activating gate enforcement.
- The loop guard checks before each iteration, not within an iteration. A single extremely long iteration that exceeds the token budget will still complete before the guard fires.
