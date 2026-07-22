# knowledge.md — SanchiConnect Domain Model, Business Rules & State Machines

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 3 of 6
**Consolidates:** FRS v1.0 (§3–4), DDD v1.0 (§2–4), the three module specs, the Bulk Email BRD, the Sanchi Credits Sprint Plan, and the team's 26 feature specs and per-repo indexes.
**Positioning:** the domain layer of the specification — the business entities, the rules that govern them, and the state machines that describe their lifecycles. Independent of how the system is built (`design.md`) or stored (`database.md`).

> Gaps are marked inline as **GAP · K-N** and collected in **§99**. Business rules carry stable IDs (**BR-***) so implementing code and tests can cite them.

---

## 1. Purpose & Scope

This document states *what is true about the business*: the entities, their rules, and their lifecycles. It reconciles the requirement-level behaviour (FRS), the entity model (DDD), the real screen behaviour (module specs), the team's feature specs, and the two forward-looking sources (the Bulk Email BRD and the Sanchi Credits Sprint Plan) into one domain reference — the consolidated domain view the team's per-module specs do not provide.

## 2. Domain Overview & Entity Families

The per-tenant business schema is documented as **~106 entities across 13 families**; the AI-credit domain adds a further set (in the control-plane database) not covered by the formal data model.

| Family | Entities | Notes |
|--------|----------|-------|
| Control Plane | 2 | Organization, Tenant — shared, not per-tenant |
| Identity & Stakeholder Profiles | 10 | 8 stakeholder types + accounts + a shared approval shape |
| Programs & Applications | 15 | The two-track model — §4.3 |
| Business Challenges | 2 | Corporate innovation challenges |
| Connections | 3 | Ecosystem networking |
| Community Wall | 8 | Posts, engagement |
| Meetings & Events | 7 | Scheduling, calendar |
| Messaging | 3 | In-app chat |
| Commercial | 8 | Unified payment/order model — §4.9 |
| Learning Management | 16 | Courses, lessons, enrolments |
| Content | 4 | News, resource library |
| Administrative & Platform Services | 16 | Audit, tickets, configuration |
| Facilities | 12 | Facility booking |
| AI Credits (net-new) | 7 | Control-plane + per-tenant — §4.6 |

Per-module entity detail lives in the DDD data dictionary and in the team's per-module specs (in the repositories); this document works at the family and rule level.

## 3. Common Entity Conventions

Unless noted, every per-tenant business entity follows this base shape — platform-wide invariants:

- **BR-CONV-01 · Dual identifier.** Every entity has a numeric internal `id` and a globally unique `uuid`. All external-facing references (URLs, API responses) use the `uuid`; the sequential `id` is never exposed to clients.
- **BR-CONV-02 · Soft deletion.** A `deletedAt` timestamp marks a record removed without physical deletion; most list queries filter these out automatically.
- **BR-CONV-03 · Active flag.** A boolean `isActive`/`status` distinguishes an active record from an administratively disabled one, independent of soft deletion.
- **BR-CONV-04 · Audit timestamps.** `createdAt` and `modifiedAt` are maintained automatically on every entity.
- **BR-CONV-05 · Stakeholder approval shape.** Every stakeholder profile shares one approval shape: status (pending/approved/rejected), the approving/rejecting administrator, the timestamp, and an optional message.

## 4. Core Domains

### 4.1 Tenancy & Control Plane
- **Organization** — the billing/legal parent of one or more tenants.
- **Tenant** — one row per client deployment: name, domain(s), per-tenant database connection details, currency, SSO configuration, IP/domain access restrictions, and 218 feature-enablement flags.

**BR-TEN-01.** Tenant capability is governed by the feature-flag set; enabling or disabling a capability is a configuration change, never a code change. **BR-TEN-02.** A route or logic gate must reference a feature flag (a boolean column) that exists on the control-plane tenant entity; a rename is a cross-repo breaking change (`/trace-flag`).

### 4.2 Identity & Stakeholder Profiles
Eight stakeholder types (Startup, Investor, Mentor, Corporate, Partner, Service Provider, Program Office, Individual) plus user accounts and role assignments. Each profile carries the shared approval shape (BR-CONV-05).

