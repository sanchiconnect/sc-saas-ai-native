---
id: SAN-363
title: Tenant Management Module (List, Create, Edit, Detail & SQL Script Runner)
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/project/tenant-management-module-14ad556cf9ef
owner: nirmal.s@sanchiconnect.com
repos: [sanchiconnect-saas-tenants-admin]
contracts:
  api: ["PATCH api/v1/public/global/saas/settings"]   # existing sc-saas-backend endpoint, reused (not changed) — new Edit screen now fires resetAPISaaSSettings() too, resolved 2026-08-18
  flags: []                       # no flag ADDED/RENAMED/REMOVED — this feature only displays/edits existing TenantUsersEntity boolean columns through a new UI; the flag-name contract itself (invariant #1) is untouched
  events: []
tenant_scoped: true
depends_on: []
created: 2026-08-18
---

# Tenant Management Module (List, Create, Edit, Detail & SQL Script Runner)

Source: stakeholder BRD "Tenant Management — New Self-Contained Module" (rev.6, 2026-07-21), transcribed at
`/private/tmp/claude-501/-Users-mac-Desktop-Work-SanchiSaaS/4ed2ef57-e497-44f9-9b32-305b3d2b4182/scratchpad/tenant-onboarding-brd.md`.
This spec does not originate from a pre-existing Linear issue — Linear tracking (project + issue) was created fresh as part of authoring this spec.

## Problem

