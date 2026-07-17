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
| `reviewer` | `[NOT SPECIFIED IN SOURCE — no distinct hardcoded gate found in this pass]` — likely scoped to an application/content review workflow, not verified here |
| `recruitment_partner` | `[NOT SPECIFIED IN SOURCE]` — likely scoped to partner-recruitment workflows, not verified here |
| `jury` | `[NOT SPECIFIED IN SOURCE]` — likely scoped to an evaluation/jury workflow, not verified here |
| `program_manager` | `[NOT SPECIFIED IN SOURCE]` — likely scoped to program-oversight workflows, not verified here |
| `analyst` | `[NOT SPECIFIED IN SOURCE]` — likely scoped to reporting/analytics access, not verified here |

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

## The permission model's actual shape

There is **no per-resource or per-table ACL system** in this admin panel. Access control is a small number of blanket capability flags (`can_create`, `can_edit`, `is_dev`, plus narrower feature-specific ones like `can_broadcast_messages`, found earlier this session for the outreach-communications module) layered on top of a handful of named roles. This means:
- The **credit catalogue** has a tight, hardcoded, two-role allowlist (`super_admin`/`developer` only) — a real security boundary.
- **Tenant and entitlement management** has no equivalent hardcoded boundary — its actual real-world restriction depends entirely on how `spa_admin_roles` rows are configured today, which is DB data this pass could not read.

## Persona narrative (synthesis, not confirmed)

**Who they are:** A Sanchi platform-operations staff member (Super Admin or Developer role), not affiliated with any single tenant, responsible for provisioning and running the multi-tenant SaaS business itself.

**What they do day-to-day (inferred from available modules):** onboard new tenant organizations, configure/adjust tenant feature flags and settings, manage the AI-credit commercial catalogue (packages, task rates, promotional grants), review AI-credit purchase orders, and use Developer Zone tooling (settings, API management, data export) for operational/support tasks.

**What they are not:** they are not a tenant's own program staff, and (per the confirmed scope above) most of the platform's other 5 roles (reviewer, recruitment_partner, jury, program_manager, analyst) appear to be narrower, workflow-specific personas rather than platform operators — though their exact scopes were not traced in this pass.

---

## Open Questions for the Product Owner / Platform-Ops Lead

1. Is "Super Admin + Developer = the operator" the intended, permanent design, or should a narrower dedicated "Platform Operator" role exist, distinct from "Developer" (which reads more like an engineering-access role than a business-operations one)?
2. Are `can_create`/`can_edit` actually restricted to `super_admin`/`developer` today in the live `spa_admin_roles` table, or can other roles (reviewer, analyst, etc.) also create/edit `tenant_users`/`organizations`? This is a real, checkable fact this document could not confirm without database access.
3. What are the actual scopes of the other 5 roles (reviewer, recruitment_partner, jury, program_manager, analyst)? Not traced in this pass — would need a dedicated follow-up read of their gated modules.
4. Should the credit-catalogue's hardcoded two-role gate be the model applied to tenant/entitlement management too, given how sensitive those tables are?

---

## Change Log

- 2026-07-17 | Initial draft, closing external gaps-register item P-4. Role/permission facts confirmed directly from `sanchiconnect-saas-tenants-admin`'s `config/config.php` and the four `ai_credits/*.php` handlers' identical role-ID gate. Persona narrative is a reasonable synthesis, not confirmed. Explicitly flagged what remains DB-data-dependent (actual flag assignments) rather than guessing.