- **BR-STK-01 · Approval lifecycle.** A profile moves `pending → approved` or `pending → rejected`; a rejection records the administrator, timestamp, and optional message.
- **BR-STK-02 · Self-service data rights.** A member may request deactivation or deletion of their own account and personal data. The individual profile additionally supports flags for multiple profiles, profile locking, and limited access.
- **BR-STK-03 · Logout on rejection.** Where the `logout_on_rejection` flag is set, a stakeholder whose profile is rejected is signed out (observed across stakeholder feature specs).
- **BR-STK-04 · External sign-in / cross-tenant import.** Where external sign-in is enabled, a user may authenticate against, or be imported across, tenants via the external-auth flow (OTP plus feature flags, no standard JWT on that path).

### 4.3 Programs & Applications — the two-track model
The platform's defining structural rule, confirmed at entity and feature-spec level. There are **two genuinely separate entity families** sharing a common round/jury/rating pattern but not unified under a type flag:

**Track 1 — Profile-linked "Program"** ("Startup Programs"). Entities: **Program** → **Program Round** → **Program–Startup Round Progress** → **Program Round Jury Assignment**.

**Track 2 — General-application "Application Program"** ("Custom Programs"). Entities: **Application Program** (with a related **Analysis Record**) → **Application Program Round** → **Application Program Submission Progress** → **Application Program Submission Rating** → **Application Program Round Jury Assignment** → **Jury Question / Jury Question Answer** → **Round Notes** → **Jury Call Request** → shared **Form / Form Submission**.

- **BR-PROG-01 · Two tracks are distinct.** Build Program and Application Program as separate entities sharing a common pattern — not one entity with a type flag — because their field sets differ (profile requirement vs public URL/program type).
- **BR-PROG-02 · Staged save/publish.** The 3-step create wizard (Program Information → Application Form → Finalize & Go Live) requires each step to be independently saved before the next unlocks; Go Live is a distinct, confirmed, one-way action, not the same as saving the form step.
- **BR-PROG-03 · Additive system fields.** Company/Entity Name, Applicant Name, Applicant Email, and Mobile Number are always present and cannot be removed from the form builder; toggles add to this baseline set.
- **BR-PROG-04 · Destructive import.** Importing a form's structure from another program can delete existing fields and is irreversible — implement as a full-section replace with explicit confirmation, never a silent merge.
- **BR-PROG-05 · Submission with payment.** Where a program requires payment, the applicant completes payment as part of submission before the application can be finalized.
- **BR-PROG-06 · Document re-submission.** Where a program requests corrected or additional documents post-submission, the applicant re-submits through a dedicated flow.
- **BR-PROG-07 · External submission.** Business challenges (and certain applications) can be submitted via a public form without a platform account, entering the same review workflow.

### 4.4 Jury & Evaluation
Jury members are assigned per round, answer structured per-round jury questions per submission, and produce ratings (rater, recommendation, structured ratings, overall score, comments, approval state). The administrative jury experience (assignment, scoring dashboards, submission review) is covered by the admin `jury` module; the jury member's own scoring detail lives in the repo module specs.

- **BR-JURY-01 · Scoped assignment.** A jury member evaluates only submissions assigned to them within a round; a "not interested" flag with reason is recorded per assignment.
- **BR-JURY-02 · Rating method per round.** A round's rating method is weighted or unweighted per its configuration; rating requirement and whether jury may edit ratings or view overall ratings are round settings.
- **BR-JURY-03 · Jury masking.** An Application Program may mask jury identity per its jury-masking option.

### 4.5 AI Analysis
AI Analysis scores applicants on the Application Program (general) track. It is delivered by an independent evaluation service (`ai-startups-analyzer`) called one-directionally by the administration panel. Entities: **Analysis Run** (scope, evaluation thesis, status, batch count, applicants scored, average rating, model, provider, timestamps) and **Analysis Result** (run, applicant submission, rating, rank, justification).

The service flow: **generate-thesis** → **upload-csv** (returns run_id + batch metadata) → **start-all-background** (enqueue batches) → **status-summary** (poll completion) → **finalize-analysis** (merge results, roll up cost). Separate operations exist for **re-enrich** (re-run enrichment without re-scoring) and enrichment diagnostics.

