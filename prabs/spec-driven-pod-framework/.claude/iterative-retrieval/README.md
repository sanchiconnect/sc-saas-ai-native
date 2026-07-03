# IterativeRetrieval

Progressive, demand-driven context loading for AI agents. Retrieves the
minimum context needed to answer a question, fetching more only when a
reasoning gap is detected. Typically cuts input tokens 5–10x compared to
loading an entire knowledge base upfront.

---

## When to Use Iterative Retrieval

### Use iterative retrieval when

- The knowledge base has **more than ~50 documents** and a typical question
  requires fewer than 10 of them to answer.
- Questions are **specific and targeted** (policy lookups, eligibility
  determinations, procedure walkthroughs) rather than holistic summaries.
- **Token cost or latency per inference call** is a concern and you can afford
  multiple smaller calls instead of one large one.
- The index has **good coverage and quality** — embeddings are meaningful,
  chunks are well-sized (300–700 tokens), and metadata is accurate.
- Tasks have **clear stop criteria** — there is a deterministic answer once
  the right documents are loaded.

### Use upfront full-context loading instead when

- The total retrievable corpus fits comfortably within the model's context
  window (e.g. fewer than 20 short documents).
- The question requires **holistic reading** across many documents (e.g.
  "summarise all policy changes from this year" or "find inconsistencies
  across the documentation").
- **Latency is critical** and the round-trip cost of multiple retrieval calls
  exceeds the token cost savings.
- The **index is poor quality** — misaligned embeddings or oversized chunks
  produce low-relevance first slices and force unnecessary extra rounds.
- The task requires **all or most** of the available context to be safe
  (e.g. legal review requiring no document to be missed).

### Rule of thumb

If you expect the answer to require fewer than 15% of your total documents,
iterative retrieval will almost always be more efficient. Above 40%, the
overhead of multiple round-trips typically outweighs the token savings.

---

## Configuring Stop Criteria

The three stop criteria interact to create a speed/accuracy tradeoff. Adjust
them in `input/retrieval-config.json`.

### Confidence threshold (`confidence_threshold`)

Controls how certain the agent must be before accepting an answer.

| Threshold | Effect | Use case |
|-----------|--------|----------|
| 0.70 | Stops earlier, lower accuracy | Exploratory tasks, drafts, low-stakes lookups |
| 0.85 | Balanced (default) | Production customer service, standard policy lookups |
| 0.95 | More rounds, higher accuracy | Legal, compliance, refund disputes above $500 |

Setting the threshold too low risks under-retrieval: the agent stops with
open gaps and produces a partially grounded answer. Setting it too high can
exhaust the round budget before reaching the threshold on legitimately
ambiguous questions — in that case the fallback path (human review flag) is
triggered.

### Maximum rounds (`max_rounds`)

A hard safety ceiling independent of confidence.

| Setting | Effect |
|---------|--------|
| 3 | Fast; sufficient for well-indexed single-domain questions |
| 5 | Default; handles multi-domain questions with 1–2 cross-references |
| 8 | Slow; for deeply nested policy questions with many cross-references |

Increasing `max_rounds` alone does not improve accuracy if the index cannot
surface relevant documents. If you find the agent consistently hitting the
round ceiling, diagnose the index first.

### Token budget (`max_tokens`)

Sets an absolute ceiling on how much content can be loaded, regardless of
round count or confidence.

| Setting | Notes |
|---------|-------|
| 6 000 | Tight; forces very selective retrieval |
| 12 000 | Default; leaves ~3 000 tokens for system prompt + answer generation in a 16K context |
| 20 000 | For larger context windows (32K+); allows more supporting evidence |

The token budget should be set as `model_context_window - system_prompt_tokens - answer_generation_reserve`. A common reserve is 2 000–4 000 tokens.

### Combining criteria for common scenarios

| Scenario | Recommended config |
|----------|--------------------|
| Fast tier-1 support lookup | threshold: 0.80, rounds: 3, tokens: 8000 |
| Standard billing dispute | threshold: 0.85, rounds: 5, tokens: 12000 (default) |
| Legal/compliance review | threshold: 0.92, rounds: 7, tokens: 20000 |
| High-volume FAQ deflection | threshold: 0.75, rounds: 2, tokens: 5000 |

---

## Building the Document Index

The quality of the index is the single largest determinant of iterative
retrieval efficiency. A good index means the first slice is highly relevant
and fewer rounds are needed.

### Document structure

Each entry in the index should contain:

```json
{
  "doc_id": "unique_snake_case_identifier",
  "title": "Human-readable title",
  "category": "one of your defined categories",
  "summary": "2-4 sentence description of what the doc covers and what questions it answers",
  "token_count": 480,
  "last_updated": "YYYY-MM-DD",
  "relevance_tags": ["tag1", "tag2", "tag3"]
}
```

The `summary` field is the most important: it should describe the document
in terms of the *questions it can answer*, not just what it is. Compare:

- Weak: "This document covers the Professional plan."
- Strong: "Defines the 7-day grace period for PRO-tier post-cancellation
  charges and specifies refund eligibility and the refund API endpoint."

### Chunking strategy

- Target **300–700 tokens per chunk**. Shorter chunks lose context; longer
  chunks dilute relevance scores.
- Chunk at **semantic boundaries** (section headers, policy clauses) rather
  than fixed token counts.
- Include the document title and section heading at the top of each chunk
  so that retrieved content is self-contained.
- For policy documents, treat each numbered section (§1, §2, etc.) as a
  separate chunk and include the section number in the summary.

### Embedding model choice

- `text-embedding-3-small` (default): good balance of cost and quality for
  English-language support documentation.
- `text-embedding-3-large`: higher accuracy for technical or multi-lingual
  content; ~6x more expensive.
- Re-embed the entire index whenever the embedding model is updated — old
  and new embeddings are not comparable.

### Keeping the index fresh

- Set a maximum staleness threshold per category (e.g. billing policy
  documents should be re-indexed within 24 hours of any update).
- Include `last_updated` in each index entry and surface a warning if a
  document loaded during retrieval is older than the staleness threshold.
- For high-change categories (`billing_policy`, `refund_procedures`), use
  a webhook or document change event to trigger incremental re-indexing
  rather than nightly full rebuilds.

### Relevance tags

Tags allow the retrieval config to apply `category_filter_enabled: true`
to narrow the initial search space. Use tags that match the `target_category`
values your gap detection will produce. Consistent tag vocabulary across all
documents is more important than completeness.

---

## Interpreting the Outputs

### retrieval-trace.json
The trace is the primary debugging artifact. If an answer is wrong or
confidence is unexpectedly low, read the trace to identify:
- Which round introduced the decisive document
- Whether gaps were correctly identified and targeted
- Whether the index surfaced high-scoring documents for the right queries

### coverage-report.json
Use the `efficiency_vs_full_load.reduction_pct` to track the value of the
iterative approach over time. If reduction falls below 50%, either the index
is too small to benefit from iterative loading, or the task type requires
broad coverage and upfront loading should be used.

### grounded-answer.md
Every claim should have an inline citation. An answer with uncited claims
indicates the agent reached the confidence threshold on partially ungrounded
reasoning — lower `confidence_threshold` calibration is likely needed, or
the relevant documents are not in the index.

---

## Integration with the Customer Service Stack

In the sample project (React + FastAPI + PostgreSQL + Salesforce CRM), the
IterativeRetrieval agent is invoked by the FastAPI backend when a support
case requires policy lookups. The typical call flow is:

1. Customer submits dispute via React frontend.
2. FastAPI creates a case record in PostgreSQL and triggers the agent.
3. The agent reads `task-spec.md` (generated from the case record), runs
   the retrieval loop against the vector store, and writes outputs.
4. `coverage-report.json` is read by FastAPI to determine routing:
   - `confidence >= 0.85` and `human_review_required: false`: agent
     executes the recommended action automatically.
   - `confidence < 0.85` or `human_review_required: true`: case is queued
     for human review in the Salesforce CRM queue.
5. The Salesforce CRM is updated with the retrieval trace and grounded
   answer as case notes, regardless of routing outcome.
