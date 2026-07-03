---
name: tool-surface-auditor
description: "Audits enabled MCP servers and tool schemas against usage telemetry to produce disable/keep recommendations, reclaim standing-context tokens, and surface a config snippet ready for human review before applying."
---

**name:** tool-surface-auditor

**description:** Audits enabled MCP servers and tool schemas against usage telemetry to produce disable/keep recommendations, reclaim standing-context tokens, and surface a config snippet ready for human review before applying.


# ToolSurfaceAuditor

Audits the enabled MCP server and tool surface for an AI agent deployment.
The goal is to reclaim standing-context tokens by identifying idle tool
descriptions that consume window space every session without providing value.

## Target ceilings

| Dimension       | Ceiling |
|-----------------|---------|
| MCP servers     | ≤ 10    |
| Total tools     | ≤ 80    |

Exceeding these ceilings wastes permanent context on descriptions the model
never invokes.

---

## Audit procedure

### Step 1 — Load tool inventory

Read `input/enabled-tools.json`.  For each tool, record:

- `server` — parent MCP server name
- `name` — tool identifier
- `description_tokens` — tokens consumed by the tool's description string
- `param_schema_tokens` — tokens consumed by the JSON parameter schema
- `total_tokens` — `description_tokens + param_schema_tokens`

Compute per-server totals and the grand total.  Flag immediately if
`total_tools > tool_ceiling` or `total_servers > mcp_ceiling` from
`audit-config.json`.

### Step 2 — Load usage telemetry

Read `input/usage-telemetry.json`.  For each tool, extract:

- `calls_30d` — total calls in the last 30 days
- `calls_7d` — total calls in the last 7 days  
- `last_called` — ISO-8601 timestamp (null if never called)
- `error_rate` — fraction of calls that returned an error (0.0–1.0)
- `avg_latency_ms` — mean call latency in milliseconds

Compute a **recency_score** from `last_called`:
- Called within last 7 days → 1.0
- Called within last 30 days → 0.5
- Called more than 30 days ago → 0.1
- Never called (null) → 0.0

### Step 3 — Score each tool

```
usage_score = (calls_per_session * 0.5)
            + (recency_score     * 0.3)
            + ((1 - error_rate)  * 0.2)
```

Where `calls_per_session` is normalised to [0, 1] by dividing by the maximum
`calls_30d` value observed across all tools in the inventory.

Round to 4 decimal places.

### Step 4 — Classify every tool

| Class       | Condition                                | Action trigger       |
|-------------|------------------------------------------|----------------------|
| active      | score > 0.4                              | KEEP                 |
| occasional  | score 0.1 – 0.4 (inclusive)             | KEEP (monitor)       |
| dormant     | score 0.0 – 0.1 (exclusive), calls > 0  | FLAG FOR REVIEW      |
| never-used  | calls_30d == 0 AND last_called == null   | RECOMMEND DISABLE    |

### Step 5 — Generate recommendations

**Auto-disable candidates** (all conditions must be true):
1. Class is `never-used`
2. `calls_30d == 0`
3. `last_called == null`
4. Tool is not the sole tool in a server flagged as potentially emergency-use

**Safety rule — do NOT auto-disable** without explicit human confirmation if:
- `error_rate == 0.0` AND `calls_30d == 0` simultaneously  
  (zero errors on zero calls is ambiguous; the tool may be emergency-only and
  has simply never been needed during the telemetry window)

Mark these as `REVIEW_REQUIRED` with reason `"zero-call-zero-error: possible emergency tool"`.

**Server-level decisions:**
- If ALL tools in a server are `never-used` → recommend disabling the entire server.
- If ≥ 80 % of tools in a server are `never-used` or `dormant` → recommend
  server partial disable (enumerate tools to keep).
- If a server substantially overlaps with another (same tool categories) →
  flag for consolidation review.

### Step 6 — Produce outputs

**tool-audit-report.json**  
Array of tool objects sorted by `usage_score` descending.  Include a `summary`
block with aggregate counts and `servers` block with per-server decisions.

**disabled-mcps-config.md**  
Config snippet in two formats:

1. Environment variable (ECC_DISABLED_MCPS style):
   ```
   ECC_DISABLED_MCPS=server_a,server_b
   ECC_DISABLED_TOOLS=server_c.tool_x,server_c.tool_y
   ```

2. JSON config block for `.mcp/config.json`:
   ```json
   {
     "disabled_servers": ["server_a", "server_b"],
     "disabled_tools":   ["server_c.tool_x", "server_c.tool_y"]
   }
   ```

Human-review items are included but commented out with a `# REVIEW:` prefix
explaining the reason.

**token-impact-report.json**  
Compute:
- `total_tool_tokens_before` — grand total from inventory
- `tokens_from_disabled` — sum of `total_tokens` for all DISABLE-recommended tools
- `total_tool_tokens_after` — `before - tokens_from_disabled`
- `savings` — `tokens_from_disabled`
- `window_recovered_percentage` — `(savings / 200000) * 100`  
  (assumes 200 K-token context window as baseline)
- `cost_per_session_saved` — `savings * standing_context_per_token_cost` from config
- `monthly_savings_at_1k_sessions_per_day` — `cost_per_session_saved * 1000 * 30`

---

## Limitations

1. **Recency bias** — tools called only during incidents or seasonal peaks will
   score low during quiet telemetry windows.  Always apply the zero-call-zero-error
   safety rule before acting.

2. **Telemetry gaps** — if the telemetry window is shorter than the tool's use
   cycle (e.g., a monthly billing tool), classification will be wrong.  Check
   `audit-config.json` for the configured window length before interpreting results.

3. **Disable decisions need human confirmation** — this agent produces
   *recommendations*, not automated changes.  Paste the config snippet after
   review and staged rollout.

4. **Overlap detection is heuristic** — server consolidation suggestions are
   based on tool-name pattern matching, not semantic equivalence.  Verify before
   merging.