- **BR-AI-01 · Immutable run snapshots.** Each run captures a scope, thesis, and resulting scores at a point in time; changing thesis or scope requires a new run, not an edit.
- **BR-AI-02 · Asynchronous, batched scoring.** Scoring runs as background batches (default 5 applicants per LLM call; per-run concurrency 5, global concurrency 16; per-batch retries and a hard timeout), not synchronously.
- **BR-AI-03 · Provider abstraction.** The service uses a configured LLM provider (gemini/openai/anthropic) per run; model/provider are run-level metadata reported after scoring, not an administrator selection. Per-provider JSON-forcing and USD cost computation are applied; per-domain pricing overrides exist.
- **BR-AI-04 · Enrichment is optional and best-effort.** Enrichment (Serper web search + Firecrawl website scrape per applicant) is off by default (`ENABLE_ENRICHMENT=0`), runs under a per-batch time budget, and never blocks scoring if it fails.
- **BR-AI-05 · Thesis uses form schema.** Thesis generation (and scoring) is given the program's current form schema as context, because generated theses cite specific application-form questions.
- **BR-AI-06 · Scope determines cost and result size.** The applicant count and total cost are direct functions of the scope selection (all-in-pipeline / submitted / accepted / round-wise).
- **BR-AI-07 · Incremental re-scoring.** Scoring supports being re-run against only newly added applicants without resetting or re-charging already-scored ones.
- **BR-AI-08 · Frozen scoring scale.** The service outputs a 0–500 score, persisted as 1–5 (divided by 100); `_coerce_rating()` is the single conversion point and the scale must never change.
- **BR-AI-09 · Non-destructive versioning.** Each run inserts a new result marked latest; previous results for the same application are marked not-latest, never deleted.
- **BR-AI-10 · Weighted criteria.** The service supports a weighted-criteria scoring mode alongside a fallback scoring path.

**Run lifecycle:** `pending → processing → ready` (immutable once ready).

The four analyzer operations map directly to the four credit task types in §4.6: full scoring → `ai_analysis`; re-score without enrichment → `ai_rescore`; re-enrich without scoring → `ai_source_refresh`; thesis generation → `ai_thesis_generation`.

### 4.6 AI Credits *(net-new — sourced only from the sprint plan)*
A **prepaid, per-tenant credit system** metering AI actions. It is absent from the formal documentation and from the team's feature specs, and is not yet fully built (the backend `grants` module is a stub). The rules below are reconciled from the sprint plan and the live-observed UI, pending a feature spec.

**Entities.** Control-plane: **Package**, **Task Rate**, **Order**, **Transaction**, **Grant**. Per-tenant: **Wallet** (balance, reserved_balance, total_purchased, total_consumed) and **Ledger** (append-only). Schema in `database.md`.

**Task rates (DB-driven, cached, never hardcoded):** `ai_analysis` 50 SC/applicant, `ai_thesis_generation` 20 SC/program, `ai_rescore` 3 SC/applicant, `ai_source_refresh` 2 SC/applicant (Phase-1 defaults).

- **BR-CR-01 · Rates are configuration.** Rates live in the Task Rate table and load into an in-memory cache at bootstrap; an operator rate change fires a cache-refresh so new rates take effect without redeploy. No rate is hardcoded.
- **BR-CR-02 · Reserve-then-settle.** A run reserves credits pre-flight (available = balance − reserved; if insufficient, raise with {required, available, shortfall}) and settles on completion (release the reservation, deduct the actual amount, write a debit ledger entry).
- **BR-CR-03 · Settlement atomicity.** The wallet update and the ledger insert in settlement must occur in a single database transaction. A partial write is a billing-integrity failure. *(The most important invariant in this domain.)*
- **BR-CR-04 · Rate snapshot at reservation.** A run settles at the rate captured at reservation time, even if the operator changes the rate mid-run.
- **BR-CR-05 · Charge only successes.** Actual charge = successfully-scored count × rate. Applicants that fail due to LLM error are not charged; their reservation is released and retry is free.
- **BR-CR-06 · Append-only ledger.** Every wallet movement (credit/debit/reserve/release) writes an immutable ledger entry with `balance_after`; corrections are new entries, never edits.
- **BR-CR-07 · Grants.** Free credits are granted as onboarding (auto, default 100 SC, once, on first enablement), manual (with reason), promotion (bulk, idempotent via a unique promotion key), or refund adjustment.
- **BR-CR-08 · Two-tier revenue separation.** Credit purchases flow through the platform Easebuzz gateway to the operator account — never the tenant's gateway (contrast the tenant Payment Order domain in §4.9). See `design.md` §8.
- **BR-CR-09 · Packages.** Standard packs: Growth (₹4,999 / 5,000 SC), Professional (₹9,999 / 11,000 SC, +10%), Enterprise (₹24,999 / 30,000 SC, +20%); base ₹1/SC; custom top-up minimum ₹4,999. GST (18%) shown separately on invoices.
- **BR-CR-10 · Balance display states.** The credit widget shows blue > 500, amber < 500, red < 100; low-balance and 30-day-expiry events additionally email the org's Super Admins.

