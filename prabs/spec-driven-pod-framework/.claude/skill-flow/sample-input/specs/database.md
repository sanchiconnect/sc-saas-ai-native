# Database Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-MFCE-001
**Last Updated:** June 2026
**Version:** 1.0
**Pod:** Backend Pod / Data Pod

---

## Platform

| Property | Value |
|----------|-------|
| Engine | PostgreSQL 16 |
| Hosting | AWS RDS Multi-AZ — us-east-1 (primary); eu-west-1 (EU GDPR replica); ap-southeast-1 (APAC replica) |
| ORM | SQLAlchemy 2.x async — asyncpg driver |
| Migration Tool | Alembic 1.x |
| Connection Pooling | SQLAlchemy built-in async pool; pool_size=20, max_overflow=10 per ECS Fargate task |
| Read Replicas | Yes — analytics and Data Pod reporting queries routed to read replica |
| Backup | RDS automated daily snapshots; 35-day retention; point-in-time recovery enabled |

---

## Schema Overview

```
[customers] ──< [checkout_sessions]       one customer → many sessions
[customers] ──< [orders]                  one customer → many orders
[customers] ──< [shipping_addresses]      one customer → max 5 addresses (BR-032)
[customers] ──< [payment_method_tokens]   one customer → max 3 tokens (BR-040)

[checkout_sessions] ──> [orders]          one session owns exactly one order (UNIQUE FK on session_id)

[orders] ──< [payments]                   one order → 1 to 3 payments for retries (BR-021)
[orders] ──> [shipping_addresses]         order references one shipping address
[orders] .──> [payments]                  orders.payment_id is a SOFT REFERENCE only (no FK — avoids
                                          circular dependency); authoritative lookup:
                                          SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC
```

**All primary keys:** UUID (`gen_random_uuid()` PostgreSQL default)
**All tables:** `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`; `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` maintained by trigger

---

## Table Definitions

### customers

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| customer_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| email | VARCHAR(254) | NOT NULL | — | UNIQUE | ⚠️ PII — AES-256 encrypted at rest; masked in logs |
| is_guest | BOOLEAN | NOT NULL | FALSE | — | TRUE until account registration confirmed |
| locale | VARCHAR(20) | NOT NULL | 'en-US' | — | BCP 47 tag; drives currency display and address format |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | Maintained by `trg_set_updated_at` trigger |
| deleted_at | TIMESTAMPTZ | YES | NULL | — | GDPR soft erasure; PII columns anonymised on request |

**Indexes:**
- `idx_customers_email` ON (email) UNIQUE — session recovery and login lookup
- `idx_customers_active` ON (customer_id) WHERE deleted_at IS NULL — active customer queries

**Foreign Keys:** none — `customers` is the root entity

**Business Rule Notes:**
- BR-002: `email` NOT NULL ensures it exists on record; application captures email at IDENTITY step before advancing
- GDPR erasure: `email` column anonymised to `anon_{uuid}@deleted.invalid`; `deleted_at` set; PII address fields nulled (see Data Retention)

---

### checkout_sessions

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| session_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| customer_id | UUID | YES | NULL | FK → customers(customer_id) ON DELETE SET NULL | NULL for guest sessions until identity step completes |
| order_id | UUID | NOT NULL | — | FK → orders(order_id) ON DELETE RESTRICT, UNIQUE | One session owns exactly one order |
| step | VARCHAR(12) | NOT NULL | 'IDENTITY' | CHECK (step IN ('IDENTITY','SHIPPING','PAYMENT','REVIEW','SUBMITTING','COMPLETE')) | Current checkout flow position |
| status | VARCHAR(12) | NOT NULL | 'ACTIVE' | CHECK (status IN ('ACTIVE','COMPLETE','EXPIRED','ABANDONED')) | Session lifecycle state |
| expires_at | TIMESTAMPTZ | NOT NULL | — | — | Set to created_at + INTERVAL '15 minutes'; refreshed on activity (BR-001) |
| recovery_email | VARCHAR(254) | YES | NULL | — | ⚠️ PII (transient) — cleared on session expiry (BR-001); used for recovery link dispatch |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | Maintained by trigger |

