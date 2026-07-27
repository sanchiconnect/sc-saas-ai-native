# api.md — SanchiConnect API Contract

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 5 of 6
**Consolidates:** the team's `contracts.api` declarations across the 26 feature specs (307 declared routes), `FT-005` (the as-built AI-credit routes), the tenant-verification contract (FT-002), the AI-analyzer service contract (FAI-001/002), and the `sc-saas-backend` steering file.
**Positioning:** the endpoint, authentication, and contract layer — assembled from the team's feature specs (the authoritative route source).

> Gaps are marked inline as **GAP · A-N** and collected in **§99** (forward-only). Route paths are the declared contract; field-level DTO schemas live in the code and the feature specs — confirmed as the final scope decision, not an open gap (A-1, §99).

---

## 1. Purpose & Scope

Defines the API contract: conventions, route namespaces, the authentication/authorization contract, the frozen cross-repo contracts, the domain route groups, the as-built AI-credit API, and the separate AI-evaluation and third-party service contracts. It maps the surface (307 declared routes) and specifies the contracts that must not break silently.

## 2. Conventions

- **Base prefix & versioning.** Business API routes under a global `api` prefix with URI versioning: `api/v{n}/…` (current `v1`). Control-plane routes use their own prefixes.
- **Content type.** JSON.
- **Response envelope.** A consistent structured shape via `TransformInterceptor`.
- **Error shape.** A consistent structured error shape.
- **Validation.** DTOs via `class-validator` under a global whitelisting `ValidationPipe`.
- **External identifiers.** Resources addressed by `uuid`/stable code, never the internal `id`.
- **Pagination.** List/search endpoints paginate at the database layer.

## 3. Route Namespaces

| Namespace | Auth | Purpose | Owner |
|-----------|------|---------|-------|
| `api/v1/public/*` | none | Registration, OTP, public directories/profiles, public search | `sc-saas-backend` |
| `api/v1/*` | JWT | Authenticated member and business functionality | `sc-saas-backend` |
| `api/v1/admin-actions/*` | admin | Administrative operations, incl. the support-session mechanism and Bulk Email dispatch | `sc-saas-backend` |
| `api/v1/ai-credits/*` | mixed | Credit catalogue, purchase, webhooks, invoices | `sanchiconnect-saas-tenants` |
| `/public/global/*`, `/ecosystem/*`, `/organizations`, `/subscriptions`, `/tenants` | mixed | Control plane: verification, provisioning, cross-tenant hubs | `sanchiconnect-saas-tenants` |
| (analyzer base URL) | service | AI scoring/enrichment (separate FastAPI service) | `ai-startups-analyzer` |
| (`THIRD_PARTY_SERVICE_BASE_URL`) | network | Third-party provider proxies | `sc-saas-3rdparty-webservices` |

**Not a REST surface:** the operator panel (`sanchiconnect-saas-tenants-admin`) and the credit subsystem's reserve/settle/refund/grant operations are **direct database writes**, not API routes (the 3-writer pattern — `design.md` §10). The credit API below is only the purchase/catalogue/invoice surface; everything else is raw SQL.

## 4. Authentication & Authorization Contract

- **Passwordless OTP (members).** Public auth and OTP endpoints — e.g. `POST api/v1/public/auth/mobile/login` then `.../login/verify`, and `POST api/v1/public/otp_verifications/send|verify` with `.../whatsapp` variants. A verified login establishes an HTTP-only session cookie; no plaintext passwords.
- **JWT model.** Authenticated routes accept a JWT via the `accessToken` cookie with a `Bearer` fallback. `single_session_login_enabled` toggles session tracking.
- **Guards.** `JwtAuthGuard`, `RolesGuard` (role + scope), `FeatureGuard` with `@Features([...])`, `OptionalJwtAuthGuard`. Authorization is backend-enforced per request.
- **External sign-in / cross-tenant import.** `POST api/v1/public/auth-external/login` and `.../login/verify/import`.
- **Support session.** `GET api/v1/admin-actions/backdoor-login/:userId/:adminMd5` — a documented endpoint of the platform contract; controls assessed under Track B.
- **Account lifecycle.** `GET api/v1/users/logout`, `DELETE api/v1/users/delete_account`, `PATCH api/v1/users/deactivate_account`.

## 5. Frozen Contracts

Consumed cross-repo at bootstrap; must not change shape without coordinated updates:

