---
id: SAN-16
title: Tenant Data Export (Download Backup Data)
type: feature
status: in-review                # draft → approved → in-progress → in-review → done
linear: https://linear.app/sanchiconnect/project/tenant-data-export-download-backup-data-ab320d3353d8
owner: nirmal.s@sanchiconnect.com
repos:
  - sanchiconnect-saas-tenants-admin
contracts:
  api: []                       # no sc-saas-backend endpoint added or changed — direct-DB PHP feature
  flags: []                     # gated by existing is_dev role, not a new cockpit-owned flag
  events: []
tenant_scoped: true
depends_on: []
created: 2026-07-15
---

# Tenant Data Export (Download Backup Data)

## Problem

When a client (tenant) wants to exit the SanchiConnect SaaS product, there is currently no self-serve way for a platform operator to pull a full backup of that tenant's data. This feature adds a "Download Backup Data" entry to the Developer Zone dropdown in `sanchiconnect-saas-tenants-admin` (`adm.tenants.sanchidev.in`) — the platform-operator control panel — so an `is_dev`-role operator can pick a specific tenant, pick which categories of that tenant's data to export, pick an output format (CSV, Excel, or ZIP), and download it.

**Re-scoped 2026-07-15** (was originally scoped to `sc-saas-admin`, per-tenant admin panel — see git history on this file). Corrected because: `sanchiconnect-saas-tenants-admin` already stores every tenant's DB credentials in `tenant_users` (`database_host`, `database_user`, `database_password`, `database_port`, `database_name` — `sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts:63-75`), and already has **live, working code that connects to an arbitrary tenant's DB using those columns**: `modules/scrapper.php:7-15` loops every active `tenant_users` row and opens a per-tenant Medoo connection for cross-tenant reporting. This is a better fit than the original plan — a platform operator can action a client's exit request without needing to log into that specific tenant's own `sc-saas-admin` panel.

**Trade-off reversed 2026-07-15 (same day, later):** the generic-dump approach was shipped first, then reviewed against `sc-saas-admin`'s reference export (`modules/csv/export.php`, `table/startups` → CSV) and found insufficient — a raw dump would hand a departing client foreign-key IDs instead of names (e.g. `registered_country: 14` instead of a country name), which isn't a usable backup. Decision: **port the 8 curated per-table cases** already built in `sc-saas-admin/modules/csv/export.php` (`startups`, `mentors`, `investors`, `partners`, `service_providers`, `corporates`, `program_office_members`, `individuals` — joins, ID-to-name resolution) into this repo's handler, adapted to run against the selected tenant's connection. `startups` is added to the **Stakeholders** category bundle (it wasn't in the original bundle definition — an oversight, since it's clearly a stakeholder entity and has its own curated case in the reference file). Generic `getColumns()` dumps remain for **Application/Program data** — that has no curated reference to port from.

**Simplified 2026-07-15 (product decision, same day):** three simplifications were made to the shipped feature, all in `_data_export_generate.php` / `data_export.php`:
1. **S3 URL resolution removed entirely.** The curated Stakeholders builders no longer resolve file-reference columns (`pitch_document`, `company_logo`, `avatar`, `organization_logo`, `logo`) to public/signed S3 URLs — the `buildTenantS3FileUrl()`/`buildTenantS3SignedUrl()` helpers and the `S3Client` dependency were deleted. Exports now carry the **raw stored value** (an S3 key/path string) in those columns, untouched.
2. **The "Other" category was removed.** A table that matches neither the Stakeholders allowlist nor the Application/Program-data prefix pattern is now silently excluded from export — not bucketed into a catch-all.
3. **The "Users" category was removed.** The `users` table (if present) is never categorized/exportable through this tool now — same silent-exclusion treatment as Other.

Only **2 categories** exist going forward: **Stakeholders** and **Application/Program data**.