**Indexes:**
- `idx_checkout_sessions_order_id` ON (order_id) UNIQUE — enforces one-session-per-order invariant
- `idx_checkout_sessions_customer_id` ON (customer_id) — session lookup by customer
- `idx_checkout_sessions_active_expiry` ON (expires_at) WHERE status = 'ACTIVE' — Celery expiry cleanup job (BR-001)
- `idx_checkout_sessions_recovery_email` ON (recovery_email) WHERE recovery_email IS NOT NULL — recovery endpoint lookup

**Foreign Keys:**
- `customer_id` → `customers(customer_id)` ON DELETE SET NULL
- `order_id` → `orders(order_id)` ON DELETE RESTRICT

**Business Rule Notes:**
- BR-001: Celery worker queries `idx_checkout_sessions_active_expiry` every minute; transitions ACTIVE sessions past `expires_at` to EXPIRED; sets associated Order to CANCELLED
- UNIQUE on `order_id` prevents duplicate sessions per order at the database level

---

### orders

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| order_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| session_id | UUID | NOT NULL | — | FK → checkout_sessions(session_id) ON DELETE RESTRICT | Checkout lineage reference |
| customer_id | UUID | NOT NULL | — | FK → customers(customer_id) ON DELETE RESTRICT | Order owner |
| status | VARCHAR(16) | NOT NULL | 'DRAFT' | CHECK (status IN ('DRAFT','PENDING_PAYMENT','CONFIRMED','FULFILLED','CANCELLED')) | See Order state machine in knowledge.md |
| line_items | JSONB | NOT NULL | '[]' | — | Price-snapshotted at PENDING_PAYMENT transition; immutable after (BR-013) |
| total_amount | NUMERIC(10,2) | NOT NULL | 0.00 | CHECK (total_amount >= 0) | Sum of line items + shipping rate; recalculated on change (BR-011) |
| currency | CHAR(3) | NOT NULL | 'USD' | — | ISO 4217; derived from Customer.locale |
| shipping_address_id | UUID | YES | NULL | FK → shipping_addresses(address_id) ON DELETE RESTRICT | Set at SHIPPING step |
| payment_id | UUID | YES | NULL | — (soft reference; no FK constraint) | Cached pointer to most recent Payment; see schema overview note |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | Maintained by trigger |
| confirmed_at | TIMESTAMPTZ | YES | NULL | — | Set when status transitions to CONFIRMED (BR-010) |

**line_items JSONB element schema** (array of objects):
```json
[
  {
    "product_id": "string (UUID)",
    "name":       "string, maxLength: 255",
    "sku":        "string",
    "quantity":   "integer, minimum: 1",
    "unit_price": "string (NUMERIC as string — avoids float precision loss)",
    "line_total": "string (NUMERIC as string)"
  }
]
```
*Stored as strings to preserve decimal precision; parsed by application layer using Python `Decimal`.*

**Indexes:**
- `idx_orders_customer_id` ON (customer_id) — customer order history
- `idx_orders_status` ON (status) — fulfillment system polls for CONFIRMED orders
- `idx_orders_created_at` ON (created_at DESC) — analytics time-series queries
- `idx_orders_customer_status` ON (customer_id, status) — "active orders for customer" lookup pattern

**Foreign Keys:**
- `session_id` → `checkout_sessions(session_id)` ON DELETE RESTRICT
- `customer_id` → `customers(customer_id)` ON DELETE RESTRICT
- `shipping_address_id` → `shipping_addresses(address_id)` ON DELETE RESTRICT

**Business Rule Notes:**
- BR-010: `confirmed_at` is set atomically with status change to CONFIRMED by application; SQLAlchemy validator raises if confirmed_at is NULL when status = CONFIRMED
- BR-011: Application recalculates `total_amount` on any line_items mutation; CHECK (total_amount >= 0) provides floor
- BR-013: Application sets `line_items` once at PENDING_PAYMENT transition; treated as immutable by all subsequent reads
- BR-012: CANCELLED status is terminal; application rejects any status transition out of CANCELLED

