# ToolSurfaceAuditor

MCP / tool footprint reduction for AI agent deployments.

Audits enabled MCP servers and tool schemas against 30-day usage telemetry.
Produces a ranked disable/keep recommendation list, a ready-to-apply config
snippet, and a projected token savings report. Designed to reclaim tens of
thousands of standing-context tokens per session by pruning idle tool
descriptions.

---

## Quick summary — what this audit found

| Metric                         | Value  |
|--------------------------------|--------|
| Servers audited                | 14     |
| Tools audited                  | 96     |
| Tool ceiling                   | 80     |
| MCP ceiling                    | 10     |
| Tools above ceiling            | 16     |
| Tools recommended for disable  | 23     |
| Tools flagged for human review | 8      |
| Tokens reclaimed (confirmed)   | 34,200 |
| Window recovered               | 17.1%  |
| Monthly cost saving (1K/day)   | $3,078 |

---

## Repository structure

```
skills/ToolSurfaceAuditor/
├── SKILL.md                          # Agent instructions and scoring formula
├── README.md                         # This file
├── input/
│   ├── enabled-tools.json            # Inventory of all 14 MCP servers and 96 tools
│   ├── usage-telemetry.json          # 30-day call counts, recency, error rates
│   └── audit-config.json             # Ceilings, thresholds, cost parameters
└── output/
    ├── tool-audit-report.json        # Full ranked tool list with scores and decisions
    ├── disabled-mcps-config.md       # Config snippets ready for human application
    └── token-impact-report.json      # Before/after token counts and cost projections
```

---

## How to run the audit

### Prerequisites

- Claude Code with the `claude-haiku-4-5` model available
- Usage telemetry exported from your observability system (see section below)
- `input/enabled-tools.json` updated to match your current MCP configuration

### Running the agent

```sh
# From the optimization project root
claude -p "Run the ToolSurfaceAuditor skill using the inputs in
skills/ToolSurfaceAuditor/input/ and write updated outputs to
skills/ToolSurfaceAuditor/output/"
```

Or invoke via the skill system:

```sh
/ToolSurfaceAuditor
```

The agent will:
1. Read all three input files
2. Compute usage scores for all 96 tools
3. Classify each tool (active / occasional / dormant / never-used)
4. Apply the zero-call-zero-error safety rule
5. Write updated versions of all three output files

### Updating the tool inventory

When MCP servers are added or removed, update `input/enabled-tools.json`:

```json
{
  "server": "my_new_server",
  "description": "What this server does",
  "status": "enabled",
  "tools": [
    {
      "name": "tool_name",
      "description": "What the tool does",
      "description_tokens": 38,
      "param_schema_tokens": 72,
      "total_tokens": 110
    }
  ]
}
```

To count tokens accurately, use the tokenizer for your model:

```python
import anthropic

client = anthropic.Anthropic()

def count_tokens(text: str) -> int:
    # Use the Messages API token counting endpoint
    response = client.messages.count_tokens(
        model="claude-haiku-4-5",
        messages=[{"role": "user", "content": text}]
    )
    return response.input_tokens
```

---

## How to collect usage telemetry

The agent expects `input/usage-telemetry.json` with 30-day call data per tool.

### Option 1: From your observability platform

If you use Datadog, Grafana, or a similar platform, export tool-call metrics:

```sql
-- Example: PostgreSQL query if tool calls are logged to a database
SELECT
    server_name,
    tool_name,
    COUNT(*) FILTER (WHERE called_at >= NOW() - INTERVAL '30 days') AS calls_30d,
    COUNT(*) FILTER (WHERE called_at >= NOW() - INTERVAL '7 days')  AS calls_7d,
    MAX(called_at)                                                   AS last_called,
    AVG(CASE WHEN status = 'error' THEN 1.0 ELSE 0.0 END)           AS error_rate,
    AVG(latency_ms)                                                  AS avg_latency_ms
FROM tool_call_log
GROUP BY server_name, tool_name
ORDER BY calls_30d DESC;
```

### Option 2: From Claude API request logs

If you use the Anthropic API directly, tool calls appear in the `content`
array of assistant messages with `type: "tool_use"`. Extract them from
your request logs:

