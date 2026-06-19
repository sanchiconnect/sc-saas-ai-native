---
id: FA-002
title: Stakeholder Management
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api:
    - POST api/v1/auth/register — creates backend user account during stakeholder provisioning
    - POST api/v1/startup — creates startup entity profile
    - POST api/v1/investor — creates investor entity profile
    - POST api/v1/mentors — creates mentor entity profile
    - POST api/v1/partner — creates partner entity profile
    - POST api/v1/corporate — creates corporate entity profile
    - POST api/v1/programs/enroll — auto-enrolls stakeholder in default program if configured
  flags: []
admin_modules:
  - sc-saas-admin/modules/stakeholder-crud/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/auth/module.spec.md
  - sc-saas-backend/src/modules/startup/module.spec.md
  - sc-saas-backend/src/modules/investor/module.spec.md
  - sc-saas-backend/src/modules/corporate/module.spec.md
  - sc-saas-backend/src/modules/mentors/module.spec.md
  - sc-saas-backend/src/modules/partner/module.spec.md
updated: 2026-06-18
---

# FA-002: Stakeholder Management

## Summary

Stakeholder management is the generic CRUD engine that covers every entity type the admin panel handles: startups, investors, corporates, mentors, partners, service providers, and individuals. The list/browse view (`table.php`), create form (`add.php` / `add-plain.php`), and edit form (`edit.php` / `edit_minimal.php`) are all driven by a shared configuration layer in `config/default-settings/fields_management.php` and `config/admin-data/spa_table_view_admin.php` — swapping the `table_name` URL parameter switches which entity type is in scope. Creating a new stakeholder is the heaviest path: it chains up to 18 sequential backend API cURL calls to fully provision an account (user record, entity profile, ecosystem sync, optional program enrollment). Edit and delete are lighter but the delete path contains an unparameterized SQL injection vector.

## Admin entry points

**Browse / list — `table.php`:** The admin navigates to a URL like `table.php?table_name=startups`. The page reads `spa_table_view_admin.php` config to determine visible columns, filters, and action buttons for the given entity type. It queries the client DB and renders a Bootstrap table with pagination, search, and per-row action links (view detail, edit, delete).

**Create — `add.php` and `add-plain.php`:** The admin opens the create form for a given `table_name`. `fields_management.php` config drives which form fields appear and their validation rules. On POST, the handler writes the entity row to the client DB and then calls `includes/stakeholder_account_creation_funcs.php` to provision the backend account. `add-plain.php` is a stripped-down variant used in modal or embedded contexts where the full page chrome is not wanted.

**Edit — `edit.php` and `edit_minimal.php`:** Pre-populates the form from the client DB row. On save, writes directly to the client DB. `edit_minimal.php` restricts which fields are editable; it is used for restricted admin roles or for quick-edit flows (e.g., toggling active status). No backend API call is made on edit — the backend's copy of profile data is only updated via the backend's own API if the admin explicitly triggers a re-sync.

**Detail pages — `startup-detail.php`, `partner-detail.php`, `corporate-detail.php`:** Entity-type-specific pages with hardcoded sections (metrics, team members, linked programs, documents). These are not generic and do not share the `table.php` / `fields_management.php` stack. They are read-only from the admin's perspective; writes go through `edit.php`.

**Master data — `master_data.php`:** Browses reference tables (industries, skills, funding stages, technology categories, etc.) sourced from `config/master-data/`. These rows populate the dropdowns in `add.php` and `edit.php`. Master data is tenant-global and not entity-type-specific.

## DB flow

1. **Tenants DB (read):** Admin panel resolves the per-tenant client DB connection from the current session's `admin_domain`. No stakeholder data lives in the tenants DB.
2. **Client DB (read) — list view:** `table.php` SELECTs from the entity table (e.g., `startups`, `investors`) using Medoo with dynamic column and filter config. Pagination via `LIMIT => [offset, per_page]`.
3. **Client DB (read) — detail / edit pre-fill:** Reads the single entity row by primary key for the detail and edit views.
4. **Client DB (write) — create:** Inserts the new entity row on form POST. The insert uses Medoo's parameterized insert; the row gets a generated `id`.
5. **Backend API calls — account provisioning:** Immediately after the client DB insert, `stakeholder_account_creation_funcs.php` fires a sequential chain of cURL calls (see Backend API calls below).
6. **Client DB (write) — post-provisioning update:** After the backend returns the new `user_id` and entity-specific IDs, the admin handler updates the client DB row to store those backend-assigned foreign keys.
7. **Client DB (write) — edit save:** `edit.php` and `edit_minimal.php` UPDATE the entity row directly. No backend API call.
8. **Client DB (write) — delete:** `table.php` DELETE action removes the entity row. The delete query in this path uses raw SQL with the row ID interpolated directly from the GET/POST parameter (see Known issues).