- **Tenant verification.** `GET /public/global/verify_tenant/:hostname` (consumed by the frontend at boot) and `GET /public/global/tenant-settings/:hostname` (consumed by the backend at bootstrap) — resolve the operating tenant, the backend API address, enabled features, and branding.
- **Feature-flag columns.** The boolean flag columns on the control-plane tenant entity *are* the entitlement contract; the `verify_tenant` payload projects them. A rename breaks the backend `Feature` enum, the frontend `IFeatures`, and the admin `config.php` simultaneously.

Changes to either — or to any controller signature/DTO consumed by another repo — are cross-repo breaking changes (`/audit-contract`, `/trace-flag`).

## 6. Domain Route Groups

The 307 declared routes, organised. Each group's full list and DTO detail is in the cited feature spec; representative endpoints shown.

| Group | Representative endpoints | Routes | Spec |
|-------|--------------------------|--------|------|
| Auth & account | `public/auth/mobile/login`, `otp_verifications/*`, `auth-external/*`, `users/*` | 20 | FE-001 |
| Ecosystem discovery & search | public/elastic search, ecosystem directories, profile typeahead | 45 | FE-002 |
| Programs & applications (two-track) | `programs-management/*`, `application-programs-management/*`, `.../apply`, `.../submit` | 22 | FE-009 |
| Payments & membership | `payments/gateways`, `payments/create-order`, `payments/paypal/capture-order/:id`, `payments/coupon/verify`, `payments/orders` | 26 | FE-008 |
| Meetings & chat | scheduling, calendar, chat sessions | 26 | FE-011 |
| Community feed | posts, engagement, moderation | 30 | FE-006 |
| Challenges | challenge lifecycle, submissions | 20 | FE-004 |
| Jobs & hiring | postings, applications | 17 | FE-003 |
| Learning | courses, lessons, enrolment, progress | 18 | FE-010 |
| Mentorship | sessions, approvals | 16 | FE-005 |
| Connections | requests, settings | 15 | FE-007 |
| Dashboard & metrics | growth metrics, milestones | 14 | FE-012 |
| Admin (FA groups) | stakeholder approve/reject, VS management, analysis trigger, finance config, **Bulk Email dispatch** (`admin-actions/broadcast-ceo-message`) | ~12 | FA-001/002/003/004/007 |
| Control plane — provisioning | `organizations`, `subscriptions`, `tenants`, global modules | 5 | FT-001 |
| Control plane — verification | `verify_tenant/:hostname`, `tenant-settings/:hostname` | 2 (frozen) | FT-002 |
| Control plane — ecosystem sync | directory sync of 8 stakeholder types | 5 | FT-003 |
| Control plane — IP/facility hubs | `ecosystem/patents`, `ecosystem/facilities`, `.../connect` | 6 | FT-004 |

The two-track model surfaces directly: **`programs-management`** and **`application-programs-management`** are separate route trees. Broadcast (FA-003) declares no backend routes for message composition (admin-direct); only the Bulk Email email-dispatch step calls the backend (`admin-actions/broadcast-ceo-message`).

## 7. AI-Credit API *(as-built, per `FT-005`)*

Seven routes, all owned by `sanchiconnect-saas-tenants` under `api/v1/ai-credits/*`:

- `GET api/v1/ai-credits/packages` — public, the active package catalogue.
- `GET api/v1/ai-credits/task-rates` — public, per-task credit rates.
- `POST api/v1/ai-credits/purchase` — initiates an Easebuzz purchase order; `InternalApiKeyGuard` (fail-open if `AI_CREDITS_INTERNAL_API_KEY` unset). Called by `sc-saas-admin` over HTTP with `X-Internal-Api-Key`.
- `POST api/v1/ai-credits/webhooks/easebuzz/success` — Easebuzz success callback; `InternalApiKeyGuard` + **mandatory HMAC-SHA512 signature check** (always enforced).
- `POST api/v1/ai-credits/webhooks/easebuzz/failure` — Easebuzz failure callback; same guard shape.
- `GET api/v1/ai-credits/invoices` — `InternalApiKeyGuard`.
- `GET api/v1/ai-credits/invoices/:id` — `InternalApiKeyGuard`, requires `?domain=`.

