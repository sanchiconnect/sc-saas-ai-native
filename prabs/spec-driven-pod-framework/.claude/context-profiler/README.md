# ContextProfiler

Live context-window accounting and headroom alerts for AI agent sessions.

---

## What It Does

ContextProfiler measures the token footprint of every segment loaded into the active context window, reports utilisation percentage and remaining headroom, and recommends the right action when thresholds are crossed. It does not summarise, rewrite, or modify context — it only measures and advises.

The core insight it surfaces is the **silent context tax**: in this customer service chatbot, the 8 Salesforce/CRM MCP tool schemas consume approximately 12,000 tokens before any conversation begins. On a 200K model this is manageable (6% overhead), but on a smaller model it becomes existential. ContextProfiler makes this visible and quantified rather than implicit.

---

## Segments Measured

| Segment | Typical Size | Growth Pattern |
|---|---|---|
| `system_prompt` | 600–1,200 tokens | Fixed per session |
| `tool_schemas` | 10,000–15,000 tokens | Fixed unless tools are added/removed |
| `conversation_history` | 200 tokens/turn growing | Linear, accelerates with tool results |
| `injected_files` | 0–50,000+ tokens | Spiky — large step changes when files are loaded |
| `memory_blocks` | 200–600 tokens | Slow growth from accumulated session facts |

---

## Thresholds

- **Healthy (< 70%):** No action required. Growth projections are included so the operator can anticipate when action will be needed.
- **Warn (70–84.9%):** Invoke StrategicCompactor. Immediate risk is low, but the session is approaching a zone where context pressure will affect quality. This is the right time to compact before it becomes urgent.
- **Critical (85–94.9%):** Invoke StrategicCompactor immediately. Do not defer. New tool-heavy operations should pause until compaction is complete.
- **Emergency (≥ 95%):** Invoke RelevancePruner first to quickly drop unreferenced content, then StrategicCompactor. Consider routing the session to a model with a larger window if available.

---

## When to Invoke

**At session start** — get a baseline budget before the conversation begins. The fixed cost snapshot (system prompt + tool schemas + memory blocks) tells you how much effective window is available for conversation.

**After every 25–30 turns** — conversation history grows monotonically. Regular snapshots catch growth trends early.

**Before loading large files** — before injecting a billing PDF, CRM export, or knowledge base article, check current headroom. If you're already at 50%, a 30K-token file could push you to 65% instantly.

**Before heavy tool use** — some tool results (full CRM exports, large account histories) can return 5,000–40,000 tokens. Know your headroom before issuing those calls.

**When another skill requests a reading** — StrategicCompactor and RelevancePruner both call ContextProfiler to get a pre-action baseline and a post-action verification.

---

## How to Read the Output

The primary output is `output/context-budget.json`. Key fields:

- **`total_percentage`** — The number to watch. This is context utilisation as a percentage of the model window.
- **`alert_level`** — `none`, `warn`, `critical`, or `emergency`. Act on anything above `none`.
- **`segments.injected_files.prune_candidates_total_tokens`** — Quick wins available from RelevancePruner. Check this first before compacting.
- **`action_payload.recommended_sequence`** — When present, follow this sequence. It's ordered to minimise risk (prune first, compact second).
- **`silent_context_tax_analysis`** — Compares the effective usable window across model sizes. Use this to identify whether a session that's healthy on 200K would be in trouble if routed to a smaller model.
- **`growth_projection`** — Projects utilisation at future turn counts. Use this to decide whether to compact now or wait.

---

## Integration with Other Optimization Skills

### StrategicCompactor
ContextProfiler triggers StrategicCompactor when `conversation_history` grows large enough to cross the warn threshold. The `action_payload` includes `suggested_compaction_target_tokens` (40% of current history size) and the rationale. StrategicCompactor reads this payload and uses the target as its compression goal.

After compaction, StrategicCompactor should invoke ContextProfiler again to verify the new utilisation and confirm the session is back in the healthy range.

### RelevancePruner
ContextProfiler identifies injected files that are no longer actively referenced (`prune_candidate: true` on individual file entries). RelevancePruner reads this list and drops those files from context without requiring compaction of the conversation history.

ContextProfiler prioritises RelevancePruner over StrategicCompactor when prune candidates are available, because pruning is zero-risk (dropping unreferenced content cannot cause information loss) while compaction involves summarisation with associated fidelity tradeoffs.

The recommended sequence when both are needed:
1. ContextProfiler identifies prune candidates and compaction targets.
2. RelevancePruner drops unreferenced injected files.
3. ContextProfiler re-runs to get updated utilisation.
4. If still above threshold, StrategicCompactor compacts conversation history.
5. ContextProfiler re-runs to confirm healthy status.

### Session Router (future)
If a session reaches the emergency threshold and no compaction is feasible (e.g. all content is actively referenced), ContextProfiler's output provides the data needed to route the session to a model with a larger context window. The `silent_context_tax_analysis.model_comparison` section quantifies the tradeoffs across window sizes explicitly.

---

## Limitations

- **Tokeniser estimates differ from server-side counts.** The character heuristic (chars / 3.8 for prose, chars / 3.5 for JSON) overestimates slightly. Real server-side token counts may be 5–8% lower, meaning ContextProfiler's alerts are intentionally early-fire. This is by design — better to trigger compaction at 70% estimated than to find out at 75% actual that you're already at 78%.
- **Measures size, not relevance.** ContextProfiler cannot tell you which parts of the conversation are still relevant and which can be safely dropped. That judgment belongs to RelevancePruner.
- **Tool schema costs are fixed.** The 12,340-token tool schema tax cannot be reduced by ContextProfiler or its downstream skills without unloading tools from the session. If tool schemas are the primary bottleneck, the solution is architectural (lazy tool loading, tool schema compression) rather than runtime compaction.
- **No real-time monitoring.** ContextProfiler is invoked on demand — it does not continuously monitor context growth. The responsibility for scheduling invocations rests with the session orchestrator.

---

## Files

```
skills/ContextProfiler/
├── SKILL.md                          # Full skill instructions for Claude
├── README.md                         # This file
├── input/
│   ├── conversation-transcript.md    # Sample 15-turn customer service session
│   ├── system-prompt.md              # Sample verbose agent system prompt
│   └── mcp-tools.json                # 8 Salesforce/CRM tool schemas
└── output/
    ├── context-budget.json           # Example healthy-state output (8.44% utilisation)
    └── context-budget-warn.json      # Example warn-state output (78.13% utilisation)
```
