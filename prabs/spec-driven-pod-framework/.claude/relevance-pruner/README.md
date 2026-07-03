# RelevancePruner

Pre-prompt relevance filtering for retrieval-heavy agent tasks. Scores candidate
context chunks against the current task query, drops irrelevant chunks before
they reach the reasoning model, and packs the highest-value survivors into a
token budget.

---

## Quick Start

1. Populate `input/candidate-chunks.json` with your retrieved chunks.
2. Write `input/task-query.md` describing the current intent (primary, secondary,
   keywords).
3. Review `input/pruning-config.json` — adjust `threshold` and `max_tokens` for
   your use case.
4. Run the skill. Read `output/pruned-context.json` for the context to inject and
   `output/pruning-summary.json` for efficiency metrics.

---

## RelevancePruner vs. ContextCompactor — Which to Use

These two optimization agents address different problems. Use the right one, or
chain them in order.

| Condition | Use |
|---|---|
| You have too many chunks and many are irrelevant to the query | **RelevancePruner** |
| You have chunks that are all relevant but individually too long | **ContextCompactor** |
| You have too many long chunks, some of which are irrelevant | **RelevancePruner first, then ContextCompactor** |
| You have a single long document that is definitely relevant | **ContextCompactor only** |
| Your context pool is already within budget | **Neither — inject directly** |

The key distinction: RelevancePruner removes whole chunks. ContextCompactor
compresses or summarizes individual chunks to reduce their length. Running
Compactor on irrelevant chunks wastes compute; always prune first.

---

## Scoring Formula

```
relevance_score = (semantic_similarity * 0.6)
                + (recency_weight      * 0.2)
                + (source_authority   * 0.2)
```

Semantic similarity is the dominant term (60%). The other two terms act as
tiebreakers and can shift a borderline chunk above or below the threshold by
roughly 0.1-0.2 points. If your primary concern is topical relevance, do not
raise the semantic weight above 0.7 or the recency/authority signals become
negligible.

---

## Threshold Tuning

The default threshold of **0.35** is calibrated for general customer service
tasks with a balanced retrieval corpus (mix of topical and off-topic documents).

### Raise the threshold (0.45 – 0.65) when

- The task involves legal, financial, or compliance content where noise chunks
  could cause the model to make incorrect commitments.
- Your retrieval system returns a large number of loosely related documents
  (semantic search with high top-k, or keyword search with broad matching).
- You see the model hallucinating details that trace back to low-relevance chunks
  in the pruned context.
- The token budget is tight (under 4K tokens) and every slot must count.

### Lower the threshold (0.20 – 0.30) when

- The task is exploratory and the model needs broad context to reason correctly
  (e.g., "what might have caused this error?" with no single obvious answer).
- Your retrieval corpus is small and highly curated — low-scoring chunks may
  still be load-bearing.
- The dropped-chunk log shows chunks being missed that a human reviewer would
  consider relevant.
- You are debugging a new RAG pipeline and want to understand the full score
  distribution before tightening.

### Measuring threshold quality

The best signal is the score gap between the lowest-kept chunk and the
highest-dropped chunk. A gap of 0.10 or more indicates clean separation. A gap
near zero means you are on a dense part of the score distribution and the
threshold is splitting nearly-tied chunks — consider adjusting or reviewing
borderline chunks manually.

---

## Warning: Load-Bearing Chunks

The embedding-based scoring is a semantic proxy, not a ground-truth measure of
whether a chunk matters for the current task. The following categories of chunks
are dangerous to drop on low scores and should be handled with care:

### Chunks with prior commitments

If a previous agent or human agent made a promise to the customer — a refund
timeline, a callback commitment, a waived fee — that information is
**contractually and legally significant** regardless of its semantic score.
A prior case note about a commitment to expedite a refund may score only 0.30
because its language is more administrative than task-specific. The protected
pattern `commitment_made` catches this case; ensure your CRM case notes use this
tag consistently.

### Chunks providing negative constraints

A policy that says "do NOT do X in situation Y" may score low because its
vocabulary is about the general policy domain rather than the specific query, but
a model that does not see it may confidently recommend X. Negative constraint
chunks are the most common cause of post-pruning errors in production.
Mitigation: add an `authority_score` override of 0.85+ to known constraint
documents, which raises their floor score.

### Cross-chunk dependencies

Some chunks only make sense as a pair. For example, a known-issue chunk (high
score) and a resolution procedure chunk (lower score) may both be needed. If
packing drops the procedure chunk due to budget, the model has diagnosis context
but no fix. Watch for this pattern in your dropped-chunk log: if a dropped chunk
has a title or ID that mirrors a kept chunk, investigate whether they are
dependent.

### Mitigation strategies

- Use the `protected_patterns` field in `pruning-config.json` to immunize
  chunk categories from threshold dropping.
- Add explicit `authority_score` overrides to chunks you know are high-stakes.
- Review `dropped-chunks-log.json` after each run during pipeline development.
  Look for drops that a domain expert would question.
- Set a conservative threshold during initial deployment. Tighten it after you
  have observed the score distribution on real production queries.

---

## Interpreting the Outputs

### pruned-context.json

Inject this array into the reasoning model's context in the order provided
(relevance descending). The most relevant chunks are first; most attention
mechanisms will weight them accordingly.

### dropped-chunks-log.json

Use this log for:
- **Threshold tuning**: If multiple high-quality chunks appear in this log with
  scores just below threshold, lower the threshold slightly.
- **Debugging model errors**: If the model makes an incorrect statement,
  cross-reference the dropped log — the missing context may be here.
- **Audit and compliance**: Demonstrates which chunks were considered and
  intentionally excluded.

### pruning-summary.json

Review `reduction_percentage` and `budget_utilization_percentage` together:
- High reduction + low utilization: the query is narrow and well-specified.
  Consider whether the unused budget could be used to pull in the next-ranked
  dropped chunks.
- Low reduction + high utilization: many chunks scored above threshold. Either
  lower the threshold or raise the token budget.
- `budget_exceeded_by_protection: true` in the summary means protected chunks
  alone filled the budget. This is a rare condition but requires manual review —
  the reasoning model will receive protected context but no policy context.

---

## Limitations

1. **Embedding relevance is a proxy.** Semantic similarity captures topical
   overlap, not logical necessity. A chunk can be highly relevant in vocabulary
   and irrelevant in content (or vice versa). The scoring formula is a
   probabilistic filter, not a guarantee.

2. **Aggressive thresholds risk missing load-bearing chunks.** See the warning
   section above. Start conservative.

3. **Recency weight assumes newer is better.** For stable policy documents, a
   two-year-old authoritative policy may be more reliable than a six-month-old
   draft. Override with explicit `authority_score` on chunks where recency is
   not a good proxy for quality.

4. **Token estimates are approximate.** `estimated_tokens` in candidate chunks
   is a pre-computed estimate. Actual tokenization may differ by 5-10%. Budget
   overruns of this magnitude are expected and acceptable. If exact budget
   adherence is critical, use a real tokenizer to compute counts before packing.

5. **Not a summarizer.** RelevancePruner does not reduce chunk length. If your
   highest-scoring chunk is 2,000 tokens and your budget is 3,000 tokens, only
   one more chunk can fit. For length reduction, chain with ContextCompactor.
