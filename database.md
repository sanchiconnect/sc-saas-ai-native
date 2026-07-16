# SanchiSaaS — Workspace Data Ownership Index

Last updated: 2026-07-14

A cross-repo **data ownership index** — which repo owns which schema/database, and where the same physical
tables are mutated by more than one independently-deployed codebase. This is not a re-listing of any single
repo's tables; see each repo's own `database.md` for full entity/table detail. `[AS-IS]` throughout unless
tagged.

---

## 1. Who owns which database

| Database | Owning repo(s) | Mechanism | Notes |
|---|---|---|---|
| **Tenants control-plane DB** (shared, single instance) | `sanchiconnect-saas-tenants` (NestJS/TypeORM, `synchronize: true`, no migrations) | One TypeORM connection, `autoLoadEntities: true` | Also read/written directly by `sc-saas-admin` (`$mainDatabase`) and `sanchiconnect-saas-tenants-admin` (its one and only connection) — see §2 |
| **Per-tenant business DB** (one per tenant, N instances) | `sc-saas-backend` (NestJS/TypeORM, `synchronize: true`, no migrations; one deployment = one DB) | One TypeORM connection per deployment | Also read/written directly by `sc-saas-admin`'s resolved `$database` connection for the same tenant |
| **Analyzer's own DB** (`api_keys`, `analyses`, `batches`) | `ai-startups-analyzer` (SQLAlchemy async, add-only auto-migration) | Owns and is the sole writer | No other repo has DB access to this schema — `sc-saas-admin` only talks to it over HTTP |
| **No database at all** | `sc-saas-3rdparty-webservices` (stateless, confirmed — `typeorm` is a dependency with zero imports anywhere in `src/`) | — | — |
| **No server-side database** | `sc-saas-frontend` (pure client — `localStorage`, NgRx in-memory state, and the service-worker cache are its only "persistence layers") | — | See `sc-saas-frontend/database.md` for the localStorage-key/NgRx-slice inventory |

`[Source: sanchiconnect-saas-tenants/database.md §Schema strategy; sc-saas-backend/database.md §Schema
strategy; ai-startups-analyzer/database.md; sc-saas-3rdparty-webservices/database.md §This Service Has No
Database; sc-saas-frontend/database.md §Purpose of this document]`

---

## 2. The tenants control-plane DB has THREE independently-deployed direct readers/writers

This is the single most important data-ownership fact in the workspace: the "tenants DB" is not owned and
accessed by one repo — it is a shared MySQL instance three separately-versioned codebases all connect to
directly, with **no shared schema-versioning contract** between any of them.

| Codebase | Connection mechanism | What it touches |
|---|---|---|
| `sanchiconnect-saas-tenants` | TypeORM, `synchronize: true`, `autoLoadEntities: true` | `tenant_users`, `global_settings`, `organizations`/`subscriptions`, `ai_credit_*` (9 entities), 20 `spa_*` admin entities (yes — this NestJS repo registers the *same* `spa_admin_users`/`spa_settings`/etc. table names the two PHP repos also use), ecosystem/IP-management tables |
| `sc-saas-admin` | Medoo, `$mainDatabase` (a second, tenant-*scoped* connection, `$database`, points at the per-tenant business DB instead) | `tenant_users` (lookup by `admin_domain`), `global_settings` (read `third_party_service_base_url` etc.), `ai_credit_wallets`/`ai_credit_ledger`/`ai_credit_task_rates`/`ai_credit_packages`/`ai_credit_grants` (raw SQL reserve/settle/refund/debit) |
| `sanchiconnect-saas-tenants-admin` | Medoo, one connection only (the per-tenant-lookup code is present, commented out, deliberately disabled) | Same `tenant_users`/`global_settings`/`spa_*` tables as above, plus its own AI-Credits CRUD (`grants`/`task_rates`/`packages`/`orders` — see §3), plus (via `modules/scrapper.php`) ad-hoc direct connections into **every individual tenant's own business DB**, reading `tenant_users.database_password` in plaintext to do so |

`[Source: sanchiconnect-saas-tenants/knowledge.md §Shared Database With sanchiconnect-saas-tenants-admin —
Verified; sc-saas-admin/database.md §The two-database connection model;
sanchiconnect-saas-tenants-admin/database.md §One connection, not two, §modules/scrapper.php]`

`sanchiconnect-saas-tenants`'s own `synchronize: true` + no-migrations posture (see §4) means any of its
column renames/drops silently propagates into a live schema both PHP codebases already assume is stable,
with zero compile-time or type-level warning on either PHP side.

---

## 3. Primary Known Issue — AI-Credits schema has three independent direct mutators

Restating the workspace `knowledge.md`'s §2 finding in data-ownership terms, since this is the most
consequential shared-schema risk in the platform:

