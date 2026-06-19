---
type: index
repo: backend
updated: 2026-06-17
---

# Backend Module Specs — Index

All 58 `sc-saas-backend` modules have a `module.spec.md`. This index maps each module to its spec, summarises its role, and flags security/quality notes surfaced during spec authoring.

> **How to use:** When working on a module, read its spec first — it records owned routes, consumed flags, tenant-scoping mechanism, invariants, and known footguns. When adding a route or flag gate, update the spec's `owns` / `consumes` frontmatter and `updated` date.

---

## Auth & Identity

| Module | Spec | Notes |
|---|---|---|
| `auth` | [spec](../sc-saas-backend/src/modules/auth/module.spec.md) | JWT issuance, OTP login, per-type registration. The auth contract every other module depends on. |
| `auth-external` | [spec](../sc-saas-backend/src/modules/auth-external/module.spec.md) | Cross-tenant user import/export flow. No JWT on any route — OTP + feature flags only. Bug: `default` branch passes `undefined` userId. |
| `user` | [spec](../sc-saas-backend/src/modules/user/module.spec.md) | Profile CRUD for all stakeholder types; widest-dependency module (11 imports). `update/notification` and `profile-views/increment` are unauthenticated. `deleteUserInformation` DB cleanup is commented out. |
| `verifications` | [spec](../sc-saas-backend/src/modules/verifications/module.spec.md) | OTP send/verify. **High-severity bug:** OTP stored as md5 but compared against raw plaintext — verification always fails unless client sends md5. |

---

## Applications & Programs

| Module | Spec | Notes |
|---|---|---|
| `application-management` | [spec](../sc-saas-backend/src/modules/application-management/module.spec.md) | Form submission, review, and scoring pipeline. |
| `form-management` | [spec](../sc-saas-backend/src/modules/form-management/module.spec.md) | Dynamic form builder and renderer. |
| `program-management` | [spec](../sc-saas-backend/src/modules/program-management/module.spec.md) | Incubator program CRUD + payment reminders. `payment-reminder/:adminMd5` has admin-check commented out — fully unauthenticated write. |
| `program-office-members` | [spec](../sc-saas-backend/src/modules/program-office-members/module.spec.md) | POM stakeholder lifecycle + ecosystem sync. Circular dep with `EcoSystemModule` via `forwardRef`. |
| `vs-programs-management` | [spec](../sc-saas-backend/src/modules/vs-programs-management/module.spec.md) | Venture Studio program rounds. Most `@Features(VENTURE_STUDIO)` annotations commented out. `getProgram` creates a DB row on every read. |

---

## Stakeholder Profiles

| Module | Spec | Notes |
|---|---|---|
| `startup` | [spec](../sc-saas-backend/src/modules/startup/module.spec.md) | Largest module (46 routes, 6 controllers). Pitch-deck, founders, funding, advisory board. `public/startup-information` uses unverified JWT for gating. |
| `individual` | [spec](../sc-saas-backend/src/modules/individual/module.spec.md) | Individual stakeholder profile. |
| `investor` | [spec](../sc-saas-backend/src/modules/investor/module.spec.md) | Investor profile and portfolio. |
| `corporate` | [spec](../sc-saas-backend/src/modules/corporate/module.spec.md) | Corporate stakeholder profile. |
| `mentors` | [spec](../sc-saas-backend/src/modules/mentors/module.spec.md) | Mentor profile + application management. `FeatureGuard` on application controller but no `@Features` — gate never fires. Ecosystem sync on edit is NOT best-effort. |
| `partner` | [spec](../sc-saas-backend/src/modules/partner/module.spec.md) | Partner lifecycle + startup onboarding. `premium-module/request` is fully open and can trigger SES to arbitrary addresses. `admin-console` leaks JWT in URL. |
| `service-providers` | [spec](../sc-saas-backend/src/modules/service-providers/module.spec.md) | Service provider profile. `public/service-provider-information` exposes all columns unauthenticated. |

---

## Ecosystem & Discovery