---

### payments

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| payment_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| order_id | UUID | NOT NULL | — | FK → orders(order_id) ON DELETE RESTRICT | Multiple payments per order allowed (retries) |
| method | VARCHAR(12) | NOT NULL | — | CHECK (method IN ('CARD','APPLE_PAY','GOOGLE_PAY')) | Payment instrument type |
| gateway_token | VARCHAR(512) | NOT NULL | — | — | ⚠️ Sensitive — AES-256 encrypted at rest; never logged (BR-020) |
| status | VARCHAR(12) | NOT NULL | 'INITIATED' | CHECK (status IN ('INITIATED','AUTHORIZED','CAPTURED','FAILED','REFUNDED')) | See Payment state machine in knowledge.md |
| amount | NUMERIC(10,2) | NOT NULL | — | CHECK (amount > 0) | Must equal order.total_amount at initiation (BR-024) |
| attempt_count | SMALLINT | NOT NULL | 1 | CHECK (attempt_count BETWEEN 1 AND 3) | Sequential retry number; BR-021 caps at 3 |
| authorized_at | TIMESTAMPTZ | YES | NULL | — | Set when gateway returns authorization |
| captured_at | TIMESTAMPTZ | YES | NULL | — | Set when funds are debited |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | Maintained by trigger |

**Indexes:**
- `idx_payments_order_id` ON (order_id) — get all payments for an order; non-unique (retries create multiple rows)
- `idx_payments_order_status` ON (order_id, status) — get active/latest payment for an order
- `idx_payments_inflight` ON (status) WHERE status IN ('INITIATED','AUTHORIZED') — monitoring in-flight payments

**Foreign Keys:**
- `order_id` → `orders(order_id)` ON DELETE RESTRICT

**Business Rule Notes:**
- BR-020: No PAN, CVV, or full expiry column exists in this table. `gateway_token` is an opaque Stripe reference only.
- BR-021: `CHECK (attempt_count BETWEEN 1 AND 3)` enforces per-record validity. Application enforces aggregate limit: `SELECT COUNT(*) FROM payments WHERE order_id = ?` before creating a new payment.
- BR-024: Application validates `payment.amount == order.total_amount` before INSERT; enforced in SQLAlchemy model validator, not at DB constraint level (requires cross-table check).
- BR-022: No DB enforcement needed — wallet tokens are generated per-attempt by Stripe SDK at the application layer.

---

### shipping_addresses

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| address_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| customer_id | UUID | YES | NULL | FK → customers(customer_id) ON DELETE SET NULL | NULL for one-time guest addresses |
| line1 | VARCHAR(255) | NOT NULL | — | — | ⚠️ PII — AES-256 encrypted at rest |
| line2 | VARCHAR(255) | YES | NULL | — | ⚠️ PII |
| city | VARCHAR(100) | NOT NULL | — | — | — |
| state_province | VARCHAR(100) | YES | NULL | — | Required for US/CA; absent for some countries (address format varies by country_code) |
| postal_code | VARCHAR(20) | NOT NULL | — | — | Format varies by country_code |
| country_code | CHAR(2) | NOT NULL | — | — | ISO 3166-1 alpha-2 |
| is_validated | BOOLEAN | NOT NULL | FALSE | — | TRUE after autocomplete selection or explicit validation (BR-031) |
| is_default | BOOLEAN | NOT NULL | FALSE | — | At most one TRUE per customer (enforced by partial unique index) |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| deleted_at | TIMESTAMPTZ | YES | NULL | — | Soft delete when customer removes address |

**Indexes:**
- `idx_shipping_addresses_customer_id` ON (customer_id) WHERE deleted_at IS NULL — customer's active saved addresses
- `idx_shipping_addresses_one_default` ON (customer_id) WHERE is_default = TRUE AND deleted_at IS NULL UNIQUE — enforces at-most-one default per customer