**Security note:** `modules/scrapper.php` (the connection precedent) has **no role gate at all** — only `checkLoggedIn()`. This is not the pattern to copy for permissions. This feature reuses the same `checkRole("is_dev")` gate already used by this repo's own `modules/developer/database_management.php:5`, `api_management.php:4`, `form_fields_management.php:5`. Audit logging was considered (this repo has no existing audit-log mechanism, unlike `sc-saas-admin`'s `createAdminLogs()`/`spa_admin_logs`) but is explicitly **out of scope** per product decision (2026-07-15) — not being added.

## Acceptance criteria

- [ ] An `is_dev`-role operator sees a new "Download Backup Data" entry in the Developer Zone dropdown, added to the array returned by `getDeveloperMenus()` (`includes/core_functions.php:98`), following the existing `{title, link, icon, target}` shape.
- [ ] Loading the new page/action directly by URL as a non-`is_dev` session redirects away, matching the pattern in `modules/developer/database_management.php:5-8`.
- [ ] The screen lets the operator pick one active tenant (from `tenant_users` where `active = "1"`, the same filter `modules/scrapper.php:7` already uses) via a searchable selector — plain `<select>` is fine if the theme doesn't already have a search-enabled dropdown component; check the theme's existing JS libs before adding a new one.
- [ ] Selecting a tenant opens a per-tenant Medoo connection using that row's `database_host`/`database_name`/`database_user`/`database_password`/`database_port`, exactly matching `modules/scrapper.php:9-16`'s connection shape — never the platform `$database` connection, and never accepting a DB host/name/credentials from anything other than the looked-up `tenant_users` row itself (no client-supplied connection parameters).
- [ ] Tables from that tenant's DB are enumerated dynamically (`SHOW TABLES FROM` + `getColumns()`, adapting `modules/developer/database_management.php:103-150` to run against the selected tenant's connection instead of the platform DB) and grouped into exactly **2 categories**: **Stakeholders** (`startups`, `investors`, `mentors`, `corporates`, `service_providers`, `partners`, `individuals`, `program_office_members`) and **Application/Program data** (`application_programs` + its rounds/jury/submissions/ratings/analysis sub-tables, `programs` + its rounds/jury/faqs/submissions sub-tables) — one checkbox per bundle, not per table. Any table matching neither bucket (including `users`) is silently excluded from export — **Users and Other categories were removed by explicit product decision (2026-07-15)** and no longer exist.
- [ ] The operator selects one or more categories and exactly one output format (CSV, Excel, or ZIP) before generating.
- [ ] **Stakeholders category**: each of the 8 tables (`startups`, `mentors`, `investors`, `partners`, `service_providers`, `corporates`, `program_office_members`, `individuals`) uses the curated query/joins/ID-resolution ported from `sc-saas-admin/modules/csv/export.php`'s matching `case` block, adapted to run against the selected tenant's connection — not a generic dump. **No S3 URL resolution is performed** (removed by explicit product decision, 2026-07-15): file-reference columns (`pitch_document`, `company_logo`, `avatar`, `organization_logo`, `logo`) are exported with their raw stored value (an S3 key/path string) exactly as read from the base query.
- [ ] **Application/Program data category**: generic `getColumns()`-driven column dump per table (no curated reference exists for this — out of scope to build one).
- [ ] Excel output: via `phpoffice/phpspreadsheet` (new composer dependency, matching `sc-saas-admin`'s `^5.7` — confirm compatibility with this repo's actual PHP runtime, not just its stale `"php": ">=5.5.0"` composer floor).
- [ ] ZIP output: bundles one file per selected category using this repo's existing `Zipper` class (`core/filemanager.php:206`, confirmed present and identical in shape to `sc-saas-admin`'s).
- [ ] No audit logging is added (product decision, 2026-07-15) — do not build a new logs table or call any logging function for this action.
- [ ] Generation is synchronous — the handler streams the response directly, no persisted file, no queue.

## Per-repo plan

### sanchiconnect-saas-tenants-admin