| Module | Spec | Notes |
|---|---|---|
| `ecosystem` | [spec](../sc-saas-backend/src/modules/ecosystem/module.spec.md) | Proxies search/profiles to the cockpit directory. Shared mutable `requestHeader` — concurrency bug. Admin push routes have no JWT. |
| `search` | [spec](../sc-saas-backend/src/modules/search/module.spec.md) | Stakeholder typeahead across 9 types. Profile typeahead has no feature gate or JWT. `StakeholderAccess` computed but never forwarded — partner scoping is a no-op. |
| `elastic-search` | [spec](../sc-saas-backend/src/modules/elastic-search/module.spec.md) | Elasticsearch index sync (20 routes). **All routes unauthenticated** — only `elastic_search` feature flag. Controller registered as both controller and provider. |
| `compare` | [spec](../sc-saas-backend/src/modules/compare/module.spec.md) | Side-by-side stakeholder comparison. |
| `connections` | [spec](../sc-saas-backend/src/modules/connections/module.spec.md) | Connection requests between stakeholders. |
| `connections-wishlist` | [spec](../sc-saas-backend/src/modules/connections-wishlist/module.spec.md) | Saved / wishlist connections. |

---

## Events & Community

| Module | Spec | Notes |
|---|---|---|
| `events` | [spec](../sc-saas-backend/src/modules/events/module.spec.md) | Event creation, registration, and attendance. |
| `community-wall` | [spec](../sc-saas-backend/src/modules/community-wall/module.spec.md) | Social feed / wall posts. |
| `challenges` | [spec](../sc-saas-backend/src/modules/challenges/module.spec.md) | Innovation challenge lifecycle. |
| `news` | [spec](../sc-saas-backend/src/modules/news/module.spec.md) | External news proxy + per-user category prefs. **All 4 routes have `JwtAuthGuard` commented out.** Preference write has no ownership check. |
| `notifications` | [spec](../sc-saas-backend/src/modules/notifications/module.spec.md) | Inbox + badge-count aggregator. 6 cron-trigger POSTs are completely open. `getNotifications` has likely `andWhere/orWhere` precedence bug. |

---

## Mentorship & Learning

| Module | Spec | Notes |
|---|---|---|
| `mentorship` | [spec](../sc-saas-backend/src/modules/mentorship/module.spec.md) | Mentorship session booking + hour logging. Auto-entry email commented out. `console.log(session)` leaks session data. |
| `learning-management` | [spec](../sc-saas-backend/src/modules/learning-management/module.spec.md) | LMS — courses, modules, videos. `GET videos/:id/hls-url` is fully unprotected (returns signed CloudFront HLS URLs). Only `STARTUP` role can enroll. |
| `certificates` | [spec](../sc-saas-backend/src/modules/certificates/module.spec.md) | Certificate generation and issuance. |
| `id-cards` | [spec](../sc-saas-backend/src/modules/id-cards/module.spec.md) | Digital ID card generation. |

---

## Finance & Payments

| Module | Spec | Notes |
|---|---|---|
| `payment-management` | [spec](../sc-saas-backend/src/modules/payment-management/module.spec.md) | Multi-gateway hub (PayPal, Razorpay, Stripe, Easebuzz, PayU). **Nearly every route is unauthenticated** (`JwtAuthGuard` commented out). Self-import `forwardRef`. |
| `memberships` | [spec](../sc-saas-backend/src/modules/memberships/module.spec.md) | Membership tiers + upgrade requests. Majority of routes have JWT commented out. Any caller can submit upgrade for any `profileId`. |
| `invoice` | [spec](../sc-saas-backend/src/modules/invoice/module.spec.md) | PDF invoice generation → S3 upload. Single unauthenticated endpoint; no DTO validation on file-write path. |
| `grants` | [spec](../sc-saas-backend/src/modules/grants/module.spec.md) | Entity stub only (no controller/service). Two grant entities registered for admin panel use. |
| `schemes-management` | [spec](../sc-saas-backend/src/modules/schemes-management/module.spec.md) | Empty controller stub — no routes. Entities scaffolded for admin panel. |

---

## Meetings, Chat & Messaging

