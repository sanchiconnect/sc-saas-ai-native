---
name: relevance-pruner
description: "Embeds and scores candidate context chunks against the current task query, drops chunks below a relevance threshold, and greedily packs the highest-value survivors into a token budget. Delivers a pruned context set ordered by relevance, a dropped-chunk log with scores, and a summary of tokens reclaimed. Typically produces 20-50% smaller p"
---

**name:** relevance-pruner

**description:** Embeds and scores candidate context chunks against the current task query, drops chunks below a relevance threshold, and greedily packs the highest-value survivors into a token budget. Delivers a pruned context set ordered by relevance, a dropped-chunk log with scores, and a summary of tokens reclaimed. Typically produces 20-50% smaller prompts on retrieval-heavy tasks by raising signal-to-noise before the reasoning model ever sees the context window.


# RelevancePruner Skill

## Purpose

Customer service agents, RAG pipelines, and multi-turn assistants accumulate
large pools of candidate context — knowledge base articles, prior case notes,
product documentation, conversation history — before each model call. Injecting
all of it wastes tokens and dilutes attention. RelevancePruner runs a fast
scoring pass (embeddings + heuristic weights) to drop irrelevant chunks before
they reach the reasoning model.

## When to Invoke

Invoke RelevancePruner when:

- The candidate context pool exceeds 1.5x the target injection budget.
- The retrieval system returns more than 10 chunks and their relevance to the
  current query is not guaranteed.
- You are building or debugging a RAG pipeline and want visibility into which
  chunks survive scoring.
- A downstream agent (e.g., ContextCompactor) will receive the pruned set — run
  RelevancePruner first to remove irrelevant material before compaction.

Do NOT invoke RelevancePruner when:

- The context pool is already within budget and all chunks are known-relevant
  (e.g., a single retrieved document).
- The task is purely generative with no retrieval (no candidate chunks to score).
- Use ContextCompactor instead when chunks are all relevant but individually too
  long; pruning removes chunks, compaction summarizes them.

---

## Inputs

| File | Description |
|------|-------------|
| `input/candidate-chunks.json` | Array of candidate context chunks to evaluate. |
| `input/task-query.md` | The current task intent, decomposed into primary/secondary goals. |
| `input/pruning-config.json` | Threshold, budget, scoring weights, protected patterns. |

### candidate-chunks.json schema

```json
[
  {
    "id": "string — unique stable identifier",
    "source": "string — origin system (knowledge_base, crm, prior_turn, etc.)",
    "title": "string",
    "content": "string — full chunk text",
    "estimated_tokens": "integer",
    "created_at": "ISO-8601 timestamp (used for recency weight)",
    "authority_score": "float 0-1 (optional; defaults to source-class default)"
  }
]
```

### pruning-config.json schema

```json
{
  "threshold": 0.35,
  "max_tokens": 8000,
  "scoring_weights": {
    "semantic": 0.6,
    "recency": 0.2,
    "authority": 0.2
  },
  "protected_patterns": ["customer_id", "ticket_id", "commitment_made"],
  "embedding_model": "text-embedding-3-small"
}
```

---

## Outputs

| File | Description |
|------|-------------|
| `output/pruned-context.json` | Kept chunks ordered by relevance_score descending. |
| `output/dropped-chunks-log.json` | Dropped chunks with scores and drop reasons. |
| `output/pruning-summary.json` | Aggregate statistics: tokens reclaimed, reduction %. |

---

## Scoring Formula

Each chunk receives a composite relevance score in [0, 1]:

```
relevance_score = (semantic_similarity * 0.6)
                + (recency_weight      * 0.2)
                + (source_authority   * 0.2)
```

### semantic_similarity

Computed as the cosine similarity between:
- The embedding of the task query (concatenation of primary intent + secondary
  intent + any explicit context keywords from `task-query.md`).
- The embedding of the chunk's `title + " " + content[:512]` (first 512 chars
  are sufficient for embedding; full content is not re-embedded to control cost).

Use the model specified in `pruning-config.json` (`embedding_model` field).
Default: `text-embedding-3-small`.

Cosine similarity is already in [-1, 1]; clamp to [0, 1] with
`max(0, cosine_sim)` before applying the weight.

### recency_weight

Rewards recently created or updated chunks, which are more likely to reflect
current policy:

```
days_old = (now - chunk.created_at).days
recency_weight = exp(-days_old / 365)   # exponential decay, half-life ~6 months
```

If `created_at` is absent, assign `recency_weight = 0.5` (neutral).

### source_authority

Default authority scores by source class:

| source value | authority_score |
|---|---|
| `knowledge_base` (official policy docs) | 0.9 |
| `product_documentation` | 0.85 |
| `faq` | 0.75 |
| `crm_case_note` | 0.70 |
| `prior_turn` | 0.65 |
| `external_article` | 0.50 |
| `user_generated` | 0.30 |
| unknown / missing | 0.50 |

If a chunk supplies an explicit `authority_score` field, use that value instead
of the class default.

---

## Algorithm: Greedy Budget Packing

After scoring all chunks, apply the following pipeline:

### Step 1 — Protect safety-critical chunks

