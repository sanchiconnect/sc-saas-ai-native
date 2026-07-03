---
name: memory-persistence
description: "Saves session state at session end and rehydrates a capped digest at session start, preserving decisions, commitments, and unresolved work while preventing context bloat and excluding sensitive data."
---

**name:** memory-persistence

**description:** Saves session state at session end and rehydrates a capped digest at session start, preserving decisions, commitments, and unresolved work while preventing context bloat and excluding sensitive data.


# MemoryPersistence Skill

This skill runs at two lifecycle points — session end and session start — to create
continuity across Claude Code sessions without rebuilding context from scratch each time.

---

## MODE 1 — SAVE (Stop Hook)

**Trigger:** Fired automatically when the Claude Code session ends (`Stop` hook).

### What to Extract

Scan the session transcript and working context to identify:

| Field | Description | Example |
|---|---|---|
| `active_task` | The primary task in progress when session ended | "Debugging ticket TKT-9871 in billing queue" |
| `open_decisions` | Decisions pending human approval or system action | `["approve_refund_CS78234", "escalate_to_fraud_team_CS91045"]` |
| `unresolved_threads` | Work streams started but not completed | Case CS78234 pending supervisor callback |
| `key_entity_ids` | IDs needed to resume work (ticket IDs, case numbers, customer refs) | `["CS78234", "CS91045", "TKT-9871"]` |
| `constraints` | Rules or limits discovered this session that affect future actions | "Billing API rate-limited after 50 req/min" |
| `commitments_made` | Promises made to customers or stakeholders with deadlines | Refund to Sarah Chen by Dec 4 |
| `tools_state` | Last known state of external tools (NOT tokens; status only) | Salesforce sync lag detected |

### What to NEVER Persist

The following must be explicitly scrubbed before writing session-state.json:

- `auth_tokens` / `session_cookies` — rotate each session, never carry over
- `customer_passwords` / `credit_card_numbers` / `SSN` — PII, use IDs instead
- Raw API responses larger than 500 chars — summarize, do not dump
- Temporary file paths that will not exist next session

### Serialization Format

```json
{
  "version": "1.2",
  "schema": "session-state/v1",
  "session_id": "<sess-YYYY-MMDD-HHMM>",
  "agent_id": "<agent-id>",
  "saved_at": "<ISO-8601>",
  "session_duration_minutes": <int>,
  "state": {
    "active_task": "<string>",
    "active_cases": [ /* structured case objects */ ],
    "commitments": [ /* structured commitment objects with deadlines */ ],
    "open_decisions": [ /* decision IDs with context */ ],
    "constraints": [ /* discovered constraints */ ],
    "context_notes": [ /* freeform observations */ ],
    "key_entity_ids": { /* categorized ID maps */ }
  },
  "metadata": {
    "state_complexity": "low|medium|high",
    "model_used": "claude-haiku-4-5|claude-sonnet-4-6",
    "estimated_chars": <int>,
    "open_thread_count": <int>,
    "interdependency_count": <int>
  }
}
```

### Model Escalation Logic

Start with `claude-haiku-4-5`. Escalate to `claude-sonnet-4-6` if ANY of the following:

- `open_thread_count > 3` — multiple parallel work streams are harder to compress faithfully
- `interdependency_count > 2` — threads that affect each other require nuanced summarization
- `state_complexity == "high"` — explicitly flagged by prior session or by heuristic scan
- Any commitment has a deadline within 12 hours — high-stakes accuracy required

Escalation adds ~4K tokens but produces significantly more reliable state for complex sessions.
Use it when dropping a detail would cause real downstream harm (missed SLA, dropped callback).

### Customer Service Chatbot — Domain-Specific Fields

For the CS chatbot, always capture:

```json
"active_cases": [
  {
    "case_id": "CS<number>",
    "customer_name": "<name>",
    "issue_summary": "<1-sentence>",
    "status": "pending_callback|pending_department|escalated|awaiting_approval",
    "next_action": "<what needs to happen>",
    "next_action_owner": "supervisor|billing|fraud_team|agent",
    "sla_deadline": "<ISO-8601 or null>"
  }
],
"pending_callbacks": [
  {
    "customer_name": "<name>",
    "scheduled_time": "<ISO-8601>",
    "case_id": "<CS-id>",
    "callback_number": null
  }
],
"escalations_in_progress": [
  {
    "case_id": "<CS-id>",
    "escalated_to": "<team>",
    "escalated_at": "<ISO-8601>",
    "reason": "<string>"
  }
]
```

---

## MODE 2 — REHYDRATE (SessionStart Hook)

**Trigger:** Fired automatically at the start of a new Claude Code session (`SessionStart` hook).

### Load and Validate

1. Locate `session-state.json` for `agent_id` in the persistent store path (default: `.claude/memory/<agent_id>/session-state.json`).
2. Check `saved_at` against current timestamp:
   - `< 24h` → state is **fresh**, load normally
   - `24h – 168h` → state is **potentially_stale**, include staleness warning in rehydration block
   - `> 168h (7 days)` → state is **stale**, flag prominently and reduce confidence weighting on cached details
3. Validate schema version — if `version < 1.0`, reject and log a warning rather than injecting malformed state.

### Build the Capped Context Block

Default cap: **6000 chars** (configurable via `rehydration-config.json`).

Fill the context block using this priority order — highest priority is included first,
lowest is truncated if the cap is reached:

1. **commitments** — Promises with deadlines. Missing these causes real-world failures.
2. **open_decisions** — Decisions awaiting action. Losing these causes duplicated work.
3. **active_task** — The primary task in flight. Needed for immediate resumption.
4. **constraints** — Discovered limits and rules. Prevents re-hitting known walls.
5. **context_notes** — Background observations. Lowest priority; drop first if over cap.

When truncation occurs:
- Log which items were dropped to `persistence-log.json`
- Add a note in the rehydration block: `[N lower-priority items truncated to stay within 6000-char cap]`

### Inject as First System Message

The rehydration block must be the **first** content in the new session context window,
before any user message or tool description. Format it as Markdown for readability.

### Staleness Detection

```
state_age = current_time - saved_at (in hours)

if state_age < 24:
    staleness_status = "fresh"
    staleness_label  = null

elif state_age < 168:
    staleness_status = "potentially_stale"
    staleness_label  = "⚠ State is {age}h old — verify before acting on cached details"

else:
    staleness_status = "stale"
    staleness_label  = "STALE STATE ({age}h old) — treat all cached values as unverified"
```

Items from prior sessions that are older than 24h should carry inline staleness markers
so the agent can distinguish fresh vs. aged information within a single rehydration block.

---

## Persistence Store Layout

```
.claude/memory/
  <agent_id>/
    session-state.json        # Current (latest) snapshot
    session-history/
      sess-YYYY-MMDD-HHMM.json  # Archived prior sessions (keep last 10)
    persistence-log.json      # Audit log of all save/rehydrate events
```

For multi-agent projects, each agent maintains its own subtree. Shared state
(e.g., a global decision log) can be placed at `.claude/memory/shared/`.

---

## Operational Notes

- **Token budget:** SAVE mode uses ~3K tokens on Haiku, ~7K on Sonnet when escalated.
  REHYDRATE uses ~1K tokens to build the context block (most is template fill).
- **Idempotency:** Running SAVE twice in the same session overwrites the snapshot;
  the previous version is moved to `session-history/` before overwrite.
- **No-op conditions:** If session produced no new decisions or state changes, SAVE
  writes a minimal heartbeat record (`{"session_id": ..., "no_changes": true}`) rather
  than duplicating unchanged state.
