---
type: index
repo: sanchiconnect-saas-tenants-admin
updated: 2026-07-20
---

# Tenants-Admin Module Specs Index

Master index of all `sanchiconnect-saas-tenants-admin` module specs. This is the **platform-operator** panel (PHP/Medoo/sparkAdminTpl, QUCod framework) over the SanchiSaaS tenants control-plane — used by Sanchi's own staff, not tenant staff, and distinct from `sc-saas-admin`. Unlike that sibling repo, there is **one DB connection, not two**: a single shared Medoo connection to the tenants MySQL DB (the same DB owned by `sanchiconnect-saas-tenants`'s NestJS/TypeORM app), plus direct calls out to AWS S3 and a live `sc-saas-backend` deployment (`resetAPISaaSSettings()` on tenant edit, admin-account-created notification). There is no per-tenant scoping rule here — this is deliberate: it is a platform-level tool operating on global cockpit data, not per-tenant data (see workspace `CLAUDE.md` invariant #5, which explicitly excludes this repo).

**Most tables in this panel are not hand-built per-table features.** `add.php`/`edit.php`/`table.php`/`detail.php` are one generic **Dynamic CRUD framework** — a single engine parameterized by table name, driven by field metadata in `spa_data_management` (read via `db_mapping_fields()`), with an optional sectioning override (`spa_form_layouts` → `spa_form_sections` → `spa_form_section_fields`) edited through `developer/forms_layout_management.php`. A `spa_form_layouts` row created without full section coverage renders a completely blank add/edit form — a known landmine that can hit any table, not just the one being actively configured. Only a handful of `modules/` subdirectories are genuinely bounded, hand-written contexts (`ai_credits`, `finance_management`, `auth`, `developer`, the file/data utility plugins) — the rest of the operator experience rides the shared engine, whose own contract is captured in the root-level `module.spec.md` rather than a `modules/` subdirectory.

> **How to use:** When working on a module, read its spec first — it records owned files, DB access, known bugs, and security findings surfaced during spec authoring. When adding a handler or changing a table this panel touches, update the spec's frontmatter and `updated` date.

**Coverage:** all 9 directories under `modules/` have a `module.spec.md` (`ai_credits`, `ajax`, `auth`, `aws`, `csv`, `developer`, `filemanager`, `finance_management`, `upload`) — full coverage, no gaps. `developer/_actions/` is an internal subdirectory of `developer` (one file, `_data_export_generate.php`) and is covered by that module's spec rather than having its own.

---

## CRUD Framework Core

| Module | Spec | Description |
|---|---|---|
| core | [module.spec.md](../sanchiconnect-saas-tenants-admin/module.spec.md) | Root-level spec for the panel itself — `index.php` routing, `config/`, `core/db.php` + `session.php`, `includes/core_functions.php`, and the generic `add.php`/`edit.php`/`table.php`/`detail.php` engine; platform-operator tool, no relationship to `sc-saas-admin` |
| ajax | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/ajax/module.spec.md) | 5 JSON AJAX handlers behind swapped names — `crud_actions.php` does table/column DDL, `spa_actions.php` does `spa_*` config CRUD + generic per-record ops; admin/role/partner CRUD is NOT here, it's in `auth/admins.php` |

---

## Auth & Developer Tools

| Module | Spec | Description |
|---|---|---|
| auth | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/auth/module.spec.md) | Login, session-based RBAC, operator profile, and admin/role/partner account CRUD (`admins.php`); notifies `sc-saas-backend` on new-admin creation |
| developer | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/developer/module.spec.md) | Platform config tools — API route registry, email/settings/menu/form-field/form-layout/table-view management, per-tenant data export; gated by `is_dev` or hardcoded `super_admin`/`developer` role-code checks (inconsistent per file) |

---

## AI Credits

| Module | Spec | Description |
|---|---|---|
| ai_credits | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/ai_credits/module.spec.md) | Operator screens for the AI Credits commercial catalogue — packages, per-task rates, one-off tenant grants, cross-tenant read-only orders view; one of three independent, non-validated writers to the shared `ai_credit_*` tables (with `sanchiconnect-saas-tenants` NestJS and `sc-saas-admin`) |

---

## Finance

| Module | Spec | Description |
|---|---|---|
| finance_management | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/finance_management/module.spec.md) | The **platform's own billing of tenants** for AI Credits purchases — GST/VAT tax profiles, invoice supplier settings, read-only invoice register against `ai_credit_orders`; not a port of `sc-saas-admin`'s member-facing `finance_management` (no shared code, tables, or contract) |

---

## File & Data Utilities