**Credit-aware application analysis lifecycle:**
```
submitted → queued (reserved) → analyzing → analyzed (settled)
                                    │→ failed (reservation released; retry free)
                                    │→ pending_credits (reservation released; batch paused → resume on top-up)
```
Resume re-queries the live filter excluding already-analyzed applicants. **Order** lifecycle: `pending → paid | failed | refunded`; **Transaction**: `pending → captured | failed | refunded` (webhook confirmation is idempotent; a failed payment creates no wallet credit and no ledger entry).

> **GAP · K-1 — Credit expiry and refund rules undefined.** Packages carry `valid_days` and the ledger has expiry/refund entry types, but the consumption/expiry order (which credits expire or are spent first) and the refund policy (when, how much, reversal mechanics) are not defined. *Sanchi to provide:* expiry-consumption ordering and refund policy.

> **GAP · K-2 — Reserve-settle crash recovery undefined.** Settlement atomicity is specified, but what reconciles an orphaned reservation if the process dies between reserve and settle (a timeout or a sweeper) is not. *Sanchi to provide:* the reservation-recovery mechanism.

*(The analysis-rate decision (10 vs 50) is a commercial decision tracked in `program.md` P-6; the scoring-precision alignment is tracked in `design.md` D-3.)*

### 4.7 Business Challenges
Corporate-posted innovation challenges; can be submitted externally (BR-PROG-07) and can optionally link to an Application Program.

### 4.8 Ecosystem Engagement & Cross-Tenant Directory
**Connections** (networking between stakeholders, gated by connection settings), **Community Wall** (posts and engagement), **Meetings & Events** (scheduling, calendar, video sessions), **Messaging** (in-app chat, in-house or third-party per tenant).

Beyond a single tenant, an **ecosystem directory** in the control plane holds the eight stakeholder types and is populated by **best-effort sync** from per-tenant backends; ecosystem discovery and search read from it. Cross-tenant sharing is further expressed as **IP hubs and Facility hubs** — a tenant marked as a hub exposes its patents or facilities to a domain-allowlisted set of other tenants.

- **BR-ENG-01 · Connection gating.** Visibility of the Connections capability is governed by tenant connection-setting flags and administrator permission.
- **BR-ENG-02 · Best-effort ecosystem sync.** The shared ecosystem directory is populated best-effort from per-tenant data; it may lag the source of truth (there is no strong reconciliation guarantee).
- **BR-ENG-03 · Hub allowlisting.** Cross-tenant patent/facility visibility is controlled per hub by a domain allowlist; only allowlisted tenant domains may read a hub's shared data.

### 4.9 Commercial (existing) — and its relation to credits
The unified payment domain: **Payment Order** (checkout for any payable module — membership, course, facility booking — with gateway type, status, purchased-item reference, amounts, tax, currency) → **Payment Transaction**, with **Coupon**, **Coupon Usage**, **Tax Profile**, **Proforma Invoice**, **Membership Type**.

- **BR-COMM-01 · Unified checkout.** All tenant-level payable modules share one Payment Order/Transaction model regardless of gateway (PayPal/Razorpay/Stripe/Easebuzz/PayU).

