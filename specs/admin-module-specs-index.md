---
type: index
repo: admin
updated: 2026-06-18
---

# Admin Module Specs Index

Master index of all `sc-saas-admin` module specs. The admin panel is PHP/Medoo/sparkAdminTpl with **two DB connections per request**: `$mainDatabase` (tenants DB — reads feature flags, api_url, per-tenant DB creds) and `$database` (per-tenant client DB — all business data). Plus cURL calls to `$api_server_url` (sc-saas-backend REST API).

Three modules perform cross-DB **writes** back to the tenants DB:
- `finance-memberships` — `memberships/settings.php` updates tenant-level membership config
- `integrations` — `intellectual_property/` writes patents data to tenants DB
- `growth-metrics` — `metric_types.php` updates `tenant_users.growth_metrics_duration_set`

> **How to use:** When working on a module, read its spec first — it records owned files, consumed flags, DB connections, known bugs, and security findings surfaced during spec authoring. When adding a handler or flag gate, update the spec's `owns` / `consumes` frontmatter and `updated` date.

---

## Foundation

| Module | Spec | Description |
|---|---|---|
| core-bootstrap | [module.spec.md](../sc-saas-admin/module.spec.md) | Dual DB connection setup, tenancy resolution, router, template engine, feature flag loading |
| auth | [module.spec.md](../sc-saas-admin/modules/auth/module.spec.md) | Admin login, session, password reset, profile — CSRF on login is commented out |
| ajax-handlers | [module.spec.md](../sc-saas-admin/modules/ajax/module.spec.md) | 7 jQuery AJAX endpoints: api_actions, crud_actions, email_actions, spa_actions, whatsapp_actions, stakeholder_export, fields_mapping |

---

## Stakeholder & Generic CRUD

| Module | Spec | Description |
|---|---|---|
| stakeholder-crud | [module.spec.md](../sc-saas-admin/modules/stakeholder-crud/module.spec.md) | Generic CRUD engine (table.php/add.php/edit.php) for all entity types driven by fields_management.php config |

---

## Application Lifecycle

| Module | Spec | Description |
|---|---|---|
| application-management | [module.spec.md](../sc-saas-admin/modules/application_management/module.spec.md) | Program + round + application + submission management; approve/reject triggers backend API sync |
| startup-application-management-flow | [flow.spec.md](../sc-saas-admin/modules/startup-application-management-flow.spec.md) | Kanban/table/reports view for a program's applications — 13 AJAX handlers; bulk email; round moves via backend `:adminMd5` API |
| stakeholder-detail-pages | [spec.md](../sc-saas-admin/modules/stakeholder-detail-pages.spec.md) | startup-detail.php (1784 lines, 15+ inline actions incl. ID card auto-gen on approval), application-submission-detail.php, pm_dashboard, mentor/investor detail |
| venture-studio | [module.spec.md](../sc-saas-admin/modules/venture-studio/module.spec.md) | VS-specific program and application management (separate funcs from standard application-management) |
| jury | [module.spec.md](../sc-saas-admin/modules/jury/module.spec.md) | Jury assignment, scoring dashboards, review of application submissions |
| program-management | [module.spec.md](../sc-saas-admin/modules/program-management/module.spec.md) | PM dashboards + program creation wizard (create-program.php — 3-step: details/forms/team) |
| challenges | [module.spec.md](../sc-saas-admin/modules/challenges/module.spec.md) | Challenge creation, participant management — details.php JSON comparison bug locks non-super-admin PMs |

---

## Learning & Events

| Module | Spec | Description |
|---|---|---|
| learning-management | [module.spec.md](../sc-saas-admin/modules/learning_management/module.spec.md) | LMS course + enrollment management; flag gate missing from handlers; sidebar menu commented out |
| events-meetings | [module.spec.md](../sc-saas-admin/modules/events-meetings/module.spec.md) | Event creation/attendee management + meeting session management; reject email API call commented out |

---

## Community & Connections

