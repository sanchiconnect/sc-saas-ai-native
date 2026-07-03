# RollingSummarizer

Continuously-updated compact session memory for long-running agent sessions.

---

## What It Does

RollingSummarizer folds newly accumulated conversation turns into a structured rolling summary on a fixed cadence — every 10 turns or every 3,000 new-turn tokens, whichever fires first. The updated summary replaces the raw turns it covers, keeping total active context at a stable, bounded size regardless of how long a session runs.

A single summarization cycle for a typical customer service session recovers 1,500–3,000 tokens. Over a 200-turn session with 20 cycles, the difference between linear growth and rolling summarization can exceed 40,000 tokens of headroom.

---

## How It Differs from StrategicCompactor

Both skills reduce context size, but they operate on different philosophies:

| Dimension | RollingSummarizer | StrategicCompactor |
|---|---|---|
| **Trigger** | Cadence-based: fixed turn/token schedule | Pressure-based: fires when context nears limit |
| **Timing** | Proactive — runs regularly throughout session | Reactive — runs when forced by context pressure |
| **Scope** | Folds only the most recent turn batch | May compact large portions of history at once |
| **Predictability** | Highly predictable context size at all times | Context size variable; can spike before compaction fires |
| **Detail retention** | Progressive loss across cycles | Potentially higher loss in a single large compaction |
| **Best for** | Long-running sessions where steady state matters | Sessions where compaction is rare but critical |

Use RollingSummarizer when you need **consistent, bounded context** throughout a session. Use StrategicCompactor when you have a session where most interactions are lightweight and you only need to compact occasionally under pressure.

You can combine both: run RollingSummarizer on cadence for steady-state management, and keep StrategicCompactor as a circuit breaker if an unusually dense batch still causes context pressure between cycles.

---

## Best Practices

### When to Prefer Rolling Summarization

- **Long customer service sessions** where a customer and agent are working through a complex, multi-step issue over 30+ minutes. Rolling summarization keeps the agent's working context clean and consistently bounded.
- **Multi-session continuity** where a summary is persisted between calls and used to seed the next session's context. RollingSummarizer's structured output (6 fixed sections) is easier to restore than a freeform compaction blob.
- **Sessions with formal commitments** — the escalation logic ensures Sonnet is used when precision matters, and the verbatim preservation policy keeps commitments character-accurate through cycles.
- **Predictable latency requirements** — because RollingSummarizer runs on a fixed schedule, you can predict exactly when a summarization call will be made and build that into your p95 latency budget. Pressure-based compaction introduces latency spikes at unpredictable points.

### When to Prefer On-Demand Compaction

- **Short sessions** (under 20 turns): Rolling cadence will never fire; use on-demand or skip compaction entirely.
- **Exact-wording requirements throughout**: If downstream logic (e.g., dispute adjudication, legal review) needs to reference precise customer statements at any point, archive raw turns to a sidecar log and do not rely on summarization for working context.
- **Audit trails**: Summarization is not a substitute for a conversation audit log. Always write raw turns to a durable store if compliance or auditability is required.

---

## Risk: Compounding Detail Loss

Each summarization cycle discards some raw information. Over many cycles, this compounds:

- **Cycle 1:** Raw turns → summary. ~5% detail loss (routine filler, exact phrasing).
- **Cycle 5:** Summary is now a summary-of-summaries. Subtle context (tone shifts, hedge language, implied subtext) progressively absent.
- **Cycle 10+:** Only the most salient facts survive. High-signal items (amounts, commitments, ticket IDs) are preserved; conversational texture is gone.

### Mitigations

1. **Verbatim preservation fields.** Configure `preserve_verbatim` in the config to protect the highest-value fields from paraphrasing. At minimum: customer IDs, ticket IDs, commitment text, and dollar amounts.

2. **Escalation to Sonnet.** When the session contains formal commitments or legal language, escalate to Sonnet for the full run. Sonnet's stronger comprehension reduces the probability of semantic drift during compression.

3. **Sidecar archive.** Write every raw turn to a separate durable log (database, blob storage) before it is folded into the summary. The rolling summary is your working memory; the archive is your ground truth.

4. **Cycle count monitoring.** Track `summarization_cycles_completed` in session state. If a session exceeds 8–10 cycles, consider flagging for human review before making high-stakes decisions (e.g., processing a large refund, escalating to legal). Surface this count in the run log and in agent reasoning.

5. **Structured sections.** The 6-section output format is not aesthetic preference — it is a compounding-loss mitigation. By keeping commitments in a dedicated, never-compressed section, critical information survives indefinitely regardless of cycle count.

---

## File Structure

```
skills/RollingSummarizer/
├── SKILL.md                          # Full skill specification and instructions
├── README.md                         # This file
├── input/
│   ├── recent-turns.md               # Sample: 12 new turns triggering summarization
│   ├── prior-summary.md              # Sample: prior rolling summary (turns 1–20)
│   └── summarizer-config.json        # Configuration: cadence, models, verbatim fields
└── output/
    ├── rolling-summary-updated.md    # Sample: updated summary after folding turns 21–32
    └── summarizer-run-log.json       # Sample: full run metadata and quality checks
```

---

## Quick Configuration Reference

| Config Key | Default | Description |
|---|---|---|
| `cadence.turns` | 10 | Run after this many new turns |
| `cadence.token_trigger` | 3000 | Run when new turns exceed this token count |
| `models.default` | claude-haiku-4-5 | Model for routine runs |
| `models.escalation` | claude-sonnet-4-6 | Model for runs with escalation signals |
| `max_summary_tokens` | 800 | Output summary token budget |
| `preserve_verbatim` | [customer_id, ticket_id, commitment_text, amounts] | Fields copied exactly, never paraphrased |