The AI-credit Order/Transaction (§4.6) is a deliberately separate parallel to this, because credit revenue is the operator's, not the tenant's (BR-CR-08).

### 4.10 Communications & Broadcast
**Broadcast Messaging** — compose a single message to a filtered stakeholder cohort across one or more channels (Email, Chat Tool, Community Wall). Broadcast delivery is handled in the administration panel directly and does not call the backend. Audience is filtered by stakeholder type, profile status, geography/industry, and optionally by program.

- **BR-BC-01 · At least one channel.** At least one delivery channel must be selected (Email pre-checked).
- **BR-BC-02 · Async batched dispatch.** Broadcast sending is asynchronous/batched; a 50,000-recipient broadcast must dispatch within an agreed window without delaying unrelated notifications.
- **BR-BC-03 · Permission-gated.** Access requires the broadcast permission flag (Super Admins always).
- **BR-BC-04 · Test send.** A test send dispatches to a test channel without reaching real recipients.
- **BR-BC-05 · Broadcast attachment (current).** The Broadcast composer accepts a single attachment of doc/docx/pdf/ppt only, max 10 MB, and an image of gif/jpeg/jpg/png only.

**Bulk Email Multi-File Attachments** (BRD — a distinct feature under Custom Programs → Application Review Board → Bulk Email) deliberately reverses Broadcast's attachment limits:
- **BR-BE-01 · Any type, any number.** Attachments may be of any type and any number (no allow/block list, no hard count cap; a configurable soft ceiling), with a live combined-size indicator and per-file remove/retry.
- **BR-BE-02 · Size-based delivery mode.** Under a threshold, attachments are sent inline; above it, via object storage and a signed, time-limited link, with the delivery mode visible pre-send.
- **BR-BE-03 · Mandatory malware scan.** Every file is scanned before it is available; a detection quarantines that file with a clear error without blocking clean ones. Storage is access-controlled signed-URL, never public.
- **BR-BE-04 · Same set to all; async.** The same attachment set goes to every recipient (not personalized); send is async/batched and recorded in send history.

**Attachment state machine:** `uploading → scanning → available | failed | quarantined`; delivery mode `inline | link` by size.

> **GAP · K-3 — WhatsApp broadcast-channel status.** WhatsApp is wired for OTP and admin actions, but the Broadcast composer offers only Email/Chat/Community Wall. *Sanchi to confirm:* whether WhatsApp is a live broadcast channel, flag-gated, or dropped.

> **GAP · K-4 — Bulk Email attachment specifics undetermined.** The soft file-count ceiling, the inline/link size threshold, the link-expiry period, the gating permission flag, the current Bulk Email compose screen, and whether delivery routes through the backend or the admin (given Broadcast is admin-direct) are all unconfirmed. *Sanchi to provide:* confirmed values, the current screen, and the delivery path.

### 4.11 Learning, Content, Facilities, Administrative Services
**Learning Management** (courses, lessons, enrolments, progress; course payment verified through the payment domain), **Content** (news, resource library), **Facilities** (listings and bookings, some cross-tenant shared), **Administrative & Platform Services** (audit logs, support tickets, system configuration).

- **BR-ADM-01 · Audit of material actions.** Approvals, financial transactions, configuration/permission/connection changes, credential changes, and data exports write an audit entry capturing actor, action, and timestamp.

## 5. Cross-Cutting Business Rules

- **BR-X-01 · Feature-flag gating.** Every optional capability is gated by a feature flag; settings screens are configuration surfaces over the flag set, not standalone modules.
- **BR-X-02 · Permission gating.** Destinations and actions are filtered by the administrator's role and granular Allowed Features flags; a manager lacking a flag does not see the corresponding item.
- **BR-X-03 · Backend authorization.** Authorization is evaluated on the backend for every request; front-end role-aware layout is convenience, not the boundary.
- **BR-X-04 · Persistent-save settings pattern.** Multi-tab settings screens use a single page-level save over a tab-scoped state object; switching tabs must not discard unsaved edits.
- **BR-X-05 · Audit logging.** (See BR-ADM-01.)

## 6. State Machine Catalogue

