# database.md — SanchiConnect Data Model & Schema

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 4 of 6
**Consolidates:** DDD v1.0 (whole), the Sanchi Credits Sprint Plan (credit-schema DDL), the Bulk Email BRD (proposed entities), and the team's per-repo indexes (physical DB facts).
**Positioning:** the persistence layer — how the domain entities in `knowledge.md` are stored, isolated, indexed, migrated, and retained. Column-level detail for individual business modules lives in the DDD data dictionary and the per-module specs; this document defines the physical model, the conventions, the concrete schema for the net-new subsystems, and the isolation/migration/retention policy.

> Gaps are marked inline as **GAP · DB-N** and collected in **§99**. Types shown are MySQL.

---

## 1. Purpose & Scope

Defines the physical data model: the database topology, the schema conventions every table follows, the control-plane and per-tenant schemas, the full schema for the net-new AI-credit subsystem, and the platform's indexing, isolation, migration, and retention policy. It is the source of truth for *where data lives and how it is shaped*.

## 2. Database Topology

The platform uses **two physical layers**, matching the tenancy model in `design.md` §5:

- **Control-plane database** — a **single shared MySQL database** holding one row per tenant (keyed by `domain`) plus the operator-level catalogue data. Owned by `sanchiconnect-saas-tenants`.
- **Per-tenant business databases** — **one MySQL database per tenant** holding all of that tenant's operational data. Resolved dynamically per request; connection details for each are stored on the tenant's control-plane row.

Which layer a table lives in is a first-class design fact and is stated for every table below.

| Data | Layer |
|------|-------|
| Tenant identity, connection details, branding, feature flags | Control plane (shared) |
| AI-credit catalogue: packages, task rates, orders, transactions, grants | Control plane (shared), keyed by `domain` |
| All business entities (identity, programs, applications, ecosystem, commercial, learning, content, facilities, admin) | Per-tenant DB |
| AI-credit wallet and ledger; analysis results | Per-tenant DB |

## 3. Schema Conventions

Every per-tenant business table follows this base shape (from the DDD):

- **Primary key** — a numeric internal `id` (auto-increment) as the primary key; relationships are expressed through foreign keys.
- **External identifier** — a globally unique `uuid`, used in all external-facing references; the sequential `id` is never exposed to clients.
- **Soft deletion** — a `deletedAt` timestamp marks a record removed without physical deletion; most list queries filter it out.
- **Active flag** — a boolean `isActive`/`status` for administratively disabled records, independent of soft deletion.
- **Audit timestamps** — `createdAt` and `modifiedAt`, maintained automatically.
- **Approval shape** — stakeholder profiles carry a status (pending/approved/rejected), the acting administrator, an approval/rejection timestamp, and an optional message.
- **Enumerations** — constrained value sets are stored as MySQL `ENUM` columns (see the credit tables for examples).
- **JSON columns** — semi-structured payloads (gateway responses, ledger metadata) are stored as `JSON`.

Referential integrity is enforced with foreign keys, every one of which is indexed (§7).

## 4. Control-Plane Schema

### 4.1 Tenant identity
- **Organization** — the billing/legal parent (name, website, official/technical email, hub flag). Relates to Tenants, Invoices, Payments, Contacts, Contracts.
- **Tenant** (`TenantUsersEntity`, one row per tenant, keyed by `domain`) — name, domain(s) and custom domain, backend API and admin URLs, **per-tenant database connection details**, currency, SSO configuration, IP/domain access restrictions, and **218 boolean feature-flag columns**. The `verify_tenant`/`tenant-settings` response is projected from this row and is a frozen contract (see `design.md` §5–6).

### 4.2 AI-credit catalogue (control-plane, keyed by `domain`)

```
ai_credit_packages
  id, name, credits BIGINT, price DECIMAL, original_price, currency,
  is_active, is_featured, valid_days (default 365), description,
  sort_order, created_at, updated_at

ai_credit_task_rates
  id, task_type VARCHAR UNIQUE,
  pricing_mode ENUM('fixed_per_unit','cost_multiplier'),
  credits_per_unit BIGINT, cost_multiplier DECIMAL, unit_label,
  is_active, updated_at
  -- seeded: ai_analysis=50, ai_thesis_generation=20, ai_rescore=3, ai_source_refresh=2

ai_credit_orders
  id, order_ref UNIQUE, domain, gateway_txn_id, package_id FK,
  credits, amount, currency, gateway,
  status ENUM('pending','paid','failed','refunded'),
  purchased_by_name, expires_at, created_at, updated_at

ai_credit_transactions
  id, order_ref FK, domain, gateway_payment_id, easebuzz_hash,
  amount, currency,
  status ENUM('pending','captured','failed','refunded'),
  gateway_response JSON, created_at

ai_credit_grants
  id, domain, credits,
  grant_type ENUM('onboarding','manual','promotion','refund_adjustment'),
  promotion_ref, reason, expires_at, granted_by,
  wallet_credited TINYINT(1), created_at
  -- UNIQUE KEY (promotion_ref, domain)  → idempotent promotion grants
```

