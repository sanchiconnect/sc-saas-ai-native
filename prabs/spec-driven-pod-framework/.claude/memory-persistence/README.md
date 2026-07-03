# MemoryPersistence

Cross-session state save and rehydrate for Claude Code agents. Eliminates the cold-start
re-explanation tax by serializing working context on session end and injecting a capped
digest on the next session start.

---

## How to Hook into Claude Code Stop / SessionStart Events

MemoryPersistence runs on two lifecycle hooks that Claude Code fires automatically.

### settings.json configuration

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "claude --skill MemoryPersistence --mode save --agent-id cs-agent-007"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "claude --skill MemoryPersistence --mode rehydrate --agent-id cs-agent-007"
          }
        ]
      }
    ]
  }
}
```

The `matcher` field can be left empty to fire on every session, or scoped to a project
directory pattern (e.g., `"matcher": "customer-service"`) to restrict the hook to sessions
in matching directories.

### Manual invocation (for testing)

```bash
# Force a save from current session state
claude /MemoryPersistence --mode save --agent-id cs-agent-007

# Rehydrate and print the context block without injecting it
claude /MemoryPersistence --mode rehydrate --agent-id cs-agent-007 --dry-run
```

### Verifying the hook is running

Check `.claude/memory/cs-agent-007/persistence-log.json` after a session ends.
A `save_event` entry with `"status": "success"` confirms the Stop hook fired correctly.

---

## What to Persist vs. What to Leave Out

### Always persist

| Category | Examples | Why |
|---|---|---|
| Active case IDs | `CS78234`, `TKT-9871` | Opaque references, needed to resume work |
| Customer names | `Sarah Chen` | Required for callbacks and commitments |
| Deadlines and SLAs | `2024-12-04T17:00:00Z` | Missing these causes real-world SLA breaches |
| Open decisions | Pending approvals, escalation gates | Dropping these causes duplicated discovery work |
| Discovered constraints | API rate limits, policy rules | Prevents re-hitting known walls |
| Tool status summaries | "Salesforce CRM: sync lag detected" | Actionable at next session start |

### Never persist

| Field type | Why | What to store instead |
|---|---|---|
| Auth tokens / session cookies | Rotate each session; stale tokens cause auth failures | Nothing — re-authenticate at runtime |
| Customer passwords | PII; storing them is a security violation | Account ID only |
| Credit card numbers | PCI-DSS; never log these | Last 4 digits if needed for reference |
| SSN / passport / license numbers | PII; potential regulatory liability | Customer account ID |
| Raw API responses > 500 chars | Bloats state, may contain embedded tokens | Summarize the outcome |
| Temp file paths | Will not exist next session | The logical outcome the file represented |
| OAuth tokens / JWTs | Short-lived; dangerous if persisted | Re-fetch from auth service at session start |

### PII handling for customer service agents

Customer names are permitted because they are needed for callbacks and commitments.
Everything else identifying (email, phone, address) should be stored as an account ID
and retrieved from the CRM at session start when needed. This limits the blast radius
if the state store is ever read by an unauthorized process.

The `never_persist` list in `rehydration-config.json` is the enforcement mechanism —
the SAVE mode scrubs any field matching those names before writing to disk.

---

## Managing State Across Multiple Agents in the Same Project

Each agent maintains its own subtree under `.claude/memory/`:

```
.claude/memory/
  cs-agent-007/
    session-state.json
    session-history/
    persistence-log.json
  cs-agent-008/
    session-state.json
    ...
  shared/
    project-decisions.json
    escalation-registry.json
```

### Shared state

For decisions or constraints that span agents (e.g., a system-wide outage notice,
or a cross-agent escalation), write to `.claude/memory/shared/`. Each agent's SAVE
mode checks `shared/` and includes relevant shared-state items in its own rehydration
block without duplicating the full store.

Shared state follows the same staleness rules as per-agent state. The agent that
writes a shared item sets its `owner_agent_id` so other agents know where the
canonical version lives.

### Avoiding write conflicts

If multiple agents run simultaneously, use advisory locking before writing
`session-state.json`:

```bash
# SAVE mode uses a lockfile per agent
flock .claude/memory/cs-agent-007/session-state.lock \
  claude --skill MemoryPersistence --mode save --agent-id cs-agent-007
