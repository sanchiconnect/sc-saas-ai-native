# design.md — SanchiConnect Technical Design & Architecture

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 2 of 6
**Consolidates:** TAD v1.0, SRS v1.0 (§2.5, §5–8), the team's six per-repo module-spec indexes and 26 feature specs, the `sc-saas-backend` steering file, and the Sanchi Credits Sprint Plan.
**Positioning:** the architecture overview that sits above the team's per-repo indexes and feature specs — the single system-wide view their bottom-up specs do not consolidate.
**Security scope:** this document describes the security *architecture*. Security *findings, verification, and remediation* belong to Track B and are held in the companion Reconciliation document; they are out of scope here.

> Gaps are marked inline as **GAP · D-N** and collected in **§99**. The register lists only open items requiring resolution.

---

## 1. Purpose & Scope

Specifies **how** SanchiConnect is built: architectural style, component and repository topology, the technology stack of each part, the multi-tenancy and entitlement mechanisms, the integration boundaries, the security architecture, the non-functional requirements, and the deployment model. It is the home of the parts the FRS excludes — backend services, third-party gateways, and the tenant control plane.

## 2. Architectural Style & Principles

A layered, service-oriented architecture with strict separation of presentation, application/business-logic, and data layers. The client applications are architecturally independent front ends that never touch a database directly. Four principles govern every part: **separation of concerns**, **API-first integration** (every cross-boundary interaction goes through a versioned contract), **configuration over code** (tenant behaviour is data-driven, never per-tenant code branches — the same binaries serve every tenant), and **tenant isolation by design** (data access is scoped to a single resolved tenant at the point of access).

## 3. System Context & Component Architecture

### 3.1 High-level architecture
Two client applications call the Business API, which depends on the Tenant Control Plane, the per-tenant Data Layer, and the Integration Gateway. The AI Evaluation Service is called one-directionally by the administration panel. Real-time features use WebSocket channels alongside REST.

### 3.2 Component & repository topology
| Component | Repo | Stack | Scale |
|-----------|------|-------|-------|
| Member Web Application | `sc-saas-frontend` | Angular / NgRx PWA (38 NgRx effects) | 26 modules |
| Administration Panel | `sc-saas-admin` | PHP / Medoo / sparkAdminTpl, server-rendered + AJAX | ~20 modules |
| Business API Services | `sc-saas-backend` | NestJS 8 / TypeScript / TypeORM 0.3 / MySQL | 58 modules |
| Tenant Control Plane | `sanchiconnect-saas-tenants` | NestJS / TypeORM, single shared MySQL | organizations, subscriptions, tenants, global, ecosystem, ip/facility |
| AI Evaluation Service | `ai-startups-analyzer` | Python / FastAPI, own MySQL, async SQLAlchemy | scoring-engine, ai-provider, enrichment |
| Integration Gateway | `sc-saas-3rdparty-webservices` | NestJS, stateless, no DB | 7 provider proxies |

Three architectural facts shape the rest of this document. The **admin panel connects directly to two databases** (`$mainDatabase` = the control-plane DB; `$database` = the per-tenant business DB) *and* calls the backend REST API, so it is not a pure API client. The **AI analyzer is one-directional** — the admin calls it; it never calls back. The **3rd-party gateway is a stateless leaf** reachable only by the backend via `THIRD_PARTY_SERVICE_BASE_URL`.

## 4. Technology Stack

Polyglot, per §3.2. Backend conventions: global prefix `api`, URI versioning (`api/v{n}/…`), Swagger (`api/docs`, local only), `class-validator` with a global `ValidationPipe({ whitelist: true })`, `TransformInterceptor` responses, JWT via cookie `accessToken` with Bearer fallback, guards `JwtAuthGuard`/`FeatureGuard`/`RolesGuard`/`OptionalJwtAuthGuard`, and a per-module structure of controller + service + `dto/` + `entities/` + `repositories/`. The analyzer uses `DEFAULT_PROVIDER` (gemini/openai/anthropic) with per-provider JSON-forcing and USD cost computation.

## 5. Multi-Tenancy Architecture

Two distinct isolation layers:

