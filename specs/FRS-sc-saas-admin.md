---
type: frs
repo: sc-saas-admin
updated: 2026-07-06
---

# Functional Requirement Specification — `sc-saas-admin`

## 1. Purpose & Scope

This document specifies the functional behavior of `sc-saas-admin`, the PHP/Medoo/sparkAdminTpl panel used by tenant operators — super-admins, program managers, corporate program managers, jury members, recruitment partners, developers, and ecosystem partners — to run their incubator/accelerator program on the SanchiSaaS platform.

It is organized by functional domain. Requirements were re-expressed from a pre-existing, code-verified suite of 22+ technical module specs (`sc-saas-admin/modules/*/module.spec.md`, indexed at `specs/admin-module-specs-index.md`) as user-facing functional flows, not as a code inventory. Known bugs and security-relevant behavior are called out under **Notable business rules / limitations** per module — these describe actual current behavior, not intended design, and should not be read as recommendations.

This FRS covers the admin panel only. The companion document `specs/FRS-sc-saas-frontend.md` covers the end-user PWA. Per the workspace constitution, feature-flag names are owned by `sanchiconnect-saas-tenants` and the business API contract is owned by `sc-saas-backend` — this document treats both as given.

## 2. Actors

| Actor | Description |
|---|---|
| Super-admin | Full access across all modules for a tenant; the only role that bypasses program/partner scoping checks. |
| Developer (`is_dev`) | Access to System Admin tooling — schema, API routes, email/menu/table-view config, BI report authoring. |
| Program Manager (PM) | Scoped to programs/challenges they're assigned to; reviews and progresses applications. |
| Corporate Program Manager | Scoped to their own corporate account's challenges and linked CFA programs. |
| Jury member | Restricted to reviewing/rating allotted applications; explicitly excluded from most other modules. |
| Jury Reviewer | Sub-role with authority to bulk-approve jury ratings. |
| Recruitment partner (admin role) | Scoped to jobs where they're listed; manages applicants/interviews for those jobs only. |
| Partner (own login) | A tenant sub-admin scoped to their own `partner_id` slice of the ecosystem (own stakeholders, programs, contacts). |
| Finance/operations staff | Uses membership, payment gateway, tax, and invoicing tooling (no dedicated role ID — governed by general admin access). |

## 3. System-Wide Mechanics