**Foreign Keys:**
- `customer_id` → `customers(customer_id)` ON DELETE SET NULL

**Business Rule Notes:**
- BR-030: `is_validated` flag signals application that address passed geocoding verification; application blocks SHIPPING step advancement until format validation passes
- BR-031: Manual entry sets `is_validated = FALSE`; this is a valid state for checkout
- BR-032: Application checks `SELECT COUNT(*) FROM shipping_addresses WHERE customer_id = ? AND deleted_at IS NULL` before INSERT; raises if count = 5

---

### payment_method_tokens

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| token_id | UUID | NOT NULL | gen_random_uuid() | PK | — |
| customer_id | UUID | NOT NULL | — | FK → customers(customer_id) ON DELETE CASCADE | Token useless without customer; cascade on customer deletion |
| gateway_token | VARCHAR(512) | NOT NULL | — | — | ⚠️ Sensitive — AES-256 encrypted at rest; never logged (BR-020) |
| method_type | VARCHAR(12) | NOT NULL | — | CHECK (method_type IN ('CARD','APPLE_PAY','GOOGLE_PAY')) | Instrument type |
| display_label | VARCHAR(100) | NOT NULL | — | — | e.g., "Visa ending 4242" — UI display only; never derived from raw PAN |
| is_default | BOOLEAN | NOT NULL | FALSE | — | At most one TRUE per customer (enforced by partial unique index) |
| expires_at | DATE | YES | NULL | — | Card expiry date; NULL for wallet tokens |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | — |
| deleted_at | TIMESTAMPTZ | YES | NULL | — | Soft delete when customer removes token |

**Indexes:**
- `idx_payment_tokens_customer_id` ON (customer_id) WHERE deleted_at IS NULL — customer's active saved payment methods
- `idx_payment_tokens_one_default` ON (customer_id) WHERE is_default = TRUE AND deleted_at IS NULL UNIQUE — enforces at-most-one default per customer

**Foreign Keys:**
- `customer_id` → `customers(customer_id)` ON DELETE CASCADE

**Business Rule Notes:**
- BR-040: One-click checkout eligibility: `COUNT(active tokens) >= 1 AND COUNT(active addresses) >= 1`; checked by application before offering one-click path
- BR-020: `gateway_token` holds Stripe opaque reference only; no PAN anywhere in this table

---

## Indexes Summary

| Index | Table | Columns / Condition | Type | Rationale |
|-------|-------|---------------------|------|-----------|
| idx_customers_email | customers | (email) | UNIQUE BTREE | Session recovery; login |
| idx_customers_active | customers | (customer_id) WHERE deleted_at IS NULL | PARTIAL BTREE | Active customer queries |
| idx_checkout_sessions_order_id | checkout_sessions | (order_id) | UNIQUE BTREE | One-session-per-order invariant |
| idx_checkout_sessions_customer_id | checkout_sessions | (customer_id) | BTREE | Session lookup by customer |
| idx_checkout_sessions_active_expiry | checkout_sessions | (expires_at) WHERE status = 'ACTIVE' | PARTIAL BTREE | Celery expiry cleanup (BR-001) |
| idx_checkout_sessions_recovery_email | checkout_sessions | (recovery_email) WHERE recovery_email IS NOT NULL | PARTIAL BTREE | Session recovery endpoint |
| idx_orders_customer_id | orders | (customer_id) | BTREE | Customer order history |
| idx_orders_status | orders | (status) | BTREE | Fulfillment polling; analytics |
| idx_orders_created_at | orders | (created_at DESC) | BTREE | Time-series analytics |
| idx_orders_customer_status | orders | (customer_id, status) | BTREE | Active orders per customer |
| idx_payments_order_id | payments | (order_id) | BTREE | Payment lookup by order |
| idx_payments_order_status | payments | (order_id, status) | BTREE | Active payment for order |
| idx_payments_inflight | payments | (status) WHERE status IN ('INITIATED','AUTHORIZED') | PARTIAL BTREE | In-flight payment monitoring |
| idx_shipping_addresses_customer_id | shipping_addresses | (customer_id) WHERE deleted_at IS NULL | PARTIAL BTREE | Saved addresses for customer |
| idx_shipping_addresses_one_default | shipping_addresses | (customer_id) WHERE is_default = TRUE AND deleted_at IS NULL | PARTIAL UNIQUE | At-most-one default address |
| idx_payment_tokens_customer_id | payment_method_tokens | (customer_id) WHERE deleted_at IS NULL | PARTIAL BTREE | Saved tokens for customer |
| idx_payment_tokens_one_default | payment_method_tokens | (customer_id) WHERE is_default = TRUE AND deleted_at IS NULL | PARTIAL UNIQUE | At-most-one default token |