Scan every chunk's content for the patterns listed in
`pruning-config.json → protected_patterns`. A chunk that matches ANY pattern is
**immune to threshold dropping**. It is still scored, but even a score of 0.00
cannot cause it to be dropped. Record `kept_reason: "protected_pattern"` in the
output for these chunks.

Current protected patterns (customer service context):
- `customer_id` — any chunk referencing a customer identifier
- `ticket_id` — any chunk referencing a support ticket number
- `commitment_made` — any chunk describing a commitment already made to the
  customer (promises about refunds, callbacks, SLAs)

### Step 2 — Apply threshold

Drop all non-protected chunks with `relevance_score < threshold`.
Record each dropped chunk in `dropped-chunks-log.json` with
`drop_reason: "below_threshold"`.

### Step 3 — Greedy packing by relevance

Sort surviving chunks by `relevance_score` descending.

Iterate through the sorted list, accumulating tokens:
```
kept = []
token_count = 0
for chunk in sorted_survivors:
    if token_count + chunk.estimated_tokens <= max_tokens:
        kept.append(chunk)
        token_count += chunk.estimated_tokens
    else:
        drop(chunk, reason="over_budget_after_threshold")
```

Protected chunks that were immune to threshold dropping are prepended to the
sorted list before this loop (they have first claim on the budget).

### Step 4 — Emit outputs

Write `pruned-context.json` (kept list, ordered by relevance_score descending),
`dropped-chunks-log.json`, and `pruning-summary.json`.

---

## Customer Service Context — Source Priorities

For the sample project (React + FastAPI + PostgreSQL + Salesforce CRM), the
following chunk sources appear in the retrieval pipeline. Apply these labels in
`source` fields and the authority table above:

| Retrieval origin | source label to use |
|---|---|
| Zendesk/Salesforce knowledge base | `knowledge_base` |
| Product feature docs (Confluence/Notion) | `product_documentation` |
| FAQ database | `faq` |
| Salesforce case history | `crm_case_note` |
| Prior conversation turns | `prior_turn` |
| HR / internal ops docs | `internal_ops` (authority 0.20) |

Internal ops documents (HR policy, onboarding checklists, etc.) carry low
authority for customer-facing tasks and will almost always fall below the 0.35
threshold when the task query is customer-issue-focused.

---

## Safety Rules

1. **Never drop a chunk containing a customer ID, ticket number, or open
   commitment made to the customer.** These are load-bearing for legal and
   compliance reasons. If they score below threshold, they are kept with
   `kept_reason: "protected_pattern"` and their tokens are reserved before
   budget packing of other chunks.

2. **Log every drop.** `dropped-chunks-log.json` must contain every chunk that
   did not make it into the pruned set, with its score and the reason it was
   dropped (`"below_threshold"` or `"over_budget_after_threshold"`). This log is
   the primary debugging surface for threshold tuning.

3. **Do not mutate chunk content.** RelevancePruner only selects or rejects
   whole chunks. It never summarizes, truncates, or rewrites content. Use
   ContextCompactor for that.

4. **Respect the token budget strictly.** Never exceed `max_tokens` in the
   pruned set. If protected chunks alone exceed the budget, emit a
   `budget_exceeded_by_protection: true` flag in `pruning-summary.json` and
   include all protected chunks anyway — the downstream model must handle an
   oversized context rather than lose safety-critical content.

---

## Threshold Tuning Guidance

| Use case | Recommended threshold |
|---|---|
| High-precision customer service (billing disputes, legal) | 0.45 – 0.55 |
| General customer service Q&A | 0.35 (default) |
| Exploratory research / brainstorming | 0.20 – 0.30 |
| Strict budget environments (< 4K tokens) | 0.55 – 0.65 |

Raise the threshold when you see hallucination caused by tangentially-relevant
noise chunks. Lower it when dropped-chunk logs show chunks being missed that a
human reviewer would consider relevant.

---

## Output File Schemas

### pruned-context.json

```json
[
  {
    "id": "string",
    "title": "string",
    "source": "string",
    "relevance_score": "float",
    "semantic_similarity": "float",
    "recency_weight": "float",
    "source_authority": "float",
    "tokens": "integer",
    "kept_reason": "above_threshold | protected_pattern",
    "content": "string"
  }
]
```

### dropped-chunks-log.json

```json
[
  {
    "id": "string",
    "title": "string",
    "source": "string",
    "relevance_score": "float",
    "tokens": "integer",
    "drop_reason": "below_threshold | over_budget_after_threshold"
  }
]
```

### pruning-summary.json

```json
{
  "task_query_summary": "string",
  "total_candidate_tokens": "integer",
  "total_kept_tokens": "integer",
  "tokens_reclaimed": "integer",
  "reduction_percentage": "float",
  "chunks_evaluated": "integer",
  "chunks_kept": "integer",
  "chunks_dropped": "integer",
  "below_threshold": "integer",
  "over_budget_after_threshold": "integer",
  "protected_chunks_kept": "integer",
  "budget_exceeded_by_protection": "boolean",
  "threshold_used": "float",
  "max_tokens_budget": "integer"
}
```