1. **Stakeholder approval** — `pending → approved | rejected` (BR-STK-01).
2. **Program create wizard** — Step 1 saved → Step 2 saved → Step 3 Finalize → Go Live (one-way) (BR-PROG-02).
3. **Application submission progress** — `draft → submitted → (per round) advanced | rejected → final`.
4. **AI Analysis run** — `pending → processing → ready` (immutable) (BR-AI-01).
5. **Credit-aware application analysis** — `submitted → queued(reserved) → analyzing → analyzed(settled) | failed(released) | pending_credits(released, paused)` (BR-CR-02/05).
6. **Credit order / transaction** — `pending → paid|captured | failed | refunded` (idempotent confirm).
7. **Broadcast dispatch** — `compose → queued → dispatching(async batched) → sent | failed (per recipient)` (BR-BC-02).
8. **Bulk Email attachment** — `uploading → scanning → available | failed | quarantined`; delivery `inline | link` (BR-BE-03).

## 7. Business Rule Register (selected)

| ID | Rule | Domain |
|----|------|--------|
| BR-CONV-01..05 | Base entity conventions (uuid, soft delete, active, audit, approval shape) | All |
| BR-PROG-01 | Two-track model kept distinct | Programs |
| BR-PROG-02 | Staged save + one-way Go Live | Programs |
| BR-AI-08 | Frozen 0–500 → 1–5 scoring scale | AI Analysis |
| BR-CR-03 | Settlement atomicity (billing integrity) | Credits |
| BR-CR-05 | Charge only successful applicants | Credits |
| BR-CR-08 | Two-tier revenue separation (operator vs tenant) | Credits |
| BR-BE-03 | Mandatory malware scan before availability | Bulk Email |
| BR-ENG-03 | Cross-tenant hub domain allowlisting | Ecosystem |
| BR-X-03 | Backend-enforced authorization | Cross-cutting |

*(The full set is the BR-* identifiers throughout §3–5.)*

## 8. Glossary

| Term | Definition |
|------|------------|
| Program / Application Program | The two program tracks (profile-linked vs general application) |
| Round | An evaluation stage within a program |
| Submission Progress | An applicant's record and status through a program's rounds |
| Analysis Run / Result | An immutable AI-scoring job and its per-applicant outputs |
| Enrichment | Optional per-applicant web-search + website-scrape context for scoring |
| Wallet | A tenant's credit balance (available + reserved) |
| Ledger | The append-only record of every credit movement |
| Reserve / Settle | Pre-flight credit hold and post-completion actual deduction |
| Task Rate | The configurable SC cost of an AI action, per unit |
| Grant | Operator-issued free credits (onboarding/manual/promotion/refund) |
| Delivery mode | Whether a Bulk Email attachment is sent inline or via signed link |
| Ecosystem directory | The shared, best-effort-synced cross-tenant stakeholder directory |
| Hub | A tenant sharing its patents or facilities to a domain-allowlisted set of tenants |
| SC | Sanchi Credit |

## 9. Source Traceability

Consolidates the **FRS** (§3–4 behaviour), the **DDD** (§2 conventions, §3–4 entities, entity counts), the **three module specs** (entities, cross-cutting rules, screen behaviour), the **Bulk Email BRD** (attachment domain), the **Sanchi Credits Sprint Plan** (credit domain), and the **team's feature specs and indexes** (as-built behaviour, flags, the analyzer detail). Their reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| K-1 | §4.6 | Credit expiry-consumption order + refund rules | Ledger correctness and revenue | Product owner |
| K-2 | §4.6 | Reserve-settle crash recovery (orphaned reservations) | Billing integrity under failure | Team |
| K-3 | §4.10 | WhatsApp broadcast-channel status | Broadcast scope | Product owner |
| K-4 | §4.10 | Bulk Email thresholds, gating, current screen, delivery path | Blocks the Bulk Email pilot | Product + team |

**Cross-references (tracked in other documents):** the analysis-rate decision (10 vs 50) — `program.md` P-6; scoring-rating precision — `design.md` D-3; the credit domain needing a feature spec — `program.md` P-5 / `design.md` D-1; jury-evaluator detail — the repo module specs.

*The next document is `database.md` — the schema, turning these entities into concrete tables, folding in the credit tables and marking the entities the formal model names but does not define.*