**Everything else is not an API call.** Reserve, settle, refund, instant-debit, and grant issuance are **direct Medoo/raw-PDO writes** from `sc-saas-admin` and `sanchiconnect-saas-tenants-admin` against the shared control-plane DB — there is no HTTP contract for them. Any future NestJS controller/DTO change to the purchase route must be checked against `sc-saas-admin`'s cURL payload.

> **GAP · A-2 — The Bulk Email send action is ungated.** The email-dispatch route `admin-actions/broadcast-ceo-message` has no permission gate on send (`design.md` D-4). *Product + team to decide:* whether to gate it.

## 8. AI-Evaluation Service Contract

The analyzer (`ai-startups-analyzer`, FastAPI) is a **separate service** called one-directionally; not under the NestJS `api/v{n}` scheme, own base URL. Contract (FAI-001/002): `generate-thesis` → `upload-csv` (returns `run_id` + batches) → `start-all-background` → `status-summary/{run_id}` → `finalize-analysis`, plus `re-enrich`. It scores 0–500 (persisted `decimal(4,3)`, 0.000–5.000), batched and multi-provider, with optional best-effort enrichment (`knowledge.md` §4.5).

## 9. Third-Party Gateway Contract

The seven proxies (`sc-saas-3rdparty-webservices`) are reached only by the backend via `THIRD_PARTY_SERVICE_BASE_URL`: `sms`, `sendGrid`, `ses`, `cometChat`, `videoSDK`, `shortIo`, `convertKit` (`design.md` §8). Stateless, no database.

## 10. Cross-Repo Contract Discipline

- The frozen contracts (§5) and any controller-signature/DTO change consumed by another repo are cross-repo breaking changes.
- The backend owns the REST contract consumed by `sc-saas-frontend` and `sc-saas-admin`; run `/audit-contract` after any change to a route path, method, parameter, or DTO shape.
- The credit purchase route is the one HTTP contract between `sc-saas-admin` and `sanchiconnect-saas-tenants`; all other credit interaction is shared-DB (so the schema, not an API, is the contract there — `database.md` §8).

## 11. Source Traceability

Consolidates the **team's `contracts.api` declarations** across the 26 feature specs, **`FT-005`** (the as-built credit routes), the **tenant-verification contract** (FT-002), the **AI-analyzer contract** (FAI-001/002), and the **`sc-saas-backend` steering file**. Reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| A-1 | §1/§6 | Field-level request/response DTO schemas not consolidated | 307 route paths without payload shapes; consumers need field detail | Team (extract from code + feature specs) |
| A-2 | §7 | Bulk Email send action (`broadcast-ceo-message`) is ungated | A shipped write action with no permission gate | Product + team |

**Note (resolved):** the AI-credit API is now documented (the seven as-built routes above), correcting the sprint-plan-guessed endpoints. **Note (architecture):** the credit subsystem's non-purchase operations have no API contract by design — the shared schema is the contract (`design.md` D-1 governs whether to change that).

**Note (A-1, decided 2026-07-27 — Linear SAN-63):** full field-level DTO consolidation across all 307 routes is **formally deferred, not scheduled.** Neither repo's Swagger decoration is complete enough today for a clean OpenAPI export to be worth generating as-is — `sc-saas-backend` has zero `@ApiResponse` usage anywhere (response shapes entirely undocumented) and its single largest controller, `admin-actions.controller.ts` (50 route handlers), has zero `@ApiOperation`; `sanchiconnect-saas-tenants`'s `ai-credits` DTOs and controller are similarly undecorated. Hand-authoring the ~259 DTO classes across both repos into markdown was also considered and rejected: unlike a generated export, it would start drifting from the actual code the moment any DTO changes, with no automated way to catch it. Given Low/documentation-completeness priority, the cost of either path was judged to outweigh the benefit right now. This document's existing route-level-only scope (Section 1's "field-level DTO schemas live in the code and the feature specs") is confirmed as the final decision, not an interim gap awaiting closure.

**Note (A-2, resolved 2026-07-27 — Linear SAN-52):** `sc-saas-backend`'s `admin-actions.service.ts` now enforces `AdminUsersEntity.canBroadcastMessages` on `broadcast-ceo-message` before sending, re-checked on every request rather than trusting a session flag set at login. The admin-side Bulk Email button is also now hidden client-side for admins without this permission, across all 6 places it appears.

*Next: `ui-ux.md` — the design system(s), tokens, components, and screen catalogue.*