```

The lock is held only for the duration of the file write (typically < 100ms).

### Cross-agent handoffs

When one agent hands a case to another (e.g., a tier-1 agent escalating to a
specialist), the source agent should write a handoff record to `shared/`:

```json
{
  "handoff_id": "HO-20241203-001",
  "from_agent": "cs-agent-007",
  "to_agent": "cs-specialist-002",
  "case_ids": ["CS91045"],
  "handoff_at": "2024-12-03T17:22:00Z",
  "context_summary": "Suspicious $249 charge — awaiting fraud team determination",
  "commitments_transferred": ["CMT-002"]
}
```

The receiving agent's REHYDRATE mode picks this up and includes it in its next
session's context block.

---

## Handling State Drift When Underlying Systems Change

State drift occurs when the codebase, external system, or data model changes between
sessions, making cached state inconsistent with the new reality.

### Common drift scenarios

| Scenario | Symptom | Detection |
|---|---|---|
| CRM migration or schema change | Cached case IDs return 404 | `key_entity_ids` lookups fail at session start |
| Policy update (e.g., refund threshold changes) | Constraints are now wrong | Constraint `policy_reference` is outdated |
| Customer data correction | Cached customer name differs from CRM | Name mismatch on CRM lookup |
| Case closed by another agent | Persisted "open" case is already resolved | Status check returns closed |
| System outage resolved | Cached "degraded" tool status is now operational | Fresh health check disagrees with persisted status |

### Drift detection strategy

At REHYDRATE time, after building the context block, run a lightweight verification pass:

1. **Entity ID validation:** For each ID in `key_entity_ids`, issue a HEAD or status
   check against the source system. If any ID returns 404 or "not found", flag the
   item in the rehydration block with a `DRIFT DETECTED` warning and prompt the agent
   to re-fetch current state before acting.

2. **Tool status refresh:** Always re-check tool health at session start rather than
   relying on the persisted `tools_state`. The persisted value is contextual background
   ("it was slow last session"); the live check is the source of truth.

3. **Staleness as a drift proxy:** Items older than 24h are flagged `potentially_stale`.
   For items older than 7 days, surface a `STALE STATE` warning and treat all cached
   values as unverified until confirmed against live systems.

### Handling breaking schema changes in the persistence store

If `session-state.json` schema version is bumped and older snapshots become incompatible:

1. Increment `schema` in the snapshot: `"schema": "session-state/v2"`
2. Write a migration function that reads v1 and emits v2 shape
3. REHYDRATE mode checks the version field and runs migration before building the
   context block
4. Archive the pre-migration snapshot to `session-history/` before overwriting

Never silently discard an old snapshot. If migration fails, surface an error and
load a minimal context block (commitments only) rather than starting fully cold.

### Invalidating state after a deployment

If the underlying codebase deployed a breaking change (e.g., renamed a CRM field,
dropped a case status value), the safest approach is to invalidate the current
snapshot explicitly:

```bash
# Mark current snapshot as invalidated
jq '.metadata.invalidated = true | .metadata.invalidation_reason = "CRM schema migration 2024-12-05"' \
  .claude/memory/cs-agent-007/session-state.json > /tmp/state-invalidated.json \
  && mv /tmp/state-invalidated.json .claude/memory/cs-agent-007/session-state.json
```

On the next REHYDRATE, the skill checks `metadata.invalidated` and emits a prominent
warning rather than injecting potentially broken state. Commitments are still surfaced
(they are human facts, not system facts) but all system-derived fields are flagged.

---

## Tuning the Rehydration Cap

The default 6,000-char cap was chosen to consume roughly one-third of a Haiku context
window at session start, leaving room for the current session's tool descriptions and
user messages.

Adjust the cap in `rehydration-config.json` to match your model and use case:

| Scenario | Suggested cap |
|---|---|
| Simple single-task agent, Haiku | 3,000 chars |
| Multi-case customer service agent, Haiku | 6,000 chars (default) |
| Complex research or coding agent, Sonnet | 10,000 chars |
| Emergency override (commitments < 2h) | 8,000 chars (auto) |

If truncation events appear frequently in `persistence-log.json`, either raise the cap
or prune low-value `context_notes` from your SAVE output before they accumulate.
