---
type: index
repo: ai-analyzer
updated: 2026-07-19
---

# AI Analyzer Module Specs Index

Master index of all `ai-startups-analyzer` module specs. This is a **Python/FastAPI AI scoring service** called by `sc-saas-admin` to evaluate startup applications using LLMs (OpenAI/Anthropic/Gemini via `DEFAULT_PROVIDER`). It has its own MySQL database and is one-directional — admin calls it, it never calls back.

**Scoring invariant:** Model outputs 0–500. Persisted as 1–5 (÷100). Backend column `decimal(4,3)`. `_coerce_rating()` in `routes.py` is the ONLY place this conversion happens — never change the scale.

**No test suite.** Manual integration testing only.

## Core

| Module | Spec | Description |
|---|---|---|
| core-bootstrap | [module.spec.md](../ai-startups-analyzer/api/app/module.spec.md) | FastAPI app setup, lifespan (DB init + task cleanup), status.json, async SQLAlchemy pool, _sync_missing_columns() auto-migration, CORS (currently allows all origins) |
| data-models | [models_spec.md](../ai-startups-analyzer/api/app/core/models_spec.md) | 17 Pydantic DTOs + 3 SQLAlchemy ORM models (Analysis, Batch, APIKey); cost tracking columns added via migration 001 |

## Scoring

| Module | Spec | Description |
|---|---|---|
| scoring-engine | [scoring_engine_spec.md](../ai-startups-analyzer/api/app/api/v1/scoring_engine_spec.md) | All 19 API endpoints; batch orchestration; _coerce_rating (0–500→1–5); weighted criteria mode; fallback scoring; concurrency semaphores; routes_back.py is legacy, not imported |
| ai-provider | [ai_provider_spec.md](../ai-startups-analyzer/api/app/core/ai_provider_spec.md) | Provider facade (DEFAULT_PROVIDER switch); per-provider JSON-forcing; token extraction; USD cost computation; per-domain pricing overrides |

## Enrichment

| Module | Spec | Description |
|---|---|---|
| enrichment | [enrichment_spec.md](../ai-startups-analyzer/api/app/core/enrichment_spec.md) | Serper.dev search + Firecrawl scrape; best-effort (never blocks scoring); 75s budget cap per batch; ENABLE_ENRICHMENT=0 default |

---

## Security & architectural findings

| Severity | Area | Finding |
|---|---|---|
| 🟡 Medium | core-bootstrap | CORS defaults to `allow_origins=["*"]` when `ANALYZER_CORS_ORIGINS` is unset. Downgraded from Critical (as of the `Harden analyzer` fix, 2026-07-02): `allow_credentials` is now correctly forced `False` whenever origins are `["*"]`, so the wildcard no longer leaks credentialed cross-origin access. Residual risk: unauthenticated non-credentialed cross-origin calls until the env var is set explicitly in prod |
| 🟠 High | core-bootstrap / scoring-engine | API key auth is O(N × bcrypt) per request — `get_api_key` (routes.py) iterates every row in `api_keys` and calls `bcrypt.checkpw` on each; scales poorly with issued-key count |
| 🟠 High | scoring-engine | Single CLOUD_API_KEY shared across all tenants — rate-limit hit on one run affects all concurrent analyses |
| 🟠 High | scoring-engine | No test suite — scoring logic changes cannot be validated before deploy |
| 🟠 High | enrichment | Scraped website content embedded in scoring prompt without sanitization — prompt injection risk |
| 🟡 Medium | scoring-engine | Dual status tracking (DB + responseStatus.json file) can drift on crash between writes |
| 🟡 Medium | scoring-engine | routes_back.py (2,434 lines) sits in routes folder but is NOT imported — dead code causing confusion |
| 🟡 Medium | scoring-engine | `scoring_engine_spec.md`'s Invariants section is stale re: `_weighted_rating()` — a 2026-07-17 fix (`8e4677c`) changed it to round to 3 decimals directly (`round(x, 3)`, matching its own docstring); the spec still describes it as producing 2-decimal output via an internal call to `_coerce_rating`, which is no longer accurate |
| 🟡 Medium | ai-provider | Temperature parameter silently ignored for some OpenAI models (OPENAI_TEMPERATURE optional) |
| 🟡 Medium | enrichment | Both Serper and Firecrawl keys optional — silently skipped with no user warning if absent |
| 🟡 Medium | data-models | Thesis generation cost not stored in DB — no audit trail for thesis calls |

Updated: 2026-07-19
