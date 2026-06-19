---
id: FA-005
title: Reporting & Analytics
repos:
  - sc-saas-admin
status: draft
contracts:
  api: []
  flags: []
admin_modules:
  - sc-saas-admin/modules/reporting-certificates/module.spec.md
  - sc-saas-admin/modules/growth-metrics/module.spec.md
backend_modules: []
updated: 2026-06-18
---

# FA-005: Reporting & Analytics

## Summary

The reporting and analytics feature gives super-admins and tenant admins a unified view of their program's health across four sub-systems: structured report templates executed against the live client DB, growth metrics tracked per tenant, certificate and ID card issuance tied to program milestones, and form submission exports. All reads and writes go directly to the client DB (or tenants DB for metric type configuration) — the backend exposes no reporting endpoints that the admin calls. Because the entire flow bypasses the API layer, report templates execute raw SQL on the live tenant database with no parameterization and no backend audit trail.

## Admin entry points

The admin user arrives at reporting through the **Reporting** sidebar section. From there, four flows branch:

- **Report templates** (`modules/reporting/`): Admin selects an existing template or creates a new one, picks a category, and executes it to view results in a paginated table.
- **Growth metrics** (`modules/growth_metrics/metric_types.php`): Admin configures metric type definitions (e.g. ARR, headcount) and sets the reporting duration window for the tenant.
- **Certificates / ID cards** (`modules/certificates/`, `modules/id_cards/`): Admin issues credentials to selected program participants.
- **Form submissions** (`modules/form_builder/`): Admin views and exports custom-form responses.

## DB flow

The following sequence describes the full reporting lifecycle for the template execution path, which is the most complex:

1. **Client DB read** — `spa_report_template_categories`: load category list for the template picker UI.
2. **Client DB read** — `spa_report_templates`: load stored (real) templates for the selected category.
3. **`getAutoReportTemplates()` called** (`includes/reporting_auto_templates.php`): synthesises virtual templates at runtime. As a side effect this function may **INSERT** new rows into `spa_report_template_categories`. Because of this, **the category list fetched in step 1 is now stale**. The UI must re-query categories after this call if it wants the auto-template categories to appear.
4. **Client DB read** — merged template list (real + auto) rendered to admin.
5. **Admin selects a template and triggers execution.**
6. **Client DB execute** — template SQL runs raw against the live tenant DB. In production there is no dev-only gate; the SQL is executed as-is. Results are fetched and rendered as a table.

For the **growth metrics** path:

1. **Client DB read** — metric list (metric names, values per entity) from the client DB.
2. **Tenants DB write** (`$mainDatabase`) — `metric_types.php` is the only reporting-module file that writes to the tenants DB. It updates `tenant_users.growth_metrics_duration_set` to record the reporting window the admin configured.

For the **application count widgets** on the reporting dashboard:

1. **Client DB read** — `getApplicationCounts()` queries application rows grouped by status and returns counts per bucket.

For **certificate / ID card issuance**:

1. **Client DB read** — `spa_certificate_builders` (or equivalent) to load the built template.
2. **Client DB read** — `spa_settings` to retrieve the certificate template key. Bare key is used for the `startup` stakeholder type; `{type}_` prefix is used for all other stakeholder types.
3. **Client DB write** — issued certificate/ID card record written per recipient.

For **form submission exports**:

1. **Client DB read** — form submission rows for the target form.
2. Admin downloads as CSV; no DB write required.

## Backend API calls

None. Reporting is entirely direct-DB. The backend is not involved in any reporting, analytics, certificate, ID card, or form submission export flow.

## Feature flags

None. Reporting is always available to any admin user who has access to the reporting module. There is no PHP constant in `config.php` that gates any reporting sub-system.

## Auth & access

- All reporting sub-sections require an authenticated admin session.
- Growth metrics duration configuration (`metric_types.php`) writes to the tenants DB and is treated as a super-admin operation; tenant-level admins should not have access.
- Certificate and ID card issuance requires at minimum a program-admin role level (the issuing admin must have access to the target program's participant list).
- Report template execution is available to any admin with reporting access — no extra role gate beyond authentication is enforced at the template-execution level.

## Cross-repo impact

Because reporting is entirely direct-DB and calls no backend API:

- A schema change to any client-DB table that a report template queries against will silently break that template — there is no contract check.
- If `spa_report_template_categories` or `spa_report_templates` schema changes, `getAutoReportTemplates()` and all callers must be updated together.
- The backend may read the same LMS/portfolio tables that reporting writes to; a reporting-driven write has no backend cache invalidation path.
- `tenant_users.growth_metrics_duration_set` is written by the admin and read by the tenants service — a column rename or type change in the tenants DB entity must be coordinated with `modules/growth_metrics/metric_types.php`.

## Known issues

1. **Auto-template category side-effect causes stale UI.** `getAutoReportTemplates()` may INSERT new rows into `spa_report_template_categories` as a side effect of synthesising templates. Any caller that loaded the category list before calling this function (e.g. to populate a filter dropdown) will display a stale list that is missing the auto-template categories. The fix is to re-query `spa_report_template_categories` after `getAutoReportTemplates()` returns, never before.

2. **`getApplicationCounts()` increments the wrong bucket for rejected applications.** Due to a copy-paste error in the counting SQL, rejected applications are counted in the `shortlisted` bucket instead of the `rejected` bucket. This means the shortlisted count is inflated and the rejected count is understated on any reporting widget that calls `getApplicationCounts()`. The bug is in the SQL `CASE`/`WHERE` condition that identifies rejected rows.

3. **Raw template SQL executes against the live tenant DB with no parameterization.** Report templates store arbitrary SQL that is executed verbatim against the client DB. There is no allowlist, no read-only connection, and no transaction rollback. A misconfigured or malicious template can issue writes, drops, or truncates. This is by design (to allow flexible reporting) but is a significant operational risk in a multi-tenant environment.

4. **`spa_settings` key prefix scheme is undocumented and easy to misconfigure.** Certificate and ID card template lookup uses a bare key for the `startup` stakeholder type but a `{type}_` prefix for all other types. There is no schema-level enforcement of this convention; a key written with the wrong prefix will silently result in a missing template at issuance time.