## Backend API calls

All calls in `stakeholder_account_creation_funcs.php` are sequential cURL calls using the tenant's `api_server_url` and a service-level `accessToken` from config.

1. **POST api/v1/auth/register** — registers the user account. Payload: `{ email, password (auto-generated), firstName, lastName, accountType }`. Response: `{ userId, accessToken }`. The returned `accessToken` is used for all subsequent calls in this provisioning chain.
2. **POST api/v1/startup** (or `api/v1/investor`, `api/v1/mentors`, `api/v1/partner`, `api/v1/corporate` — entity-type-dependent) — creates the entity profile. Payload: the full set of profile fields from the admin form. Response: `{ entityId }`.
3. **POST api/v1/programs/enroll** — auto-enrolls the new stakeholder in the tenant's default program if `default_program_id` is set in tenant config. Payload: `{ userId, programId }`. Skipped if no default program is configured.
4. **Ecosystem sync calls** — up to ~15 additional cURL calls that push the new entity and user to the tenants directory ecosystem index. These are best-effort; individual failures are caught and logged but do not abort the provisioning chain.

The total provisioning chain can reach ~18 sequential cURL calls. All are synchronous and block the PHP request. A slow or unavailable backend causes the admin browser to hang until PHP's `default_socket_timeout` expires.

## Feature flags

No PHP feature-flag constant gates the generic CRUD engine. `table.php`, `add.php`, and `edit.php` are always available to authenticated admin users. Individual entity type visibility within the sidebar nav may be controlled by role-level checks in the nav config, but there is no `application_management`-style constant that disables the entire stakeholder CRUD surface.

## Auth & access

- Admin must have an active PHP session.
- Role level 2 (program manager) and above can browse and view stakeholder detail pages.
- Creating and editing stakeholders requires role level 1 (super-admin) or an explicit create/edit permission on the role.
- Delete requires role level 1 (super-admin). The delete action in `table.php` does not have a separate permission check beyond the role level gate at the top of the page.
- `edit_minimal.php` is used for restricted roles that have targeted edit permission but not full profile edit access.

## Cross-repo impact

- **sc-saas-backend auth/register:** If the register endpoint changes its expected payload shape (e.g., renames `accountType` to `role`, adds a required field), the admin provisioning chain fails at step 1 and no account is created. The client DB row is already written at this point, leaving an orphaned row with no backend account.
- **sc-saas-backend entity endpoints:** If a profile endpoint (e.g., `api/v1/startup`) adds a new required field, admin-created startups will fail to provision with a 400/422. The admin error display depends on the provisioning function checking the HTTP status code on every call — any missed status check silently continues the chain with a null `entityId`.
- **sc-saas-frontend:** The frontend reads entity profiles via the backend. If the admin creates a stakeholder but the backend provisioning fails mid-chain, the frontend may see a user account with no entity profile, causing blank or error states on profile pages.
- **Ecosystem / tenants directory:** The ecosystem sync calls at the end of the chain write to the tenants directory. A tenants-side schema change to the ecosystem index endpoint will cause the sync calls to fail silently, and the newly created stakeholder will not appear in the global directory.

## Known issues

1. **`renderAr()` boolean-count bug in sparkAdminTpl:** The template helper `renderAr()` evaluates `count($dataAr && is_array($dataAr))` — this expression applies `&&` to `$dataAr` and `is_array($dataAr)`, producing a boolean (0 or 1), and then calls `count()` on that boolean. `count(true)` is always 1 and `count(false)` is always 1 in PHP. The intent was `count($dataAr)` guarded by an `is_array` check. The result is that multi-item template rendering in any view that uses `renderAr()` always behaves as if the array has exactly one item, silently truncating display of list data such as team members, co-founders, or multiple industry tags on detail pages.

2. **Unparameterized ID interpolation in `table.php` DELETE queries:** The delete action in `table.php` constructs a raw SQL DELETE by interpolating the row ID directly from the GET/POST parameter without parameterization or escaping. An authenticated admin user who can manipulate the request can supply a crafted ID value to delete arbitrary rows from the entity table, or — depending on the SQL parser's handling — inject additional SQL clauses. Medoo's parameterized API is not used for this path.

3. **Orphaned client DB rows on provisioning failure:** Because the client DB insert happens before the backend API provisioning chain, any failure in `stakeholder_account_creation_funcs.php` (network timeout, backend 5xx, schema mismatch) leaves an entity row in the client DB with no corresponding backend user account. There is no rollback and no cleanup job; these rows accumulate and can appear in the admin list view as apparently valid records that have no usable frontend session.
