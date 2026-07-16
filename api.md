# SanchiSaaS — Workspace API Index

Last updated: 2026-07-14

This is a cross-repo API surface **index**, not a re-listing of every endpoint — each repo's own `api.md`
already has the exhaustive route-by-route detail. This document exists to answer two questions a per-repo
doc can't: "which repo owns what, at a glance" and "what actually calls what, across the whole workspace,
including the calls the per-repo docs don't yet agree on." Citations point to the per-repo `api.md`/
`knowledge.md` this was pulled from; `[AS-IS]` throughout.

Of the seven repos, **four own a real machine-callable API surface**: `sanchiconnect-saas-tenants`,
`sc-saas-backend`, `ai-startups-analyzer`, `sc-saas-3rdparty-webservices`. The other three do not:
`sc-saas-frontend` is a pure client with no server-side API of its own; `sc-saas-admin` and
`sanchiconnect-saas-tenants-admin` are PHP request-handler dispatchers (`index.php?action=...`), not
versioned REST APIs meant for external consumption — they are documented in this workspace's `knowledge.md`
and `design.md` as consumers, not producers, of API contracts.

---

## What each API-owning repo owns, in one line

| Repo | Owns | Most cross-repo-critical endpoint |
|---|---|---|
| `sanchiconnect-saas-tenants` | Tenant-verification contract + feature-flag names + AI-Credits purchase-side API | `GET /api/v1/public/global/verify_tenant/:hostname` — the frontend's app-init-blocking bootstrap call; also read by nothing else, since `tenant-settings` is the *backend's* bootstrap call instead (two different routes for two different consumers — see `design.md`) |
| `sc-saas-backend` | The platform's business REST API contract (58 feature modules) | `GET /api/v1/public/global/saas/settings` (PATCH variant) — undocumented cross-repo caller: `sanchiconnect-saas-tenants-admin` hits this unauthenticated route directly on every `tenant_users` edit (see `knowledge.md` §5) |
| `ai-startups-analyzer` | AI-scoring lifecycle (upload → batch → poll → finalize) | `POST /api/v1/finalize-analysis/` — the one point where the frozen 0–500→1–5 scoring contract becomes irreversible in the admin's own DB |
| `sc-saas-3rdparty-webservices` | Seven third-party integration proxies (SMS, 2×email, chat, 2×video, short-links, doc-convert) | `GET /api/v2/video-sdk/meetings/:meetingId/sessions` and `POST /api/v1/short-io/short-url` — the two routes `sc-saas-admin` calls directly, bypassing the documented `sc-saas-backend`-only caller path, one of them with **no auth header at all** |

For the full endpoint-by-endpoint contract of each, see:
- `sanchiconnect-saas-tenants/api.md`
- `sc-saas-backend/api.md`
- `ai-startups-analyzer/api.md`
- `sc-saas-3rdparty-webservices/api.md`

---

## The real call graph — every confirmed cross-repo call relationship

Each row cites the per-repo doc that confirmed it. "Documented?" reflects whether the workspace `CLAUDE.md`'s
blast-radius graph already shows this edge.