| Module | Spec | Notes |
|---|---|---|
| `meetings` | [spec](../sc-saas-backend/src/modules/meetings/module.spec.md) | Meeting scheduling + video integration. `feedback-reminder/trigger` and `/:code/complete` are unauthenticated. |
| `chat` | [spec](../sc-saas-backend/src/modules/chat/module.spec.md) | CometChat integration and messaging. |
| `conversations` | [spec](../sc-saas-backend/src/modules/conversations/module.spec.md) | Threaded conversation management. |
| `tickets` | [spec](../sc-saas-backend/src/modules/tickets/module.spec.md) | Support ticket system. Clean, fully gated. SES failures on create are NOT swallowed (can block writes). |

---

## Content & Resources

| Module | Spec | Notes |
|---|---|---|
| `resources` | [spec](../sc-saas-backend/src/modules/resources/module.spec.md) | Resource library + download tracking. Two `send-email` endpoints on different guard levels. `convert-to-image` has no auth. `ResourceCategoriesEntity.title` typed `number` but maps to `varchar`. |
| `glossary` | [spec](../sc-saas-backend/src/modules/glossary/module.spec.md) | Term dictionary. No auth on either route. `getWord()` doesn't filter by `isActive`. |
| `dashboard` | [spec](../sc-saas-backend/src/modules/dashboard/module.spec.md) | Analytics dashboard aggregation. |
| `metrics` | [spec](../sc-saas-backend/src/modules/metrics/module.spec.md) | Custom chart metrics. Invite codes generated but never persisted — can't be redeemed. Two v1 endpoints use different time-bucketing keys. |

---

## Jobs & Opportunities

| Module | Spec | Notes |
|---|---|---|
| `job` | [spec](../sc-saas-backend/src/modules/job/module.spec.md) | Job board + applications. `@Roles(JOB_SEEKER)` applied but `RolesGuard` missing from `@UseGuards` — role check silent no-op. `PATCH hiring-profile` body is commented out (no-op). |
| `startup-kit` | [spec](../sc-saas-backend/src/modules/startup-kit/module.spec.md) | Curated startup resource catalogue. Browse is unauthenticated. In-memory cache with 10-hour TTL — edits invisible until restart. |
| `ip-management` | [spec](../sc-saas-backend/src/modules/ip-management/module.spec.md) | Intellectual property tracking (cockpit proxy). Shared mutable `requestHeader` concurrency bug (same as ecosystem). |

---

## Facilities & Physical

| Module | Spec | Notes |
|---|---|---|
| `facility_management` | [spec](../sc-saas-backend/src/modules/facility_management/module.spec.md) | Facility booking + kiosk check-in (5 controllers, 30+ routes). Inconsistent auth — some write paths accept unauthenticated callers. `PaymentTransactionsEntity` registered twice. |

---

## Tasks & Projects

| Module | Spec | Notes |
|---|---|---|
| `task-management` | [spec](../sc-saas-backend/src/modules/task-management/module.spec.md) | **Empty stub.** Controller and service are unimplemented. Entities scaffolded (`tasks`, subtasks, comments, attachments). Missing `@Controller` version → routes would land at `api/task-management` not `api/v1/`. |
| `milestones` | [spec](../sc-saas-backend/src/modules/milestones/module.spec.md) | Program milestone tracking. Ownership checks commented out — any authed user can mutate any milestone. `formatMileStoneInformation` does a DB write on every read call. |

---

## Platform Infrastructure

