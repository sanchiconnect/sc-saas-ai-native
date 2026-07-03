---
name: iterative-retrieval
description: "Retrieves only the context actually needed to answer a question, loading the minimum slice first and fetching more only when a reasoning gap is detected. Typically cuts input tokens 5-10x compared to loading entire knowledge bases upfront, at the cost of extra round-trip latency."
---

**name:** iterative-retrieval

**description:** Retrieves only the context actually needed to answer a question, loading the minimum slice first and fetching more only when a reasoning gap is detected. Typically cuts input tokens 5-10x compared to loading entire knowledge bases upfront, at the cost of extra round-trip latency.


# IterativeRetrieval Skill

## Overview

Most agent tasks require only a small fraction of available documentation to
produce a confident answer. IterativeRetrieval exploits this by starting with
a minimal high-relevance slice, reasoning over it, and fetching additional
chunks only when the current context contains a detectable knowledge gap. The
process halts as soon as confidence crosses a threshold or the retrieval
budget is exhausted.

**Inputs required**
- `task-spec.md` — the question or task the agent must resolve
- `document-index.json` — vector-store or keyword index of available documents
- `retrieval-config.json` — budget, thresholds, and index connection settings

**Outputs produced**
- `grounded-answer.md` — final answer with inline citations
- `retrieval-trace.json` — ordered record of every retrieval round
- `coverage-report.json` — confidence score, efficiency metrics, gap summary

---

## Stop Criteria

The retrieval loop halts when **any** of the following conditions is first met:

| Condition | Default | Notes |
|-----------|---------|-------|
| Confidence threshold reached | >= 0.85 | Configurable in `retrieval-config.json` |
| Maximum retrieval rounds | 5 rounds | Each round may load 2-3 chunks |
| Token budget exhausted | 12 000 tokens loaded | Counts tokens of retrieved content only |
| Unresolvable gap detected | enabled | Stops if gap cannot be targeted in index |

When the loop exits, the current confidence level is recorded in
`coverage-report.json` as `confidence` regardless of why it stopped. The
`stop_reason` field in the final trace round records which condition fired.

---

## Gap Detection Heuristics

During the reasoning step (Step 3), scan your internal reasoning for any of
these patterns. Their presence signals a knowledge gap that warrants another
retrieval round.

### Explicit uncertainty phrases
- "I don't have information about X"
- "It is unclear what the policy is for Y"
- "I cannot determine whether Z applies here"
- "I need to verify / confirm X"
- "The document does not address X"

