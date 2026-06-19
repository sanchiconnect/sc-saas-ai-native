---
id: FA-008
title: Learning Management Admin
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api: []
  flags:
    - learning_management
admin_modules:
  - sc-saas-admin/modules/learning_management/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/learning-management/module.spec.md
updated: 2026-06-18
---

# FA-008: Learning Management Admin

## Summary

The learning management admin flow lets admins create and manage courses, modules, and content; manually enroll or override enrollment for users; and view progress and completion reports. All write operations go directly to the client DB — the backend reads from the same tables via its own query path but is never called by the admin during a write. The feature is in soft-launch state: the sidebar menu entry is commented out, and the `learning_management` feature flag is checked in an unrelated module (proforma invoices) but is not enforced inside any LMS handler itself, meaning any authenticated admin can reach LMS pages by direct URL regardless of the flag value.

## Admin entry points

The LMS module is **not reachable from the sidebar** — the menu entries are commented out in `config/default-settings/menues.php`. An admin reaches LMS pages only via a direct URL:

- `?action=learning_management/list` — course list
- `?action=learning_management/create` — create course
- `?action=learning_management/edit&id=<courseId>` — edit course
- `?action=learning_management/enrollments` — enrollment management
- `?action=learning_management/reports` — LMS reports

Because LMS handlers do not check the `learning_management` flag, these URLs are accessible to any authenticated admin session regardless of tenant flag settings.

## DB flow

**Course list:**

1. **Client DB read** — course rows fetched from the LMS course table for the tenant.
2. Course list rendered with module count, enrollment count, and published status per row.

**Course creation / edit:**

1. Admin fills in course metadata (title, description, category, published status).
2. Admin adds or reorders modules within the course.
3. Admin uploads content per module (video, PDF, or link). Uploaded files are sent to S3 or local storage depending on tenant config.
4. **Client DB write** — course row inserted or updated.
5. **Client DB write** — module rows inserted, updated, or deleted to match the submitted module list.
6. **No backend notification is sent.** The backend's in-memory cache for LMS data is not invalidated. The backend may serve stale course data until its cache naturally expires.

**Enrollment management:**

1. Admin searches for a user by name or email.
2. **Client DB read** — user row fetched to confirm identity.
3. Admin selects a course and enrollment action (enroll, unenroll, mark complete, reset progress).
4. **Client DB write** — enrollment row inserted, updated, or deleted.
5. **No backend notification.** Same cache gap as course edits.

**LMS reports:**

1. Admin selects a date range for the report. Date inputs are stored in the PHP session.
2. **Client DB read** — enrollment and progress rows queried. The date range filter is applied using `addslashes()` on the session-stored date values before interpolation into the SQL query string.
3. Results rendered as a table showing enrollment counts, completion rates, and per-user progress.
4. Admin can export the result as CSV (direct download, no additional DB write).

## Backend API calls

None. All LMS CRUD (course creation, module management, enrollment management, report queries) goes directly to the client DB. The backend reads from the same LMS tables via its own service layer but is never called by the admin. There are no sync, notification, or cache-invalidation API calls made after any admin LMS write.

## Feature flags

**`learning_management`** — defined in `config.php` as a PHP constant. This flag is currently:

- Checked in the **proforma invoices** module (as a guard condition unrelated to LMS).
- **Not checked** inside any LMS handler (`list.php`, `create.php`, `edit.php`, `enrollments.php`, `reports.php`). All LMS pages are reachable by direct URL regardless of whether `learning_management` is defined or truthy for the tenant.

Until the flag check is added to the LMS module entry point, toggling `learning_management` in the tenant config has no effect on LMS page access.

## Auth & access

- Course creation and editing requires a super-admin or content-admin role.
- Enrollment management requires at minimum a program-admin role.
- LMS reports are available to any admin user who can reach the reports URL.
- Because the sidebar menu is commented out, practical access is limited to admins who know the direct URLs — but this is not a security boundary. Any valid admin session can access any LMS page.

## Cross-repo impact

Because LMS writes are direct-DB with no backend notification:

- **Cache invalidation gap**: When the admin creates, edits, or deletes a course, the backend's in-memory LMS cache is not invalidated. The backend (`sc-saas-backend/src/modules/learning-management/`) may serve stale course data (old title, removed modules, stale enrollment state) to frontend users until the cache naturally expires. The duration of staleness depends on the backend cache TTL, which is not visible to the admin.
- **Schema coupling**: The admin and backend share the same client DB LMS tables with no API contract between them. A schema change (column rename, table restructure) applied via a migration in the backend will break the admin's direct SQL queries without any compile-time warning.
- **Soft-launch coordination**: When the LMS feature is officially launched (sidebar menu uncommented, flag check added to handlers), both the admin and the backend must be deployed together to avoid a window where the admin serves the flag gate but the backend does not, or vice versa.
- If the `learning_management` flag is ever enforced in the backend (e.g. as a `FeatureGuard` on LMS endpoints), the admin's lack of flag enforcement means admin writes can create data that the backend then refuses to serve — creating orphaned DB records visible only via direct DB query.

## Known issues

1. **`learning_management` flag is not enforced inside any LMS handler.** The flag constant is defined in `config.php` and checked in the proforma invoices module, but no LMS page (`list.php`, `create.php`, `edit.php`, `enrollments.php`, `reports.php`) checks it at the entry point. Any authenticated admin can access LMS functionality by direct URL regardless of whether the tenant's flag is set. The fix is to add a flag-constant guard at the top of each LMS handler file (consistent with how other flag-gated modules are implemented).

2. **`reports.php` uses `addslashes()` on session-stored date inputs for SQL interpolation.** The LMS reports page stores admin-supplied date range values in the PHP session and later retrieves them, applies `addslashes()`, and interpolates them directly into a SQL query string. `addslashes()` is not a sufficient escaping mechanism for MySQL in all charsets (e.g. multi-byte encodings can bypass it). A prepared statement or `PDO::quote()` should be used instead. The risk is limited to authenticated admin users but is still a SQL injection vector.

3. **No cache invalidation call to the backend after admin LMS writes.** When the admin creates or edits a course or changes an enrollment, the backend's LMS cache is not cleared. End users on the frontend may see stale course data (old titles, removed modules, incorrect enrollment status) for the duration of the backend cache TTL. There is no visible indicator to the admin that the backend is serving a cached version. The fix requires adding a best-effort cache-bust API call (or a cache key invalidation via a shared store) after each admin LMS write.

4. **LMS sidebar menu is commented out — feature is inaccessible to new admins by default.** The LMS menu entries in `config/default-settings/menues.php` are commented out as part of the soft-launch state. A new tenant admin who has not been explicitly told the direct URLs cannot discover or access the LMS module through normal navigation. If a tenant has `learning_management` enabled and expects to use it, they will find no entry point. This is a product completeness gap that must be resolved before the feature can be considered generally available.