| Module | Spec | Notes |
|---|---|---|
| `global` | [spec](../sc-saas-backend/src/modules/global/module.spec.md) | Platform backbone: reference data, tenant settings, admin actions (85+ routes). `backdoor-login` issues real JWTs with only an md5 token. `forgot-password` has no token at all. Exports `GlobalService` + `AdminActionsService`. |
| `audit-log` | [spec](../sc-saas-backend/src/modules/audit-log/module.spec.md) | `@Global()` write-only auditing. Exports `AuditedUpdateService`. Raw `repo.update()` calls bypass the audit trail. |
| `cron` | [spec](../sc-saas-backend/src/modules/cron/module.spec.md) | Scheduled job orchestration. `COMMUNITY_WALL_POSTS_WEEKLY_REMINDER` callback is missing `()` — no-op. Timezone hardcoded to `Asia/Kolkata`. |
| `notifications` | [spec](../sc-saas-backend/src/modules/notifications/module.spec.md) | *(also listed under Events & Community)* Exports `NotificationsRepository` write methods for sibling modules. |
| `migrations` | [spec](../sc-saas-backend/src/modules/migrations/module.spec.md) | Data migration scripts behind `:adminMd5` token. **No JWT, no feature gate** — only the md5 token protects bulk mutations. |
| `import` | [spec](../sc-saas-backend/src/modules/import/module.spec.md) | Bulk profile seeding. **5 routes with zero auth or feature gate** — open to anyone with network access. |

---

## Integrations & External

| Module | Spec | Notes |
|---|---|---|
| `factacy` | [spec](../sc-saas-backend/src/modules/factacy/module.spec.md) | Proxies Factacy AI-news API. Errors swallowed silently (returns HTTP 200 with `data: undefined`). |
| `power-pitch-module` | [spec](../sc-saas-backend/src/modules/power-pitch-module/module.spec.md) | Power Pitch video platform bridge. CFA + transcript routes have no JWT. |

---

## Stubs / Data-Model Only

| Module | Spec | Notes |
|---|---|---|
| `portfolio-management` | [spec](../sc-saas-backend/src/modules/portfolio-management/module.spec.md) | 8 entities, zero controller/service. Schema consumed by PHP admin via direct DB. Three `date` columns typed `number` in TS. |
| `grants` | *(see Finance above)* | |
| `schemes-management` | *(see Finance above)* | |
| `task-management` | *(see Tasks above)* | |

---

## Security findings summary (surfaced by spec authoring)

These findings were captured in module `Watch out for` sections. They are **not fixed here** — they are documented for awareness and prioritisation.

| Severity | Module | Finding |
|---|---|---|
| 🔴 Critical | `verifications` | OTP stored as md5 but compared against plaintext — verification always fails |
| 🔴 Critical | `global` | `backdoor-login` issues real JWTs with only an md5 token; `forgot-password` has no token |
| 🔴 Critical | `import` | 5 bulk-import endpoints have zero auth or feature gate |
| 🔴 Critical | `payment-management` | Nearly every payment route has `JwtAuthGuard` commented out |
| 🔴 Critical | `milestones` | Ownership checks commented out — any authed user can mutate any milestone |
| 🟠 High | `migrations` | All mutation routes protected only by md5 token, no JWT |
| 🟠 High | `news` | All 4 routes have JWT commented out; preference write has no ownership check |
| 🟠 High | `learning-management` | `GET videos/:id/hls-url` fully unprotected — leaks signed CloudFront HLS URLs |
| 🟠 High | `memberships` | Majority of routes have JWT commented out; any caller can submit upgrade for any profile |
| 🟠 High | `elastic-search` | All 20 routes unauthenticated — only a feature flag gates index/search operations |
| 🟠 High | `partner` | `premium-module/request` is open and can trigger SES to arbitrary addresses |
| 🟠 High | `user` | `update/notification` and `profile-views/increment` are unauthenticated |
| 🟠 High | `auth-external` | `default` branch passes `undefined` as userId → crash on unsupported user types |
| 🟡 Medium | `cron` | `COMMUNITY_WALL_POSTS_WEEKLY_REMINDER` callback missing `()` — scheduled job is a no-op |
| 🟡 Medium | `job` | `@Roles(JOB_SEEKER)` applied but `RolesGuard` missing from `@UseGuards` — role check ignored |
| 🟡 Medium | `notifications` | 6 cron-trigger POST endpoints are completely open |
| 🟡 Medium | `meetings` | `feedback-reminder/trigger` and `/:code/complete` are unauthenticated |
| 🟡 Medium | `vs-programs-management` | `getProgram` creates a DB row on every read call |
| 🟡 Medium | `program-management` | `payment-reminder/:adminMd5` admin-check commented out |
