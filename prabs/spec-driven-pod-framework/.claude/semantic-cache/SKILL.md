---
name: semantic-cache
description: "SemanticCache eliminates redundant model invocations by returning stored results for inputs that are identical (exact hash match) or semantically equivalent (cosine similarity >= threshold) to a previously-answered query. On a hit the full downstream model call is skipped; on a miss the result is computed normally and then seeded into the"
---

**name:** semantic-cache

**tagline:** Content-hash + near-match result reuse

**model:** deterministic + claude-haiku-4-5

**tokens_per_invocation:** ~1K (semantic path only; exact hits are zero-token)

**inputs:**
- prompt / file / artifact (the raw input to the agent pipeline)
- content_hash: SHA-256 of normalized input
- cache_store: path or handle to the JSON/vector cache store
- similarity_threshold: float, default 0.92

**outputs:**
- cached result (hit) or pass-through signal (miss)
- hit_metadata: { cache_type, similarity, tokens_saved, latency_ms, warning? }
- session_metrics: { hit_rate, tokens_avoided }

**description:** SemanticCache eliminates redundant model invocations by returning stored results for inputs that are identical (exact hash match) or semantically equivalent (cosine similarity >= threshold) to a previously-answered query. On a hit the full downstream model call is skipped; on a miss the result is computed normally and then seeded into the cache for future callers.

# SemanticCache Skill

## Purpose

Repeatable agent pipelines — FAQ bots, policy look-ups, template generation —
receive the same or near-identical inputs thousands of times a day.
SemanticCache intercepts every inbound request, checks a two-tier cache
(exact hash first, then embedding similarity), and returns a stored answer
instantly when the input has already been handled.  A cache hit avoids the
full model invocation, cutting both latency and token cost to near-zero on
the hot path.

---

## Lookup Algorithm (6 steps)

### Step 1 — Normalize and Hash

Normalize the raw input before hashing to maximise exact-hit rate:

```
normalized = input
  .strip()
  .lower()
  .replace(/\s+/g, ' ')        # collapse all whitespace to single space
  .replace(/[^\w\s?.,!]/g, '') # remove special characters except punctuation
```

Compute the SHA-256 content hash:

```
content_hash = sha256(normalized)   # 64-character hex string
```

The hash is the primary cache key.  Normalization is critical: "What is your
refund policy?" and "what is your refund policy ?" must produce the same hash.

### Step 2 — Exact Lookup (zero tokens, ~1–3 ms)

Query the cache store by `content_hash`:

```
entry = cache_store.get(content_hash)
if entry and not is_expired(entry):
    entry.hit_count += 1
    entry.last_accessed = now()
    return CacheResult(
        status       = "hit",
        cache_type   = "exact",
        result       = entry.result,
        similarity   = 1.0,
        tokens_saved = entry.tokens_saved,
        latency_ms   = measured_lookup_time
    )
```

An exact hit requires zero LLM tokens.  Return immediately; do not proceed to
semantic search.

Expiry check:

```
is_expired(entry) = (now() - entry.created_at) > entry.ttl_hours * 3600
```

Expired entries are removed lazily on access (or eagerly by a background
sweep — see Cache Invalidation section).

### Step 3 — Compute Input Embedding (semantic path, ~200–400 tokens)

Only reached on a cache miss or an expired exact entry, **and** only when
`semantic_cache_enabled: true` in `cache-config.json`.

Use the configured embedding model (`text-embedding-3-small` by default) to
embed the normalized input:

```
input_vector = embed(normalized, model=config.embedding_model)
# returns float[1536] for text-embedding-3-small
```

This step consumes roughly 200–400 tokens depending on input length.  The
embedding call is made against the same API key as the main model; cost is
~$0.00002 per 1K tokens (text-embedding-3-small) and is negligible compared
to a full Sonnet invocation.

### Step 4 — Nearest-Neighbor Search (vector index)

Search the cache embedding index for the closest stored vector:

```
(best_entry, cosine_sim) = vector_index.nearest_neighbor(
    query_vector = input_vector,
    top_k        = 1
)
```

The embedding index is a flat FAISS index (for ≤ 100K entries) or an
approximate HNSW index (for larger stores).  The index is rebuilt from the
JSON cache store at startup and updated incrementally on each new cache write.

Cosine similarity ranges from -1 (opposite) to 1 (identical).  For
production customer-service queries, valid matches typically fall in the
0.90–0.99 range.

### Step 5 — Semantic Hit Decision

```
if cosine_sim >= config.similarity_threshold:   # default 0.92
    if not is_expired(best_entry):
        return CacheResult(
            status    = "hit",
            cache_type = "semantic",
            result    = best_entry.result,
            similarity = cosine_sim,
            tokens_saved = best_entry.tokens_saved,
            latency_ms   = measured_lookup_time,
            warning   = "semantic_match_verify_appropriateness"
        )
```

The `warning` flag is **mandatory** for semantic hits.  The caller (or a thin
verification layer) must confirm the cached answer is appropriate for the
specific phrasing before surfacing it to the end user.  See Safety Rules below.

If `cosine_sim < config.similarity_threshold`, treat as a miss and proceed to
Step 6.

### Step 6 — Cache Miss: Pass Through and Seed

```
# Pass the original (un-normalized) input to the model
model_result = invoke_downstream_model(original_input)

# Store the result for future callers
new_entry = {
    cache_key     : generate_cache_key(),   # UUID
    content_hash  : content_hash,
    embedding_vector : input_vector,        # store for future ANN search
    query         : original_input,
    result        : model_result,
    created_at    : now(),
    ttl_hours     : select_ttl(model_result),  # see TTL Policy
    hit_count     : 0,
    last_accessed : now(),
    cache_type    : "seeded"
}
cache_store.put(content_hash, new_entry)
vector_index.add(input_vector, cache_key=new_entry.cache_key)

return CacheResult(
    status       = "miss",
    result       = model_result,
    tokens_saved = 0,
    new_entry_created = true
)
```