1. **Menu entry** — add a `{title: "Download Backup Data", link: "data_export", icon: "fa-download", target: ""}` item to `getDeveloperMenus()` (`includes/core_functions.php:98`).
2. **New module** `modules/developer/data_export.php` — `checkLoggedIn()`, `include(getcwd() . "/modules/common.php")`, then `if (!checkRole("is_dev")) { ...redirect... }` matching `modules/developer/database_management.php:5-8`. Renders the tenant selector (querying `tenant_users` where `active = "1"`).
3. **New template** under `themes/default/html/developer/` — tenant selector + category checklist + format radio, styled consistent with the existing `themes/default/html/developer/database_management.php`.
4. **New generation handler** `modules/developer/_actions/_data_export_generate.php`:
   - Re-gates with `checkRole("is_dev")` independently (defense in depth).
   - Looks up the selected tenant's `tenant_users` row by id, opens the per-tenant Medoo connection exactly as `modules/scrapper.php:9-16` does.
   - Enumerates tables via `SHOW TABLES FROM`/`getColumns()` against that connection (adapted from `modules/developer/database_management.php:103-150`).
   - Generates CSV (generic column dump), Excel (`phpoffice/phpspreadsheet`), or ZIP (`Zipper` class, `core/filemanager.php:206`) per the selected format.
5. **Composer** — add `phpoffice/phpspreadsheet` to `composer.json` (not present today; `aws/aws-sdk-php` and others already are, so adding a new require is an established pattern in this repo).

_No other repo is touched. `sc-saas-admin`, `sc-saas-backend`, `sc-saas-frontend`, and `sanchiconnect-saas-tenants` have no work items in this spec._

## Contracts & invariants

- **Flags:** None added. Gated by the existing `is_dev` session role (`checkRole("is_dev")`), same mechanism already used by this repo's `database_management.php`, `api_management.php`, `form_fields_management.php`.
- **API:** None. No `sc-saas-backend` change — this reads the target tenant's DB directly via Medoo, the same way `modules/scrapper.php` already does.
- **Events:** None.
- **Invariants at risk:** This repo has **no tenant-scoping mechanism by design** (per its own `CLAUDE.md` — it's a platform-operator tool operating on global cockpit data) — this feature is the **second** deliberate, ad-hoc exception to that (after `modules/scrapper.php`), not a violation of a rule that applies here. The safety property that matters instead: the per-tenant connection must be opened **only** from a server-side lookup of the operator's explicit tenant selection against the real `tenant_users` row (id + `active = "1"`), never from a client-suppliable host/credential value. Call this out explicitly in code review — it's the one place this feature could go wrong.

## Test plan

- `sanchiconnect-saas-tenants-admin` has no automated test framework (`php -l` only). Run `php -l` on every new/edited file. Manually verify: (a) an `is_dev` session sees and can open the new menu entry; (b) a non-`is_dev` session hitting the URL directly is redirected; (c) the tenant selector only lists `active = "1"` tenants; (d) CSV/Excel/ZIP each open correctly for at least one real tenant in a local/staging setup; (e) selecting a different tenant produces that tenant's data, not a previously-selected one (no session/connection bleed between requests).
- cross-repo: none required.

## Rollout

Single-repo, no flag, no migration. The Developer Zone menu entry itself is the rollout gate (`is_dev`-only, already a small trusted population).

## Out of scope

- Any change to `sc-saas-admin`, `sc-saas-backend`, `sc-saas-frontend`, or `sanchiconnect-saas-tenants`.
- Curated/per-table export formatting for the **Application/Program data** category — generic column dumps only (no reference implementation exists for this). Stakeholders category IS curated, per the reversed decision above.
- Audit logging of export actions — explicit product decision (2026-07-15), not being added.
- The **Users** and **Other** categories — removed entirely by explicit product decision (2026-07-15); a table matching neither remaining bucket is silently excluded from export, not bucketed into a catch-all.
- S3 URL resolution for stakeholder file-reference columns — removed entirely by explicit product decision (2026-07-15); exports carry the raw stored S3 key/path string.
- Automated/scheduled/recurring backups.
- Data import or restore tooling (export-only).
- A new feature flag — reuses the existing `is_dev` role gate.
- Bulk multi-tenant export in a single action — one tenant selected per export, per the tenant-scoping safety property above.
- Background/async export generation — synchronous streaming only.

## Open questions

None.
