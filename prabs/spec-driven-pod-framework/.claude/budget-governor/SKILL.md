---
name: budget-governor
description: "Deterministic cost accounting for AI agent pipelines. Loads a task graph with"
---

**name:** budget-governer

**description:** Deterministic cost accounting for AI agent pipelines. Loads a task graph with
per-step model and I/O token estimates, computes projected cost against live
pricing, compares projections against tiered budget caps, and emits a gate
decision (proceed / warn / block) before any tokens are spent. Maintains a
running spend ledger for POD Lead visibility. No LLM required — pure arithmetic.


# BudgetGovernor

## What It Does

BudgetGovernor enforces token and dollar budgets on AI agent task graphs **before** execution begins and **at every loop iteration** during execution. It prevents surprise bills and runaway agentic loops by:

1. Computing a deterministic cost forecast from the task graph
2. Comparing the projection against tiered caps (task / session / sprint)
3. Emitting a **gate decision**: `proceed`, `warn`, or `block`
4. On block, identifying the highest-cost steps and suggesting model downgrades
5. Maintaining a running spend ledger updated after each completed step

No LLM is needed. All logic is arithmetic.

---

## Pricing Table (Claude API, USD per million tokens)

> Reference these prices when computing step costs. Update when Anthropic revises pricing.

| Model | Input ($/MTok) | Output ($/MTok) | Cache Read ($/MTok) |
|---|---|---|---|
| claude-haiku-4-5 | $0.80 | $4.00 | $0.08 |
| claude-sonnet-4-6 | $3.00 | $15.00 | $0.30 |
| claude-opus-4-7 | $15.00 | $75.00 | $1.50 |

Cache write pricing is charged at the same rate as normal input tokens for all models.

---

## Accounting Algorithm (Deterministic — No LLM)

### Step 1 — Load the Task Graph

Read `input/task-graph.json`. Extract per-step fields:
```
step_id, model, estimated_input_tokens, estimated_output_tokens,
is_optional, depends_on, estimated_iterations (if present)
```

For looping steps (e.g., `research_loop`), multiply token estimates by `estimated_iterations` to get the worst-case projection.

```
effective_input_tokens  = estimated_input_tokens  * max(1, estimated_iterations)
effective_output_tokens = estimated_output_tokens * max(1, estimated_iterations)
```

### Step 2 — Compute Cost Per Step

Look up `input_price` and `output_price` from `input/pricing-table.json` using the step's `model` field.

```
input_cost_usd  = (effective_input_tokens  / 1_000_000) * input_price
output_cost_usd = (effective_output_tokens / 1_000_000) * output_price
step_total_usd  = input_cost_usd + output_cost_usd
```

Round to 6 decimal places for precision. Dollar display rounds to 4.

### Step 3 — Roll Up Totals

Sum all mandatory steps (where `is_optional == false`) for the primary projection. Compute a secondary "worst-case" projection that includes optional steps.

```
task_total_usd    = sum(step_total_usd for all mandatory steps)
task_worst_usd    = sum(step_total_usd for all steps including optional)
session_total_usd = task_total_usd + sum(prior_tasks_in_session)
sprint_total_usd  = session_total_usd + sum(prior_sessions_in_sprint)
```

### Step 4 — Compare Against Caps

Load `input/budget-caps.json`. Compute utilization percentages:

```
task_utilization_pct    = (task_total_usd    / task_cap_usd)    * 100
session_utilization_pct = (session_total_usd / session_cap_usd) * 100
sprint_utilization_pct  = (sprint_total_usd  / sprint_cap_usd)  * 100
```

### Step 5 — Gate Decision Logic

Evaluate the **most constrained** cap (highest utilization percentage):

```
if   utilization_pct <= 80:  gate = "proceed"
elif utilization_pct <= 100: gate = "warn"
else:                        gate = "block"
```

The gate decision uses the **highest utilization** across all cap levels (task, session, sprint). A single cap breach blocks the entire run.

Report `budget_headroom` for each level:
```
headroom = cap_usd - projected_total_usd
```

### Step 6 — On Block: Identify Remediation Options

