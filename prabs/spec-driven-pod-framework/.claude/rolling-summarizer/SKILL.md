---
name: rolling-summarizer
description: "RollingSummarizer maintains a bounded, predictable context size across long-running agent sessions. Instead of allowing raw conversation history to grow linearly — eventually crowding out working memory — this skill folds newly accumulated turns into a compact rolling summary on a regular cadence."
---

--#
name: rolling-summarizer
tagline: Continuously-updated compact session memory
version: 1.0.0
default_model: claude-haiku-4-5
escalation_model: claude-sonnet-4-6
approx_tokens_per_invocation: 10000
category: memory-management
triggers:
  - turns_since_last_summary >= 10
  - new_turns_token_count > 3000
---

# RollingSummarizer Skill

## Purpose

RollingSummarizer maintains a bounded, predictable context size across long-running agent sessions. Instead of allowing raw conversation history to grow linearly — eventually crowding out working memory — this skill folds newly accumulated turns into a compact rolling summary on a regular cadence. The prior summary is updated in place and stale raw turns are replaced with the digest, keeping total context stable regardless of session length.

This is a cadence-based approach, distinct from pressure-based compaction (see StrategicCompactor). RollingSummarizer runs proactively on a schedule; it does not wait for context pressure to become critical before acting.

---

## Trigger Conditions

Run RollingSummarizer when **either** of the following conditions is true:

1. **Turn count trigger:** The number of raw turns accumulated since the last summarization run is **>= 10**.
2. **Token trigger:** The raw token count of new turns since the last summarization run **exceeds 3,000 tokens**.

Evaluate these conditions at the end of every agent turn. If both fire simultaneously, treat this as a single summarization event (do not double-process). Log which trigger fired in the run log (`turns_trigger` or `token_trigger` or `both`).

---

## Model Selection: Haiku vs. Sonnet

### Default: claude-haiku-4-5

Use Haiku for the vast majority of summarization runs. Haiku is fast, inexpensive, and sufficient for compressing routine conversational content such as:
- Status inquiries and factual updates
- Navigation or clarification exchanges
- Standard troubleshooting steps
- Casual conversational filler

### Escalation: claude-sonnet-4-6

Escalate to Sonnet when any single turn in the new-turns batch contains one or more of the following escalation signals:

| Signal Category | Examples |
|---|---|
| `legal_language` | Terms like "per our SLA", "as contractually agreed", "pursuant to", "binding agreement", "terms and conditions" |
| `formal_commitment` | Agent explicitly commits to a dollar amount, timeline, or specific action using confirmatory language ("I can confirm", "I guarantee", "you will receive") |
| `regulatory_compliance` | References to GDPR, PCI-DSS, HIPAA, CCPA, SOX, or any regulatory framework |
| `dispute_escalation` | Customer mentions chargeback, BBB complaint, legal action, attorney, or formal dispute |

When escalation is triggered:
- Use Sonnet for the **entire** summarization run (do not split processing between models).
- Log `escalation_triggered: true` and record the specific `escalation_reason` in the run log.
- Apply extra care to preserve nuanced wording — especially for commitments — verbatim in the output (see Verbatim Preservation below).

---

## Input Contract

The skill expects three inputs:

### 1. Recent Turns (`input/recent-turns.md`)
Raw conversation turns accumulated since the last summarization. Each turn must include:
- Turn number (sequential, continuing from prior session)
- Speaker role: `[Customer]`, `[Agent]`, or `[System]`
- Timestamp (ISO 8601)
- Full turn text

### 2. Prior Rolling Summary (`input/prior-summary.md`)
The output of the previous RollingSummarizer run (or a seed summary if this is the first run). Contains the structured 6-section block described below. If no prior summary exists, initialize all sections as empty with a `## Session Context` note indicating session start time.

### 3. Config (`input/summarizer-config.json`)
JSON configuration controlling cadence, model routing, token budgets, and verbatim preservation fields.

---

## Folding Logic: How to Merge New Turns into the Existing Summary

Follow these steps in order when processing a summarization run:

### Step 1 — Identify New Facts
Read all new turns and extract distinct facts: new information that does not already appear in the prior summary. Ask: "Does the prior summary already capture this?" If yes, it is not a new fact. If no, it must be incorporated.

