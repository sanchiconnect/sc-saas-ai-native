# SemanticCache

Content-hash + near-match result reuse for the customer-service chatbot optimization layer.

SemanticCache sits at the front of the agent pipeline and intercepts every inbound request. It returns stored answers for inputs that are identical (SHA-256 hash match) or semantically equivalent (cosine similarity >= 0.92) to a previously-answered query. On a hit, the downstream model is never invoked. On a miss, the model runs normally and the result is seeded into the cache.

In 30-day production data: 71.7% hit rate, 7.5M tokens avoided, $22.58 saved at Sonnet pricing.

---

## What to Cache vs. What to Never Cache

### Cache these

| Category | Examples | Rationale |
|---|---|---|
| FAQ answers | "What are your support hours?", "Do you offer a free trial?" | High frequency, stable content, no PII |
| Policy explanations | "What is your refund policy for double charges?", "How does annual billing work?" | Governed by policy docs; invalidated on doc change |
| Refund eligibility rules | "Can I get a refund after 30 days?", "How long does a refund take?" | General rules, not per-customer decisions |
| Standard apology templates | Service outage apology, wrong-item apology | Fixed text; cosmetic variation handled by semantic match |
| Escalation scripts | Upset customer script, business outage script | Template text; high reuse value |
| Product and pricing info | "What integrations do you support?", "Is there a user seat limit?" | Stable; changes rarely |
| Security policy | "Is my data secure?", "What do I do if my account is compromised?" | General guidance, not per-account status |

### Never cache these

| Category | Why |
|---|---|
| Per-customer account data | "What is my current balance?" — answer differs per customer |
| Order-specific queries | "Was I charged correctly for order #12345?" — references specific transaction |
| PII mutations | "My name is John, please update my email" — modifies personal data |
| Real-time status | "Is my payment processing right now?" — state changes faster than TTL |
| Salesforce CRM live lookups | Any query routed to a Salesforce tool call with live Account/Contact data |
| Queries containing account numbers | 10+ digit numbers are treated as account identifiers |
| Queries containing email addresses | Any string matching `@` pattern is treated as PII |
| Explicit account references | Queries containing "my account", "my order #", "my invoice #" |

The `never_cache_patterns` and `never_cache_regex_patterns` lists in `cache-config.json` enforce these rules automatically. Any matching query is passed directly to the model; no hash is stored.

---

## Similarity Threshold Tuning

The similarity threshold is the most consequential tuning parameter. It controls the trade-off between hit rate and answer correctness.

### Default: 0.92

This is a conservative setting appropriate for high-stakes customer-service responses involving billing and policy. At 0.92, you capture clear paraphrases ("What is your refund policy for double charges?" / "If a customer is billed twice, can they get their money back?") while rejecting queries with meaningfully different scope ("What happens to my account if I dispute a charge with my bank?" / "What is the policy for disputed transactions?" — similarity 0.81, correctly rejected).

### When to lower the threshold (0.88–0.91)

Lower the threshold for content that is stylistically flexible and low-risk to approximate:

- **Apology templates**: "I'm sorry for your experience" and "Please accept my apologies" carry identical customer impact. Set `apology_template` tag TTL to 72h and threshold to 0.88.
- **Escalation scripts**: Fixed procedural text. A 0.90 threshold captures more paraphrase variants without meaningful accuracy risk.
- **FAQ answers about non-policy facts**: "What payment methods do you accept?" is factually stable. 0.89 is appropriate.

To apply per-tag thresholds, add a `tag_similarity_overrides` block to `cache-config.json`:

```json
"tag_similarity_overrides": {
  "apology_template": 0.88,
  "escalation_script": 0.90,
  "payment_methods": 0.89
}
```

### When to raise the threshold (0.94–0.97)

Raise the threshold for content where small wording differences indicate meaningfully different intent:

- **Refund eligibility with time references**: "Can I get a refund after 14 days?" vs. "Can I get a refund after 30 days?" — similarity ~0.96 but the answer is completely different. Set `refund_rules` threshold to 0.97.
- **SLA and compliance topics**: "What is your SLA for billing disputes?" vs. "What is your SLA for security incidents?" — similarity ~0.93, different answers.
- **Anything touching regulatory language**: Raise to 0.95 minimum.

### How to measure threshold impact

```
SELECT
  similarity_bucket,
  COUNT(*) as hits,
  SUM(CASE WHEN verified_correct THEN 1 ELSE 0 END) / COUNT(*) as accuracy
FROM semantic_hit_log
GROUP BY FLOOR(similarity * 100) / 100 AS similarity_bucket
ORDER BY similarity_bucket;
```

In production data, the inappropriate hit rate at 0.92 threshold is 1.1% (23 out of 2,104 semantic hits). Raising to 0.95 would drop inappropriate hits to near-zero but would reduce the semantic hit rate from 16.9% to approximately 11%.

---

## Cache Invalidation Strategies

Stale entries serving outdated answers are the primary correctness risk. Apply all three layers:

### Layer 1: TTL-Based (automatic safety net)

Every entry is written with a `ttl_hours` value that forces expiry on a schedule, even if no explicit invalidation fires. This is the backstop for undetected changes.

| Tag | TTL | Rationale |
|---|---|---|
| `faq` | 72h | Stable content; long TTL maximizes hit rate |
| `billing_policy` | 24h | Policy can change; short TTL limits stale window |
| `refund_rules` | 24h | Same — financial impact of stale answer is high |
| `security_policy` | 48h | Medium stability; balance freshness vs. hit rate |
| `outage_response` | 1h | Outage status changes rapidly |
| Hard maximum | 168h | No entry persists longer than 7 days regardless of tag |

Configure in `cache-config.json` → `ttl_policy.ttl_by_source_tag`.