## 5. Per-Tenant Business Schema

The per-tenant database holds ~106 entities across 13 families (DDD entity counts):

| Family | Entities | Representative tables |
|--------|----------|----------------------|
| Identity & Stakeholder Profiles | 10 | user accounts, the 8 stakeholder-type profiles, role assignments |
| Programs & Applications | 15 | the two-track model — §5.1 |
| Business Challenges | 2 | challenge, challenge submission |
| Connections | 3 | connection, connection setting |
| Community Wall | 8 | post, engagement |
| Meetings & Events | 7 | meeting, event, attendee |
| Messaging | 3 | conversation, message |
| Commercial | 8 | payment order, transaction, coupon, tax profile, invoice, membership — §5.2 |
| Learning Management | 16 | course, lesson, enrolment, progress |
| Content | 4 | news, resource item |
| Administrative & Platform Services | 16 | audit log, support ticket, configuration |
| Facilities | 12 | facility, booking |

Column-level detail for these lives in the DDD data dictionary and the per-module specs.

### 5.1 Programs & Applications — two-track model
Two separate entity families (not one entity with a type flag — `knowledge.md` BR-PROG-01):
- **Profile-linked track:** `program` → `program_round` → `program_startup_round_progress` → `program_round_jury_assignment`.
- **General-application track:** `application_program` → `application_program_round` → `application_program_submission_progress` → `application_program_submission_rating` → `application_program_round_jury_assignment` → `jury_question` / `jury_question_answer` → `round_notes` → `jury_call_request`; shared `form` / `form_submission`.

The general-application track also relates to the analysis records in §6.3.

### 5.2 Commercial
Unified payment model: `payment_order` (checkout for any payable module, with gateway type, status, purchased-item reference, amounts, tax, currency) → `payment_transaction` (immutable — §10), with `coupon`, `coupon_usage`, `tax_profile`, `proforma_invoice`, `membership_type`. This funds the tenant; the AI-credit tables (§6) fund the operator and are deliberately separate.

## 6. AI-Credit Schema *(net-new; authoritative source is the sprint plan, not the formal DDD)*

The AI-credit subsystem's schema spans both layers. The control-plane catalogue tables are in §4.2; the per-tenant wallet, ledger, and analysis tables are below.

### 6.1 Wallet (per-tenant DB)
```
ai_credit_wallets
  id, balance BIGINT DEFAULT 0, reserved_balance BIGINT DEFAULT 0,
  total_purchased BIGINT DEFAULT 0, total_consumed BIGINT DEFAULT 0,
  updated_at
  -- one row per tenant, auto-created on first credit event
  -- available balance = balance − reserved_balance
```

### 6.2 Ledger (per-tenant DB, append-only)
```
ai_credit_ledger
  id,
  entry_type  ENUM('credit','debit','reserve','release'),
  credits BIGINT, balance_after BIGINT,
  source_type ENUM('package_purchase','ai_analysis','ai_rescore','ai_thesis',
                   'ai_source_refresh','bonus','refund','expiry',
                   'reserve','release','free_grant'),
  source_id VARCHAR, description, created_by INT,
  metadata JSON, created_at
  -- INDEX (source_type, source_id), INDEX (created_at)
  -- append-only: corrections are new rows (knowledge.md BR-CR-06)
```

### 6.3 Analysis result & run linkage (per-tenant DB)
```
ai_analysis_results
  id, application_id, batch_id,
  score DECIMAL(4,2),               -- 0–5.00 (see DB-3)
  feedback TEXT, provider VARCHAR(30), model VARCHAR(80),
  is_latest TINYINT(1) DEFAULT 1,   -- non-destructive versioning (BR-AI-09)
  credits_charged BIGINT, cost_usd DECIMAL(10,6),
  created_by INT, created_at DATETIME
  -- INDEX (application_id, is_latest), INDEX (batch_id)

application_program_analysis  (existing table, extended)
  + credits_charged   BIGINT NULL
  + credits_ledger_id BIGINT NULL   -- FK → ai_credit_ledger.id
```

The **settlement invariant** (`knowledge.md` BR-CR-03): the wallet update and the ledger insert must occur in a single transaction. The rate is snapshotted into ledger `metadata` at reservation time (BR-CR-04).