```python
import json
from collections import defaultdict
from datetime import datetime, timedelta

def extract_telemetry(log_lines: list[str], window_days: int = 30) -> dict:
    """Parse JSONL API request logs and compute tool-call telemetry."""
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    tool_stats = defaultdict(lambda: {
        "calls_30d": 0, "calls_7d": 0,
        "last_called": None, "errors": 0,
        "latencies": []
    })
    cutoff_7d = datetime.utcnow() - timedelta(days=7)

    for line in log_lines:
        record = json.loads(line)
        ts = datetime.fromisoformat(record["timestamp"])
        if ts < cutoff:
            continue
        for msg in record.get("response", {}).get("content", []):
            if msg.get("type") != "tool_use":
                continue
            key = f"{msg['server']}.{msg['name']}"
            tool_stats[key]["calls_30d"] += 1
            if ts >= cutoff_7d:
                tool_stats[key]["calls_7d"] += 1
            if tool_stats[key]["last_called"] is None or ts > datetime.fromisoformat(tool_stats[key]["last_called"]):
                tool_stats[key]["last_called"] = ts.isoformat() + "Z"
            if record.get("tool_result", {}).get("is_error"):
                tool_stats[key]["errors"] += 1
            if "latency_ms" in record:
                tool_stats[key]["latencies"].append(record["latency_ms"])

    result = []
    for key, stats in tool_stats.items():
        server, name = key.split(".", 1)
        calls = stats["calls_30d"]
        result.append({
            "server": server,
            "name": name,
            "calls_30d": calls,
            "calls_7d": stats["calls_7d"],
            "last_called": stats["last_called"],
            "error_rate": round(stats["errors"] / calls, 4) if calls > 0 else 0.0,
            "avg_latency_ms": round(sum(stats["latencies"]) / len(stats["latencies"])) if stats["latencies"] else None
        })

    return {"tools": sorted(result, key=lambda x: x["calls_30d"], reverse=True)}
```

### Option 3: Zero-call stub (first audit)

If you have no telemetry yet, run the audit with all tools set to zero calls.
This identifies which servers and tools are structurally unnecessary (e.g.,
developer_tools_server in production) before any runtime data is available.

```sh
# Generate a zero-telemetry stub
python3 -c "
import json

with open('input/enabled-tools.json') as f:
    inventory = json.load(f)

tools = []
for server in inventory['servers']:
    for tool in server['tools']:
        tools.append({
            'server': server['server'],
            'name': tool['name'],
            'calls_30d': 0,
            'calls_7d': 0,
            'last_called': None,
            'error_rate': 0.0,
            'avg_latency_ms': None
        })

print(json.dumps({'tools': tools}, indent=2))
" > input/usage-telemetry.json
```

---

## Safe workflow for applying disable decisions

Disabling MCP tools in production removes them from every subsequent session's
context window. Follow this staged rollout to avoid breaking workflows.

### Step 1 — Apply in staging

Add the config snippet from `output/disabled-mcps-config.md` to your staging
environment first:

```sh
# Set environment variables in staging
export ECC_DISABLED_MCPS="developer_tools_server,legacy_crm_server,testing_server"
export ECC_DISABLED_TOOLS="analytics_server.generate_weekly_report,..."

# Restart the agent service
systemctl restart customer-service-agent
```

### Step 2 — Run smoke tests

Confirm that the 10 most-used tools still work correctly in staging:

- lookup_customer (crm_server)
- search_articles (knowledge_base_server)
- get_customer_history (database_server)
- escalate_to_human (escalation_server)
- send_notification (email_server)

### Step 3 — Monitor for 24 hours

Watch your error rate and escalation metrics in staging. A spike in
`escalate_to_human` calls after disabling tools is a signal that a tool was
needed after all.

### Step 4 — Apply to production

Once staging is stable, apply the same config to production:

```sh
# JSON config approach (.mcp/config.json)
cat > .mcp/config.json << 'EOF'
{
  "disabled_servers": [
    "developer_tools_server",
    "legacy_crm_server",
    "testing_server"
  ],
  "disabled_tools": [
    "analytics_server.generate_weekly_report",
    "analytics_server.generate_monthly_report",
    "analytics_server.export_to_data_warehouse",
    "analytics_server.get_agent_scorecard",
    "analytics_server.get_topic_distribution",
    "analytics_server.get_channel_mix",
    "analytics_server.get_handle_time_histogram",
    "analytics_server.run_cohort_analysis",
    "analytics_server.get_sentiment_trend",
    "analytics_server.trigger_ad_hoc_query"
  ]
}
EOF
```

### Step 5 — Handle human-review items

For each item in Section 2 of `disabled-mcps-config.md`, complete the
checklist and add approved items to `disabled_servers` or `disabled_tools`
in a follow-up config update.

### Step 6 — Re-run the audit

After applying changes, re-run the ToolSurfaceAuditor with updated telemetry
to confirm token counts and verify no new drift has occurred.

Recommended audit cadence: **monthly** or whenever a new MCP server is added.

---

## Rollback

If a disable decision turns out to be wrong, remove the server or tool from
the disable list and restart the agent:

```sh
# Remove a server from the disabled list
# Edit .mcp/config.json and remove the entry, then:
systemctl restart customer-service-agent
```

Tool descriptions are stateless — re-enabling a server immediately restores
its tools to the context window on the next session.

---

## Limitations

- **Recency bias**: Tools called only during incidents or low-traffic periods
  will under-score during quiet telemetry windows. Always review the
  zero-call-zero-error items before acting.

- **Telemetry window**: If a tool's natural call cycle is longer than 30 days
  (e.g., a monthly billing report), it will appear as `dormant` or
  `never-used`. Check the `audit-config.json` window setting against known
  tool use patterns.

- **Overlap detection is heuristic**: Consolidation suggestions are based on
  tool-name pattern matching. Verify semantic equivalence before merging servers.

- **Does not assess tool quality**: This audit measures frequency of use, not
  whether the tool is doing the right thing. A high-usage tool with a high
  error rate (see `translate_template` at 25%) still needs investigation.