- **Business data — database-per-tenant.** Each tenant's operational data lives in its own logical MySQL database, resolved dynamically for the request. There is no tenant-identifier column threaded through business tables.
- **Control plane — single shared DB, row-per-tenant by `domain`.** `TenantUsersEntity` holds one row per tenant, scoped by `domain`; every control-plane query filters by `domain`. This shared DB holds tenant identity, per-tenant database connection details, branding, and the feature flags.

**Tenant resolution.** Both front ends and the backend bootstrap by calling the control plane's `verify_tenant/:hostname` and `tenant-settings/:hostname` — a frozen contract. The response establishes the backend API address, the enabled features, and the branding for the session; the backend caches it in memory at boot.

Two operational constraints follow from this and shape the data and migration model: new boolean flag columns default to `null` (not `false`) for existing tenant rows until backfilled, so consumers must not rely on strict `=== true` without accounting for `null`; and the control plane uses TypeORM in development where schema changes auto-apply, so **production requires explicit migrations**. Both are elaborated in `database.md`.

## 6. Feature Configuration & Entitlement Architecture

Feature flags are **boolean columns on `TenantUsersEntity`** in the control-plane DB — 218 of them (217 genuine feature flags plus one status field, `active`), for example `application_management`, `learning_management`, `jobs`, `startups`, `business_challenges`, `mentors`, `community_feed`, `connections`, `payment_gateways`, `venture_studio`, `online_meetings`, `chat`, `elastic_search`, `is_patent_hub`, `is_facility_hub`, `single_session_login_enabled`, `external_sign_in_enabled`). The `verify_tenant` response payload *is* the flag source of truth. The backend loads them into an in-memory map and enforces them with `@Features([...]) + FeatureGuard`; the frontend reads them as `IFeatures`; the PHP admin reads them via `config.php`. Note that only **78** of these 217 flags currently have a `Feature`-enum member, so roughly **143 have no backend `@Features(...)` gate** today — a coverage gap worth confirming (frontend/admin-only toggles vs missed backend enforcement). Code-verified 2026-07-21.

**Cross-repo contract invariant.** `TenantUsersEntity` column names are the contract: a rename breaks the backend `Feature` enum, the frontend `IFeatures`, and the admin `config.php` simultaneously. Run `/trace-flag` before any flag-column change.

## 7. API Design

Versioned REST. Every endpoint validates and authorises independently — no endpoint trusts client-side validation as an authorisation boundary. Responses and errors use consistent structured shapes (`TransformInterceptor`); request bodies are validated by DTOs under a whitelisting `ValidationPipe`. The team's feature specs already declare a substantial partial API contract in their `contracts.api` blocks (auth, ecosystem, search, programs, payments, meetings, and more); **`api.md` consolidates these into the full endpoint contract.**

## 8. Integration Architecture

Each category is a discrete boundary so a provider can be swapped or added without touching core domain logic. The gateway proxies:

| Provider proxy | External provider | Backend caller |
|----------------|-------------------|----------------|
| `sms` | Auth.key.io | `sms.service.ts` |
| `sendGrid` | SendGrid | `ses-email.service.ts` |
| `ses` | AWS SES | `ses-email.service.ts` |
| `cometChat` | CometChat | `comet-chat.service.ts` |
| `videoSDK` | VideoSDK | `video-sdk.service.ts` |
| `shortIo` | short.io | `url.service.ts` |
| `convertKit` | ConvertAPI | `convertapi.service.ts` |

Plus **Search** (Elasticsearch or MySQL full-text, selected by the `elastic_search`/`search_type` flags), **CRM** sync via OAuth, **SSO** for administrators, **Video** via the embedded SDK, and **Real-time chat** via CometChat.

**Payments — two-tier.** `payment-management` is a multi-gateway hub — PayPal, Razorpay, Stripe, Easebuzz, PayU — tenant-selectable, with a unified internal order/transaction record; these funds flow to the tenant (incubator). Separately, the **AI-credit purchase flow uses a distinct platform-level Easebuzz gateway** whose funds flow to the SanchiConnect operator, explicitly not reusing any tenant gateway config.

> **GAP · D-2 — Two Easebuzz configurations.** Easebuzz appears both as a tenant gateway option and as the platform credit gateway. *Sanchi to confirm:* the two configurations are isolated (distinct keys and accounts).

