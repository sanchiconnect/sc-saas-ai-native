---
id: FA-006
title: System Administration
repos:
  - sc-saas-admin
status: draft
contracts:
  api: []
  flags: []
admin_modules:
  - sc-saas-admin/modules/system-admin/module.spec.md
  - sc-saas-admin/modules/ajax/module.spec.md
backend_modules: []
updated: 2026-06-18
---

# FA-006: System Administration

## Summary

System administration covers the meta-operational layer of the admin panel itself: the developer module that lets super-admins mutate panel configuration (API routes, database structure, email settings, form field mappings, table view config, and sidebar menu overrides), and the audit/log modules that surface what has happened (system action logs, profile change history, internal task tracking). None of these flows call the backend API — all reads and writes go directly to the tenants DB or the client DB. Access is gated by role code (`is_dev`, `super_admin`, or `developer`) rather than a feature flag. Because the developer module can execute DDL on live databases and send email bypassing CSRF, it carries the highest blast radius of any admin module.

## Admin entry points

Access is via the **Developer** and **Audit** sidebar sections, both of which are hidden from non-developer roles.

- **Developer → API route management**: Admin views and edits custom REST route definitions stored in the config tables.
- **Developer → Database management** (`database_management.php`): Admin issues DDL operations (CREATE TABLE, DROP TABLE, ALTER TABLE, TRUNCATE, RENAME TABLE) against the client DB.
- **Developer → Email management** (`email_management.php`): Admin configures SMTP credentials and edits email templates. The send-email action is also available here.
- **Developer → Form field mappings**: Admin defines which fields appear in entity forms (e.g. startup profile, mentor profile). Writes to `spa_form_fields` or equivalent config tables.
- **Developer → Table view config**: Admin defines which columns appear in `table.php` views. Writes to `spa_table_view_admin`.
- **Developer → Menu management**: Admin overrides the sidebar menu structure for the tenant, overriding `config/default-settings/menues.php`.
- **Developer → WhatsApp / WATI settings**: Admin sets WATI API credentials. Stored in `spa_settings`.
- **Audit → System logs** (`modules/system_logs/`): Admin browses and filters `spa_admin_logs` entries by action type, date, and user.
- **Audit → Profile audit logs** (`modules/profile_audit_logs/`): Admin browses per-entity profile change history.
- **Task management** (`modules/task_management/`): Admin creates and manages internal to-do items for the admin team. Written to the `tasks` table in the client DB.

## DB flow

All system administration flows touch the client DB except where noted. The tenants DB is not written by system admin flows (WATI settings and menu overrides go into client DB `spa_settings`/`spa_admin_menu`).

**Database management DDL path:**

1. Admin submits a DDL form (e.g. RENAME TABLE) with `$_POST['table_name']` and operation type.
2. `database_management.php` constructs a raw SQL string using the posted table name, backtick-quoted.
3. **Client DB execute** — DDL is run directly against the live tenant DB.
4. For `RENAME TABLE`: eight config tables that reference the old table name must be updated in sync. These updates run as sequential statements with no wrapping transaction.

**API route CRUD path:**

1. Admin submits form. CSRF token is verified before write.
2. **Client DB write** — route definition inserted or updated in the config table.

**Email management path:**

1. Admin views/edits SMTP config and email templates.
2. **Client DB write** — SMTP credentials and template content saved.
3. Admin triggers send-email action. CSRF check is present in the code but **commented out** for this action. Email is dispatched via the configured SMTP transport.

**Form field mapping / table view config path:**

1. Admin submits column/field configuration.
2. **Client DB write** — `spa_form_fields` or `spa_table_view_admin` updated.

**Menu management path:**

1. Admin edits the menu tree.
2. **Client DB write** — tenant menu override persisted. The default `menues.php` is no longer used for this tenant until the override is cleared.

**System logs / profile audit log read path:**

1. Admin applies filters (action type, date range, user).
2. **Client DB read** — `spa_admin_logs` rows returned and rendered in a paginated table.
3. For profile audit logs: **Client DB read** — per-entity change history rows returned.

**Task management path:**

1. Admin creates, edits, or closes a task.
2. **Client DB write** — `tasks` table updated.

## Backend API calls

None. All system administration and audit flows are direct-DB operations. The backend is not called for any developer module operation, log browsing, or task management action.

## Feature flags

None. The developer module and all system administration sub-pages are gated by role code (`is_dev`, `super_admin`, or `developer`), not by a feature flag PHP constant in `config.php`. Removing a role code from a session is sufficient to deny access; no flag needs to be toggled.

## Auth & access

- All developer sub-pages require the session to carry `is_dev === true` or a role code of `super_admin` or `developer`. Requests from other role levels are rejected at the module entry point.
- System logs and profile audit logs are readable by super-admins; tenant admins do not have access.
- Task management is available to all authenticated admin users.
- There is no per-operation secondary confirmation (e.g. re-authentication before a DROP TABLE). The role check at the module entry point is the only gate.

## Cross-repo impact

Because system administration is entirely direct-DB:

- A DDL change made via `database_management.php` (e.g. DROP TABLE, RENAME TABLE) is invisible to the backend and frontend until they next query the affected table. There is no schema migration record, no cache invalidation, and no backend restart triggered. If a table renamed in the admin panel is also queried by the backend, the backend will throw at the next query.
- Menu overrides stored in the client DB shadow the PHP default `config/default-settings/menues.php`. If a new module is added to the default menu in a code deploy, tenants with a stored menu override will not see it until they clear the override.
- WATI / WhatsApp settings written to `spa_settings` are consumed by notification-dispatch code. An incorrect WATI credential stored here will silently break WhatsApp notifications without any backend log entry.

## Known issues

1. **`database_management.php` constructs raw DDL from `$_POST['table_name']` — no allowlist.** Backtick quoting is applied to the table name before interpolation, but backtick quoting is not a full sanitization barrier. An authenticated super-admin can craft a table name that closes the backtick context and appends arbitrary SQL. The mitigation (an explicit allowlist of permitted table names) is absent. This is a post-authentication SQLi risk on DDL operations.

2. **`rename_table` cascade across 8 config tables runs outside a transaction.** When a table is renamed, `database_management.php` updates references in eight configuration tables sequentially. No `START TRANSACTION` / `COMMIT` wraps the sequence. A failure midway (DB timeout, deadlock, connection drop) leaves a subset of config tables pointing to the old name and the rest pointing to the new name. The panel is permanently inconsistent until manually repaired; there is no rollback path.

3. **`email_management.php` send-email action has CSRF protection commented out.** The CSRF token verification that guards other developer-module actions is present in the file but commented out for the send-email POST handler. An attacker who can load a page in a browser where an admin is authenticated can trigger an arbitrary email send (to any address, with any body) via a cross-site POST. This is an authenticated CSRF — the admin session is required, but the CSRF token is not.

4. **No re-authentication before destructive DDL.** DROP TABLE and TRUNCATE operations execute immediately on form submission. The only gate is the session role check at module entry. A session hijack, or an admin who forgets to log out on a shared machine, can result in irreversible data loss with a single form submit.