- **Two DB connections per request**: `$mainDatabase` (the shared tenants DB — feature flags, `api_url`, per-tenant DB credentials) and `$database` (the tenant's own client DB — all business data). These must never be cross-queried; a small number of modules deliberately write back to the tenants DB (see §3.1).
- **Tenant resolution by hostname**: incoming requests are matched against `tenant_users.admin_domain`/`admin_custom_domain` to open the correct tenant DB connection and branding config.
- **Backdoor tokens, not JWTs**: most admin→backend calls authenticate via a short-lived, single-use, MD5-derived admin token (`:adminMd5`/`:adminToken`) appended to the URL, rather than a bearer JWT. Round-state mutations, notification emails, and ecosystem sync all flow through this mechanism — never a direct DB write for anything the backend also needs to know about.
- **Feature flags gate visibility, not enforcement**: nearly every module's own guard is "is this flag on for the tenant," checked once at page load — several modules noted below have gaps where a flag check exists on the UI but not on the underlying AJAX/API handler.
- **Role-based scoping, not flag-based, for PM/partner/jury access**: role IDs (`super_admin_role_id`, `program_manager_role_id`, `jury_role_id`, `corporate_program_manager_role_id`, `recruitmentpartner_role_id`, etc.) are fixed per deployment via `.env`. Any new query path in a scoped module must filter by the assignee/partner ID or it is a tenant-isolation-style violation within the admin's own role model.

### 3.1 Modules that write back to the tenants DB (cross-DB writes)

Three modules perform deliberate writes to the shared tenants DB from within an otherwise tenant-DB-scoped admin panel:
- `finance-memberships` — `memberships/settings.php` updates tenant-level membership label/visibility/moderation config.
- `integrations` — the Intellectual Property sub-module writes patent records to the tenants DB (by design — patents are a cross-tenant registry).
- `growth-metrics` — `metric_types.php` writes `growth_metrics_duration`/`growth_metrics_financial_year_start_month`/`growth_metrics_duration_set` to `tenant_users`.
- `outreach-communications` — the outreach-request/tracking flow *reads* `tenant_users`, `program_promotions`, `program_promotions_tracking` from the tenants DB (a deliberate exception to normal tenant scoping, since promotion is inherently cross-tenant).

## 4. Functional Requirements by Domain

---

### 4.1 Foundation, Auth & Generic CRUD

*Modules: core-bootstrap, auth, ajax-handlers, stakeholder-crud.*

#### 4.1.1 Core Bootstrap

**Purpose**: Resolves the requesting tenant from the hostname, opens tenant-scoped data access, applies tenant branding/feature configuration, and routes every request — the platform layer every other module runs on.

**Actors**: All admin panel users, implicitly.

1. `FR-CB-01: Tenant resolution by domain` — Any request hits the panel → hostname matched against `tenant_users.admin_domain`/`admin_custom_domain` → a per-tenant DB connection and branding config are opened → operator sees only their tenant's data and branding.
2. `FR-CB-02: Feature availability by tenant plan` — Page render or action attempt → feature-flag columns from the tenant's row are loaded once → menu items and page sections are gated accordingly.
3. `FR-CB-03: Branded session experience` — Login or any authenticated action → DB-backed (not filesystem) session + tenant branding applied to every page.
4. `FR-CB-04: Cross-tenant promotion visibility` — A tenant configured to allow promoting/showing CFAs from partner tenants → the whitelisted partner-tenant list is read and names resolved for display.

**Notable business rules / limitations**: Tenant DB and tenants DB must never be cross-queried. Hostname `www` stripping is naive and can misresolve hostnames like `www2.example.com`. A tenant-level config value can silently override a newer flag column if names collide. The app always reports itself as HTTPS internally, even served over plain HTTP locally.

#### 4.1.2 Auth

**Purpose**: Authenticates operators (password, Microsoft SSO, or backdoor link), manages their profile/credentials, and administers the roster of admin accounts and roles.

1. `FR-AU-01: Email/password login` — Credentials checked → session issued → role-based landing page chosen (jury/PM/corporate-PM/recruitment-partner/default dashboard).
2. `FR-AU-02: Microsoft SSO login` — Only shown when tenant SSO is enabled → Azure AD auth → shorter-lived (1-hour) session.
3. `FR-AU-03: Backdoor auto-login` — Business backend redirects an already-authenticated user with a one-time token → token validated and immediately invalidated → session created for the target admin.
4. `FR-AU-04: Forgot / reset password` — Operator requests reset by email → backend sends a reset email with a token → operator submits a new password against it.
5. `FR-AU-05: Profile self-service` — Operator updates name/email (uniqueness enforced) or password.
6. `FR-AU-06: Admin account & role management` — Super-admin/developer creates a new admin account (triggers a welcome email with temp credentials) or defines/edits a role's permissions.

**Dependencies**: `GET v1/admin-actions/forgot-password/{email}`, `POST v1/admin-actions/admin-account-created/{adminMd5}`. Flag: `SSO_LOGIN_ENABLED`.

**Notable business rules / limitations**: Login form has CSRF verification disabled (token generated but not checked) — a crafted cross-site form submit could pin attacker-controlled credentials into a victim's login attempt. Backdoor login's redirect target is not allowlisted — a theoretical open-redirect after an authenticated backdoor login. **Password-change does not verify the current password before accepting a new one** — an operator with a hijacked/left-open session can silently take over the account. Backdoor tokens are strictly single-use.

#### 4.1.3 AJAX Handlers

**Purpose**: Back-end configuration and utility actions invoked asynchronously — custom API route management, raw database schema operations, email/WhatsApp template and credential management, dashboard/form configuration, and pushing a stakeholder record to the ecosystem directory.

1. `FR-AJ-01: Custom API route management` — Developer defines a supplemental backend route → add/edit/delete/duplicate.
2. `FR-AJ-02: Database schema management` — Developer creates/drops tables/columns, renames tables (dependent config auto-updated), runs maintenance, or truncates a table.
3. `FR-AJ-03: SMTP & email template management` — Configure SMTP profiles (one default) and template content.
4. `FR-AJ-04: Dashboard & form configuration` — Manage dashboard counters and stakeholder form field-mapping/layout.
5. `FR-AJ-05: WhatsApp (WATI) configuration` — Edit templates; validate/save WATI endpoint, token, template prefix.
6. `FR-AJ-06: Stakeholder ecosystem export` — Push a full startup profile to the ecosystem hub (`POST {ecosystem_hub_api_url}/v1/import/<type>`, unauthenticated call, no response validation).
7. `FR-AJ-07: Field-mapping helper lookups` — Query available columns of a chosen table to wire into form field types via UI.

**Notable business rules / limitations**: **Stakeholder export has no CSRF protection and no cross-tenant ownership check** — any authenticated admin session, including via a forged cross-site request, can trigger a push of an arbitrary startup ID. **Database schema management is the single most powerful/dangerous endpoint in the panel**: raw DDL, no extra role restriction, and the table-rename cascade across 8 config tables is not transactional. Dashboard counter configuration allows a developer-supplied function name with no server-side allowlist. WATI access token is stored as plaintext. All other mutating handlers enforce CSRF and sanitization normally.

#### 4.1.4 Stakeholder CRUD

**Purpose**: The generic, config-driven list/add/edit/detail engine powering management of every stakeholder entity type (startups, investors, corporates, mentors, service providers, partners, program-office members, individuals) and dozens of lookup/master-data tables.

1. `FR-SC-01: List any stakeholder/entity type` — Table existence and role-based access validated → filter/sort/paginated records fetched.
2. `FR-SC-02: Add / edit a record` — Config-driven form (relationship dropdowns, S3 file uploads, rich text, dates) → insert/update; new user-type records also fire-and-forget register in CometChat.
3. `FR-SC-03: View stakeholder detail` — Read-only profile with resolved relationship fields.
4. `FR-SC-04: Master/lookup data management` — Inline modal add/edit of reference data.
5. `FR-SC-05: Tenant-scoped stakeholder-type visibility` — Which entity tabs appear is filtered by the tenant's provisioned entity types.
6. `FR-SC-06: Short profile link backfill (developer-only)` — Batch job (up to 200/run) backfills missing public short links; no rollback if interrupted mid-run.

**Dependencies**: `POST v1/public/auth/register_user/comet_chat/{uuid}` (fire-and-forget). Flags: `limited_access`, `enable_sub_industries`, plus per-stakeholder-type flags.

**Notable business rules / limitations**: Table-name input is validated against actual schema before any query, and role-based table access is a hard gate — both prevent arbitrary table exposure via URL manipulation. Duplicate-cleanup DELETE queries on Programs/Application-Programs lists run automatically on every list view using raw (non-parameterized) SQL interpolation — a latent injection-shape risk if row IDs are ever non-integer. A known template-engine bug can silently render at most one item when looping over arrays in certain templates. Short-link backfill has no rate limiting and can exceed PHP's execution time mid-batch, non-recoverably.

---

### 4.2 Application & Program Lifecycle

*Modules: application-management, startup-application-management-flow, stakeholder-detail-pages, venture-studio, jury, program-management, challenges.*

#### 4.2.1 Application Management

**Purpose**: End-to-end lifecycle management of Call-for-Applications (CFA) programs — creation, round configuration, submission review, AI-assisted scoring, and outreach — plus the legacy direct-enrollment "startup programs" flow.

1. `FR-AM-01: Create a CFA program via 3-step wizard` — Info/media/payment → application-form builder → PM/jury assignment → draft program.
2. `FR-AM-02: Publish / close / reopen / delete a program` — Lifecycle toggles from the detail page; delete cascades to all linked child data.
3. `FR-AM-03: Configure a round` — Rating criteria (weighted/unweighted), video/document requirements, jury assignment.
4. `FR-AM-04: Review submissions on a kanban board` — Per-round kanban with filters, bulk actions, search; a flat table view is an alternate layout.
5. `FR-AM-05: Move / reject / mark-tentative a submission` — Backend round-state API called with a one-time backdoor token → backend updates state, fires applicant email, syncs ecosystem directory.
6. `FR-AM-06: Bulk-email applicants in a round`.
7. `FR-AM-07: Export submissions (CSV/XLSX)`.
8. `FR-AM-08: Run AI-assisted scoring on submissions` — Sends applicant data + scoring thesis to the AI analyzer; results polled and finalized; PM can re-score only unscored applicants or refresh enrichment without re-scoring.
9. `FR-AM-09: Send outreach / promotion requests` — To target tenants/partners; tracked on the program page.
10. `FR-AM-10: Legacy startup-program enrollment flow` — Same round-movement actions backed by `programs`/`program_startup_rounds` instead of CFA tables.

**Dependencies**: `POST v1/application-programs-management/{programUUID}/update-round|reject-round|tentative-round/{adminToken}` (and legacy `v1/programs-management/...` equivalents); `POST .../promotion-request/send/{adminToken}`; AI analyzer direct HTTP (`/upload-csv/`, `/generate-thesis/`, `/start-all-background/`, `/get-response-status/`, `/finalize-analysis/`, `/re-enrich/`). Flags: `application_management`, `call_for_applications_video_enabled`, `request_call_jury`, `corporate_backdoor_login_enabled`.

**Notable business rules / limitations**: Round moves/reject/tentative must go through the backend API — never a direct DB write. Program deletion cascades across 12+ tables with no transaction. A latent bitwise-AND bug in related-data lookups can silently drop data for certain ID arrays. No execution-time/memory cap on export code paths.

#### 4.2.2 Startup Application Management Flow

**Purpose**: Standalone kanban/table/report workspace for moving startups (legacy accelerator programs) through program rounds — the day-to-day evaluator workspace.

1. `FR-SF-01: View startup pipeline as kanban`.
2. `FR-SF-02: Drag a startup to the next round` — Calls the backend round-state API.
3. `FR-SF-03: Reject or mark tentative`.
4. `FR-SF-04: Switch to table or report view`.
5. `FR-SF-05: Create/delete a round`.
6. `FR-SF-06: Bulk-email a round's startups` — Opted-out startups silently excluded; can be saved as a reusable template.
7. `FR-SF-07: Filter and persist filter state` — Per-program, per-PM-session.
8. `FR-SF-08: Export program data / round ratings / jury allotments` (three separate CSV exports).
9. `FR-SF-09: Close a program`.

**Notable business rules / limitations**: PM visibility must always be scoped to assigned programs. `deleteRound` should but does not consistently guard against non-empty rounds. Backend token is MD5-derived, not a JWT — all three round-mutation call sites must be updated together if derivation changes. Broadcast opt-outs are silent (no "N skipped" indicator).

#### 4.2.3 Stakeholder Detail Pages

**Purpose**: Single-entity detail/lifecycle pages for startups, mentors, investors, plus a per-submission detail page and a PM home dashboard — the core "profile review and approve/reject" surface.

1. `FR-SD-01: Review and approve/reject a startup profile` — Status flags update atomically (mutually exclusive); ID card auto-generated on approval if enabled.
2. `FR-SD-02: Issue certificates and ID cards`.
3. `FR-SD-03: Set Technology Readiness Level (TRL)`.
4. `FR-SD-04: Manage connection permissions` — Per-profile toggle of connect/search/moderation and a request limit.
5. `FR-SD-05: Request supporting documents / video pitch` — Notifies the startup via backend call.
6. `FR-SD-06: Upload / delete supporting documents` — Deletion does not remove the underlying S3 object (audit trail retained).
7. `FR-SD-07: Rate a startup` — Overall score computed as the mean of sub-ratings.
8. `FR-SD-08: View/generate pitch video transcript` — Program/tenant-gated PowerPitch transcript or async CLI-worker field transcript.
9. `FR-SD-09: Review a single application-round submission` — With PDF export.
10. `FR-SD-10: Mentor / investor profile review` — Same approve/reject pattern, role-specific fields.
11. `FR-SD-11: Program Manager home dashboard` — Counts scoped to the PM's own assignment; no mutation actions.

**Dependencies**: `POST v1/admin-actions/request-supporting-documents/{adminToken}`, `GET v1/admin-actions/request-video-pitch/{startupId}/{adminToken}`, `GET/POST v1/power-pitch/transcript/{videoUUID}`. Flags: `startup_id_cards`, `powerpitch_transcript_enabled`, `form_video_transcript_enabled`.

**Notable business rules / limitations**: ID-card auto-generation failure never rolls back the approval. `startup_id_cards` is only checked at render time, not re-validated on the POST handler. Connection-matrix writes are direct DB, not backend-synced — a backend that caches this at boot may not reflect changes until restart. PDF export silently drops oversized images rather than erroring.

#### 4.2.4 Venture Studio

**Purpose**: Parallel program-management track for Venture Studio programs, where individuals (not companies) apply and can be grouped into teams afterward.

1. `FR-VS-01: Create a VS program via 3-step wizard` — Mirrors CFA, with `account_type=individual`.
2. `FR-VS-02: Manage VS rounds`.
3. `FR-VS-03: Review and progress individual applicants` — Same backend-API pattern as CFA.
4. `FR-VS-04: Assign jury to individual applicants`.
5. `FR-VS-05: Form teams from accepted individuals` — No enforced member-count or referential constraint.
6. `FR-VS-06: Delete a team`.

**Dependencies**: `POST v1/vs-programs-management/{programUUID}/update-round|reject-round|tentative-round/{adminToken}`. Flag: `venture_studio_application_management`.

**Notable business rules / limitations**: VS data must never mix with CFA tables. Team creation has no idempotency guard. Same bitwise-AND related-data bug present in one of two lookup implementations.

#### 4.2.5 Jury

**Purpose**: The fully-restricted interface for jury-role users — reviewing allotted items and submitting ratings — plus a reviewer/super-admin sub-view for bulk-approving jury ratings.

1. `FR-JU-01: Jury login redirect and restricted navigation`.
2. `FR-JU-02: Dashboard overview of allotments` — Segmented by program type, gated by which types are enabled.
3. `FR-JU-03: Review and rate a startup/CFA/mentor/individual application` — Overall rating computed weighted or unweighted per round config.
4. `FR-JU-04: Mark an item "not interested"` — Admin-DB-only status; not propagated to backend/PWA.
5. `FR-JU-05: Answer jury-specific questions` — Text or file upload, separate from the main form.
6. `FR-JU-06: Reviewer bulk-approve ratings`.
7. `FR-JU-07: Re-rate an existing allotment` — Updates the existing row, never duplicates.

**Notable business rules / limitations**: Both the session check and the explicit jury-role check are required on every jury route. "Not interested" status never propagates cross-system, so allotment counts can diverge from the applicant-facing side. The rating-summary handler is N+1 (one query per allotment). File-answer uploads derive extension from a user-supplied filename, not MIME sniffing — combined with public-read storage config, a potential upload-of-executable-content risk.

#### 4.2.6 Program Management

**Purpose**: Role-scoped home dashboards for PMs and Corporate PMs, the mentor-application onboarding pipeline, and the (existing-record) program setup wizard.

1. `FR-PM-01: PM home dashboard` — Scoped to assigned programs/challenges.
2. `FR-PM-02: Corporate PM home dashboard` — Scoped to the corporate's challenges and linked CFA programs.
3. `FR-PM-03: Manage the mentor pipeline` — Kanban ordered by profile completeness; backend-API-driven advance/reject/tentative.
4. `FR-PM-04: Edit an existing program (3-step wizard)` — Details/media/payment, application form management, PM/jury assignment.
5. `FR-PM-05: Publish a program`.
6. `FR-PM-06: Scoped access enforcement on the wizard` — Jury bounced; partner/PM scoping checked; super-admin bypasses all three.

**Dependencies**: `POST v1/mentor-application-management/update-round|reject-round|tentative-round/{adminToken}`.

**Notable business rules / limitations**: All PM-facing queries must scope via `JSON_CONTAINS` on the assignee field — never list all programs/challenges for a PM. The role-mismatch redirect target on the PM dashboard is itself — a genuine redirect-loop bug on unexpected role-check failure. Mentor application numbers are backfilled lazily with no uniqueness constraint — concurrent requests can duplicate.

#### 4.2.7 Challenges

**Purpose**: Manage corporate-originated "Business Challenge" listings — approval, assignment, CFA-program linkage, participant review.

1. `FR-CH-01: Create a challenge` — Enters `pending` approval status; optionally linked to a CFA program.
2. `FR-CH-02: List and search challenges`.
3. `FR-CH-03: View challenge detail and participants` — Enriched with industry, delivery model, maturity stage.
4. `FR-CH-04: Approve / assign a challenge`.
5. `FR-CH-05: Activate / deactivate a challenge`.
6. `FR-CH-06: Corporate PM scoped challenge view`.
7. `FR-CH-07: Geo cascade selection` — Country → state → city.

**Notable business rules / limitations**: **Live bug** — `details.php` compares the raw JSON `assigned_to` string against a scalar admin ID, which effectively never matches, locking out all non-super-admin PMs from challenge detail pages they should have access to; needs `json_decode()` + `in_array()`. No backend notification on publish/status-change. Participant enrichment is N+1 (3–4 queries per participant).

---

### 4.3 Learning, Events & Community

*Modules: learning-management, events-meetings, community-connections, connections.*

#### 4.3.1 Learning Management

**Purpose**: Author and publish online courses, manage learner enrollments, and monitor LMS activity — a content-management layer feeding the member-facing frontend.

1. `FR-LMS-01: Create Course` — Draft with UUID + slug.
2. `FR-LMS-02: Build Course Structure` — Sections/lessons/resources, reordered by admin-defined sort order.
3. `FR-LMS-03: Publish / Unpublish Course`.
4. `FR-LMS-04: Manage Course Categories`.
5. `FR-LMS-05: Manage Instructors`.
6. `FR-LMS-06: View LMS Dashboard` — Course/learner counts, 7-day enrollment trend, top 6 courses, recent enrollments, quick-publish widget.
7. `FR-LMS-07: Run Enrollment Reports` — Filter by date range/type.
8. `FR-LMS-08: View & Search Enrollments`.

**Dependencies**: no backend API calls — direct tenant-DB writes; the backend independently reads the same tables. Flag: `learning_management` (currently consumed only for invoice line items, not as an in-module gate).

**Notable business rules / limitations**: Sidebar links are commented out platform-wide (soft-launch), but the module remains reachable by direct URL regardless of the flag. No cache-invalidation signal to the backend. CSRF protection is inconsistent (enforced in Settings, absent on course creation). Report date-range filtering uses weak escaping (`addslashes`) on raw SQL fragments — a latent injection risk if session values are ever populated from unsanitized input.

#### 4.3.2 Events & Meetings

**Purpose**: Organize multi-date events with an approval-gated booking flow, and oversee peer-to-peer meetings (notes, feedback, video session history).

1. `FR-EVT-01: Create/Edit Event` — Multiple date/time slots with breaks, banner image, draft state.
2. `FR-EVT-02: Publish / Unpublish Event`.
3. `FR-EVT-03: Approve Attendee Booking` — Notifies backend, which sends a calendar invite and confirmation email.
4. `FR-EVT-04: Reject Attendee Booking` — See limitation: currently a direct DB archive+delete, bypassing the intended backend call.
5. `FR-EVT-05: Reschedule Attendee Booking` — Backend-notified, triggers a reschedule notification.
6. `FR-EVT-06: Manually Add Attendee`.
7. `FR-EVT-07: Cancel Event` — Backend-notified.
8. `FR-MTG-01: View Meeting Detail` — Both participants' notes, grouped feedback answers, live video-SDK session log.
9. `FR-MTG-02: Configure Meeting Feedback Questionnaire`.
10. `FR-MTG-03: Review Feedback Responses`.

**Dependencies**: `PATCH v2/events/approve_request|reject_request|cancel|remove_attendee|reschedule/{uuid}/{adminToken}`; external `GET {3p_api_server_url}/v2/video-sdk/meetings/{meetingCode}/sessions`. Flag: `jury_role_id` hard-excludes jury admins from both modules; no tenant flag gates the modules themselves.

**Notable business rules / limitations**: **Rejection does not notify the backend today** — the intended reject API call is bypassed for a direct archive+delete, so rejection emails are silently not sent and any backend-side copy of the record can drift. A one-time legacy-date-format migration shim runs on every events-list load, adding per-row overhead on tenants with large unmigrated volumes. Feedback question ordering uses a non-atomic `COUNT(*) + 1` — concurrent creation can produce duplicate positions.

#### 4.3.3 Community & Connections (Moderation)

**Purpose**: Moderate the member-facing Community Wall and provide the admin entry point into connection oversight (full matrix configuration is covered in 4.3.4).

1. `FR-CW-01: Moderate / Remove Wall Post` — Soft-deletes the post and any attached poll together.
2. `FR-CW-02: Delete Comment` — Top-level or reply.
3. `FR-CW-03: Create Admin-Authored Post` — Flagged as an official/system post; optionally tags a member profile.
4. `FR-CW-04: Review Post Comment Thread`.
5. `FR-CN-OVERVIEW: Browse Connections (entry point)` — All top-level connection requests platform-wide, for support/analysis.

**Notable business rules / limitations**: No pre-publish approval queue — moderation is reactive only. Admin-authored posts must never carry a `user_id` (only optional profile tagging) — this flag distinguishes system posts. A known bug: comments from program-office members display no author name in the single-post comment view. The connections overview here loads **all** connections and **all** approved profiles into memory with no pagination — a scalability risk on large tenants.

#### 4.3.4 Connections (Permission Matrix)

**Purpose**: Manage all peer-to-peer connection requests and configure the two-tier permission system (global defaults + per-user overrides) governing who may connect with, search for, and require moderation against whom.

1. `FR-CON-01: View Connection List` — Root (non-threaded) requests, filterable by profile type.
2. `FR-CON-02: View Connection Detail` — Type-specific context (mentorship, kit-application, shared meetings) plus a backdoor-login link for support.
3. `FR-CON-03: Configure Global Connection Matrix` — Per profile-type pair: can-connect / can-search / requires-moderation.
4. `FR-CON-04: Set Daily Connection Request Limit` — Per profile-type pair.
5. `FR-CON-05: Cascade Global Change to Existing Users` — Any global matrix save bulk-overwrites every existing user's per-pair override with the new default, discarding prior customization.
6. `FR-CON-06: Reset an Individual Profile's Overrides` — Reseeds from current global defaults.
7. `FR-CON-07: Auto-Seed Matrix on First Use` — Generates one row per ordered stakeholder-type pair (excluding `other`/`job_seeker`) the first time the matrix is opened for a tenant with no rows.

**Notable business rules / limitations**: **The global-matrix cascade (FR-CON-05) is destructive and immediate with no undo** — the only safeguard is an easily-missed UI warning banner. The matrix does not auto-expand for a newly-added stakeholder type — seeding only runs on a completely empty table. The matrix-update endpoint can return success even when the secondary user-level bulk-update fails, silently desyncing the two permission layers. `parent_id = null` is the mandatory filter for root connection requests — any new report must preserve it.

---

### 4.4 Finance & Memberships

*Modules: finance-memberships, payment-gateways, memberships, tax-management.*

#### 4.4.1 Finance & Memberships (Overview)

**Purpose**: Central admin surface for membership plan/policy configuration and finance operations — orders, transactions, proforma invoices, coupons, taxes, gateway settings.

1. `FR-FM-01: Configure global membership settings` — Label text, visibility type, moderation on/off; writes to the shared tenants DB.
2. `FR-FM-02: Manage per-stakeholder membership plans` — Pricing, duration, tax/charge config per enabled stakeholder type.
3. `FR-FM-03/04: View orders / transactions` — Transaction view hidden from jury-role users.
4. `FR-FM-05: Generate & send a proforma invoice` — Auto-includes LMS line items when learning management is enabled.
5. `FR-FM-06: Resend an order invoice`.
6. `FR-FM-07: Backfill historical invoices`.
7. `FR-FM-08: Manage coupons`.
8. `FR-FM-09/10: Tax and gateway settings (duplicate entry point)` — Mirrors the standalone Tax Management and Payment Gateways modules.

**Dependencies**: `POST v1/payments/invoice-manual/{orderId}/{transactionId}`, `POST v1/payments/proforma-invoice/send/{uuid}/{adminToken}`, `POST v1/memberships/upgrade-request/accept|reject/{requestId}/{adminToken}`. Tenants-DB write: `tenant_users.membership_label_text/membership_visibility_type/membership_moderation_enabled`.

**Notable business rules / limitations**: The tenants-DB config write can silently no-op if that connection errored at bootstrap — the UI reports success regardless. Gateway credential validation runs synchronously against live provider APIs; a slow/down provider blocks the PHP process. Two parallel UI paths exist for gateway settings that must be kept in sync by hand.

#### 4.4.2 Memberships (Lifecycle & Certificates)

**Purpose**: Manage the full lifecycle of membership records across all stakeholder types.

1. `FR-MEM-01: Manually create a membership` — Activates the plan, expires any prior active membership, marks pending upgrade requests "renewed," optionally auto-issues a certificate, approves the profile, records a manual order+transaction, emails an invoice.
2. `FR-MEM-02: Edit membership dates` — Linked certificate dates re-sync; cached image cleared to re-render.
3. `FR-MEM-03: Soft-delete a membership` — No automatic status/expiry cleanup.
4. `FR-MEM-04: Approve profile via membership action` — Bulk-approve; backend sends the approval email.
5. `FR-MEM-05: Review upgrade requests` — Accept (records target plan) or reject (records reason); accepting still requires a separate FR-MEM-01 run to actually provision the upgrade.
6. `FR-MEM-06: Generate a certificate` — Idempotent.
7. `FR-MEM-07: Regenerate a certificate` — Preserves the original number.
8. `FR-MEM-08: Bulk-generate certificates` — Up to 200 eligible memberships at a time.

**Dependencies**: `POST v1/admin-actions/send-profile-approval-email/{token}`, `POST v1/admin-actions/approve/{profile_type}/{profile_id}/{token}`, `POST v1/payments/invoice-manual/{orderId}/{transactionId}`, `POST v1/memberships/upgrade-request/accept|reject/{requestId}/{token}` — all via short-lived, single-use backdoor tokens. Flags: `certificates` AND `certificates_membership` both required for auto-issuance on create.

**Notable business rules / limitations**: Only one active membership per profile, enforced synchronously (no background job). No standalone cancel/auto-expiry action exists. Auto-issued certificates stamp today's date rather than the order/invoice date used elsewhere — a known inconsistency. Backend email/approval calls are fire-and-forget — failures don't roll back the already-saved membership record.

#### 4.4.3 Payment Gateways

**Purpose**: Configure per-tenant gateway credentials, activation state, primary gateway, and the tenant-wide test/live mode.

1. `FR-PG-01: View gateway status`.
2. `FR-PG-02: Activate / deactivate a gateway` — Activation validates credentials against the provider's live API.
3. `FR-PG-03: Set the primary gateway` — Re-validates, then clears "primary" from all others.
4. `FR-PG-04: Update gateway credentials`.
5. `FR-PG-05: Switch payments mode (test ↔ live)` — Re-validates every active gateway; commits only if all pass, else reports which failed.

**Dependencies**: direct provider APIs (Stripe, Razorpay, Easebuzz, PayPal — the last dormant/unseeded). Flag: `payment_gateways`.

**Notable business rules / limitations**: Credentials stored in plaintext with no encryption at rest. **Validating Easebuzz in live mode fires a real ₹1 transaction** — a billable side effect of simply enabling the gateway, not a dry-run. Duplicate UI exists elsewhere requiring manual sync. A seeding defect leaves `live_client_secret` unpopulated for new tenants until saved once via the UI. No CSRF protection on any gateway action.

#### 4.4.4 Tax Management

**Purpose**: Maintain the master list of tax profiles used to compute tax on orders and invoices.

1. `FR-TAX-01: Create a tax profile`.
2. `FR-TAX-02: Edit a tax profile`.
3. `FR-TAX-03: Activate / deactivate a tax profile`.
4. `FR-TAX-04: Delete a tax profile` — Permanent.
5. `FR-TAX-05: Browse tax profiles`.

**Notable business rules / limitations**: Deletion is permanent — deleting a profile referenced by historical invoices leaves those records pointing at a profile that no longer exists. The "name required" validation has a logic bug that effectively disables it in some input forms. Input strings are stripped of quote characters (not escaped) before saving.

---

### 4.5 Outreach, Content, Certificates, Metrics & Reporting

*Modules: outreach-communications, content-management, certificates, growth-metrics, milestones, tickets, reporting, reporting-certificates.*

#### 4.5.1 Outreach & Communications

**Purpose**: Reach cohorts of stakeholders via bulk email/WhatsApp, maintain a lightweight CRM contact book, manage chat canned responses, and exchange cross-tenant program-promotion requests.

1. `FR-OUT-01: Send a broadcast message` — Filter recipients by status/industry/geography/technology; email via SES or WhatsApp via WATI templates.
2. `FR-OUT-02: Review broadcast history`.
3. `FR-OUT-03: Manage canned chat responses`.
4. `FR-OUT-04: Maintain CRM contacts`.
5. `FR-OUT-05: Send an outreach/promotion request` — Backend emails the target partner and logs the request.
6. `FR-OUT-06: Approve/reject an inbound promotion request`.
7. `FR-OUT-07: Track promotion delivery` — Reads the tenants DB.
8. `FR-OUT-08: Configure WhatsApp (WATI) integration`.

**Dependencies**: `POST v1/application-programs-management/promotion-request/{accept|reject|send}/{adminToken}`. Flags: `canbroadCastMessage` (a role permission, not a tenant flag — inconsistent with the platform's usual model), `promotions_enabled`, `promotions_partners_enabled`, `limited_access`.

**Notable business rules / limitations**: Recipient targeting builds raw SQL (`JSON_CONTAINS`) from user-selected IDs — currently safe only because inputs come from UI selects, not free text. WhatsApp template-prefix mismatches silently leave templates unmatched with no visible error.

#### 4.5.2 Content Management

**Purpose**: Publish and manage all incubator-facing content: news, glossary, resources, video gallery, industry reports, product updates, ad banners, and the startup "booster kit" marketplace.

1. `FR-CM-01: Publish a news article`.
2. `FR-CM-02: Manage glossary terms`.
3. `FR-CM-03: Upload a resource file` — S3-backed, tagged by industry and visibility.
4. `FR-CM-04: Add a video to the gallery` — YouTube URL validated as genuine before saving.
5. `FR-CM-05: Publish an industry report` — PDF or external URL.
6. `FR-CM-06: Post a product update`.
7. `FR-CM-07: Manage ad banners` — Placement zone, image, link, active dates.
8. `FR-CM-08: List a booster-kit service` — Optionally auto-provisions a service_provider account.
9. `FR-CM-09: View booster-kit service detail`.

**Dependencies**: no backend API calls — direct tenant-DB writes; every create/edit busts the backend's content cache explicitly. Flag: `service_kit_stakeholder_accounts`.

**Notable business rules / limitations**: Content is not real-time to end users — visible only after the backend's cache expires or is busted. Booster-kit creation silently reuses an existing service_provider account if the contact email matches one already — two services can end up sharing (and potentially orphaning) the same provider profile.

#### 4.5.3 Certificates & ID Cards

**Purpose**: Design certificate/ID-card visual templates per stakeholder type, then bulk-issue, revoke, reactivate, or regenerate issuance records — visual rendering happens client-side in the frontend, not as a generated PDF.

1. `FR-CERT-01: Design a certificate template` — Theme, colors, logo, text, up to 3 signatories.
2. `FR-CERT-02: Bulk-issue certificates` — Auto-formatted number, 2-year validity; re-selecting a certified startup updates dates only, keeping the original number.
3. `FR-CERT-03: Review issued certificates`.
4. `FR-CERT-04: Design an ID-card template` — Startup-only currently; configurable validity period.
5. `FR-CERT-05: Bulk-issue ID cards`.
6. `FR-CERT-06: Revoke / reactivate an ID card` — Only revoked cards can be reactivated.
7. `FR-CERT-07: Regenerate an ID card` — Regenerates the number if the prefix changed since original issuance, invalidating previously shared QR/links.

**Dependencies**: no backend API calls — tenant-DB local, no PDF generation. Flags: `certificates` (master) + nine per-stakeholder-type flags; ID cards use a single independent `startup_id_cards` flag.

**Notable business rules / limitations**: Certificate re-issuance never regenerates the number even if the prefix changed; ID-card regeneration does — the two flows are intentionally inconsistent, worth flagging to admins. A supporting SQL view is created lazily on first list load; without `CREATE VIEW` privilege, the list silently renders with missing columns.

#### 4.5.4 Growth Metrics

**Purpose**: Define KPI types startups report against periodically, review submissions, and manage a controlled edit-request process.

1. `FR-GM-01: Configure metrics reporting period` — Cadence + financial-year start month; all metrics screens redirect here until set.
2. `FR-GM-02: Define a metric type` — Optionally restricted to specific programs.
3. `FR-GM-03: Review per-startup metrics` — Currency-converted display.
4. `FR-GM-04: Review and action edit requests`.
5. `FR-GM-05: Bulk-email a metrics reporting round`.

**Dependencies**: cross-DB write of `growth_metrics_duration`/`growth_metrics_financial_year_start_month`/`growth_metrics_duration_set` to the tenants DB. Jury-role admins excluded.

**Notable business rules / limitations**: A silent tenants-DB write failure leaves `growth_metrics_duration_set` unset, causing a redirect loop back to setup with no visible error. Currency-display selection persists in session across all startups viewed. One metrics list view is intentionally reachable without authentication (public reporting, not a bug).

#### 4.5.5 Milestones (Admin Oversight)

**Purpose**: Oversight dashboard over milestone/goal records stakeholders create and update via the PWA — admins view but do not create/edit here.

1. `FR-MS-01: Browse milestones`.
2. `FR-MS-02: View milestone detail` — Progress, assigned reviewers, owning stakeholder's profile, evidence attachments.

**Notable business rules / limitations**: Purely read-only by design for admins. The account-type switch used to resolve a stakeholder's profile covers only seven known types — a new account type added elsewhere breaks the detail page until this module is updated. Loading the detail page can indirectly trigger backend-side recomputation writes to milestone stats.

#### 4.5.6 Tickets (Support)

**Purpose**: A support inbox to triage, assign, and respond to member help requests, with outbound notification email delegated to the backend.

1. `FR-TKT-01: Browse and search tickets`.
2. `FR-TKT-02: Assign a ticket` — Backend sends an allotment email.
3. `FR-TKT-03: Reply to a ticket` — Backend emails the member.
4. `FR-TKT-04: Change ticket severity`.
5. `FR-TKT-05: Close / reopen a ticket` — Logged to the admin audit trail.
6. `FR-TKT-06: Attach a file to a ticket reply` — Direct S3 upload.

**Dependencies**: `POST v1/admin-actions/send-ticket-allotment-email/{token}`, `POST v1/admin-actions/send-ticket-response-email/{token}` — best-effort, do not roll back the DB write on failure.

**Notable business rules / limitations**: **No file-type/MIME validation on attachment upload** — any file type can be uploaded to S3. Assigned admin IDs are accepted without verifying they're real admin users. No CSRF protection on any of the seven ticket actions.

#### 4.5.7 Reporting (BI Dashboards)

**Purpose**: A self-contained analytics builder for role-gated dashboards from chart/table widgets, each backed by a SQL query — hand-authored by a developer or auto-generated from tenant data — with all queries run directly against the tenant's own database.

1. `FR-RPT-01: Browse dashboards` — Only role-permitted dashboards shown (or all, if developer role).
2. `FR-RPT-02: View a dashboard` — Widget queries execute or serve a 5-minute cache.
3. `FR-RPT-03: Build/edit a dashboard` — Any logged-in admin can access the builder page (no extra gate).
4. `FR-RPT-04: Author a SQL template` (dev only).
5. `FR-RPT-05: Define an auto-source` (dev only) — Synthesizes virtual chart templates per column × chart-type without persisting them.
6. `FR-RPT-06: Drill down on a chart`.
7. `FR-RPT-07: Export widget data` — CSV per widget, Excel per dashboard.
8. `FR-RPT-08: Clone a dashboard or template`.

**Dependencies**: no backend calls — direct tenant-DB reads. No cockpit feature flag; access controlled by admin roles (`is_dev` for authoring, dashboard-level `allowed_roles` for viewing).

**Notable business rules / limitations (flagged plainly, not exhaustively re-audited here)**: **Templates can execute raw, dev-authored SQL directly against the tenant database**, protected by a denylist of dangerous keywords that is known to be bypassable (e.g. `SELECT...INTO OUTFILE`, `SLEEP()`, `CALL <procedure>`, `UNION SELECT` against `information_schema`) — authoring is restricted to the developer role as the primary control. **No item-level authorization on chart execution, export, or drilldown** — any logged-in admin who obtains a widget's UUID can pull its data regardless of the dashboard's `allowed_roles`. Drilldown "extra_where" is interpolated unquoted/unbound and is admin-editable via the builder. The 10,000-row export cap is skippable if the template's SQL already contains its own `LIMIT`. PDO errors are returned verbatim to the browser on query failure, which can leak table/column names. The dashboard builder does not check `allowed_roles` (only the view page does).

#### 4.5.8 Reporting & Certificates (Umbrella + Form Builder)

**Purpose**: Packages the Reporting/BI dashboard builder and the Certificates/ID Cards system (both described above) together with a **Form Builder** used to construct custom data-collection forms whose submissions feed the reporting auto-template source.

1. `FR-FORM-01: Build a custom form` — Public or program-scoped visibility, optionally restricted to specific program rounds; autosave toggle for respondents.
2. `FR-FORM-02: Publish/manage form fields` — Type-specific validation and options.
3. `FR-FORM-03: Use form submissions as a reporting source` — Fields become an auto-generated reporting data source with no manual template authoring.

**Notable business rules / limitations**: All Reporting and Certificates findings above apply identically here (same underlying code). Auto-templates are synthesized live from the current form definition, not snapshotted — a form field change can silently change what an existing auto-generated widget reports on, though already-placed dashboard widgets snapshot their SQL at add-time and are unaffected until manually refreshed.

---

### 4.6 Facilities, Partners, Forms, Integrations & System Administration

*Modules: facilities, partners-recruitment, form-management, integrations, system-admin, profile-audit-logs.*

#### 4.6.1 Facilities

**Purpose**: Manage incubator physical-space booking end-to-end — space setup, availability/pricing/add-ons, bookings, and post-booking ratings.

1. `FR-FAC-01: Define a facility type` — Partner-scoped.
2. `FR-FAC-02: Configure per-type booking questions`.
3. `FR-FAC-03: Configure per-type rating criteria`.
4. `FR-FAC-04: Create/publish a facility` — Availability windows, per-user-category pricing, add-ons, images; publish makes it bookable and visible on the public ecosystem directory.
5. `FR-FAC-05: Manage bookings via calendar dashboard` — Month calendar of confirmed bookings, filterable by partner.
6. `FR-FAC-06: Approve/inspect a booking`.
7. `FR-FAC-07: Deactivate/delete a facility` — Soft-deactivates in the tenant DB and unpublishes the matching cross-tenant ecosystem-directory entry in the same action.

**Dependencies**: no backend calls — direct DB writes to both the client DB and, for the ecosystem sync, the tenants DB (`ecosystem_facilities`). Flags: `facility_management` (partner access gate), `partners_photo_gallery`, `premium_modules_visibility` (upsell CTA only).

**Notable business rules / limitations**: Facility types (and therefore facilities) are strictly partner-scoped. The ecosystem-directory sync on delete is best-effort, not transactional — a failed second write can leave a deleted facility publicly visible with no automatic reconciliation. Custom question/rating forms are schema-introspected from the DB table — a raw migration changes the admin form immediately with no validation safety net.

#### 4.6.2 Partners & Recruitment

**Purpose**: Give partner sub-admins a scoped cockpit over their own ecosystem slice, and give recruitment-partner-role admins a narrow view over jobs/applications assigned to them.

1. `FR-PTR-01: Partner login` — Session tagged with `partner_id`.
2. `FR-PTR-02: Partner dashboard summary` — Aggregated stakeholder counts across their ecosystem, gated by `partners_enable_dashboard`.
3. `FR-PTR-03: Manage stakeholder lists` — Pre-filtered to the partner, gated by relevant visibility flags.
4. `FR-PTR-04: Invite users to the platform` — Batch or single, via the backend invite API using the partner's session token.
5. `FR-PTR-05: Partner photo gallery` — Gated by `partners_photo_gallery`.
6. `FR-PTR-06: Request a premium module` — Gated by `premium_modules_visibility`; submits a lead + a backend notification for sales follow-up.
7. `FR-PTR-07: Recruitment partner job review` — Recruitment-partner-role admins see only jobs where they're listed, with application counts.
8. `FR-PTR-08: Manage job applications` — Review resumes (signed S3 URLs), shortlist/reject, schedule interviews.

**Dependencies**: `POST v1/partners/invite-users`, `POST v1/partners/invite-users-instant`, `POST v1/partners/premium-module/request/{partnerUUID}`.

**Notable business rules / limitations**: Partner session and admin session are not mutually exclusive at the code level — if both session keys are set simultaneously, query scoping can leak; session must be fully cleared on login/logout. Invite calls silently fail on an expired token (the 401 isn't checked), so "invite sent" confirmations can be false positives. A known counting bug adds rejected applications to the "shortlisted" counter on the recruitment-partner dashboard, intentionally left pending product sign-off. The premium-module lead capture and its backend notification are not transactional.

#### 4.6.3 Form Management

**Purpose**: Build, version, and publish custom application forms, plus bulk CSV import/export of stakeholder data.

1. `FR-FRM-01: Create a form` — Target account type, optional program link, permanent public form code.
2. `FR-FRM-02: Build form fields (drag-and-drop)` — 20+ field types; account-type system fields pre-merged in.
3. `FR-FRM-03: Save creates a version snapshot` — Full field JSON written to the audit-log table on every save.
4. `FR-FRM-04: View & restore a prior version` — Overwrites the live form's field definition (validated non-empty first).
5. `FR-FRM-05: Preview a published form`.
6. `FR-FRM-06: Export stakeholder data to CSV` — Resolves master data, signs S3 file-field URLs, formats for spreadsheet safety.
7. `FR-FRM-07: Import stakeholder data from CSV` — Geo-name resolution tolerant of formatting variance.

**Dependencies**: no backend API calls (a separate ecosystem-export handler pushes to the ecosystem hub outside this module's core flow — see FR-AJ-06).

**Notable business rules / limitations**: `forms.fields` must always be a valid non-empty JSON array of sections — the version-restore path has a documented history of literal-vs-real-`null` corruption; the current multi-condition guard must not be simplified. Version history piggybacks on the general admin audit-log table. CSV export sets extreme PHP memory/time limits, so a stuck export can hold a process indefinitely.

#### 4.6.4 Integrations

**Purpose**: Umbrella for third-party/service integrations: Zoho CRM sync, S3 storage administration, local file management, one-off directory scrapers, and cross-tenant Intellectual Property (patent) management.

1. `FR-INT-01: Connect Zoho CRM` — OAuth client credentials + one-time authorization code; tokens auto-refresh on expiry.
2. `FR-INT-02: Map fields to Zoho` — Per stakeholder type, standard or custom fields.
3. `FR-INT-03: Browse and manage S3 storage` — Bucket browsing, bulk ACL updates.
4. `FR-INT-04: Browse local file manager` — Server `uploads/` folder tree.
5. `FR-INT-05: Import external directories via scraper` — Developer-role only; browser-download CSV, no DB write.
6. `FR-INT-06: Manage Intellectual Property records` — Patent CRUD and connect-request visibility, gated by `intellectual_property_section`; stored in the shared tenants DB (cross-tenant registry, by design).

**Dependencies**: direct calls to Zoho's own OAuth/CRM REST API and to public scraper source URLs. Flags: `zoho_service_enabled`, `intellectual_property_section` (internally read as `partners_ip_management` — a naming mismatch worth noting).

**Notable business rules / limitations**: The IP module's tenants-DB write is intentional but easy to break by mistake — accidentally writing to the client DB silently loses records from the shared registry. The Capboard scraper has production-inappropriate error display left enabled and only basic URL validation — should stay developer-only. Zoho field mappings can go stale after a schema change to a mapped table, silently pushing nulls to Zoho thereafter.

#### 4.6.5 System Admin (Developer Console)

**Purpose**: Super-admin/developer configuration cockpit for the admin panel itself — API route exposure, raw DB schema operations, email/SMTP and templates, sidebar menus, form-field/table-view metadata, generic settings, WhatsApp templates, system logs, and internal task tracking.

1. `FR-SYS-01: Manage API route exposure` — Toggle field/relation visibility, add custom supplemental routes.
2. `FR-SYS-02: Run database maintenance` — Create/alter/rename/drop/truncate tables directly against the tenant DB; renames cascade to dependent config tables, but not atomically.
3. `FR-SYS-03: Configure outbound email` — SMTP profiles (one default), templates per trigger event.
4. `FR-SYS-04: Manage sidebar/topbar menus` — Falls back to a hardcoded default set if the config table is empty.
5. `FR-SYS-05: Configure table views and form-field mappings` — Drives every entity-list page's rendering without code changes.
6. `FR-SYS-06: Manage generic settings & WhatsApp config`.
7. `FR-SYS-07: Review system (admin action) logs` — Write-once audit trail, deep-linking to affected records where resolvable.
8. `FR-SYS-08: Track internal tasks` — Lightweight admin-team to-do tracking.

**Dependencies**: no backend calls — all configuration is local; email send uses SMTP directly.

**Notable business rules / limitations**: Only one SMTP profile may be default. Table renames touch eight dependent config tables in sequence with no transaction. Database Management's table-name input relies on backtick-escaping/existing sanitization rather than a hard allowlist — a real footgun even though access is role-gated. Email-send has CSRF verification and input sanitization explicitly disabled to allow rich HTML composition — must not be exposed to non-developer roles without restoring CSRF protection. Encrypted settings values must always go through the decrypt helper.

#### 4.6.6 Profile Audit Logs

**Purpose**: Read-only viewer for backend-generated, field-level change history on stakeholder profiles — answers "who changed what, and when?"

1. `FR-PAL-01: Browse profile change history` — Paginated (25/page), sortable, newest-first.
2. `FR-PAL-02: Filter by entity/action/actor` — Only whitelisted filter keys applied.
3. `FR-PAL-03: Free-text search` — Against stakeholder type, entity type, action.
4. `FR-PAL-04: View a clean diff` — System-noise columns suppressed via a global + per-entity denylist before rendering.

**Dependencies**: no backend calls — pure read of a table the backend's own audit-log service populates; this module writes nothing to it.

**Notable business rules / limitations**: Must never write to the audit-log table — corrections belong to the backend service. Date filters are only key-whitelisted, not value-sanitized — an invalid date string is silently coerced by MySQL rather than rejected. Free-text search state is cleared unconditionally on every page load, so it doesn't persist across navigation the way an admin might expect.

## 5. Consolidated Security & Known-Limitations Summary

The following table (carried forward from `specs/admin-module-specs-index.md`, current as of this FRS's writing) lists the highest-priority known issues across the modules above, for prioritization purposes. These are current-state defects, not designed behavior, and are repeated here because an FRS reader evaluating "what does approving/rejecting/paying actually do" needs to know where the guarantees are weaker than they appear.

| Severity | Module | Finding |
|---|---|---|
| 🔴 Critical | System Admin | Database Management constructs DDL from request input with only backtick-quoting, no allowlist. |
| 🔴 Critical | Auth | Password change skips old-password verification — any active session can change the password. |
| 🔴 Critical | Auth | Login CSRF protection is present in code but verification is disabled. |
| 🔴 Critical | Reporting | Raw SQL from stored templates executes via PDO; the dangerous-keyword denylist is bypassable. |
| 🔴 Critical | Reporting | No item-level authorization on chart execution/export/drilldown — a known widget UUID bypasses `allowed_roles`. |
| 🟠 High | AJAX Handlers | Stakeholder export has no CSRF check and no ownership validation on the target ID. |
| 🟠 High | System Admin | Email-send action has CSRF and sanitization explicitly disabled. |
| 🟠 High | Integrations | Intellectual Property writes to the shared tenants DB — cross-tenant blast radius if misdirected. |
| 🟠 High | Auth | Open redirect in backdoor login — the redirect target is not validated against an allowlist. |
| 🟠 High | Payment Gateways | Credentials stored as plaintext; Easebuzz live-mode validation fires a real transaction, not a dry-run. |
| 🟠 High | Tickets | No file-type validation on attachment upload — any file type is accepted to S3. |
| 🟠 High | Reporting | Export's 10,000-row cap is skippable via a template-embedded `LIMIT`. |
| 🟡 Medium | Stakeholder CRUD | Raw, non-parameterized SQL in duplicate-cleanup DELETE queries on two list views. |
| 🟡 Medium | Community & Connections | The connections overview loads all connections and all profiles with no pagination. |
| 🟡 Medium | Challenges | `details.php`'s JSON-vs-scalar comparison bug locks all non-super-admin PMs out of challenge detail pages. |
| 🟡 Medium | Events & Meetings | Booking rejection bypasses the intended backend notification call — rejection emails are not sent. |
| 🟡 Medium | Finance & Memberships | Payment gateway validation calls third-party APIs synchronously — a slow gateway blocks the PHP process. |
| 🟡 Medium | Connections (Matrix) | The global-matrix cascade overwrites all per-user overrides for a type pair with no undo. |
| 🟡 Medium | Learning Management | The `learning_management` flag is not enforced inside LMS handlers — reachable by direct URL regardless of flag state. |

Updated: 2026-07-06 (synthesized from module specs current as of 2026-06-18 — see `specs/admin-module-specs-index.md` for the underlying technical detail and any more recent updates).