| Module | Spec | Description |
|---|---|---|
| aws | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/aws/module.spec.md) | Two-file raw S3 bucket manager ("Files Storage" screen); same `$s3`/`$s3Client` undefined-variable bug in `create_folder` as the sibling `sc-saas-admin` module; `ajax.php` has no `checkLoggedIn()`, CSRF-only gate |
| filemanager | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/filemanager/module.spec.md) | Local-disk file browser (`list.php`/`ajax.php`/`download.php`) over the admin server's own filesystem; page itself is broken (missing template) but `ajax.php`/`download.php` remain independently reachable with no path sanitization |
| csv | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/csv/module.spec.md) | Generic table-driven CSV export/import for the dynamic CRUD engine — any table, by name, with no allow-list; `export.php`/`import.php` have no login check and no CSRF check at all |
| upload | [module.spec.md](../sanchiconnect-saas-tenants-admin/modules/upload/module.spec.md) | Single TinyMCE rich-text image-upload endpoint; least risky of the file/data modules — the only one that gates on login and validates both filename and extension before writing to disk |

---

## Security findings

| Severity | Module | Finding |
|---|---|---|
| 🔴 Critical | csv | `export.php`/`import.php` have **no `checkLoggedIn()` and no CSRF check at all** — worse than every other unauthenticated-endpoint finding in this repo, since there isn't even a "obtain a token first" step. Any anonymous caller can `GET csv/export?table:spa_admin_users` (bcrypt hashes) or `table:tenant_users` (potential per-tenant DB credentials), or `POST csv/import` a crafted row into any table on the shared platform DB. Tracked as **Linear SAN-42** (Urgent, unfixed). |
| 🔴 Critical | filemanager | `ajax.php` (`remove`/`rename`/`upload`) and `download.php` are reachable with no `checkLoggedIn()` and, for `download.php`, **no CSRF check either** — the `cleanPath()` sanitizer exists in `core/filemanager.php` but is never invoked anywhere. An unauthenticated caller can read, delete, or overwrite any file the web server process can access. Same class of bug as `sc-saas-admin`'s SAN-31. Tracked as **Linear SAN-43** (Urgent, unfixed). |
| 🟠 High | aws | `ajax.php` has no `checkLoggedIn()`; only gate is a CSRF token that any anonymous visitor can mint via one prior `GET`. `delete_object` has no `storage_domain`-prefix check (can delete any key in the shared bucket); `create_object` has no file-type/size validation. Same class of bug as `sc-saas-admin`'s SAN-22. Tracked as **Linear SAN-46** (High, unfixed). |
| 🟠 High | ajax | `crud_actions.php`/`spa_actions.php`/`api_actions.php`/`email_actions.php` skip `checkLoggedIn()` entirely (only `fields_mapping.php` calls it) — the same anonymous-CSRF-token gap as `aws/ajax.php`, but here the reachable actions include generic CRUD/DDL over arbitrary tables (`crud_management`) and `delete_record`/`change_boolean_status` on any non-`spa_` business table. |
| 🟡 Medium | ai_credits | "Cost multiplier" `rate_mode` is fully selectable and persisted in `task_rates.php`, but every reserve/settle call site in `sc-saas-admin`'s `ai_credits_functions.php` computes charge as `credits_per_unit × applicant_count` unconditionally — the mode is a no-op today. Team-confirmed as intentional Phase 2 work-ahead-of-backend, not dead code. Tracked as **Linear SAN-21**. |
| 🟡 Medium | ajax | `rename_table` cascades updates across 7 `spa_*` config tables plus the `users_table_name` setting; Medoo's error mode is silent, so a partial failure mid-cascade leaves config inconsistent while still reporting success. `drop_table` performs no equivalent cleanup, leaving orphaned `spa_*` rows pointing at a dropped table. |
| 🟡 Medium | ajax | SMTP passwords in `spa_email_settings` are stored unencrypted (unlike `spa_settings`, which supports optional AES-256-CBC) — a DB compromise exposes SMTP credentials in plaintext. |
| 🟡 Medium | auth | Profile password change does not verify the current password before allowing a change; login has no session regeneration (session fixation risk) and its CSRF check is commented out. |
| 🟡 Medium | ai_credits / finance_management | The identical five-file role-gate block is copy-pasted rather than factored into a shared helper in both modules — a future role-model change means editing up to 10 files across the two. |
| 🟡 Medium | Adminer (repo root, not a `modules/` dir) | `getDeveloperMenus()`'s "DB Administration" link embeds the live, plaintext `.env` DB password as a URL query parameter to the bundled Adminer console, which sits entirely outside `index.php`'s routing/auth (documented in this repo's `CLAUDE.md`, not a module spec finding). |

Updated: 2026-07-20