---

## Constraints & Integrity

### Universal Rules
- All tables use UUID primary keys (`gen_random_uuid()` default — requires `pgcrypto` extension)
- All tables include `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- All tables include `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` — maintained by shared trigger function:
  ```sql
  CREATE OR REPLACE FUNCTION trg_set_updated_at()
  RETURNS TRIGGER LANGUAGE plpgsql AS $$
  BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$;
  ```
  Applied to all tables as `BEFORE UPDATE` trigger.

### Status Constraints (matching knowledge.md state machines)
| Table | Column | Valid Values |
|-------|--------|-------------|
| checkout_sessions | step | IDENTITY, SHIPPING, PAYMENT, REVIEW, SUBMITTING, COMPLETE |
| checkout_sessions | status | ACTIVE, COMPLETE, EXPIRED, ABANDONED |
| orders | status | DRAFT, PENDING_PAYMENT, CONFIRMED, FULFILLED, CANCELLED |
| payments | status | INITIATED, AUTHORIZED, CAPTURED, FAILED, REFUNDED |
| payments | method | CARD, APPLE_PAY, GOOGLE_PAY |
| payment_method_tokens | method_type | CARD, APPLE_PAY, GOOGLE_PAY |

### Foreign Key ON DELETE Behaviors
| FK | Table | Behavior | Rationale |
|----|-------|----------|-----------|
| checkout_sessions.customer_id | customers | SET NULL | Guest sessions have no customer_id; prevent orphan block on customer soft-delete |
| orders.customer_id | customers | RESTRICT | Financial records must not lose customer lineage |
| orders.session_id | checkout_sessions | RESTRICT | Session records are never physically deleted |
| orders.shipping_address_id | shipping_addresses | RESTRICT | Address reference must remain for order records |
| payments.order_id | orders | RESTRICT | Financial records must not be orphaned |
| shipping_addresses.customer_id | customers | SET NULL | Guest addresses have no customer; soft-delete handles removal |
| payment_method_tokens.customer_id | customers | CASCADE | Tokens are meaningless without a customer; physical cascade is correct |

### Soft Delete Pattern
Tables using `deleted_at`: `customers`, `shipping_addresses`, `payment_method_tokens`
- All active-record queries must filter `WHERE deleted_at IS NULL`
- Partial indexes already encode this filter (see Indexes Summary)
- `orders` and `payments` do **not** use soft delete — they are financial records and must never be logically removed

---

## Migrations

- **Tool:** Alembic 1.x — migration scripts in `src/migrations/versions/`
- **Naming convention:** `{YYYYMMDD_HHMMSS}_{short_description}.py` e.g. `20260610_120000_create_customers.py`
- **Initial migration order** (respects FK dependencies):
  1. `20260610_120000_create_customers.py`
  2. `20260610_120001_create_checkout_sessions_and_orders.py` (deferred FKs used for the session↔order creation order)
  3. `20260610_120002_create_payments.py`
  4. `20260610_120003_create_shipping_addresses.py`
  5. `20260610_120004_create_payment_method_tokens.py`
  6. `20260610_120005_create_indexes_and_constraints.py`
  7. `20260610_120006_create_updated_at_trigger.py`

- **Policy:**
  - All migrations must implement both `upgrade()` and `downgrade()` functions
  - Never drop a column in the same migration it is vacated — suffix with `_deprecated` first; physical drop in a separate migration after 2 sprints
  - Zero-downtime column additions: `ADD COLUMN ... DEFAULT NULL` → backfill in batches → `ADD NOT NULL` constraint separately
  - Migrations must pass in staging for 24 hours before promotion to production
  - Schema changes that affect `spec-api` query patterns require an API team review before merge

---

## Data Retention & Compliance

| Field / Table | Classification | Retention Period | Handling |
|---------------|---------------|-----------------|---------|
| customers.email | PII | Until GDPR erasure request | AES-256 encrypted at rest; masked in all log output |
| shipping_addresses.line1, line2 | PII | Until GDPR erasure or 7yr order retention | AES-256 encrypted at rest; nulled on GDPR erasure |
| checkout_sessions.recovery_email | PII (transient) | Session lifetime (max 15 min active) | Cleared when session expires (BR-001); never in application logs |
| payments.gateway_token | Sensitive | 7 years (financial record retention) | AES-256 encrypted at rest; never logged; never returned in API responses (BR-020) |
| payment_method_tokens.gateway_token | Sensitive | Until customer deletion | AES-256 encrypted at rest; never logged; never returned in full via API |
| orders (full record) | Business record | 7 years | Retained for financial compliance; customer PII anonymised on GDPR erasure |
| checkout_sessions | Operational | 90 days then purged | Expired/abandoned sessions purged by scheduled Celery job after 90-day retention window |

**GDPR Erasure Process** (triggered by `DELETE /customers/{id}` endpoint):
1. Anonymise `customers.email` → `anon_{uuid}@deleted.invalid`; set `customers.deleted_at = NOW()`
2. Null address PII: `UPDATE shipping_addresses SET line1='[REDACTED]', line2=NULL, city='[REDACTED]', state_province=NULL, postal_code='[REDACTED]' WHERE customer_id = ?`
3. Delete `payment_method_tokens` (ON DELETE CASCADE handles this automatically)
4. Retain `orders` and `payments` records (anonymised via customer FK nullification) for financial compliance
5. Insert into `audit_log` table: `{event: 'gdpr_erasure', customer_id: ?, timestamp: NOW()}`

**PCI-DSS Scope:**
- No PAN, CVV, or full expiry date column exists anywhere in this schema (BR-020)
- `payments.gateway_token` and `payment_method_tokens.gateway_token` hold only Stripe opaque tokens
- Stripe handles PCI-DSS SAQ-A scope; our schema never enters PCI cardholder data scope

**Multi-region Data Isolation:**
- EU customers (`locale` BCP 47 tag contains region 'EU' country codes): routed exclusively to `eu-west-1` RDS instance
- APAC customers: routed to `ap-southeast-1` RDS instance
- Cross-region data replication is NOT performed for GDPR compliance; each regional instance is independent
- Application layer (identity-module) determines regional DB endpoint at request time based on Customer.locale

---

## Seed Data

No reference or lookup tables required at initialisation. All status values are enforced via CHECK constraints (no status lookup table needed).

**Staging fixture data** (applied by `alembic_seed.py` script, not part of schema migrations):
- 5 test customer records with known UUIDs for automated test suites
- Stripe test-mode `gateway_token` values for payment integration tests
- 3 test `shipping_addresses` per test customer covering US, EU (DE), and APAC (JP) formats

---

## [AS-IS] Existing Data Model
<!-- Routing: [AS-IS DATA] -->
<!-- Reverse-engineered from legacy database schemas, migration scripts, or ORM model files -->
<!-- Populated by: code-extraction (SQL DDL, migration scripts, ORM models, data dictionaries) -->
<!-- DO NOT edit manually — use extraction skills only -->
<!-- Note: all sections above are TO-BE design; this section captures current-state only -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> No database schemas, migration scripts, or ORM model files have been provided. Run code-extraction
> against existing schema files, Alembic/Flyway migrations, or ORM models to populate this section.

### Entity Relationship Summary
<!-- Expected: primary aggregates, join/junction tables, polymorphic associations, orphaned tables -->

> PLACEHOLDER — no existing schema analyzed yet.

<!-- APPEND BELOW THIS LINE -->

### Table Inventory
<!-- Entry format per table/collection:
     #### Table: [table_name]
     **Purpose**: [business meaning]
     | Column | Type | Nullable | Default | Notes |
     |--------|------|----------|---------|-------|
     | ...    |      |          |         |       |
     **Indexes**: [non-trivial indexes and purpose]
     **Relationships**: [FK references]
     **Notes**: [soft delete, audit columns, partitioning, multi-tenancy]
-->

> PLACEHOLDER — no tables reverse-engineered yet.

<!-- APPEND BELOW THIS LINE -->

### Schema Observations
<!-- Populated by code-extraction: soft-delete patterns, audit trail columns, multi-tenancy keys, partitioning -->

> PLACEHOLDER — no schema patterns documented yet.

<!-- APPEND BELOW THIS LINE -->

### Migration History
<!-- Populated by code-extraction: existing migration files analyzed for schema evolution sequence -->

> PLACEHOLDER — no migration history analyzed yet.

<!-- APPEND BELOW THIS LINE -->

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Jun 2026 | 1.0 | Sarah Chen | Initial schema — derived from knowledge.md v1.0 entities and design.md v1.0 technology decisions |
| 2026-06-01 | 1.1 | code-extraction scaffold | Added [AS-IS] Existing Data Model section — PLACEHOLDER pending codebase ingestion |
| 2026-06-01 | 1.2 | design-setup scaffold | Added [TO-BE] Data Model session output section — PLACEHOLDER pending design session |

<!-- ============================================================ -->
<!-- DESIGN-SETUP SKILL OUTPUT — DO NOT EDIT MANUALLY             -->
<!-- Populated by design-setup Phase 3, Domain 3                  -->
<!-- ============================================================ -->

## [TO-BE] Data Model — Design Session Output
<!-- Routing: design-setup Phase 3, Domain 3 — Data Architecture -->
<!-- Populated by: design-setup skill during structured session -->
<!-- AS-IS sections above are preserved and never overwritten -->

> **PLACEHOLDER — PENDING DESIGN REVIEW**
> No design session has been completed. Run `/design-setup` Domain 3 to populate.

### Database Technology
- **Primary DB:** [DESIGN DECISION PENDING] — Options: PostgreSQL / MySQL / SQL Server / MongoDB / DynamoDB / hybrid
- **ORM / data access:** [DESIGN DECISION PENDING]
- **Connection pooling:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Data Architecture Pattern
> PLACEHOLDER — [DESIGN DECISION PENDING]
> Options: Single DB / service-per-DB / CQRS read-write split / other

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Migration Strategy
- **Approach:** [DESIGN DECISION PENDING] — Options: ETL / dual-write / big-bang cutover
- **Data migration tooling:** [DESIGN DECISION PENDING]
- **Rollback plan:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Reporting & Analytics
- **Separate data store required:** [DESIGN DECISION PENDING]
- **Analytics approach:** [DESIGN DECISION PENDING] — Options: warehouse / BI tool / in-DB / none

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Data Retention & Compliance
- **PII fields requiring encryption at rest:** [DESIGN DECISION PENDING — pending entity model]
- **Retention policy by data category:** [DESIGN DECISION PENDING]
- **Purge / archival approach:** [DESIGN DECISION PENDING]
- **Audit log:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Entity Model (TO-BE)
> PLACEHOLDER — [To be elaborated in Sprint 0 detailed design]
> Core domain entities and relationships are confirmed after business rules and workflows are validated in knowledge-review.
> Migration changes from AS-IS model are documented here during Sprint 0.