Categories of new facts:
- Identity or profile updates (new name, new contact info, plan tier changes)
- New issue details or root cause findings
- Actions taken by agent or customer (commands run, forms submitted, calls made)
- Status changes (ticket opened, escalated, resolved, refund approved)
- New commitments or promises made by either party
- New pending items or unresolved questions

### Step 2 — Update Existing Summaries
For each section in the prior summary:
- If a new fact **modifies or supersedes** existing content in a section, update that content in place. Do not keep the stale version alongside the update.
- If a new fact **adds to** existing content without contradiction, append it concisely.
- If a section is **unchanged** by the new turns, preserve it exactly as-is.
- Mark each substantively changed section with `[UPDATED]` and each new item with `[NEW]` in the output. Unchanged sections receive `[UNCHANGED]`.

### Step 3 — Never Duplicate
Before writing any new content into the summary, confirm it is not already present in the prior summary (even under different wording). Deduplication is strict: if the semantic meaning is already captured, do not add it again. This prevents summary bloat across repeated cycles.

### Step 4 — Verbatim Preservation
Certain fields must be preserved character-for-character regardless of summarization:
- `customer_id` — internal CRM identifier
- `ticket_id` — support ticket reference number
- `commitment_text` — any text where the agent made a formal promise, especially dollar amounts and timelines
- `amounts` — all currency figures mentioned in the session

These fields appear in `preserve_verbatim` in the config. Never paraphrase, round, or restate these — copy them exactly as spoken/written.

### Step 5 — Token Budget Enforcement
The output summary must not exceed `max_summary_tokens` (default: 800 tokens). If the updated summary exceeds this budget:
1. Compress the `## Session Context` narrative first (reduce to 1-2 sentences).
2. Compress `## Issue Summary` next (reduce to bullet points if not already).
3. Never compress `## Commitments Made` or `## Customer Profile` — these are highest-fidelity sections.
4. If still over budget after steps 1-2, tighten `## Actions Taken` by collapsing sequential steps into a single summary line.

---

## Output Format: The Rolling Summary Block

The output summary must use exactly these six sections in this order:

```markdown
## Session Context
[1-3 sentences: when the session started, channel, session duration so far, overall tone/trajectory]

## Customer Profile
[Verified identity fields: name, customer ID, tier, account type, contact info if shared. Mark unverified fields explicitly.]

## Issue Summary
[Concise description of the core problem(s). Include root cause if identified. Update as understanding evolves.]

## Actions Taken
[Chronological bullet list of concrete actions: what was done, by whom, and outcome. Include system/CRM lookups that produced key findings.]

## Pending Items
[Bullet list of open questions, outstanding tasks, or awaited confirmations. Remove items once resolved.]

## Commitments Made
[Verbatim or near-verbatim record of any promises made by agent or company. Include: who committed, what was promised, timeline, and any reference numbers. This section is never compressed.]
```

---

## Context Replacement Procedure

After generating the updated summary, the agent runtime should:

1. Remove all raw turns that were included in this summarization run from the active context window.
2. Insert the updated rolling summary block in their place, at the position where the oldest folded turn previously sat.
3. Retain all turns **after** the summarization cutoff as raw turns (they have not yet been folded).
4. Update the session state to record: `last_summarized_at` (turn number and timestamp), `summary_token_count`, `model_used`.

The net effect: context size decreases by (`new_turns_tokens` - `summary_tokens`). For a typical run, this saves 1,500–3,000 tokens per cycle.

---

## Limitations and Mitigations

**Compounding detail loss:** Each summarization cycle discards raw turns. Over many cycles (5+), subtle context — exact phrasing, tone shifts, implied subtext — is progressively lost. Mitigation: preserve `commitment_text` and `amounts` verbatim; log session turn count so downstream agents can detect heavily-cycled sessions and apply extra caution.

**Not suitable when exact wording matters throughout:** If the downstream agent needs to reference exact prior customer statements (e.g., for dispute resolution, legal review, or audit), raw turns should be archived to a sidecar log and the summary used only for working context.

**Escalation blind spots:** Escalation triggers are keyword-heuristic. Subtle formal commitments phrased unusually may not trigger Sonnet escalation. Mitigation: when in doubt, prefer Sonnet. The cost differential is acceptable given the risk of compressing a formal commitment.