---

## Cache Invalidation Rules

Stale entries returning outdated answers are the primary risk of any cache.
Apply the following invalidation strategy in layers:

### TTL-Based (time-to-live)

| Content category | Default TTL | Rationale |
|---|---|---|
| Static FAQ answers | 72 hours | Rarely change; high hit value |
| Policy / billing rules | 24 hours | Change with policy updates |
| Dynamic data (balance, order status) | 1 hour | Frequent state changes |
| Personalized / PII-adjacent answers | Never cache | See Safety Rules |

TTL is attached to each entry at write time.  The sweep job runs every 15
minutes and prunes expired entries from both the JSON store and the vector
index.

### Content-Change-Based (proactive invalidation)

When a source document (e.g., the billing policy PDF) changes:

1. Re-hash the source document.
2. If the hash differs from the stored source hash, call `invalidate_by_tag(tag)`.
3. All cache entries tagged with that source (e.g., `tag: "billing_policy"`) are
   deleted immediately, regardless of TTL.

Register source hashes at cache write time:

```
new_entry.source_tags = detect_source_tags(model_result)
# e.g., ["billing_policy", "refund_rules"]
```

### Explicit Invalidation API

Expose three endpoints / functions for programmatic invalidation:

```
invalidate_by_hash(content_hash)         # remove one exact entry
invalidate_by_tag(tag: str)              # remove all entries with matching tag
invalidate_by_query(query: str)          # normalize → hash → remove if present
flush_all()                              # emergency full cache clear
```

Call `invalidate_by_tag("billing_policy")` whenever the billing policy
document is updated in the CRM or content management system.

### Version-Based Cache Segmentation

When the underlying model is upgraded (e.g., Haiku 3 → Haiku 4-5), responses
may differ.  Segment the cache by model version:

```
versioned_hash = sha256(f"{model_version}:{normalized_input}")
```

This prevents old cached answers from being served by the new model version.

---

## Safety Rules

### 1. Semantic hits require verification

All results returned with `cache_type: "semantic"` carry a mandatory
`warning: "semantic_match_verify_appropriateness"` field.  The calling agent
or middleware layer must either:

- Display the similarity score to a human reviewer before surfacing the answer, or
- Run a lightweight classifier (e.g., Haiku with a 2-shot prompt) that
  confirms the cached answer is semantically valid for the specific phrasing.

Never serve a semantic cache hit to an end user without at least one of the
above checks.

### 2. Never cache PII or dynamic personal data

The `never_cache_patterns` list in `cache-config.json` must be checked against
every incoming query before the cache lookup proceeds.  If any pattern matches,
skip the cache entirely:

```python
for pattern in config.never_cache_patterns:
    if pattern in normalized_input:
        return invoke_downstream_model(original_input)  # bypass cache
```

Default never-cache patterns:
- `customer_id`
- `account_number`
- `personal_data`
- `real_time_balance`
- Any query containing a 10+ digit number (likely an account or card number)
- Any query containing `@` (likely an email address)
- Any query referencing "my account", "my order #", "my balance"

### 3. Cache type transparency

Every cache response delivered to an end user must include (in internal
metadata, not necessarily visible to the user):

```json
{
  "cache_type": "exact" | "semantic" | "miss",
  "similarity": 0.0–1.0,
  "served_from_cache": true | false,
  "original_query_in_cache": "..."
}
```

This enables downstream audit and debugging when a wrong cached answer is
reported.

---

## Customer Service Caching Policy

### Cache these

- Billing policy explanations ("What is your refund policy?")
- FAQ answers ("What are your support hours?")
- Standard apology templates ("We apologize for the inconvenience...")
- Escalation scripts (fixed text, not personalized)
- Product feature descriptions
- Refund eligibility rules (general, not per-customer)

### Never cache these

- "What is my current balance?" — per-customer dynamic data
- "Was I charged correctly for order #12345?" — references specific order
- "My name is John, can you update my email?" — PII mutation
- Any query containing a Salesforce Account ID or Contact ID
- Any query routed through the Salesforce CRM tool call with live data

---

## Integration with the Optimization Pipeline

SemanticCache is the first interceptor in the pipeline, before all other
optimization agents (PromptShield, ModelRouter, etc.):

```
Inbound request
    ↓
[SemanticCache] ← check cache
    ↓ miss
[PromptShield]  ← PII / injection guard
    ↓ clean
[ModelRouter]   ← select cheapest capable model
    ↓
[Model invocation]
    ↓ result
[SemanticCache] ← seed result into cache
    ↓
Response to user
```

On a cache hit, the request exits the pipeline after SemanticCache and none of
the downstream agents are invoked.

---

## Performance Characteristics

| Path | Latency | Tokens consumed |
|---|---|---|
| Exact hit | 1–5 ms | 0 |
| Semantic hit | 20–60 ms | ~300 (embedding only) |
| Miss (with seeding) | Full model latency + 30 ms | Full prompt + completion + ~300 embedding |

At 71.7% hit rate (see `cache-metrics.json`), a deployment handling 12,450
requests/month avoids 8,927 full model invocations, saving ~7.5M tokens and
$22.58/month at Sonnet pricing — with median response latency dropping from
~1,200 ms to ~5 ms on the hot path.