> **GAP · DB-1 — AI-analysis entities are absent from the formal data model.** The DDD names an `Analysis Record` under Programs & Applications but never defines its attributes; the concrete schema above is reconstructed from the module spec and the sprint plan. *Sanchi to adopt:* the analysis and credit schema into the canonical data model.

## 7. Indexing & Performance Design

- Every foreign-key relationship is indexed to support efficient joins and cascade operations.
- **Composite indexes** are aligned to the exact high-traffic query patterns rather than relying on single-column indexes — for example resolving a jury member's assigned submissions, a startup's current round within a program, and a user's unread message/notification count. The credit ledger carries composite indexes on `(source_type, source_id)` and `(created_at)`; `ai_analysis_results` on `(application_id, is_latest)` and `(batch_id)`.
- **Archive tables** of the same shape hold large, time-bounded, high-volume data (event attendee records, certain audit/log data), moved periodically to keep primary operational tables performant over a tenant's lifetime.
- **Pagination at the database layer** on every list/search endpoint; no endpoint returns an entire table in one response.

## 8. Data Isolation

- **Business data — database-per-tenant.** No tenant-identifier column is threaded through business tables; the database boundary *is* the tenant boundary. A tenant's per-tenant DB connection details are stored on its control-plane row and resolved per request.
- **Control plane — row-per-tenant by `domain`.** The shared control-plane tables (`TenantUsersEntity`, and the credit catalogue tables) hold one row (or a set of rows) per tenant keyed by `domain`; every control-plane query filters by `domain`.
- **Cross-tenant shared data.** A small, deliberate set of capabilities crosses the tenant boundary: the **IP (patent) hubs** and **facility hubs**, where a hub tenant exposes its records to a domain-allowlisted set of other tenants (`knowledge.md` BR-ENG-03), and the best-effort-synced **ecosystem directory** in the control plane.

## 9. Migrations & Schema Evolution

- **Production migrations are explicit.** The control plane uses TypeORM; in development schema changes auto-apply, so **production must use explicit, reviewed migrations** — an operational rule, not an option. The per-tenant business DBs likewise evolve through migrations (each tenant DB migrated in turn).
- **New boolean flag columns default to `null`, not `false`,** for existing tenant rows until backfilled — consumers must not rely on strict `=== true` without accounting for `null`, and a backfill should accompany any new flag column.
- **The feature-flag column set is a cross-repo contract** — a column rename breaks the backend `Feature` enum, the frontend `IFeatures`, and the admin `config.php` simultaneously (`design.md` §6); flag-column changes go through `/trace-flag`.

## 10. Retention & Lifecycle

- **Soft deletion is the default** removal mechanism for entities with downstream referential impact, preserving historical accuracy for financial, audit, and evaluation records after a record leaves active use.
- **Immutable records** — Profile Audit Log entries, Payment Transaction records, and the **AI-credit ledger** are never modified after creation; corrections are new records (preserving complete history).
- **Archive tables** hold aged high-volume data (§7).
- **Configurable retention** — overall tenant data-retention duration is governed by the commercial service agreement (SRS §7.3).

## 11. Source Traceability

Consolidates the **DDD** (conventions, entity families and counts, indexing, isolation, retention), the **Sanchi Credits Sprint Plan** (the full credit-schema DDL across three sprints), the **Bulk Email BRD** (proposed attachment entities), and the **team's per-repo indexes** (the two-layer physical model, the control-plane row-per-tenant model, migration behaviour). Their reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| DB-1 | §6.3 | AI-analysis & credit schema absent from the canonical data model (DDD names `Analysis Record` only) | The model of record is out of date for live/near-live subsystems | Team (adopt into DDD) |
| DB-2 | §5.2/§6 | Bulk Email & Broadcast tables not modelled (BRD proposes attachment tables; Broadcast entities inferred) | Blocks the Bulk Email schema; Broadcast persistence undocumented | Team + product |
| DB-3 | §6.3 | Scoring-rating precision: `ai_analysis_results.score DECIMAL(4,2)` vs analyzer `decimal(4,3)` | Two stores of the same value at different precision | Team |

**Cross-references (tracked elsewhere):** the credit subsystem needing a canonical requirements/data home — `program.md` P-5 / `design.md` D-1; credit **expiry** processing and consumption order (the `valid_days`/`expires_at`/`expiry` mechanics have no defined job or ordering) and **refund** mechanics — `knowledge.md` K-1; the scoring-precision alignment — `design.md` D-3.

*The final document is `api.md` — the endpoint and DTO contract, seeded by the team's `contracts.api` blocks and the sprint plan's internal/credit endpoints.*