Onboarding a new tenant today means opening the admin panel's generic, all-purpose `add`/`edit` dynamic-table
form pointed at `tenant_users` and filling roughly 300 columns from scratch, including ~220 boolean feature
switches shown in raw column order with no grouping or search
[Evidenced: `tenant_users` entity has 311 `@Column` decorators, 222 of them `type: 'boolean'` —
`sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts`, confirmed by direct count;
BRD's "~307 fields" / "~218 switches" are reasonable roundings of these real numbers]. There is no way to
start from a known-good configuration, no Subscription row is ever created as part of onboarding
[Evidenced: `subscriptions.tenant_id`/`organization_id` are both `nullable: false`
(`sanchiconnect-saas-tenants/src/modules/subscriptions/entities/subscription.entity.ts`) — nothing in this
repo's generic `add.php` flow inserts a linked `subscriptions` row when a `tenant_users` row is created], and
there is no safeguard against a copy-pasted domain/database configuration colliding with another tenant's
live database [Evidenced: no domain/db-name uniqueness check exists anywhere in this repo's generic engine or
in `modules/ai_credits/grants.php`'s domain lookup, which validates *against* existing domains for a different
purpose (crediting), not duplicate-prevention on save].

Separately, once a tenant is created its own database is empty — schema/seed `.sql` files are run by hand
today through an external MySQL client, entirely outside the admin panel and with no audit trail.

## Acceptance criteria

- [x] A new "Tenant Management" sidebar section appears for `super_admin`/`developer` operators, with "All
      Tenants" and "Create Tenant" links, added by a one-time, idempotent menu-setup step that makes no
      changes on a second run.
- [x] All Tenants (List) is searchable by name/domain, filterable by Active/Inactive, sortable, and paginated;
      row actions link to the right Edit/Detail pages.
- [x] Every tenant saved via Create has a newly created `organizations` row, linked by its real `id` — Create
      never reuses or requires picking an existing organization.
- [x] "Clone Latest Tenant" pre-fills every one of the ~218 feature switches from the most recently created
      tenant, while identity/provisioning fields (name, domain, database host/name/user/password) and `active`
      are left blank/off rather than copied.
- [x] All feature switches appear grouped into named, collapsible sections with a live, client-side search box,
      identically on Create and Edit, with none missing from any group.
- [x] Every tenant saved via Create also has a newly created `subscriptions` row (`organization_id` +
      `tenant_id` both populated), defaulting to a 1-year term (`start_date` = today, `end_date` = +1 year),
      fully editable before Save.
- [x] Organization + Tenant + Subscription creation happens inside one Medoo transaction — a failure at any
      step rolls back everything created earlier in the same request.
- [x] Attempting to save (Create or Edit) with a `domain`, `admin_domain`, or `database_name` already used by
      another `tenant_users` row is blocked with a clear error and nothing is written.
- [x] Editing an existing tenant loads its real current values (identity, provisioning, all switches) with
      nothing blanked, and Save updates that same row in place — no clone side effects.
- [x] Detail shows read-only Tenant Identity (with `database_password` always masked, never rendered in
      plain text), Organization, Subscription, and a grouped feature-switch summary with per-section
      "N / total on" counts.
- [x] The Detail page's SQL Script Runner accepts only a `.sql` file upload (no freeform query textarea),
      executes it against exactly the one tenant's own database (host/name/user/password read from that
      tenant's `tenant_users` row), and can never target a different tenant's database from the same action.
- [x] ~~Every SQL Script Runner run — success or failure — creates one audit-log row recording operator,
      tenant, timestamp, filename, statement count, and result (including the failing statement number on
      failure).~~ **Removed 2026-08-18 at explicit user direction** — see Implementation notes. Success/
      failure is still reported to the operator via a flash message; nothing is persisted.
- [x] The SQL Script Runner action is gated by the same `super_admin_role_id`/`developer_role_id` check used
      by the rest of this module, re-checked independently in the handler that actually executes the script
      (not solely relied on via menu visibility).
- [x] No existing admin-panel screen — including the generic `table`/`add`/`edit`/`detail` engine used by
      every other table (`organizations`/`subscriptions` included) — changes behavior as a result of this
      feature; `tenant_users`, `organizations`, and `subscriptions` remain reachable exactly as before through
      those generic screens too.

## Per-repo plan

### sanchiconnect-saas-tenants-admin

All new files live under `modules/tenant_management/` + `themes/default/html/tenant_management/`, following
the existing `ai_credits/`/`finance_management/` module layout
[Evidenced: `modules/ai_credits/{setup_menu,packages,task_rates,grants,orders}.php`,
`modules/finance_management/{setup_menu,taxes,invoices,invoice_settings,invoice_view}.php` — both are
real, independent, non-generic-engine modules with their own sidebar section, confirmed in
`modules/ai_credits/module.spec.md` and `modules/finance_management/module.spec.md`]. Nothing here touches
`modules/{add,edit,table,detail}.php` (the generic dynamic-table engine) or `spa_data_management`/
`spa_form_layouts` rows for `tenant_users`/`organizations`/`subscriptions` — those stay exactly as-is,
avoiding the confirmed "blank form" landmine (`themes/default/html/add.php` renders only configured sections
once a `spa_form_layouts` row exists, with no fallback for unassigned columns).

1. **`modules/tenant_management/setup_menu.php` (one-time menu seeder)**
   - Model directly on `modules/finance_management/setup_menu.php` (the more defensive of the two existing
     seeders — it probes `SHOW COLUMNS FROM spa_menu_management` before writing optional columns).
   - Insert a new sidebar parent (`title = "Tenant Management"`, `side = "sidebar"`, `is_parent = "1"`) plus
     two sub-menu rows ("All Tenants" → `tenant_management/list`, "Create Tenant" →
     `tenant_management/create`).
   - **Close the confirmed duplicate-menu gap** found in the existing pattern: `finance_management/setup_menu.php`'s
     idempotency check matches *only* on `title` + `side`
     [Evidenced: `modules/finance_management/module.spec.md:146-148` — "if an operator renames the seeded
     'Finance Management' parent menu, re-running `setup_menu.php` would insert a second parent menu tree
     rather than detecting the existing one"]. This module's seeder must check for the parent title **and**
     the presence of at least one of its known sub-menu `external_link` values (e.g.
     `tenant_management/list`) before deciding it's already been run, per this spec's own risk mitigation.
   - Role-gated identically to the two existing seeders (`super_admin_role_id`/`developer_role_id` check via
     `$_SESSION['admin_roles']['code']`, redirect to `/403` otherwise).

2. **`modules/tenant_management/list.php`**
   - Stat strip (Total/Active/Inactive — `$database->count("tenant_users", ...)` variants), search by
     `name`/`domain` (Medoo `[~]` LIKE per this repo's convention), Active/Inactive filter, paginated table
     (`LIMIT => [offset, per]`), "+ New Tenant" button, row View/Edit links to `tenant_management/detail/:id`
     and `tenant_management/edit/:id`.
   - Role-gated the same way as the module's other screens.

3. **`modules/tenant_management/create.php`**
   - "Clone Latest Tenant" — one `$database->get("tenant_users", "*", ["ORDER" => ["id" => "DESC"]])`-style
     fetch; pre-fill all 222 boolean switch fields from the clone source, force `active` off, leave identity/
     provisioning fields (`name`, `domain`, `admin_domain`, `database_host`, `database_name`, `database_user`,
     `database_password`) blank — matches this spec's clone-safety acceptance criterion.
   - Organization sub-form (Name*, Website, Official Email, Technical Email) — new `organizations` row,
     `name` is the only NOT NULL column on that table
     [Evidenced: `organizations.name` is `nullable: false`; every other column, including `website` and
     both email columns, is `nullable: true` —
     `sanchiconnect-saas-tenants/src/modules/organizations/entities/organizations.entity.ts`].
   - Tenant Identity & Provisioning fields, mapped 1:1 to the real `tenant_users` columns (`name`, `domain`,
     `database_host`, `database_name`, `database_user`, `database_password`, plus `organization_id` set from
     the just-created organization).
   - Subscription sub-form (Plan Name, Plan Users, Start Date default today, End Date default +1 year) — new
     `subscriptions` row; `organization_id` and `tenant_id` are both required
     (`nullable: false` on `subscriptions.organization_id`/`subscriptions.tenant_id`) and are only available
     after steps 1–2 complete, which is why creation order is Organization → Tenant → Subscription.
   - **Grouped/searchable switches** — render the 222 boolean columns via one shared PHP include (see item 6
     below) into ~21 collapsible sections with a client-side "N / total on" counter and a plain-text live
     filter (no page reload) — same UI behavior on Create and Edit.
   - **Duplicate-domain guard (new logic — confirmed no reusable existing check)**: before insert, check
     `domain`, `admin_domain`, and `database_name` against all existing `tenant_users` rows; block save with a
     clear message on any collision. This is new validation logic — nothing in `modules/ai_credits/grants.php`
     or the generic engine performs uniqueness checking on `tenant_users` today (that file's domain lookup
     validates *against* the existing list for a different purpose — crediting an existing tenant, not
     preventing a duplicate).
   - **Atomic creation**: wrap Organization insert → Tenant insert → Subscription insert in Medoo's
     transaction wrapper, `$database->action(function ($db) use (...) { ... return true/false; })`
     [Evidenced: this exact pattern is already used in this repo — `modules/ai_credits/grants.php:152`,
     `$txn_ok = $database->action(function ($db) use (...` — reuse it verbatim rather than inventing new
     transaction-handling code]. On success, redirect to `tenant_management/detail/:new_tenant_id`.

4. **`modules/tenant_management/edit.php`**
   - Same grouped/searchable switch rendering as Create (shared include, item 6), pre-filled with the real
     current `tenant_users` row values — plain load, no clone behavior, nothing blanked.
   - Banner noting Organization/Subscription aren't editable here (BRD's own non-goal) — those remain
     reachable via the existing generic engine at `table/organizations` (labeled "Clients" in the sidebar via
     `modules/common.php:14-21`'s `$customTableHeadersTitles`) and `table/subscriptions`
     [Evidenced: `subscriptions` is already a live, generic-engine-reachable table today —
     `modules/common.php:27-31`'s `$customHeaderNames["subscriptions"]["suspend_date"] = "Suspension Date"`
     is a real header override applied to that table's existing generic list/detail views, confirming this
     BRD non-goal claim rather than assuming it].
   - Same duplicate-domain/admin-domain/database-name guard as Create, excluding the record's own current
     row from the collision check.
   - **Resolved 2026-08-18 (dev lead):** calls `resetAPISaaSSettings($tenant['api_url'])`
     (`includes/core_functions.php`) after a successful save, whenever an `api_url`-relevant field changed —
     matching the *generic* `modules/edit.php`'s existing unconditional behavior for `tenant_users` edits, so
     an `api_url` change made through either edit path reaches that tenant's live `sc-saas-backend` deployment
     the same way. This is the one place this feature makes an outbound call to another repo; it reuses the
     existing endpoint verbatim (no new/changed contract — invariant #2 is satisfied by non-modification).

5. **`modules/tenant_management/detail.php`**
   - Read-only cards: Tenant Identity (`domain`, `database_name`, `database_host`, `database_password` —
     always masked, e.g. `••••••••`, never echoed in plain text or into any HTML attribute/JS variable),
     Organization (name/website/official email via the linked `organizations` row), Subscription (plan/
     status/expiry via the linked `subscriptions` row), and a read-only render of the same shared
     section-grouping include used by Create/Edit, but as progress bars ("Call for Applications 18/24") with
     no edit controls.
   - **SQL Script Runner** (new capability):
     - Upload-only `.sql` file input (drag-and-drop or click-to-browse), same `$_FILES[...]["tmp_name"]`
       server-side read pattern already used for file ingestion in this repo
       [Evidenced: `modules/csv/import.php:29-31` reads an uploaded file server-side via
       `$_FILES["fileToUpload"]["tmp_name"]` — the closest existing precedent for "upload a file, read it,
       process its contents" in this codebase; the SQL Script Runner should follow the same shape rather than
       inventing a new upload-handling pattern] — no freeform SQL textarea anywhere in the UI.
     - **Connection reuse (critical safety property)**: open a Medoo connection using *that one tenant's own*
       `tenant_users.database_host`/`database_name`/`database_user`/`database_password` values — the exact
       per-tenant-connection construction already used today for read-only cross-tenant reporting
       [Evidenced: `modules/scrapper.php:9-17` — `new Medoo(["database_type" => "mysql", "database_name" =>
       $setting["database_name"], "server" => $setting["database_host"], "username" => $setting["database_user"],
       "password" => $setting["database_password"], ...])` inside a loop over every active `tenant_users` row].
       The Script Runner must scope this to exactly the one tenant whose Detail page it was launched from —
       never loop over all tenants the way `scrapper.php` does.
     - Split the uploaded file into individual statements and execute each via the tenant connection's
       `->query()` (DDL intentionally allowed, per BRD — this is for schema/seed setup against a brand-new,
       typically-empty tenant database); stop and report the failing statement number on the first error.
     - **Role gate, re-checked independently on the executing action** — not just on the page that renders
       the upload form — using the same `super_admin_role_id`/`developer_role_id` check as every other screen
       in this module (`checkAdminRole()`/`$_SESSION['admin_roles']['code']` pattern, e.g.
       `modules/ai_credits/setup_menu.php:11`). This directly closes the gap this spec's security framing is
       built on: **this exact repo already has a live, unauthenticated, unrestricted arbitrary-SQL-execution
       action** — `modules/ajax/crud_actions.php`'s `sql_query` case
       (`$sql = $database->query($_POST['sql'])->fetchAll();`, line 238), gated by nothing but
       `verifyCSRFToken()` (token-equality-with-current-session, not a login check)
       [Evidenced: `modules/ajax/crud_actions.php:233-238`; confirmed further by
       `modules/ajax/module.spec.md`'s "This file has no `checkLoggedIn()` and no `checkRole()` call anywhere"
       and this repo's own `CLAUDE.md` "Most AJAX endpoints skip the login check entirely" section]. The new
       Script Runner must not repeat this: `checkLoggedIn()` + role check on both the upload page and the
       execute handler, CSRF-protected, one tenant only.
     - CSRF-protected via `verifyCSRFToken()` (same as every other mutating action in this admin panel).
     - **No audit-log table.** An earlier revision of this spec called for a new `spa_tenant_sql_script_runs`
       table (operator, tenant, filename, statement count, result, failing statement number) — **removed
       2026-08-18 at explicit user direction** ("no need of this"). Success/failure is now reported to the
       operator only once, as a flash message on redirect back to Detail; nothing about who ran what against
       which tenant's database is persisted anywhere. This trades away the audit-trail advantage this
       feature's own security framing originally claimed over `crud_actions.php`'s unauthenticated `sql_query`
       action (see the invariant #5 note below) — the remaining safety property is purely the independent
       role gate on the execute handler, not a record of what happened.

6. **`modules/tenant_management/_switch_sections.php` (shared include, new)**
   - One PHP array bucketing all 222 boolean `tenant_users` columns into named sections by keyword/prefix
     (e.g. columns visibly prefixed/related to call-for-applications, facility management, events, partners,
     startups, mentors, etc., per the entity's own enum imports —
     `FacilityModuleType`, `MeetingTimeSlotsInMin`, `ChatTypes`, etc. in
     `tenant-users.entity.ts` hint at natural groupings). `require`d identically by `create.php`, `edit.php`,
     and `detail.php`'s read-only summary so there is exactly one grouping definition, computed fresh on every
     page load (no cached copy to go stale). The **exact section names and per-switch membership are new
     product content with no code precedent** — build a first-pass grouping from column-name prefixes/
     enum-import hints during implementation; per this spec's own risk framing this is a plain, easily-edited
     list, so an imperfect first pass is a one-line fix, not a blocking design decision.

## Contracts & invariants

- **Flags:** none added, renamed, or removed. This feature reads/writes the *existing* `tenant_users` boolean
  columns that `sanchiconnect-saas-tenants` (NestJS) already owns as the flag-name contract (invariant #1) —
  it only changes how they're presented and edited inside this one admin panel. No propagation to backend
  `Feature` enum, frontend `IFeatures`, or `sc-saas-admin`'s `config.php` constants is required, because no
  flag name changes.
- **API:** `PATCH api/v1/public/global/saas/settings` on `sc-saas-backend`, called via the existing
  `resetAPISaaSSettings()` helper — reused verbatim, not modified. New Edit screen fires it whenever an
  `api_url`-relevant field changes, matching the existing generic edit path's behavior (resolved 2026-08-18).
  No DTO/controller change on the backend side, so invariant #2 is satisfied by non-modification, not by
  isolation.
- **Events:** none.
- **Invariants at risk:**
  - **#5 Tenant scoping** — the primary invariant this feature touches. Judgement: **safe by construction**
    for the SQL Script Runner and Detail's per-tenant connection, because (a) the tenant DB connection is
    built from exactly one `tenant_users` row's own stored credentials, read fresh on each request, with no
    tenant-selection parameter anywhere in the request that could be tampered to target a different tenant's
    database — mirroring (and narrowing, from all-tenants-in-a-loop to exactly-one-tenant) the existing
    `scrapper.php` pattern; (b) Create/Edit's new writes to `tenant_users`/`organizations`/`subscriptions` go
    through the same single shared-DB Medoo connection every other screen in this repo already uses — no new
    connection-selection logic is introduced there. The genuine risk is not cross-tenant leakage but
    **privilege escalation into the SQL Script Runner** given this exact codebase family's confirmed
    unauthenticated `sql_query` action (`modules/ajax/crud_actions.php:238`) — mitigated by the independent
    role re-check on the execute handler specified above. Note: since the audit-log table was removed
    2026-08-18, this mitigation now rests solely on the role gate, not on any after-the-fact accountability
    trail — accepted as a deliberate trade-off, not an oversight.
  - **#1 Flag names**, **#2 API contract**, **#3 tenant-verification contract**, **#4 auth model**, **#6
    PowerPitch contract** — not touched. Single-repo, additive-only feature; no other SanchiSaaS repo needs
    review.

## Implementation notes (2026-08-18)

All files in the per-repo plan below have been written and self-verified. Left as uncommitted
working-tree changes per explicit instruction — not yet committed/pushed, and the staging manual
smoke test in the Test plan below has **not** been run yet (requires a staging tenants DB + staging
`sc-saas-backend`, which this pass didn't have access to). Do not treat this feature as done until
that manual pass actually happens.

- **Gates run:**
  - `php -l` — clean on all 14 new files (7 controllers/includes under `modules/tenant_management/`,
    6 templates under `themes/default/html/tenant_management/`, 1 `.sql` DDL file).
  - Tenant-isolation review (invariant #5) — confirmed the SQL Script Runner's per-tenant connection
    (`sql_script_execute.php`) is built from exactly one `tenant_users` row resolved server-side from
    the `:id` route segment, with no other request field able to influence which tenant's credentials
    are used, and that it never loops over tenants; confirmed Create/Edit/List/Detail only ever use
    the single shared admin-DB `$database` connection (`grep -n "new Medoo" modules/tenant_management/*.php`
    matches exactly one file, `sql_script_execute.php`).
  - API-contract review (invariant #2, the one outbound call) — confirmed the new Edit screen calls
    `resetAPISaaSSettings($t_api_url)` — same helper, same `PATCH api/v1/public/global/saas/settings`
    call shape as the generic `modules/edit.php`'s existing unconditional call — only conditioned on
    `api_url` actually having changed (per the 2026-08-18 dev-lead resolution), not a new/changed
    contract.
- **Audit-log table removed 2026-08-18, at explicit user direction** ("remove this
  spa_tenant_sql_script_runs, no need of this" → clarified as "remove audit logging entirely," not just
  the standalone migration artifact). This reverses a core piece of the original design: the
  `spa_tenant_sql_script_runs` table, its `CREATE TABLE IF NOT EXISTS` provisioning step in
  `setup_menu.php`, its insert in `sql_script_execute.php`, its read/display on `detail.php`, and the
  standalone `database/migrations/2026-08-18_create_spa_tenant_sql_script_runs.sql` DDL file were all
  deleted. The corresponding acceptance criterion above is struck through, not silently dropped. Net
  effect: the SQL Script Runner still reports success/failure to the operator (flash message on
  redirect), but no record of any run persists anywhere — the feature's remaining safety property against
  misuse is the independent role gate on `sql_script_execute.php` alone, not an audit trail. (This also
  moots the migration-convention question the original implementation pass had to work around — with no
  table to create, there's no DDL to place anywhere.)
- **Left as an explicit first-pass, flagged for follow-up (not a blocker per this spec's own risk
  framing):** `_switch_sections.php`'s 27 section names and per-switch membership are new product
  content with no code precedent. Verified programmatically at authoring time that all 221 non-`active`
  boolean `tenant_users` columns are covered exactly once (no column missing, none duplicated,
  `active` itself intentionally handled separately as an identity-level field, not a feature switch).
  Re-bucketing any single switch is a one-line array edit, not a migration.

## Test plan

- `sanchiconnect-saas-tenants-admin`: `php -l` on every new/changed file (no test suite exists in this repo).
  **`php -l` done, clean — see Implementation notes above.** Manual verification against a **staging copy
  of the tenants DB first** (never production first, per this repo's shared-DB risk with the NestJS app)
  — **not yet run, still pending**:
  - Menu setup step run twice → sidebar section appears once, second run reports "already exists, no
    changes" for both the parent-title check and the sub-link check.
  - List: search/filter/pagination/row-links.
  - Create: blank-form fallback with zero existing tenants; Clone Latest Tenant pre-fill + blanked identity/db
    fields; duplicate-domain save rejected; valid save creates Organization + Tenant + Subscription atomically
    and lands on the new Detail page; forced rollback test (e.g. temporarily break the Subscription insert) to
    confirm the whole transaction rolls back, not just the failing step.
  - Edit: real values load with nothing blanked; save updates in place; domain collision with another tenant
    rejected; own-current-domain does not false-positive as a collision; changing `api_url` fires
    `resetAPISaaSSettings()` against a staging `sc-saas-backend` (verify via that service's logs/response),
    while saving with `api_url` unchanged does not re-fire it unnecessarily.
  - Detail: correct data in all cards; `database_password` never appears in rendered HTML source, even
    masked-then-revealed via dev tools (i.e. don't send the real value to the client at all, not just CSS-mask
    it).
  - SQL Script Runner: valid `.sql` upload against a staging tenant executes only against that tenant's DB
    (verify by checking a marker table in a *second* staging tenant's DB is untouched); a non-authorized
    session (wrong role, or logged out) cannot reach the execute handler directly via POST, not just via the
    hidden menu link. (No audit-log verification — that requirement was removed 2026-08-18.)
  - Regression: confirm `table/organizations`, `table/subscriptions`, and the generic `table/tenant_users`
    (if any role still has access to it) render and behave exactly as before — zero shared-code changes to
    `modules/{add,edit,table,detail}.php`.
- Cross-repo: none required — single-repo feature. As a sanity check only (not a gate), confirm this feature
  does not alter any column TypeORM registers for `tenant_users`/`organizations`/`subscriptions` (schema-drift
  risk already flagged repo-wide in this repo's `CLAUDE.md`/`database.md` — this feature adds no new table or
  migration at all now that the audit-log table has been removed).

## Rollout

Single, independently-deployed repo — no cross-repo staging sequence needed. Suggested order:
1. Ship all new `modules/tenant_management/*` files + shared switch-grouping include, but do **not** run the
   menu-setup step yet (the module is unreachable from the sidebar until then — this is the natural
   "default-off" gate for a PHP admin panel with no feature-flag system of its own).
2. Run `tenant_management/setup_menu` once on staging, smoke-test the full flow (Test plan above).
3. Run `tenant_management/setup_menu` once on production after sign-off.
4. No backward-compatibility concerns for existing data — this feature adds no new table (audit logging was
   removed 2026-08-18) and does not alter `tenant_users`/`organizations`/`subscriptions` columns.

## Out of scope

- Any change to the existing generic `add`/`edit`/`table`/`detail` engine, or to `spa_data_management`/
  `spa_form_layouts` rows for `tenant_users`/`organizations`/`subscriptions`.
- A generic "list/create/edit any table" capability — this module is purpose-built for tenants only.
- Managing Organization or Subscription records from the new Edit screen — reachable via their own existing
  generic screens.
- Re-encrypting or otherwise changing the existing plaintext storage of `tenant_users.database_password`
  (separately tracked, pre-existing risk).
- A general-purpose, freeform SQL query console anywhere in this panel — the Script Runner is
  file-upload-and-execute only.
- Any change to the other six SanchiSaaS repos.
- Fixing the pre-existing unauthenticated `sql_query` action in `modules/ajax/crud_actions.php` — cited here
  only as security context/rationale for this feature's own design; fixing it is a separate, already-known,
  unfixed issue and not part of this feature's scope.
- **Audit logging for the SQL Script Runner** (added as a NEW-scope item originally, removed 2026-08-18 at
  explicit user direction). No table, no run history, no persisted record of who ran what against which
  tenant's database.

## Open questions

None outstanding. Both design decisions raised during authoring were resolved by the dev lead on 2026-08-18:
audit table uses a minimal fields-only schema (no uploaded-file-content storage), and the new Edit screen
fires `resetAPISaaSSettings()` on `api_url`-relevant changes, matching the existing generic edit path. See
the per-repo plan and Contracts sections above for the resolved detail.