| # | Caller | Callee | Endpoint(s) | Documented in workspace CLAUDE.md? | Confirmed by |
|---|---|---|---|---|---|
| 1 | `sc-saas-backend` | `sanchiconnect-saas-tenants` | `GET /v1/public/global/tenant-settings/:hostname` (bootstrap) | Yes | `sc-saas-backend/knowledge.md` §Bootstrap Sequence, cross-confirmed from producer side by `sanchiconnect-saas-tenants/design.md` |
| 2 | `sc-saas-frontend` | `sanchiconnect-saas-tenants` | `GET /v1/public/global/verify_tenant/:hostname` | Yes | `sc-saas-frontend/knowledge.md` §Bootstrap / Tenant-Verification Flow |
| 3 | `sc-saas-frontend` | `sc-saas-backend` | dynamic `apiUrl` from #2, all `core/service/*` | Yes | `sc-saas-frontend/knowledge.md` §Bootstrap; `sc-saas-frontend/design.md` |
| 4 | `sc-saas-admin` | `sanchiconnect-saas-tenants` DB | direct Medoo read (not an API call) | Yes | `sc-saas-admin/knowledge.md` §Tenancy Resolution |
| 5 | `sc-saas-admin` | `sc-saas-backend` | `api_server_url` (`v1/admin-actions/*`, `v1/public/global/clear/cache/all`, etc.) | Yes | `sc-saas-admin/knowledge.md` §Third-Party Integration Pattern |
| 6 | `sc-saas-admin` | `ai-startups-analyzer` | full scoring lifecycle (upload/start/poll/finalize/re-enrich) | Yes | `sc-saas-admin/knowledge.md` §Application Management — AI Analysis / Scoring Flow |
| 7 | `sc-saas-backend` | `sc-saas-3rdparty-webservices` | six proxy services (`sms`, `sendGrid`/`ses`, `cometChat`, `videoSDK`, `shortIo`, `convertKit`) | Yes | `sc-saas-backend/knowledge.md` §The Six Third-Party-Proxy Services |
| 8 | `sc-saas-backend` | `power-pitch-sanchiconnect-api` (external) | `/v1/externals/*` | Yes (invariant #6) | `sc-saas-backend/knowledge.md` §PowerPitch External Integration |
| **9** | **`sc-saas-admin`** | **`sc-saas-3rdparty-webservices`** | `GET /v2/video-sdk/meetings/{code}/sessions` (no auth header), `POST /v1/short-io/short-url` | **No — contradicts "called only by backend"** | `sc-saas-admin/knowledge.md` §Third-Party Integration Pattern; confirmed from receiving side at `sc-saas-3rdparty-webservices/knowledge.md` §Reality Check |
| **10** | **`sc-saas-admin`** | **`sanchiconnect-saas-tenants`** | `POST /api/v1/ai-credits/webhooks/easebuzz/{success,failure}` (via `easebuzz_callback.php`, outside the app's own dispatcher) | **No — undocumented 4th-repo edge** | `sc-saas-admin/knowledge.md` §Third-Party Integration Pattern |
| **11** | **`sanchiconnect-saas-tenants-admin`** | **`sc-saas-backend`** | `PATCH /api/v1/public/global/saas/settings` (every `tenant_users` edit); conditional `v1/admin-actions/admin-account-created/:token` | **No — contradicts this repo's own "fully standalone" claim** | `sanchiconnect-saas-tenants-admin/knowledge.md` §(g), cross-referenced against `sc-saas-backend/src/modules/global/global.controller.ts:51` |
| 12 | `sanchiconnect-saas-tenants-admin` | `sanchiconnect-saas-tenants` DB | direct Medoo read/write (shared DB, not an API call) | Yes | `sanchiconnect-saas-tenants-admin/knowledge.md` §(c) |
| 13 | `sanchiconnect-saas-tenants` (ecosystem/IP-management modules) | `sc-saas-backend` (another tenant's own deployment) | `GET api/v1/{type}s/public/{type}-information/{uuid}`, tenant-to-tenant | Yes (implicit in ecosystem feature) | `sanchiconnect-saas-tenants/knowledge.md` §Ecosystem Directory |
| 14 | `sc-saas-admin` | Zoho / WATI / Google Gemini / PayPal / Stripe / Razorpay / Easebuzz / PayU (all external) | direct `curl_init`, bypassing both `sc-saas-backend` and the 3rd-party gateway | N/A (external) — but undocumented in this repo's own `CLAUDE.md` | `sc-saas-admin/knowledge.md` §Third-Party Integration Pattern |
| 15 | `ai-startups-analyzer` | (nothing — confirmed leaf) | — | Yes | `ai-startups-analyzer/knowledge.md`, repo-wide |
| 16 | `sc-saas-3rdparty-webservices` | (nothing — confirmed leaf, outbound direction only) | — | Yes | `sc-saas-3rdparty-webservices/knowledge.md` §Bootstrap |

Rows 9, 10, and 11 are the three confirmed contradictions of the documented graph — see `knowledge.md` §3
for the full corrected-graph narrative and `design.md` for the architectural read on why this matters.

---

## Envelope shapes — a note for anyone writing a cross-repo client

Every NestJS repo wraps success responses in `{ status_code, message, data }` via a `TransformInterceptor`,
but **error envelopes are not uniform**: `sc-saas-3rdparty-webservices`'s `GlobalExceptionFilter` produces
`{ status_code, message, error }` (note `error`, not `data`) on failure — a client that only inspects
`data` on every response will find it silently `undefined` on that repo's error path.
`[Source: sc-saas-3rdparty-webservices/api.md/knowledge.md §Response Envelope]` `ai-startups-analyzer`
manually wraps every response as `{ message, data }` with no interceptor (Python, not Nest) — structurally
similar but not code-shared. `[Source: ai-startups-analyzer/CLAUDE.md §Conventions]`

---

## Change Log

- 2026-07-16 | Independently re-confirmed rows 9 and 11 of the real call graph directly against current code
  (exact function names, line numbers, and endpoint paths all matched) and propagated the corrections into
  the actual `sc-saas-3rdparty-webservices` and `sanchiconnect-saas-tenants-admin` `CLAUDE.md` files, which
  hadn't been updated despite this index already stating both corrections on 2026-07-14.
- 2026-07-14 | Initial workspace-level API index. Built from the four API-owning repos' own `api.md` section
  headers plus each of the seven repos' `knowledge.md` "who calls whom" findings. Assembled the 16-row real
  call graph, flagging rows 9–11 as confirmed contradictions of the workspace `CLAUDE.md`'s documented
  blast-radius graph.
