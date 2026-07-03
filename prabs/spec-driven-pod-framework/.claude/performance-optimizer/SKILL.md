---
name: performance-optimizer
description: "PerformanceOptimizer enforces intelligent model routing and sprint token budget compliance. Its dual function is: 1."
---

# PerformanceOptimizer — SKILL.md
## SpecPod Build Phase · Agent B-08
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~20K

---

## Purpose
PerformanceOptimizer enforces **intelligent model routing and sprint token budget compliance**. Its dual function is:
1. **Route each generation task to the optimal model** — matching task complexity to model capability, preventing the default failure mode of routing everything to Opus/GPT-4 regardless of task complexity
2. **Enforce the sprint token budget** — monitoring cumulative spend in real time, alerting at 80% threshold, and recommending cost-reduction interventions before the budget is exhausted

For a 2-builder team, routing simple extraction tasks to Haiku instead of Opus cuts per-task cost by 75–90% with no quality loss. This can expand effective capacity by 3–4× within the same sprint token budget.

---

## Activation Triggers
- Before any generation task is dispatched to a model (routing decision)
- Token budget threshold crossed (80% consumption alert)
- POD Lead requests a sprint cost dashboard
- End-of-sprint: generate token consumption report for budget calibration
- Explicit invocation: *"route this task"*, *"check budget status"*, *"run PerformanceOptimizer"*

---

## Inputs

| Input | Source | Role |
|-------|--------|------|
| `artifacts/task-breakdown.yaml` | Phase 3 | Task list with complexity tags and context size estimates |
| `artifacts/openspec.yaml` | Phase 3 | NFR latency targets per feature |
| `artifacts/sprint-capacity.yaml` | POD Lead | Sprint token budget (total tokens allocated for the sprint) |
| Live token consumption | Per-agent tracking | Running total tokens consumed by each agent and builder |
| PromptBench results | B-06 | Model quality/cost profiles per task type (after first few sprints) |

---

## Processing Logic

### Step 1 — Task Profiling
For each incoming generation task, classify it on three dimensions:

**Complexity:**
| Level | Criteria | Description |
|-------|---------|-------------|
| LOW | Single-step, deterministic output | Data extraction, format conversion, simple classification |
| MEDIUM | Multi-step, structured output | Code generation for defined spec, JSON extraction with validation |
| HIGH | Reasoning-intensive, long context | Complex code generation, architectural analysis, multi-constraint problem |

**Context Size:**
| Level | Input tokens | Description |
|-------|-------------|-------------|
| SMALL | < 5K tokens | Single file or short spec section |
| MEDIUM | 5K–20K tokens | Multiple files or full spec section |
| LARGE | > 20K tokens | Full spec + codebase context |

**Output Type:**
- `CODE` — executable code with correctness requirements
- `STRUCTURED` — JSON/YAML with schema requirements
- `ANALYSIS` — reasoning output, design review, conformance check
- `EXTRACTION` — data pulled from context (low hallucination tolerance)

### Step 2 — Model Routing Decision

| Complexity | Context | Output Type | Recommended Model |
|------------|---------|-------------|------------------|
| LOW | SMALL | EXTRACTION | claude-haiku-4-5 |
| LOW | SMALL | STRUCTURED | claude-haiku-4-5 |
| LOW | MEDIUM | EXTRACTION | claude-haiku-4-5 |
| MEDIUM | SMALL | CODE | claude-haiku-4-5 |
| MEDIUM | MEDIUM | CODE | claude-sonnet-4 |
| MEDIUM | MEDIUM | ANALYSIS | claude-sonnet-4 |
| MEDIUM | LARGE | CODE | claude-sonnet-4 |
| HIGH | MEDIUM | CODE | claude-sonnet-4 |
| HIGH | LARGE | CODE | claude-sonnet-4 |
| HIGH | LARGE | ANALYSIS | claude-sonnet-4 (or claude-opus-4 if NFR demands) |

**OpenAI routing:** Apply equivalent routing logic using gpt-4o-mini (≈ Haiku), gpt-4o (≈ Sonnet), o3 (≈ Opus) if the builder's workflow uses OpenAI models.

**Override:** If `openspec.yaml` NFR specifies `quality_tier: premium` for a feature, escalate one model tier regardless of task profile.