### Layer 2: Source-Document Monitoring (proactive correctness)

Register a SHA-256 hash of every source document that informs cached answers. Check document hashes on a configurable interval (default: 60 minutes). When a hash changes:

1. The CMS webhook fires `POST /cache/invalidate` with the relevant tag.
2. All entries tagged with that source are deleted immediately.
3. Entries are re-seeded by the next wave of customer traffic.

Add a cache invalidation step to every content update workflow:

```
Policy updated in CMS
  → CMS webhook fires → POST /cache/invalidate {tag: "billing_policy"}
  → 10 entries purged instantly
  → Next 10 customer queries re-seed cache with new content
```

Register sources in `cache-config.json` → `invalidation_settings.source_document_hashes`.

### Layer 3: Explicit Invalidation API (manual override)

For policy changes that originate outside the document system (e.g., a Salesforce CRM field change, a Finance team decision, a Legal requirement):

```bash
# Invalidate one specific entry
POST /cache/invalidate
{ "content_hash": "a3f8c2d17e4b9056..." }

# Invalidate all entries for a policy area
POST /cache/invalidate
{ "tag": "refund_rules" }

# Emergency full flush
POST /cache/flush_all
{ "confirm": true, "reason": "major_policy_overhaul" }
```

Integrate explicit invalidation into your change management process:

- Billing policy changes → `invalidate_by_tag("billing_policy")`
- Refund limit changes → `invalidate_by_tag("refund_rules")`
- Security policy changes → `invalidate_by_tag("security_policy")`
- SLA changes → `invalidate_by_tag("sla")`

### Invalidation Checklist for Policy Changes

Before deploying any customer-facing policy change:

- [ ] Identify all `source_tags` in `cache-store.json` affected by the change
- [ ] Fire `invalidate_by_tag` for each affected tag
- [ ] Pre-seed 3–5 representative queries via the warm-cache API to accelerate hit-rate recovery
- [ ] Monitor cache-invalidation-log.json to confirm entries were purged
- [ ] Verify the first post-invalidation misses generate correctly-updated answers before hit rate recovers

---

## Integrating SemanticCache with the Full Optimization Pipeline

SemanticCache is the first interceptor in the pipeline. On an exact or semantic hit, the request exits immediately — no other agents are invoked and the model is not called.

```
Inbound customer query
        |
        v
 [SemanticCache]
  Hash lookup → exact hit? ──────────────────────────────> Return cached result (0 tokens, 2ms)
        |
        | miss — semantic enabled?
        v
  Embed input (~300 tokens)
  ANN search in vector index
  similarity >= 0.92? ─────────────────────────────────> Return semantic hit + warning (300 tokens, 45ms)
        |
        | miss
        v
 [PromptShield]          ← PII detection, injection guard
        |
        v
 [ModelRouter]           ← Select cheapest capable model for this query
        |
        v
 [Model invocation]      ← Claude Haiku / Sonnet depending on routing
        |
        v
 [SemanticCache seed]    ← Store result: hash + embedding + metadata
        |
        v
  Return to customer
```

### Integration points

**Before SemanticCache**: No preprocessing needed. SemanticCache accepts raw query strings.

**After a cache hit**: Skip PromptShield, ModelRouter, and the model entirely. Return `cache_results.lookup_outcome.cached_result` directly to the response formatter.

**After a cache miss with seeding**: The result returned from the model is passed to `cache_store.put()` before the response is sent. This adds ~5ms overhead but ensures the next identical or near-identical query is a cache hit.

**Semantic hit verification**: When `cache_type == "semantic"`, pass the cached result through a lightweight Haiku verification prompt before surfacing to the end user:

```
SYSTEM: You are a quality-check agent. Given an original customer query and a cached answer,
confirm in one word — YES or NO — whether the cached answer appropriately addresses the query.

USER: Query: "{new_query}"
Cached answer: "{cached_result}"
Is this answer appropriate?
```

This verification call consumes ~200 tokens and takes ~300ms — still far cheaper than a full Sonnet invocation (~840 tokens, ~1200ms).

### Environment variables

```bash
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_STORE_PATH=./cache/semantic-cache.json
SEMANTIC_CACHE_THRESHOLD=0.92
SEMANTIC_CACHE_EMBEDDING_MODEL=text-embedding-3-small
SEMANTIC_CACHE_DEFAULT_TTL_HOURS=24
SEMANTIC_CACHE_MAX_ENTRIES=10000
SEMANTIC_CACHE_ADMIN_TOKEN=<your-secret>
```

### Monitoring

Watch these metrics to detect cache health issues:

| Metric | Healthy range | Alert threshold |
|---|---|---|
| Overall hit rate | 65–80% | < 50% (cache warming needed) |
| Semantic inappropriate hit rate | < 2% | > 5% (threshold too low) |
| P95 exact hit latency | < 10ms | > 50ms (index issue) |
| Entries exceeding hard max age | 0 | > 0 (TTL sweep failing) |
| Invalidation lag (change to purge) | < 5 min | > 30 min (webhook failing) |

---

## Files in This Skill

| File | Purpose |
|---|---|
| `SKILL.md` | Full algorithm specification, safety rules, TTL policy, invalidation rules |
| `input/cache-store.json` | Simulated production cache with 25 seeded entries |
| `input/new-request.json` | Three test requests covering exact hit, semantic hit, and miss scenarios |
| `input/cache-config.json` | Full configuration file with all tunable parameters |
| `output/cache-results.json` | Lookup results for all three test requests with full audit trail |
| `output/cache-metrics.json` | 30-day rolling performance metrics and recommendations |
| `output/cache-invalidation-log.json` | Recent invalidation events with correctness analysis |
