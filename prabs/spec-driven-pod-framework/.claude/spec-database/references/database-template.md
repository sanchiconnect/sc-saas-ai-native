# Database Specification
**Program:** {Program Name}
**Program ID:** {PRG-ID}
**Last Updated:** {Date}
**Version:** {N}
**Pod:** Backend Pod / Data Pod

---

## Platform

| Property | Value |
|----------|-------|
| Engine | {PostgreSQL 16 / MySQL 8 / MongoDB 7} |
| Hosting | {AWS RDS / Cloud SQL / Atlas / Self-hosted} |
| ORM / Driver | {SQLAlchemy 2.x / Prisma / Mongoose} |
| Migration Tool | {Alembic / Flyway / Prisma Migrate} |
| Connection Pooling | {PgBouncer / built-in pool size: N} |
| Read Replicas | {Yes — for reporting queries / No} |

---

## Schema Overview

```
[orders] ──< [order_line_items]
    |
    └──> [customers]
    |         └──> [addresses]
    └──> [payments]
    └──> [shipping_addresses]
```

*(Entity → Entity: one-to-many; Entity →→ Entity: many-to-many via join table)*

---

## Table Definitions

### orders
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK | Surrogate key |
| customer_id | UUID | NOT NULL | — | FK → customers(id) | Order owner |
| status | VARCHAR(32) | NOT NULL | 'DRAFT' | CHECK (status IN (...)) | See state machine in knowledge.md |
| total_amount | NUMERIC(10,2) | NOT NULL | 0.00 | CHECK (total_amount >= 0) | Sum of line items + shipping |
| currency | CHAR(3) | NOT NULL | 'USD' | — | ISO 4217 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | Updated by trigger |
| confirmed_at | TIMESTAMPTZ | YES | NULL | — | Set when status → CONFIRMED |
| deleted_at | TIMESTAMPTZ | YES | NULL | — | Soft delete |

**Indexes:**
- `idx_orders_customer_id` ON (customer_id) — frequent lookup by customer
- `idx_orders_status` ON (status) — filter by status in dashboards
- `idx_orders_created_at` ON (created_at DESC) — time-series queries

**Foreign Keys:**
- `customer_id` → `customers(id)` ON DELETE RESTRICT

---

### payments
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK | |
| order_id | UUID | NOT NULL | — | FK → orders(id), UNIQUE | One payment per order |
| gateway_token | VARCHAR(512) | NOT NULL | — | — | ⚠️ PII-adjacent: gateway reference only |
| method | VARCHAR(32) | NOT NULL | — | CHECK (method IN ('CARD','APPLE_PAY','GOOGLE_PAY')) | |
| status | VARCHAR(32) | NOT NULL | 'INITIATED' | CHECK (status IN (...)) | |
| amount | NUMERIC(10,2) | NOT NULL | — | CHECK (amount > 0) | |
| authorized_at | TIMESTAMPTZ | YES | NULL | — | |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |

**Indexes:**
- `idx_payments_order_id` ON (order_id) UNIQUE
- `idx_payments_status` ON (status)

---

### customers
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK | |
| email | VARCHAR(254) | NOT NULL | — | UNIQUE | ⚠️ PII — encrypted at rest |
| is_guest | BOOLEAN | NOT NULL | false | — | |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |
| deleted_at | TIMESTAMPTZ | YES | NULL | — | GDPR erasure |

**Indexes:**
- `idx_customers_email` ON (email) — login and session recovery

---

### addresses
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK | |
| customer_id | UUID | NOT NULL | — | FK → customers(id) | |
| line1 | VARCHAR(255) | NOT NULL | — | — | ⚠️ PII |
| line2 | VARCHAR(255) | YES | NULL | — | ⚠️ PII |
| city | VARCHAR(100) | NOT NULL | — | — | |
| state | VARCHAR(100) | YES | NULL | — | |
| postal_code | VARCHAR(20) | NOT NULL | — | — | |
| country | CHAR(2) | NOT NULL | — | — | ISO 3166-1 alpha-2 |
| is_validated | BOOLEAN | NOT NULL | false | — | Set after autocomplete verification |
| is_default | BOOLEAN | NOT NULL | false | — | |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | — | |

**Indexes:**
- `idx_addresses_customer_id` ON (customer_id)

---

## Indexes Summary

| Index | Table | Columns | Type | Rationale |
|-------|-------|---------|------|-----------|
| idx_orders_customer_id | orders | customer_id | BTREE | Customer order history |
| idx_orders_status | orders | status | BTREE | Admin/ops filtering |
| idx_payments_order_id | payments | order_id | UNIQUE BTREE | One payment per order |
| idx_customers_email | customers | email | UNIQUE BTREE | Login lookup |

---

## Constraints & Integrity

- All tables use UUID primary keys (`gen_random_uuid()` default on PostgreSQL)
- All tables include `created_at` and `updated_at` timestamps; `updated_at` maintained by trigger
- Soft delete pattern: `deleted_at` timestamp column (NULL = active); queries filter `WHERE deleted_at IS NULL`
- Status columns use CHECK constraints matching the state machine in `specs/knowledge.md`
- No orphaned foreign keys: all FK columns have explicit ON DELETE behavior defined

---

## Migrations

- **Tool:** Alembic (PostgreSQL) / Prisma Migrate / Flyway
- **Naming convention:** `{YYYYMMDD_HHMMSS}_{short_description}.py` e.g. `20260415_120000_create_orders.py`
- **Policy:**
  - Never drop columns in the same migration they're vacated — deprecate with `_deprecated` suffix first
  - All migrations must be reversible (`upgrade` + `downgrade` functions)
  - Run migrations in staging 24h before production
  - Zero-downtime: use `ADD COLUMN ... DEFAULT NULL` then backfill, then add NOT NULL constraint

---

## Data Retention & Compliance

| Field / Table | Classification | Retention | Handling |
|---------------|---------------|-----------|---------|
| customers.email | PII | Until GDPR erasure request | Encrypted at rest; masked in logs |
| addresses.line1/line2 | PII | Until GDPR erasure request | Encrypted at rest |
| payments.gateway_token | Sensitive | 7 years (financial records) | Never logged; encrypted at rest |
| orders | Business record | 7 years | Anonymize linked PII on erasure |

**GDPR Erasure Process:**
1. Null / anonymize all PII columns on the customer record
2. Set `customers.deleted_at`
3. Retain order records (anonymized) for financial compliance
4. Log erasure event in `audit_log` table

---

## Seed Data

Data required at application initialization (applied via migration or seed script):

```sql
-- Currency defaults, lookup tables, etc.
-- Example: default admin user, reference data
```

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {Date} | 1.0 | {Name} | Initial schema |