- **Schema owner**: `sanchiconnect-saas-tenants` (`src/modules/ai-credits/entities/*.entity.ts`, 9 entities:
  `AiCreditWalletEntity`, `AiCreditLedgerEntity`, `AiCreditOrderEntity`, `AiCreditTransactionEntity`,
  `AiCreditInvoiceEntity`, `AiCreditPackageEntity`, `AiCreditTaskRateEntity`, `AiCreditGrantEntity`,
  `PlatformTaxProfileEntity`). Implements the **credit (purchase)** side only —
  `handleEasebuzzCallback()` is the only wallet-balance mutation in this repo.
  `[Source: sanchiconnect-saas-tenants/database.md §AI Credits module]`
- **Spend-side mutator #1**: `sc-saas-admin`'s `includes/ai_credits_functions.php` — the four
  reserve/settle/refund/debit functions, against the identical table names, via raw PDO for the
  non-Medoo-expressible atomic UPDATEs. `[Source: sc-saas-admin/database.md §Table: ai_credit_wallets /
  ai_credit_ledger]`
- **Spend-side mutator #2, newly confirmed this pass**: `sanchiconnect-saas-tenants-admin`'s
  `modules/ai_credits/{grants,task_rates,packages,orders}.php` — direct PHP admin CRUD against the same
  tables, gated only by an inlined role check, not a schema-aware guard.
  `[Source: sanchiconnect-saas-tenants-admin/database.md §AI Credits tables — a second, undocumented writer
  of the same schema sc-saas-admin mutates]`

No migration, no shared type definition, and no runtime schema-version check exists between the three. A
column added/renamed by the NestJS owner under `synchronize: true` is a live, immediate, irreversible schema
change with no cross-repo signal to either PHP codebase that anything happened.
`[INFERRED — requires validation]`: whether any of the three codebases has ever actually broken another due
to an uncoordinated schema change is not evidenced in any of the seven repos' own docs — the finding is that
the *mechanism* for such a break exists and is currently unguarded, not that it has already occurred.

---

## 4. Secondary Known Issue — `synchronize: true` + no migrations, confirmed in every NestJS repo

Both NestJS repos in the workspace (`sanchiconnect-saas-tenants`, `sc-saas-backend`) independently
hardcode `synchronize: true` for every `NODE_ENV` branch and have no migrations directory anywhere in the
repo (`sc-saas-backend`'s `src/modules/migrations` is a NestJS feature module, unrelated to TypeORM
migrations — confirmed by directly reading it). Combined with `autoLoadEntities: true`, any new `@Entity`
class anywhere in either codebase creates a live table on next deploy with no review gate beyond ordinary
code review, and any column rename/removal auto-alters or auto-drops the corresponding live column with no
migration to revert. `[Source: sanchiconnect-saas-tenants/database.md §Schema strategy;
sc-saas-backend/database.md §Schema strategy — synchronize: true, no migrations directory]`

This is not a one-off — it is the platform-wide default posture of every NestJS repo checked, and it is the
mechanism that makes §2/§3's shared-table risk actionable rather than theoretical: the closest thing either
NestJS repo has to a schema-change safety net (a migration, a staging gate) simply does not exist.
`ai-startups-analyzer` (Python/SQLAlchemy) is the one repo with a partial mitigation — an add-only
`_sync_missing_columns()` that never drops or renames. `[Source: ai-startups-analyzer/database.md §Table:
analyses / batches, cross-referenced against knowledge.md §Configuration & Database Engine]`

---

## 5. Secondary data-sharing pattern — `spa_*` tables between tenants and tenants-admin

Separate from the AI-Credits/tenant_users sharing above: `sanchiconnect-saas-tenants` registers 20 `spa_*`
admin entities (`src/modules/global/admin/*.entity.ts`) into its single TypeORM connection against the
shared tenants DB — the same table names (`spa_admin_users`, `spa_admin_roles`, `spa_settings`,
`spa_sessions`, etc.) `sanchiconnect-saas-tenants-admin`'s Medoo connection reads/writes as its **own
primary tables**. `[INFERRED — requires validation, per sanchiconnect-saas-tenants/knowledge.md itself]`:
that repo's own knowledge.md flags this as unresolved from its side alone — it cannot determine whether
these NestJS-registered entities are vestigial/copy-pasted definitions that would collide with the real
per-tenant-admin tables under `synchronize: true`, or whether they're genuinely meant to back some other
deployment topology. Either way, this is a second live instance of the same "same table name, two
codebases, no schema contract" pattern as §2/§3, worth tracking alongside it.
`[Source: sanchiconnect-saas-tenants/knowledge.md §Tenant Provisioning — What Actually Exists in This Repo]`

---

## Change Log

- 2026-07-14 | Initial workspace-level data-ownership index. Built from all seven repos' `database.md`
  (section-header survey) plus the AI-Credits and shared-DB findings already fully traced in each repo's own
  `knowledge.md`. Assembled the three-way AI-Credits mutator finding and the tenants-DB three-reader finding
  as the two primary Known Issues, with the `synchronize:true`/no-migrations pattern as the secondary,
  platform-wide one. Flagged the `spa_*`-table double-registration between `sanchiconnect-saas-tenants` and
  `sanchiconnect-saas-tenants-admin` as a related, still-unresolved-from-either-side pattern worth watching.