### Implicit reasoning dead-ends
- A conditional branch whose condition cannot be evaluated ("if PRO accounts
  are eligible, then … but I don't know if they are")
- A reference to a policy section that has not been loaded ("see §3.2")
- A numerical threshold, date, or amount that appears relevant but was not
  present in loaded chunks
- A cross-reference to another document not yet in context

### Customer service–specific triggers
- Policy scope is ambiguous (personal vs. business, tier-specific rules)
- Refund or credit eligibility depends on account age, plan type, or event
  date that has not been confirmed
- A regulatory or legal constraint is mentioned but the source is not in
  context
- The case history references a prior resolution that is not loaded

---

## Retrieval Dimensions

Before the first retrieval round, parse the task into these dimensions to
build targeted queries for each round.

| Dimension | What to extract | Example |
|-----------|-----------------|---------|
| **Entities** | Account IDs, plan names, product names, dates | PRO-34821, Nov 1 charge |
| **Intent** | The action the agent must take | resolve billing dispute, issue refund |
| **Domain** | Document categories likely to contain the answer | billing_policy, refund_procedures |
| **Constraints** | Limits that affect eligibility | cancellation date, grace period |
| **Unresolved conditions** | Open questions from prior rounds | does grace period apply to PRO tier? |

Store these as a running retrieval context that is updated after each round.

---

## Document Categories (Customer Service)

The index for this project contains documents across six categories. Use
these category labels when formulating targeted queries in subsequent rounds.

| Category | Contents | When to query |
|----------|----------|---------------|
| `billing_policy` | Billing cycles, invoice generation, charge timing | Any billing dispute |
| `subscription_management` | Plan tiers, upgrade/downgrade, cancellation flows | Subscription state questions |
| `refund_procedures` | Refund eligibility, processing steps, timelines | Refund or credit requests |
| `account_management` | Account status, access controls, data retention | Account-level facts |
| `legal` | Terms of service, regulatory compliance, dispute resolution | Escalations, formal disputes |
| `product_faq` | Feature descriptions, known issues, usage guidance | Product-related complaints |

---

## Step-by-Step Instructions

### Step 1 — Parse the task and initialise retrieval context

Read `task-spec.md` in full. Extract and record:
- **Primary question**: the single yes/no or resolution the agent must reach
- **Key entities**: account identifiers, plan names, dates, amounts
- **Intent**: the agent action that will close the task
- **Domain hints**: which document categories are most likely relevant
- **Known facts**: any facts already present in the task spec itself

Set `confidence = 0.0`, `round = 0`, `tokens_loaded = 0`, `gaps = []`.

Do not retrieve anything yet.

### Step 2 — First slice: retrieve top-3 most relevant chunks

Formulate a query string that combines the primary question with the top two
or three entities. Submit this query to the index specified in
`retrieval-config.json`.

Load the **3 highest-scoring** chunks returned. Record them in the trace:
```json
{
  "round": 1,
  "query": "<your query string>",
  "docs_loaded": ["<doc_id_1>", "<doc_id_2>", "<doc_id_3>"],
  "tokens_this_round": <sum of token_count for loaded docs>,
  "cumulative_tokens": <running total>
}
```

Add loaded tokens to `tokens_loaded`.

### Step 3 — Reason on the current context

Read all loaded chunks as a unified context. Attempt to answer the primary
question. During reasoning, explicitly audit for gaps using the heuristics in
the section above.

After reasoning, assign a **confidence score** between 0.0 and 1.0:
- `0.0–0.4`: major gaps; core policy or eligibility facts are missing
- `0.4–0.6`: partial answer; conditional branches cannot be resolved
- `0.6–0.85`: likely answer; one or two supporting facts are unconfirmed
- `0.85–1.0`: high confidence; answer is fully grounded in loaded context

Record any detected gaps as structured objects:
```json
{
  "gap_id": "g1",
  "description": "unclear if 7-day grace period applies to PRO accounts",
  "target_query": "PRO account grace period cancellation",
  "target_category": "subscription_management",
  "severity": "blocking"  // blocking | supporting
}
```

### Step 4 — Decide whether to fetch another slice

Evaluate stop criteria in this order:

1. If `confidence >= 0.85`: set `stop_reason = "confidence_threshold_met"`, go to Step 6.
2. If `round >= max_rounds` (default 5): set `stop_reason = "max_rounds_reached"`, go to Step 6.
3. If `tokens_loaded >= max_tokens` (default 12000): set `stop_reason = "token_budget_exhausted"`, go to Step 6.
4. If no gaps detected: set `stop_reason = "no_gaps_detected"`, go to Step 6.
5. If all remaining gaps have `severity = "supporting"` and `confidence >= 0.7`:
   optionally skip to Step 6 with `stop_reason = "sufficient_for_task"`.

Otherwise: proceed to Step 5.

### Step 5 — Fetch next slice targeting the highest-severity gap

Select the gap with `severity = "blocking"` and the highest retrieval
potential (i.e. a specific query can be formed). Formulate a targeted query
using the gap's `target_query` and `target_category`.

Load the **2 highest-scoring** chunks not already in context. Record in trace.
Increment `round`. Add tokens. Return to Step 3.

### Step 6 — Produce grounded answer and trace

Write `output/grounded-answer.md`:
- Open with a concise resolution statement (one paragraph)
- For each factual claim, add an inline citation: `[doc_id §section]`
- List the recommended agent action(s) with the specific API call or workflow
  step if determinable
- Close with the coverage-confidence flag:
  `Coverage confidence: X.XX (high | moderate | low)`

Write `output/retrieval-trace.json`:
- Array of all rounds with the fields shown in Step 2, plus:
  - `confidence_after_round`: score assigned in Step 3
  - `gaps_detected`: array of gap objects from Step 3
  - `stop_reason`: present only on the final round

Write `output/coverage-report.json`:
- Aggregated metrics (see output spec below)

---

## Output Format Specification

### grounded-answer.md
```
## Resolution

<One-paragraph answer to the primary question, citing all key facts>

## Supporting Evidence

| Claim | Source |
|-------|--------|
| <factual claim> | [doc_id §section] |

## Recommended Agent Actions

1. <action> — <brief rationale> [doc_id]

## Coverage Confidence: X.XX (high)
```

### retrieval-trace.json
```json
[
  {
    "round": 1,
    "query": "string",
    "docs_loaded": ["doc_id_1", "doc_id_2"],
    "tokens_this_round": 0,
    "cumulative_tokens": 0,
    "confidence_after_round": 0.0,
    "gaps_detected": [],
    "stop_reason": null
  }
]
```

### coverage-report.json
```json
{
  "confidence": 0.0,
  "stop_reason": "string",
  "total_rounds": 0,
  "total_tokens_loaded": 0,
  "gaps_identified": 0,
  "gaps_resolved": 0,
  "gaps_unresolved": 0,
  "efficiency_vs_full_load": {
    "full_load_tokens": 0,
    "loaded_tokens": 0,
    "reduction_pct": "0.0%"
  }
}
```

---

## Limitations

- **Latency**: each retrieval round adds a network round-trip to the vector
  store. For tasks where near-complete context is needed anyway, upfront
  loading may be faster overall.
- **Index quality dependency**: a weak embedding model or poorly chunked
  index will produce low-relevance first slices, forcing more rounds and
  eroding the efficiency gain.
- **Stop criteria calibration**: a confidence threshold that is too low
  risks under-retrieval; too high risks exhausting the round budget before
  reaching it. Tune per task type.
- **Non-decomposable questions**: questions that require holistic reading of
  many documents (e.g. "summarise all billing changes in 2024") do not
  benefit from iterative retrieval — use full-context loading instead.