When `gate == "block"`, compute savings available from each high-cost step:

1. Sort steps by `step_total_usd` descending.
2. For each of the top N steps (N = 3 by default):
   a. Find the next cheaper model in the tier ladder (Opus → Sonnet → Haiku).
   b. Re-compute `step_total_usd` with the downgraded model's pricing.
   c. `savings_usd = original_step_total - downgraded_step_total`
3. Also evaluate loop iteration reduction:
   - Suggest reducing `estimated_iterations` to the originally planned value if actual exceeds it.
   - `iteration_savings = cost_at_actual_iterations - cost_at_planned_iterations`

Report `remediation_suggestions` as an ordered list (highest savings first).

### Step 7 — Emit Gate Decision and Update Ledger

Write `output/cost-forecast.json` with full per-step breakdown, rollups, utilization percentages, gate decision, and (on block) remediation suggestions.

Append a new entry to `output/spend-ledger.json`:
```json
{
  "session_id": "<uuid>",
  "timestamp_utc": "<iso8601>",
  "task_id": "<task_id>",
  "gate_decision": "<proceed|warn|block>",
  "projected_cost_usd": <float>,
  "actual_cost_usd": null
}
```

`actual_cost_usd` is populated by the runtime after execution completes (not BudgetGovernor's responsibility to fill).

---

## Customer Service Chatbot — Canonical Task Graph

For the reference implementation (React + FastAPI + PostgreSQL + Salesforce CRM), a customer service session consists of the following steps in dependency order:

```
session_init
    └── context_load
            └── intent_classification
                    ├── account_lookup
                    │       └── issue_analysis
                    │               ├── response_generation   ← primary path
                    │               ├── research_loop         ← optional, risky
                    │               └── crm_update
                    │                       ├── ticket_creation    ← optional
                    │                       └── email_notification ← optional
                    └── session_close
```

**Model assignment rationale:**
- `session_init`, `session_close`: No model needed (infra calls, $0.00)
- `context_load`: Haiku — simple retrieval formatting, low I/O
- `intent_classification`: Haiku — classification prompt, short output
- `account_lookup`: Haiku — structured data extraction from CRM JSON
- `issue_analysis`: Sonnet — requires reasoning over account history
- `response_generation`: Sonnet — customer-facing output must be high quality
- `research_loop`: Sonnet — iterative KB search; capped at 5 iterations by default
- `crm_update`: Haiku — structured JSON write to Salesforce
- `ticket_creation`: Haiku — form-fill task
- `email_notification`: Haiku — template fill

**Normal session cost target:** $0.034 mandatory, $0.082 including all optional steps.
**Cap:** $0.05 per task, $0.15 per session.

---

## Loop Guard Protocol

`research_loop` is the primary runaway risk. BudgetGovernor applies a pre-flight check:

1. Before each iteration, re-evaluate `current_projected_cost` = completed_spend + remaining_iterations * per_iteration_cost
2. If `current_projected_cost` would breach `task_cap_usd`, halt the loop immediately and emit `gate = "block"` with `halt_reason: "loop_runaway_detected"`
3. Log actual iteration count vs. planned in the ledger for calibration

---

## Integration Points

- **ModelRouter**: On `gate == "warn"`, BudgetGovernor passes remediation_suggestions to ModelRouter, which can transparently downgrade models for remaining steps without human intervention.
- **Webhook alerts**: When utilization exceeds `warn_threshold_percentage`, POST the gate decision JSON to `alert_webhook` defined in `budget-caps.json`.
- **Spend ledger**: POD Lead reads `output/spend-ledger.json` for daily/sprint visibility. The ledger is append-only; never mutate existing entries.

---

## Limitations

- Forecast accuracy is bounded by the quality of upstream I/O estimates in `task-graph.json`. Novel tasks (first time a task type runs) can over- or under-shoot by 2–3x.
- BudgetGovernor does not observe actual token usage mid-step. Actual cost is reconciled post-step by the runtime.
- Cache hit rates are not predicted (conservative: assume 0% cache hits in forecasts). Actual savings from caching are captured in the ledger as `actual_cost_usd` vs. `projected_cost_usd`.