### Step 3 — Budget Monitoring
Maintain running totals:
```
sprint_budget_total:      [from sprint-capacity.yaml]
sprint_consumed:          [sum of all agent token usage]
sprint_remaining:         budget_total - sprint_consumed
consumption_rate:         sprint_consumed / elapsed_sprint_days
projected_total:          sprint_consumed + (consumption_rate × remaining_days)
budget_risk:              projected_total / sprint_budget_total
```

Alert thresholds:
- **80% consumed** → Alert POD Lead with projected overrun estimate + cost reduction recommendations
- **95% consumed** → Force route all remaining tasks to Haiku unless explicitly overridden
- **100% consumed** → Block further LLM calls; require POD Lead intervention

### Step 4 — Cost Reduction Recommendations
When budget risk > 1.0 (projected overrun), recommend:
1. Identify highest-cost tasks remaining in `task-breakdown.yaml`
2. For each, check if a lower-tier model could handle it (cross-reference PromptBench results if available)
3. Recommend prompt compression for tasks with LARGE context (trim to essential chunks)
4. Flag any tasks that could be deferred to next sprint

---

## Elicitation Protocol

1. *"What is the sprint token budget? (From `sprint-capacity.yaml`, in tokens or USD equivalent)"*
2. *"Which model providers are in scope? (Anthropic only, OpenAI only, or both?)"*
3. *"For this routing decision: what task type is it? (code generation / analysis / extraction / structured output)"*
4. *"Are there any features with a `quality_tier: premium` NFR that must use a higher-tier model regardless of cost?"*

---

## Outputs

### Routing Decision (per task)
```yaml
task_id: "TASK-042"
routing_decision:
  recommended_model: "claude-haiku-4-5-20251001"
  rationale: "MEDIUM complexity / SMALL context / STRUCTURED output — Haiku sufficient"
  estimated_tokens: 2800
  estimated_cost_usd: 0.0034
  nfr_override: false
```

### Token Consumption Dashboard (on demand / at 80% alert)
```markdown
# Sprint Token Budget Dashboard
**Sprint:** SP-007 | **Updated:** 2025-09-17 11:30

| Metric | Value |
|--------|-------|
| Budget | 2,000,000 tokens ($6.40) |
| Consumed | 1,640,000 tokens (82%) |
| Remaining | 360,000 tokens |
| Consumed today | 480,000 tokens |
| Projected total | 2,280,000 tokens (114% — OVERRUN RISK) |

⚠️ ALERT: Budget at 82%. Projected 14% overrun.

## Cost Reduction Recommendations
1. TASK-047 (architecture analysis): Route to claude-haiku-4-5 — estimated saving: 35K tokens
2. TASK-051 (data extraction × 8 tasks): Route batch to claude-haiku-4-5 — estimated saving: 120K tokens
3. TASK-049 context: Trim KnowledgeMesh chunks from 5 to 3 per query — estimated saving: 18K tokens

## Per-Agent Consumption
| Agent | Tokens Used | % of Total |
|-------|------------|-----------|
| DevCopilot (Builder-1) | 820,000 | 50% |
| DevCopilot (Builder-2) | 560,000 | 34% |
| ReviewPilot | 180,000 | 11% |
| KnowledgeMesh | 80,000 | 5% |
```

### `token-consumption-report.yaml` (end of sprint — feeds next sprint's budget calibration)
Full per-agent, per-task, per-model token consumption log.

---

## Limitations & Escalation
- **Model routing heuristics are task-type-based**, not outcome-based. After 2–3 sprints with PromptBench data, routing accuracy improves significantly as per-task-type quality/cost profiles become empirically calibrated.
- Does not control model selection inside third-party tools (e.g. Cursor's internal model calls). Budget tracking covers agent-level API calls only.
- Budget tracking requires agents to report token usage. If an agent fails to report, consumption estimates will be inaccurate.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| DevCopilot | Upstream | Receives routing decision before each generation call |
| PromptBench | Upstream | Receives benchmark results to calibrate routing heuristics |
| All agents | Reports from | Receives token consumption reports |
| Conductor | Reports to | Budget status fed into sprint board |

---

## References
- `references/routing-matrix.md` — Full routing decision matrix with edge cases
- `references/budget-calibration.md` — How to set sprint token budgets based on historical data
- `sample_input/sample-sprint-capacity.yaml` — Example sprint capacity file
- `sample_output/sample-routing-decisions.yaml` — Example routing decisions for a sprint
