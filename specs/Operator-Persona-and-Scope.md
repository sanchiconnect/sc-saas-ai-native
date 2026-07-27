# SanchiSaaS — Operator Persona & Scope (Draft)

**Document Type:** Persona / Access-Scope Definition (companion to `Business-Perspective-Major-Modules.md` and `Product-Vision-Business-Objectives.md`)
**Status:** DRAFT — the role/permission facts below are directly confirmed from source code; the persona narrative (who this person is, what they're responsible for day-to-day) is a reasonable synthesis of those facts, not confirmed by an actual operator
**Date:** 2026-07-17
**Origin:** Closes external gaps-register item **P-4** ("Operator persona undocumented")

---

## Who this document is about

**"The operator"** is Sanchi's own platform staff — the people who run `sanchiconnect-saas-tenants-admin` (the tenants control-plane admin panel) to operate the SaaS business itself. This is a **different persona** from any tenant's own staff (a "Program Office Member," already defined in `specs/DDD-SanchiSaaS-Client.md` §4.2, who manages one tenant's own programs from inside that tenant's deployment). The operator sits above all tenants, not inside one.

---

## The 7 confirmed roles

`sanchiconnect-saas-tenants-admin/config/config.php` defines 7 role-ID constants, sourced from ENV, matched at login against `spa_admin_roles.code`:

| Role | Confirmed scope (from code) |
|---|---|
| `super_admin` | Full platform-operator access — see below |
| `developer` | Full platform-operator access, alongside `super_admin` — see below |
| `reviewer` | **Confirmed 2026-07-27: zero code-level gate.** `reviewer_role_id` (`config.php:121-123`) is referenced nowhere else in the codebase — no page, button, or data filter checks it. |
| `recruitment_partner` | **Confirmed 2026-07-27: cosmetic only.** `recruitmentpartner_role_id` is checked in exactly one place, `themes/default/html/auth/profile.php:3` — a `switch` on session role code that swaps in a different header partial (`header-partner.php`) on the Update Profile page. No permission implication. |
| `jury` | **Confirmed 2026-07-27: cosmetic + assignee-lookup only, no access gate.** `jury_role_id` is referenced in `themes/default/html/auth/profile.php:6` (same cosmetic header-partial swap, `header-cxo.php`) and in `modules/add.php:361-373`/`edit.php:367-379` (a data-population helper: looks up which `spa_admin_users` rows have the jury role, to populate a "jury members" assignee dropdown on whatever business table has that relationship field — does not restrict who can access that table). |
| `program_manager` | **Confirmed 2026-07-27: assignee-lookup only, no access gate.** `program_manager_role_id` is referenced only in `modules/add.php:347-359`/`edit.php:353-365` — the same assignee-dropdown helper pattern as `jury`, keyed on a `program_managers` relationship field. |
| `analyst` | **Confirmed 2026-07-27: zero code-level gate.** `analyst_role_id` (`config.php:136-138`) is referenced nowhere else in the codebase, exactly like `reviewer`. |

Only the first two — **`super_admin`** and **`developer`** — are confirmed, by direct code read, to be the operator this gap describes: the one who manages tenants, entitlements, and the credit catalogue.

## Confirmed scope: what "the operator" can do

**AI-Credits catalogue (packages, task rates, grants, orders) — hardcoded, not configurable:**
Every one of the four `modules/ai_credits/{packages,grants,task_rates,orders}.php` pages carries the identical gate:
```php
if ($_SESSION['admin_roles']['code'] == super_admin_role_id || $_SESSION['admin_roles']['code'] == developer_role_id) {
} else {
    header("Location:" . _admin_url . "/403");
}
```
This is a direct role-ID check, not a configurable permission flag — **only Super Admin and Developer can ever manage the AI-credit catalogue**, regardless of how any other role's permission flags are configured.

**Tenant & entitlement management (`tenant_users`, `organizations`) — configurable, not hardcoded:**
These tables are managed through the generic dynamic CRUD engine (`modules/add.php`/`edit.php`/`table.php`), which has **no table-specific role check at all** — only two blanket capability flags:
```php
// add.php
if (!checkRole("can_create")) { ... }
// edit.php
if (!checkRole("can_edit")) { ... }
```
`checkRole()` reads a named boolean column off the operator's own `spa_admin_roles` row (`$_SESSION['admin_roles'][$role]`). **Whichever role has `can_create`/`can_edit` set to `1` can create/edit any table reachable through this engine — including `tenant_users` and `organizations`, the two most sensitive tables in the platform.** `[NOT SPECIFIED IN SOURCE]`: whether `can_create`/`can_edit` are actually restricted to `super_admin`/`developer` in practice is a **live database fact** (the actual values in the `spa_admin_roles` table), not something the code itself constrains — a `reviewer` or `analyst` role *could* be granted these flags without any code change.

**Developer Zone (`is_dev` flag):** gates settings management, API management, email/DB management, the tenant-onboarding tooling, and other developer-only pages (`modules/developer/*`) — again a configurable flag, not hardcoded to a specific role ID.

## Confirmed scope: the other 5 roles (traced 2026-07-27, closing SAN-64)

None of `reviewer`, `recruitment_partner`, `jury`, `program_manager`, or `analyst` has a distinct code-level permission gate anywhere in the codebase — not a page, a button, or a data filter. Their only code footprint:

- **Cosmetic header swap:** `recruitment_partner` and `jury` each trigger a different header partial on the Update Profile page (`themes/default/html/auth/profile.php:3,6`) — visual only, no access implication.
- **Assignee-dropdown helpers:** `jury` and `program_manager` are looked up by the dynamic CRUD engine (`modules/add.php`, `modules/edit.php`) purely to populate "which admin users hold this role" dropdowns, when a business table happens to have a `jury_members` or `program_managers` relationship field — this assigns *who a record points to*, it does not gate *who can access* anything.
- **`reviewer` and `analyst`** have no code reference at all beyond their own `define()` in `config.php`.

The reason no hardcoded gate exists for any of the 5: this admin panel's entire access-control model is the small set of blanket capability flags described above (`can_create`, `can_edit`, `can_view`, `can_delete`, `is_dev`, plus JSON-encoded per-menu/per-table/per-feature overrides), read via `checkRole()`/`checkFeaturesAccess()`/`checkTableAccess()` off whatever values an operator sets on that specific role's `spa_admin_roles` row through the live "Add/Edit Role" UI (`modules/auth/admins.php`, itself gated to `super_admin`/`developer` only). There is no code-level default and no seed/migration data for any role's permission columns — confirmed no `.sql`, seed, or install script exists anywhere in the repo that sets `can_create`/`can_edit`/etc. for any role, including these 5. **The mechanism is identical for `reviewer`/`recruitment_partner`/`jury`/`program_manager`/`analyst` as it is for `super_admin`/`developer`** (aside from the two hardcoded ID-equality gates — AI-credits catalogue pages and the role-management module itself — which check specifically for `super_admin`/`developer` and exclude all 5 of these roles by construction). In practice, this means: **these 5 roles are exactly as powerful or as limited as whatever an operator configures for them in `spa_admin_roles` today** — there is no code-enforced ceiling narrower than the same `can_create`/`can_edit`/`is_dev` flags every other role uses, and (per Open Question 2 below) confirming their actual configured values requires reading the live database, not the code.

One loose end, not a gap this issue needs to close: `spa_admin_users` has `partner_id` and `is_jury_reviewer` columns that look purpose-built for recruitment-partner/jury bookkeeping, but no form field in this repo's admin-user add/edit UI ever sets them — they appear either vestigial or populated out-of-band (e.g. directly in the database, or by a process outside this repo).

## The permission model's actual shape

There is **no per-resource or per-table ACL system** in this admin panel. Access control is a small number of blanket capability flags (`can_create`, `can_edit`, `is_dev`, plus narrower feature-specific ones like `can_broadcast_messages`, found earlier this session for the outreach-communications module) layered on top of a handful of named roles. This means:
- The **credit catalogue** has a tight, hardcoded, two-role allowlist (`super_admin`/`developer` only) — a real security boundary.
- **Tenant and entitlement management** has no equivalent hardcoded boundary — its actual real-world restriction depends entirely on how `spa_admin_roles` rows are configured today, which is DB data this pass could not read.

## Persona narrative (synthesis, not confirmed)

**Who they are:** A Sanchi platform-operations staff member (Super Admin or Developer role), not affiliated with any single tenant, responsible for provisioning and running the multi-tenant SaaS business itself.

**What they do day-to-day (inferred from available modules):** onboard new tenant organizations, configure/adjust tenant feature flags and settings, manage the AI-credit commercial catalogue (packages, task rates, promotional grants), review AI-credit purchase orders, and use Developer Zone tooling (settings, API management, data export) for operational/support tasks.

**What they are not:** they are not a tenant's own program staff. The platform's other 5 roles (reviewer, recruitment_partner, jury, program_manager, analyst) are **not narrower workflow-specific personas with their own gated scope** — traced 2026-07-27 (see above), they carry no distinct code-level permission at all beyond cosmetic header swaps and assignee-dropdown lookups. Whatever scope any of them actually has today is entirely a live `spa_admin_roles` configuration fact, not something the codebase defines or constrains.

---

## Open Questions for the Product Owner / Platform-Ops Lead

1. Is "Super Admin + Developer = the operator" the intended, permanent design, or should a narrower dedicated "Platform Operator" role exist, distinct from "Developer" (which reads more like an engineering-access role than a business-operations one)?
2. **Still open — requires live database access, not resolvable from code.** Are `can_create`/`can_edit` actually restricted to `super_admin`/`developer` today in the live `spa_admin_roles` table, or can the 5 traced-but-unrestricted roles (reviewer, recruitment_partner, jury, program_manager, analyst) also create/edit `tenant_users`/`organizations`? Given the confirmed finding above — that these 5 roles use the exact same `can_create`/`can_edit` mechanism as `super_admin`/`developer`, with no code-level ceiling — this is now the single most important remaining unknown: whichever role has these flags set to `1` in the live table can touch the two most sensitive tables in the platform, and only reading the actual database resolves whether that's `super_admin`/`developer` only or something broader.
3. ~~What are the actual scopes of the other 5 roles?~~ **Resolved 2026-07-27** — see "Confirmed scope: the other 5 roles" above. None has a distinct code-level gate; whatever real-world scope they have is entirely live-database configuration.
4. Should the credit-catalogue's hardcoded two-role gate be the model applied to tenant/entitlement management too, given how sensitive those tables are?

---

## Change Log

- 2026-07-17 | Initial draft, closing external gaps-register item P-4. Role/permission facts confirmed directly from `sanchiconnect-saas-tenants-admin`'s `config/config.php` and the four `ai_credits/*.php` handlers' identical role-ID gate. Persona narrative is a reasonable synthesis, not confirmed. Explicitly flagged what remains DB-data-dependent (actual flag assignments) rather than guessing.
- 2026-07-27 | Traced all 5 previously-unspecified roles (reviewer, recruitment_partner, jury, program_manager, analyst) against the actual codebase, closing Linear SAN-64. Confirmed: none has a distinct code-level permission gate — only cosmetic header-partial swaps (recruitment_partner, jury) and assignee-dropdown lookups (jury, program_manager); reviewer/analyst have zero code references beyond their own `define()`. Confirmed no seed/migration data sets any role's `can_create`/`can_edit`/etc. defaults — entirely live-operator-configured via `modules/auth/admins.php`. Open Question 2 (the live-database `can_create`/`can_edit` check) remains genuinely open — this pass had no database access and could not resolve it; it is now understood to be higher-stakes than previously framed, since these 5 roles share the exact same unrestricted mechanism `super_admin`/`developer` use.