## 9. AI Scoring & Evaluation Architecture

The analyzer (`ai-startups-analyzer`, Python/FastAPI, own MySQL, one-directional) exposes the scoring flow: `generate-thesis` → `upload-csv` (returns run_id + batches) → `start-all-background` → `status-summary/{run_id}` → `finalize-analysis`. Scoring is async and batched (`BATCH_SIZE=5`, `ANALYZER_PER_RUN_CONCURRENCY=5`, `ANALYZER_GLOBAL_CONCURRENCY=16`), multi-provider, with **enrichment** via Serper (web search) and Firecrawl (website scrape) — best-effort under a 75-second-per-batch budget, disabled by default (`ENABLE_ENRICHMENT=0`). The **0–500 → 1–5 scoring scale is frozen**, with `_coerce_rating()` as the single conversion point.

> **GAP · D-3 — Scoring-rating precision.** The persisted rating column is cited as `decimal(4,3)` in the analyzer/backend and as `DECIMAL(4,2)` in the sprint plan. *Sanchi to align:* one precision before the analyzer and credit schemas lock.

## 10. Credit-System Architecture

The AI-credit subsystem is absent from the formal documentation and from the team's 26 feature specs; corroborating that it is not yet built as specified, the backend `grants` module is an entity stub with no controller/service and `schemes-management` is an empty controller stub. Its architecture is currently sourced only from the sprint plan: an Easebuzz platform gateway with an HMAC-verified idempotent webhook, control-plane credit tables gated by an `INTERNAL_SERVICE_TOKEN`, a DB-driven rate cache (loaded at bootstrap, refreshed without redeploy), and a reserve-then-settle deduction model. Domain rules are in `knowledge.md` §4.6; schema in `database.md`.

> **GAP · D-1 — Credit-system architecture is unspecified outside the sprint plan.** The subsystem is live-ish in code but has no feature spec. *Action:* author its architecture into a feature spec from the sprint plan and the as-built code. This is a natural first spec-driven pilot.

## 11. Notification Architecture

Backend business logic generates notifications and fans them out through the in-app feed, email, WebSocket push, and/or WhatsApp, based on tenant configuration and the user's preferences. WhatsApp is wired for OTP (`otp_verifications/send|verify/whatsapp`) and admin actions (`whatsapp_actions`); its status as a *broadcast delivery channel* in the UI remains an open product question (see `knowledge.md` §4.10).

## 12. File & Media Storage

Uploaded and generated files (documents, images, videos, certificates, exported reports) are stored in cloud object storage, referenced by a stored object key, with non-public access brokered through short-lived signed URLs. CloudFront serves signed URLs (for example, HLS video URLs); the CloudFront key material referenced in the backend is part of this substrate. This is the storage layer for the Bulk Email large-file delivery path.

> **GAP · D-4 — Bulk Email delivery architecture undetermined.** The Bulk Email attachment feature (a distinct surface from top-nav Broadcast) assumes a backend path for object storage, signed URLs, and malware scanning; the existing Broadcast delivery is admin-direct with no backend call. *Sanchi to determine:* whether Bulk Email attachments route through the backend or the admin, since that decides where the storage/scan controls live.

## 13. Security Architecture

The platform's security design. (Findings, verification, and remediation are Track B — see the Reconciliation document — and are out of scope here.)

- **Authentication.** Members authenticate passwordlessly via a one-time code (email, mobile, or WhatsApp) establishing an HTTP-only session cookie; no passwords are stored in plaintext. Administrators use credential login with optional enterprise SSO and server-side session state. A supervised support-session mechanism (`admin-actions/backdoor-login`) issues a scoped session into a member account for assistance — an architectural component whose controls are assessed under Track B. The backend uses a cookie-`accessToken`→Bearer JWT model, with `single_session_login_enabled` toggling session tracking.
- **Authorization.** Evaluated on the backend for every request against the user's role and, for administrators, their scope of assignment; front-end role-aware layout is a usability convenience, not the enforcement boundary. Enforced via `RolesGuard`, the granular per-administrator Allowed Features flags, and `FeatureGuard`.
- **Tenant data isolation.** Structural — database-per-tenant for business data, row-per-tenant-by-`domain` for the control plane (§5).
- **Transport & storage.** TLS in transit, with secure WebSocket for real-time; third-party credentials managed as protected configuration; signed, time-limited URLs for non-public files.
- **Secrets.** ~62 backend environment variables validated by a Joi schema at boot; platform gateway secrets, an internal service token, and CloudFront key material are in scope. The secrets-management posture (scanning, rotation, storage) is a Track-B concern.
- **Auditability.** An `audit-log` module records material administrative actions — approvals, financial transactions, configuration changes, and exports — capturing the actor, the action, and the timestamp.