| Module | Spec | Description |
|---|---|---|
| community-connections | [module.spec.md](../sc-saas-admin/modules/community-connections/module.spec.md) | Community wall moderation, connections global matrix; loads all connections with no pagination |
| connections | [module.spec.md](../sc-saas-admin/modules/connections/module.spec.md) | Admin-side connection moderation — user connection matrix (can_connect/can_search/limit) + global matrix per stakeholder-type pair |

---

## Finance

| Module | Spec | Description |
|---|---|---|
| finance-memberships | [module.spec.md](../sc-saas-admin/modules/finance-memberships/module.spec.md) | Membership plans, payment gateway config, invoices — settings.php writes to tenants DB |
| payment-gateways | [module.spec.md](../sc-saas-admin/modules/payment_gateways/module.spec.md) | Gateway enable/disable with live API credential validation; Stripe/Razorpay/Easebuzz; plaintext credential storage |
| memberships | [module.spec.md](../sc-saas-admin/modules/memberships/module.spec.md) | Membership lifecycle (create/edit/soft-delete/approve); single-active enforcement; certificate date sync |
| tax-management | [module.spec.md](../sc-saas-admin/modules/tax_management/module.spec.md) | Tax profile CRUD (GST/VAT rates applied to payment amounts) |

---

## Communication & Outreach

| Module | Spec | Description |
|---|---|---|
| outreach-communications | [module.spec.md](../sc-saas-admin/modules/outreach-communications/module.spec.md) | Broadcast messages (JSON_CONTAINS audience targeting), WhatsApp/WATI, contacts, outreach tracking |

---

## Content Management

| Module | Spec | Description |
|---|---|---|
| content-management | [module.spec.md](../sc-saas-admin/modules/content-management/module.spec.md) | 8 content types: news, glossary, resource files, video gallery, industry reports, product updates, ads, booster kit |

---

## Certificates & ID Cards

| Module | Spec | Description |
|---|---|---|
| certificates | [module.spec.md](../sc-saas-admin/modules/certificates/module.spec.md) | Certificate + ID card issuance (upsert, number generation) and builder (design settings per stakeholder type in spa_settings); no PDF at issuance |

## Metrics & Reporting

| Module | Spec | Description |
|---|---|---|
| growth-metrics | [module.spec.md](../sc-saas-admin/modules/growth-metrics/module.spec.md) | Growth metrics, milestones, tickets, portfolio — metric_types.php writes to tenants DB |
| milestones | [module.spec.md](../sc-saas-admin/modules/milestones/module.spec.md) | Admin-side milestone management; backend milestones spec is the counterpart |
| tickets | [module.spec.md](../sc-saas-admin/modules/tickets/module.spec.md) | Support ticket lifecycle (assign/reply/close/reopen); email delegated to backend; S3 attachments with no file-type validation |
| reporting | [module.spec.md](../sc-saas-admin/modules/reporting/module.spec.md) | Custom BI dashboards backed by stored SQL templates — raw SQL execution with bypassable denylist; highest security risk in admin |
| reporting-certificates | [module.spec.md](../sc-saas-admin/modules/reporting-certificates/module.spec.md) | Report templates (real + virtual auto-templates), form submissions, certificates, ID cards |

---

## Facilities & Partners

| Module | Spec | Description |
|---|---|---|
| facilities | [module.spec.md](../sc-saas-admin/modules/facilities/module.spec.md) | Space/facility management, booking questions, kiosk — soft-delete writes to both tenants and client DB |
| partners-recruitment | [module.spec.md](../sc-saas-admin/modules/partners-recruitment/module.spec.md) | Ecosystem partner management + recruitment partner job management (two distinct partner types) |

---

## Form & Data Management

| Module | Spec | Description |
|---|---|---|
| form-management | [module.spec.md](../sc-saas-admin/modules/form-management/module.spec.md) | Custom form builder, versioning, CSV import/export — version restore guard is critical |
| integrations | [module.spec.md](../sc-saas-admin/modules/integrations/module.spec.md) | Zoho CRM, AWS S3, file manager, data scrapers, intellectual property — IP writes to tenants DB |