## 14. Non-Functional Requirements

The binding NFRs, from the SRS. **Performance:** primary content 2–3 s, search 1–2 s, uploads show progress and support large files. **Scalability:** horizontal scaling of application services; per-tenant data scales independently; bulk operations (export/import, broadcast, batch certificates) run asynchronously and batched — a 50,000-recipient broadcast must dispatch within an agreed window without delaying unrelated notifications. **Availability:** high availability in business hours, graceful degradation of transient third-party failures. **Usability:** member app usable without training, admin usable by a trained operator, clear non-technical errors, keyboard navigation and accepted accessibility practices. **Maintainability & extensibility:** configuration applies without redeploy; features are independently enableable per tenant; new stakeholder types, fields, and criteria come through configuration rather than schema change where practicable. **Portability:** the Chrome/Firefox/Safari/Edge desktop-and-mobile matrix; cloud-portable where practicable. **Localization:** per-tenant currency and date/time/time-zone; full UI i18n is opt-in per tenant. **Licensing:** all third-party components licensed for commercial SaaS use.

> **GAP · D-5 — Backup/DR targets unspecified.** The SRS names backup/DR as a concern but states no recovery objectives. *Sanchi to provide:* RPO/RTO and the backup regime.

## 15. Deployment Architecture

Logically separated **development, pre-release/staging, and production** environments. Each component deploys as an independent, horizontally scalable unit; each tenant database is provisioned and scaled independently; static assets are served through a **CDN**; each service releases through its own pipeline with **versioned inter-service contracts**, so a service can update without lock-step redeploys except for deliberately-coordinated breaking changes. This environment separation and contract-versioning is what the spec-driven gates and CI attach to.

## 16. Cross-Cutting Concerns

Central **logging and monitoring** across all services; user-facing **error handling** in plain language with technical detail captured server-side and transient third-party failures surfaced as recoverable states; **caching** across tiers, including the bootstrap tenant-config cache and the credit-rate cache.

## 17. Coding Standards & Conventions

Backend standards are captured in the `sc-saas-backend` steering file. The team maintains per-module `module.spec.md` files across every repo, together with a `module.spec.template.md` and a `feature.spec.template.md` — these are the per-module documentation standard and the template every new module or feature spec follows. Frontend (Angular) and admin (PHP) conventions live in those per-module specs, which reside in the repositories rather than in this document.

## 18. Source Traceability

Consolidates the **TAD** (§2–10), the **SRS** (§2.5, §5–8), the **team's six per-repo indexes and 26 feature specs** — the authoritative as-built source for topology, stacks, contracts, flags, and integrations — the **`sc-saas-backend` steering file**, and the **Sanchi Credits Sprint Plan** (credit-system architecture). Their reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| D-1 | §10 | Credit-system architecture unspecified outside the sprint plan | A live-ish subsystem with no feature spec | Team + product |
| D-2 | §8 | Confirm the two Easebuzz configurations are isolated | Operator vs tenant fund separation | Product owner |
| D-3 | §9 | Align scoring-rating column precision (4,2 vs 4,3) | Schema correctness before lock | Team |
| D-4 | §12 | Determine Bulk Email delivery path (backend vs admin-direct) | Decides where storage/scan controls live | Product + team |
| D-5 | §14 | Backup/DR RPO/RTO and regime | Recovery objectives undefined | Team + infra |

**Note (not gaps):** the per-module specs referenced throughout live inside the repositories, not in this document; pull them (or point `code-extraction` at them) for module-depth work.

*The next document is `knowledge.md` — the domain model, business rules, and state machines — reconciled against the team's feature specs.*