---

## System Administration

| Module | Spec | Description |
|---|---|---|
| system-admin | [module.spec.md](../sc-saas-admin/modules/system-admin/module.spec.md) | Developer config (DDL, email, form fields, menus), system logs, profile audit logs, task management |
| profile-audit-logs | [module.spec.md](../sc-saas-admin/modules/profile_audit_logs/module.spec.md) | Read-only audit log viewer for profile/admin actions; pairs with backend audit-log module |

---

## Security findings

| Severity | Module | Finding |
|---|---|---|
| 🔴 Critical | system-admin | `database_management.php` constructs DDL from `$_POST['table_name']` — backtick-quoting only, no allowlist |
| 🔴 Critical | auth | Password change skips old-password verification — any active session can change the password |
| 🔴 Critical | auth | Login CSRF protection is commented out |
| 🟠 High | ajax-handlers | `stakeholder_export.php` has no CSRF check (only handler without it); no ownership validation on startupId |
| 🟠 High | system-admin | `email_management.php` send-email action has CSRF and sanitization commented out |
| 🟠 High | integrations | `intellectual_property/` writes to tenants DB — cross-tenant blast radius |
| 🟠 High | integrations | Capboard scraper has `display_errors=1` never removed — exposes PHP errors in production |
| 🟠 High | auth | Open redirect in backdoor login — `$_GET['redirect_url']` passed to `header(Location:...)` without protocol validation |
| 🟡 Medium | stakeholder-crud | Raw SQL with unparameterized ID in `table.php` DELETE queries |
| 🟡 Medium | application-management | `memory_limit` set to `6600000000000` — effectively no PHP memory limit |
| 🟡 Medium | community-connections | `connections/index.php` loads ALL connections with no pagination — OOM on large tenants |
| 🟡 Medium | integrations | WATI access token stored unencrypted in `spa_settings` |
| 🟡 Medium | challenges | `details.php` JSON comparison bug locks all non-super-admin PMs out of challenge details |
| 🟡 Medium | finance-memberships | Payment gateway validation calls third-party APIs synchronously — slow gateway deadlocks PHP process |
| 🟡 Medium | reporting-certificates | Report template SQL executes raw against live client DB |
| 🟡 Medium | learning-management | `learning_management` flag not enforced inside LMS handlers — accessible by direct URL |
| 🟡 Medium | system-admin | `rename_table` cascade across 8 config tables runs without transaction |
| 🔴 Critical | reporting | Raw SQL from stored templates executed via PDO; keyword denylist (`INSERT`, `DROP`, etc.) is trivially bypassed via `SELECT...INTO OUTFILE`, `CALL`, `SLEEP(N)` |
| 🔴 Critical | reporting | No item-level auth on `_execute_chart`/`_export_data`/`_drilldown` — any admin guessing an `item_uuid` can pull any widget data regardless of dashboard `allowed_roles` |
| 🟠 High | payment-gateways | Payment credentials (`live_client_id`, `live_client_secret`) stored as plaintext VARCHAR — DB dump exposes all tenant payment keys |
| 🟠 High | payment-gateways | Easebuzz credential validation POSTs a live dummy transaction payload — not a dry-run |
| 🟠 High | payment-gateways | Seed array typo: `live_client_id` appears twice; `live_client_secret` never seeded |
| 🟠 High | tickets | `upload_attachment` has no file-type validation — any file type accepted to S3 |
| 🟠 High | reporting | Export adds `LIMIT 10000` only if no LIMIT present — a template with `LIMIT 99999` can stream all rows unbounded |
| 🟡 Medium | tickets | `assigned_to_ids` written from `$_POST` without existence check; no CSRF on any ticket action |
| 🟡 Medium | payment-gateways | Duplicate entry point at `finance_management/settings/gateways/` — two paths to same `payment_gateways` table; changes to one may not reflect in the other |

Updated: 2026-06-18
