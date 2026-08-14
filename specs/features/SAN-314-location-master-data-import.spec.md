---
id: SAN-314                     # sc-saas-backend issue (ships first — admin's import logic depends on the new columns/tables existing). Admin counterpart: SAN-315. Project: see `linear:` below.
title: Unified Location Master Data Import System
type: feature
status: approved
linear: https://linear.app/sanchiconnect/project/unified-location-master-data-import-system-c06adee813ca
owner: nirmal.s@sanchiconnect.com
repos: [backend, admin]         # DEPENDENCY ORDER — backend ships schema (entities only) first, admin ships the actual import logic second
contracts:
  api: []                        # CORRECTED 2026-08-11 — no new REST surface. Admin does direct-Medoo fetch/validate/import against the tenant DB, exactly like the (now-removing) location_master.php pattern. Backend's only job is entity definitions so synchronize:true creates the schema.
  flags: []                     # no flag added, renamed, or removed
  events: []
tenant_scoped: true             # countries/states/cities/new districts/sub_districts all live in the single tenant DB this backend deployment/admin session is scoped to (see Background)
depends_on: []
created: 2026-08-11
---

# Unified Location Master Data Import System

## Evidence-tagging convention used throughout this spec
- **Evidenced** — cited to `file:line` in the real codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation, not directly stated.
- `[NOT SPECIFIED IN SOURCE]` — a real gap.
- `[DESIGN DECISION PENDING]` — a genuinely new decision with no precedent, routed to product/dev lead, never guessed.

## Linear tracking

- Project: [Unified Location Master Data Import System](https://linear.app/sanchiconnect/project/unified-location-master-data-import-system-c06adee813ca)
- [SAN-314](https://linear.app/sanchiconnect/issue/SAN-314) — sc-saas-backend (this spec's id; ships first)
- [SAN-315](https://linear.app/sanchiconnect/issue/SAN-315) — sc-saas-admin (ships second)

**SUPERSEDED 2026-08-14 (partial)**: every "unique-nullable index" reference to the `code` column below is
now stale — [SAN-341](https://linear.app/sanchiconnect/issue/SAN-341) dropped the uniqueness requirement
(`@Index({ unique: true })` → plain `@Index()`) on all five location entities, and
[SAN-342](https://linear.app/sanchiconnect/issue/SAN-342) removed the matching app-layer duplicate-`code`
rejection in `sc-saas-admin`'s `validateLocationMasterStructure()`. `code` may legitimately repeat across
rows both in the DB and within a single import batch. Everything else in this spec (schema shape, entity
names, direct-Medoo architecture, import pipeline) is unchanged.

## Correction (2026-08-11, before implementation) — architecture simplified

The first implementation attempt started building a backend REST API (`AdminActionsController` routes +
a `LocationMasterImportService`) for admin to call. **This was an unnecessary layer.** `sc-saas-admin`
already holds a direct Medoo connection to the exact same tenant DB `sc-saas-backend`'s TypeORM manages
(**Evidenced** — this is the identical pattern the now-removing `location_master.php` used against
`district_master`/`city_master`/`subdivision_master`, per `specs/features/SAN-312-location-master-removal.spec.md`
Background: "`location_master`... does direct-Medoo CRUD on three real, TypeORM-synced per-tenant
tables"). There is no reason to add a network hop through a new backend API when admin can read/write
the target tables directly, with a transactional Medoo closure — the same `$database->action(function($db)
{...})` pattern already used by `includes/startup_recognition_id_functions.php:100` and
`includes/ai_credits_functions.php:66,105,195,249` (**Evidenced**, confirmed by grep during this
correction).

**Corrected division of labor:**
- **`sc-saas-backend` (SAN-314) does only one thing: define the new entities/columns** so that
  `synchronize: true` creates the schema on deploy. No service, no controller route, no API surface at
  all for this feature.
- **`sc-saas-admin` (SAN-315) does everything else**: fetch the source URL (with its own SSRF-hardened
  cURL wrapper — PHP, not TypeScript), validate structure + relationships, build the preview, and run the
  transactional upsert — all directly against `$database` (Medoo), the same tenant DB connection every
  other admin module already uses.

Everything else in this spec (table/column names, tenant-scoping model, no-cascade-delete rule,
code-first/name-fallback upsert matching, city-mapping-safety rule, audit-log reuse) is unchanged by this
correction — only *where* the logic runs changed, not *what* it does.

## Problem

Today's general-purpose address hierarchy — `Country → State → City` — has no District or Sub-District
layer, and there is no bulk-import tooling for any of it: `countries`/`states`/`cities` rows are seeded
once and otherwise grown ad hoc (**Evidenced**: no import/upsert code exists anywhere under
`sc-saas-backend/src/modules/global/{countries,states,cities}/` — only `find`/`findOne`/`Like` read
methods, `countries.repository.ts:18-53`, `states.repository.ts:19-69`, `cities.repository.ts:19-69`).
Programs that need finer-grained administrative geography (e.g. India's district/sub-district/LGD-code
structure) have nowhere to attach that data, and there is no safe, repeatable way for an operator to load
a large reference dataset without either hand-writing SQL or risking duplicate rows. This spec adds the
missing District/Sub-District layer as optional enrichment and a single, reusable, SSRF-hardened JSON
import pipeline in the Developer Zone to populate all five entity types — without touching the existing
`Country → State → City` flow that every registration form (mentor/investor/corporate/individual/
partner/service-provider/program-office-member — **Evidenced**, e.g. `registered_city_id` on
`sc-saas-backend/src/modules/mentors/entities/mentor.entity.ts:64`) already depends on.

## Background (verified against code during this spec's authoring)

**Where Country/State/City actually live.** `sc-saas-backend/src/modules/global/{countries,states,cities}/`
— `CountriesEntity` (`countries` table: `id`, `name`), `StatesEntity` (`states` table: `id`, `name`,
`country_id` not-null FK), `CitiesEntity` (`cities` table: `id`, `name`, `state_id` nullable FK,
`country_id` nullable FK — **Evidenced**: `cities.entity.ts:1-34` already denormalizes both parent refs,
which is the precedent this spec's new tables follow). All three are registered in
`GlobalModule`'s single `TypeOrmModule.forFeature([...])` array and exposed publicly, unauthenticated,
via `GlobalController`: `GET /public/global/countries`, `GET /public/global/states/:countryId`,
`GET /public/global/states/:name/search`, `GET /public/global/cities/:stateId`,
`GET /public/global/cities/:name/search` (**Evidenced**, `global.module.spec.md` "owns.api", confirmed
directly against `global.controller.ts:1118-1232`). **These routes are read-only today and stay that way**
— this spec adds no route to this controller. None of the three entities carries any stable external
"code" column today — matching by anything other than internal auto-increment `id` or exact `name` is not
currently possible from admin's side either, which is exactly why this spec adds one.

**This must not be confused with the unrelated Startup-Recognition-ID master tables.** A completely
separate, unrelated feature — `sc-saas-backend/src/modules/startup-recognition-id/entities/
{district,city,subdivision}-master.entity.ts` (tables `district_master`/`city_master`/
`subdivision_master`) — exists for a different purpose (generating a startup's Recognition ID code) and
is, as of this writing, mid-removal under **SAN-312/SAN-313**
(`specs/features/SAN-312-location-master-removal.spec.md`, status `in-review`, not yet deployed). That
repo runs `synchronize: true` in prod (**Evidenced**, `database.module.ts:32`), so a same-named-but
different-schema entity reappearing later would be a real destructive-migration hazard once those tables
go inert. **This spec's new tables are therefore named `districts` and `sub_districts` — never
`district_master`, `subdivision_master`, or `city_master`** — and the new nullable FK columns added to
`CitiesEntity` are named `district_id` and `sub_district_id` (not `subdivision_id`), to keep the word
"subdivision" out of this feature's schema entirely and avoid any possible collision, now or after
SAN-312/313 lands. Also unrelated and untouched: `LocationsEntity` (table `locations`, a flat
`city`+`country` string pair used only by `GET /search/locations/:keyword`,
**Evidenced** `locations.entity.ts:1-16`) — a different, older, free-text-search convenience table, not
part of the Country→State→City relational hierarchy this spec extends.

**The direct-Medoo, entities-only-from-backend pattern is established prior art, not a new idea.** The
very feature SAN-312/313 is removing (`location_master.php` + `district_master`/`city_master`/
`subdivision_master`) used exactly this shape: backend defined the TypeORM entities purely so
`synchronize: true` would create the tables; admin's PHP did all the reading and writing directly via
Medoo, with no backend controller ever existing for it (**Evidenced**, SAN-312 spec: "per SAN-253's
resolved, direct-DB-access architecture... `sc-saas-backend` ships no `StartupRecognitionIdController`").
This spec reuses that same shape for the new `districts`/`sub_districts` tables and the enriched
`countries`/`states`/`cities` columns — the pattern is being retired for *that specific feature's business
logic* (ID-code generation), not because the direct-DB-access shape itself was wrong.

**Tenant scoping — evidenced, not inferred.** `sc-saas-backend`'s tenancy model is **one deployment per
tenant**: no tenant column exists anywhere, config/flags load once at bootstrap from the cockpit, and
`global.module.spec.md`'s own `tenant_scoping` line states reference tables "contain no tenant column —
they are per-deployment DBs" (**Evidenced**). `sc-saas-admin` separately opens a distinct Medoo connection
per request, selected by `admin_domain`/`admin_custom_domain` (**Evidenced**, workspace `CLAUDE.md`
invariant #5 + `sc-saas-admin/CLAUDE.md` "Tenancy" section) — and, per the direct-DB-access precedent
above, that connection points at the **same physical database** `sc-saas-backend`'s TypeORM manages for
that tenant. Put together: **there is no single physical database that holds every tenant's location
data** — each tenant has its own copy of `countries`/`states`/`cities` (and, after this spec,
`districts`/`sub_districts`) in its own DB. Consequently, running this import from one tenant's admin
panel populates **only that tenant's DB** — it is inherently a **per-tenant, run-once-per-tenant
operation**, not a single global action, exactly like every other `modules/developer/maintenance.php`
master-data installer already behaves against `$database` (the current request's tenant connection).
`tenant_scoped: true` above reflects this.

**Existing admin-side transactional-write convention (reused, not invented).** Medoo's
`$database->action(function($db) { ...; return true/false; })` closure — commit on truthy return, rollback
otherwise — is the established transaction pattern in this repo, used by
`includes/startup_recognition_id_functions.php:100` and four call sites in
`includes/ai_credits_functions.php` (**Evidenced**, confirmed by grep). This spec's transactional
countries→states→districts→sub_districts→cities upsert reuses this exact mechanism — no new transaction
abstraction.

**Existing admin audit-log mechanism (reused, not invented).** `spa_admin_logs`, written via
`createAdminLogs($database, $module, $action, $table, $recordId, $data, $programId, $url)`
(**Evidenced**, `sc-saas-admin/includes/core_functions.php`, documented in
`modules/system_logs/module.spec.md`), is the workspace's only general-purpose admin-action audit trail —
called opportunistically by ~90 existing admin modules, viewed read-only by `modules/system_logs/`. This
is the mechanism this spec's admin-side work reuses; `profile_audit_logs` (the *other* audit table in this
repo) is a distinct, backend-written trail for stakeholder profile edits and is not relevant here
(**Evidenced**, `modules/profile_audit_logs/module.spec.md`). No SSRF-fetch utility exists anywhere in
`sc-saas-admin` today (**Evidenced**: every outbound call in `core_functions.php` is a raw, individually
configured `curl_init()` block; repo-wide grep for `ssrf`/private-IP/metadata-address patterns returns
nothing) — the hardened fetcher this spec requires is genuinely new PHP code, not a reuse gap.

## Acceptance criteria

- [ ] Every existing `GlobalController` Country/State/City route (`GET /countries`, `/states/:countryId`,
  `/states/:name/search`, `/cities/:stateId`, `/cities/:name/search`) and every existing consumer of
  `CountriesEntity`/`StatesEntity`/`CitiesEntity` (mentor/investor/corporate/individual/partner/
  service-provider/program-office-member `registered_city_id`-style fields, `GET /master_data`,
  `GET /custom/:types`) returns unchanged output for unchanged input — the only schema change to these
  three entities is new, nullable, currently-unused columns (`code` on all three; `district_id`/
  `sub_district_id` additionally on `CitiesEntity`). No new backend route exists for this feature at all.
- [ ] `districts` and `sub_districts` tables exist post-deploy with the columns specified in Per-repo
  plan → backend; zero existing rows in any table are modified by the schema change itself (verified by
  row-count and spot-check diff before/after a `synchronize: true` deploy in a non-prod environment first).
- [ ] Admin's new Developer Zone page's "Validate" action, given a well-formed fixture URL, shows
  per-entity-type counts (`countries`, `states`, `districts`, `sub_districts`, `cities`) computed by
  counting the fetched payload's arrays — never a hardcoded number — and zero validation errors.
- [ ] The same "Validate" action, given payloads engineered to violate each rule below, shows a non-empty,
  specific error list and performs zero DB writes: (a) a duplicate id/code within one entity type; (b) an
  empty/missing `name`; (c) a `state` referencing a non-existent country; (d) a `district` referencing a
  non-existent state; (e) a `sub_district` whose declared state disagrees with its parent district's
  state; (f) a `city` whose declared state disagrees with its referenced district's state, or whose
  declared district disagrees with its referenced sub_district's district.
- [ ] "Confirm Import" re-validates from scratch server-side (PHP never trusts a client-cached "already
  validated" claim from the browser) and, only if valid, imports in the strict order
  countries → states → districts → sub_districts → cities inside a single Medoo `->action()` transaction.
- [ ] A forced failure injected after districts but before sub_districts leaves zero committed rows from
  the entire import operation, across all five entity types (full rollback) — verified manually (no
  automated test framework exists in this repo, per this workspace's standing note on `sc-saas-admin`).
- [ ] Running the same valid payload twice produces zero duplicate rows on the second run: an incoming
  row matching an existing row by `code` is updated in place; absent a `code` match (including the
  first-ever run, before any `code` has been backfilled), an incoming row matching an existing row by
  parent + exact `name` is updated in place, not duplicated (verified with a fixture where a pre-seeded
  "Haryana" state, with no `code` set, is matched by name+country rather than duplicated).
- [ ] No import run ever deletes a row absent from the incoming payload — verified by re-running against a
  payload that omits a pre-existing state/district/city and confirming its row count only increases or
  stays equal, never decreases.
- [ ] `cities.district_id`/`sub_district_id` are populated only when the incoming city row resolves to
  exactly one district/sub_district via stable code/id references; an incoming city whose district/
  sub_district reference is missing or ambiguous is left with those columns `null` and is listed by name
  in the import summary's "requires manual mapping" list — never guessed from `name` alone (verified with
  a fixture containing two same-named cities in different districts).
- [ ] The URL fetcher rejects, before completing any request where feasible: non-`https://` URLs;
  `localhost`/`127.0.0.1`; RFC1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`);
  link-local (`169.254.0.0/16`, including the `169.254.169.254` cloud-metadata address); and any hostname
  that DNS-resolves to one of those ranges (not just a literal-string check). It also enforces a connect
  timeout, a response timeout, a maximum response byte size, and a maximum total record count, and does
  not follow a redirect to a URL that itself fails any of the same checks.
- [ ] `sc-saas-admin`'s new Developer Zone page is reachable only to `is_dev`-role admins; shows the
  dynamic preview before enabling "Confirm Import"; and, on a successful import, writes exactly one
  `createAdminLogs()` row summarizing the source URL and per-entity-type created/updated/unmapped counts.
- [ ] Zero code changes in `sc-saas-frontend`, `sc-saas-3rdparty-webservices`, `ai-startups-analyzer`,
  `sanchiconnect-saas-tenants`, `sanchiconnect-saas-tenants-admin`; zero changes to
  `district_master`/`city_master`/`subdivision_master`/`StartupEntity` (SAN-312/313 scope) or to
  `LocationsEntity`; zero new routes on `AdminActionsController` or anywhere else in `sc-saas-backend`.

## Per-repo plan

### backend (sc-saas-backend) — Linear SAN-314

Entities/schema only — no service, no controller route, no API surface.

- New `src/modules/global/districts/districts.entity.ts` (`@Entity('districts')`): `id`
  (`@PrimaryGeneratedColumn`), `name` (`varchar`, not null), `code` (`varchar`, nullable, indexed — not
  unique as of SAN-341, see SUPERSEDED note above — stores whatever stable identifier the source JSON
  provides, e.g. an LGD code), `state_id` (`int`, not null, FK → `states.id`), plus a
  `@ManyToOne(() => StatesEntity)` relation — same shape as `StatesEntity`'s own
  `@ManyToOne(() => CountriesEntity)` (`states.entity.ts:26-28`).
- New `src/modules/global/sub_districts/sub-districts.entity.ts` (`@Entity('sub_districts')`): `id`,
  `name` (not null), `code` (nullable, indexed, not unique as of SAN-341), `district_id` (`int`, not null,
  FK → `districts.id`), `state_id` (`int`, not null, FK → `states.id`, denormalized — mirroring
  `CitiesEntity`'s existing `state_id` + `country_id` double-FK precedent, `cities.entity.ts:20-24`).
- `countries/countries.entity.ts`, `states/states.entity.ts`, `cities/cities.entity.ts`: add one new
  nullable `code` column (`varchar`, indexed, not unique as of SAN-341) to each. No other column,
  relation, route, or method on these three entities/repositories/controllers changes.
- `cities/cities.entity.ts`: add `district_id` (`int`, nullable, FK → `districts.id`) and
  `sub_district_id` (`int`, nullable, FK → `sub_districts.id`) with matching `@ManyToOne`/`@JoinColumn`
  relations, alongside the existing `state_id`/`country_id`. **Never** named `subdivision_id` — see
  Background.
- `global.module.ts`: add `DistrictsEntity`/`SubDistrictsEntity` to `TypeOrmModule.forFeature([...])`.
  **No repository, no service, no controller change** — nothing in this feature needs backend-side code
  beyond entity registration; `synchronize: true` does the rest on deploy.
- **Confirmed source-JSON structure** (from the product requirement): a single document
  `{ version, source, countries[], states[], districts[], sub_districts[], cities[] }` where
  `countries[i]` = `{ id, name, code }`; `states[i]` = `{ id, country_id, name, code }`; `districts[i]` =
  `{ id, state_id, name, code }`; `sub_districts[i]` = `{ id, district_id, state_id, name, code }`;
  `cities[i]` = `{ id, state_id, district_id, sub_district_id, name, code }` (the last three optional).
  `code` is optional per row (falls back to parent+name matching when absent). This structure is what
  admin's PHP (below) parses and validates directly — the backend never sees or processes this JSON.

### admin (sc-saas-admin) — Linear SAN-315

All fetch/validate/preview/import logic lives here, mirroring the shape of the now-removing
`location_master.php`'s direct-Medoo pattern (fetch/read/write via `$database`, not an HTTP call to
backend). Build it as a small set of PHP functions (not all inline in the controller file) so
fetch/validate-structure/validate-relationships/preview/import stay independently testable/readable —
the spec's "reusable service" intent, expressed as PHP functions/includes rather than a NestJS service
since this repo has no service-class convention of its own.

- New `includes/location_master_import_functions.php` (mirrors the existing convention of
  `includes/startup_recognition_id_functions.php`/`includes/ai_credits_functions.php` — shared logic in
  `includes/`, not duplicated per-module):
  - `fetchLocationMasterSource($url)` — the SSRF-hardened fetcher: reject non-`https://` URLs; reject
    `localhost`/`127.0.0.1`/RFC1918 ranges/link-local (incl. `169.254.169.254`) both as a literal
    host/IP-string check **and** after resolving the hostname via `gethostbyname()`/`dns_get_record()`;
    `curl_setopt` connect timeout + total timeout; cap response size (`CURLOPT_PROGRESSFUNCTION`/
    `CURLOPT_NOPROGRESS => false` abort-over-limit, or a `Content-Length` pre-check plus a hard read cap);
    cap total parsed record count (sum of all five arrays) after `json_decode`; on any redirect
    (`CURLOPT_FOLLOWLOCATION`), re-run every host/IP check against the redirect target before following —
    or simplest/safest: set `CURLOPT_FOLLOWLOCATION => false` and treat any 3xx as a rejected response
    (no legitimate JSON data source needs a redirect here).
  - `validateLocationMasterStructure($payload)` — per-entity-type: required fields present, no duplicate
    `id`/`code` within a type, no empty `name`.
  - `validateLocationMasterRelationships($payload)` — `states[i].country_id` must match some
    `countries[].id`; `districts[i].state_id` must match some `states[].id`; `sub_districts[i].district_id`
    must match some `districts[].id` **and** `sub_districts[i].state_id` must equal that matched
    district's own `state_id`; for `cities[i]`, whichever of `state_id`/`district_id`/`sub_district_id`
    are present (District/Sub-District refs on a city are optional) must resolve the same way, with
    `district_id`'s resolved state equal to `state_id`, and `sub_district_id`'s resolved district equal
    to `district_id`.
  - **Payload-local ids, not DB ids.** Every `id` field in the source JSON is a reference id **local to
    that one JSON document**, used only to resolve parent→child links within the same payload — never
    assumed to equal, and never written directly as, an existing or new row's actual DB primary key. The
    import function resolves each payload row to a real DB row via the code-first/parent+name-fallback
    matching below, and uses *that* row's real `id` when writing any FK column.
  - `buildLocationMasterPreview($payload)` — dynamic per-entity-type counts (simple `count()` per array);
    this is what "Validate" renders — no separate preview step needed.
  - `importLocationMasterData($database, $payload)` — re-runs both validators first (defense against a
    stale/tampered client-side "already validated" claim — the browser's validate call and the confirm
    call are two separate requests), then wraps the whole import in
    `$database->action(function($db) use (...) { ...; return true; })` (rollback on any exception/
    `return false`), upserting in order countries → states → districts → sub_districts → cities. Matching
    order per row: `code` (if the incoming row has one and an existing row has the same `code`) → else
    parent + exact `name` match → else insert new (`$db->get(...)` to check existence, then
    `$db->update(...)`/`$db->insert(...)`). No `DELETE`/`TRUNCATE` of anything absent from the payload.
    Cities: set `district_id`/`sub_district_id` only when the incoming city row's district/sub_district
    reference resolves to exactly one row; otherwise leave `null` and append the city's name to a returned
    `$unmapped` array. Returns a summary array (`created`/`updated`/`unmapped` counts per entity type) for
    the controller to render and log.
- New `modules/developer/location_master_import.php` (controller — renders the page **and** dispatches
  the two AJAX actions, exactly like `modules/developer/maintenance.php`'s shape), gated by
  `checkRole("is_dev")` at the top of the file (**Evidenced convention**, `developer/module.spec.md`'s
  gating table — the majority pattern in this module) — **the AJAX action blocks below must also be
  inside/after this same gate check, not only the page-render fallthrough**, per the precedent risk
  already documented in this module (`database_management.php`'s AJAX backend lacking its own role check)
  — do not repeat that gap here.
  - `$_POST['submitAction'] == 'validate_location_master'` → `fetchLocationMasterSource($_POST['sourceUrl'])`
    → `validateLocationMasterStructure()` → `validateLocationMasterRelationships()` →
    `buildLocationMasterPreview()`; `echo json_encode([...])`; `exit`.
  - `$_POST['submitAction'] == 'import_location_master'` → fetch + re-validate + `importLocationMasterData($database, $payload)`
    → on success, `createAdminLogs($database, "developer", "location_master_import", null, null,
    array("sourceUrl" => $_POST['sourceUrl'], "summary" => $summary))` (**Evidenced helper**,
    `includes/core_functions.php`) → `echo json_encode([...])`; `exit`.
  - CSRF: call `verifyCSRFToken()` on both POST actions — this is the repo-wide convention for mutating
    admin actions (note: `maintenance.php`'s own `install_master_data` skips it, an existing gap in that
    file, not a pattern to copy into new code).
- New template `themes/default/html/developer/location_master_import.php` — a source-URL text field, a
  "Validate" button, and an initially-disabled "Confirm Import" button, following `maintenance.php`'s
  existing jQuery/Bootstrap idioms (`$.post(current_url(), {...}, cb)`, `#loaderOverlay`, `showToast()`).
  Renders the dynamic per-entity-type counts and any "requires manual mapping" city names from the
  validate response; enables "Confirm Import" only after a successful validate response for the
  currently-entered URL (re-disable if the URL field changes); renders the created/updated/unmapped
  summary after a successful import.
- Add a nav link/feature entry to the Developer Zone sidebar for this new page, alongside the existing
  `database_management`/`maintenance`/`api_management`/etc. entries — `[NOT SPECIFIED IN SOURCE]` exact
  menu-row wording/icon; follow the existing `spa_menu_management` seed pattern in
  `config/default-settings/menues.php` used for sibling Developer Zone pages.

## Contracts & invariants

- **Flags:** none added, renamed, or removed. This is an `is_dev`-role-gated admin tool with no backend
  API and no tenant-facing surface — no cockpit flag makes sense here.
- **API:** **none.** No route added, changed, or removed anywhere in `sc-saas-backend`. `/audit-contract`
  has nothing to check for this feature — confirmed, not merely assumed, since the corrected design has
  zero new controller code.
- **Events:** none — no event/message-bus mechanism exists in this workspace.
- **Invariants at risk:**
  - **Invariant #5 (tenant scoping)** is the one genuinely load-bearing invariant here, and it changes
    *how this feature must be operated*, not just how it's coded: because both `sc-saas-backend` (one
    deployment per tenant) and `sc-saas-admin` (one Medoo connection per `admin_domain` per request, the
    same physical DB per the direct-DB-access precedent) are scoped to a single tenant's DB at a time,
    **this import is inherently a per-tenant action** — a platform operator managing N tenants must run
    "Validate" → "Confirm Import" separately against each tenant's own admin panel. There is no code path
    anywhere in either repo that writes across tenant DBs, and this spec introduces none.
  - No other of the six named cross-repo invariants (flag names / API contract / tenant-verification shape
    / auth / tenant scoping beyond the above / PowerPitch contract) is touched: no auth model change (this
    is a page inside admin's existing session+role-based auth, `checkLoggedIn()`+`checkRole("is_dev")`, no
    new mechanism); no tenant-verification (`verify_tenant`/`tenant-settings`) shape changes; no PowerPitch
    surface involved.
  - **`synchronize: true`, additive direction.** `sc-saas-backend` runs with `synchronize: true` in prod
    (**Evidenced**, `database.module.ts:32`) — the two new tables and the new nullable columns on
    `countries`/`states`/`cities`/`cities.district_id`/`cities.sub_district_id` will be created
    automatically on next deploy. This is the **safe** direction of the risk SAN-312/313 is managing
    (additive-only, nothing dropped, nothing renamed, no existing row touched) — but it is still a live
    schema mutation on a shared, high-blast-radius module (`GlobalModule` registers 72+ entities and is
    imported by most of the backend), so it should still be deployed and smoke-tested deliberately, not
    assumed inert just because it's additive.
  - **Direct-DB-access risk, inherited from the pattern being reused, named explicitly.** Because admin
    writes directly to tables the backend's TypeORM also manages under `synchronize: true`, a *future*
    backend entity-shape change to `countries`/`states`/`cities`/`districts`/`sub_districts` (e.g. a column
    rename) could silently break admin's PHP without any compiler/type check catching it — the same class
    of risk already named in SAN-312/313's own Contracts section for `district_master`/etc. Anyone editing
    these five entities later must grep `sc-saas-admin` for direct references first.

## Test plan

- **backend:** `tsc --noEmit` and `npm run lint` clean after adding the two new entities and the new
  columns on `countries`/`states`/`cities`. No new unit tests needed — there is no new backend logic to
  test, only declarative entity/column additions; verify via a non-prod `synchronize: true` deploy that
  the two new tables and five new nullable columns appear with zero rows changed on existing tables.
- **admin:** `php -l` on every new/edited file; manual test: (a) `is_dev` gate blocks a non-dev admin from
  the new page (including a direct POST to the AJAX actions, not just the page load); (b) "Validate"
  against a well-formed fixture URL shows correct dynamic counts and no errors; (c) "Validate" against a
  malicious URL (e.g. an internal/metadata address, a private-IP literal, and a hostname that resolves to
  one) shows a clear rejection with zero DB writes; (d) "Confirm Import" against the same well-formed
  fixture performs the import and a matching `spa_admin_logs` row appears in `system_logs/list`; (e)
  running the same fixture twice produces zero duplicate rows (row-count check before/after each run); (f)
  a fixture with a forced mid-import error (e.g. a malformed row injected after districts) leaves zero
  committed rows across all five tables; (g) a fixture with two same-named cities in different districts
  leaves both cities' `district_id` null and both listed in the "unmapped" summary.
- **cross-repo:** after backend deploys and is confirmed live (new columns/tables exist), admin's new page
  completes an end-to-end validate→import cycle against a real (non-prod) tenant DB; spot-check that an
  existing registration form's Country/State/City dropdown (e.g. mentor signup) is visually and
  functionally unchanged before and after the backend deploy.

## Rollout

1. **`sc-saas-backend` ships first (SAN-314).** Purely additive schema (two new tables, five new nullable
   columns across three existing tables) — nothing for any existing consumer to break, and no new route
   for anything to depend on incorrectly. Deploy-safe on its own.
2. **`sc-saas-admin` ships second (SAN-315), once step 1 is confirmed live.** New Developer Zone page
   reads/writes the now-existing tables/columns directly via Medoo; it is not deploy-safe before step 1
   (the columns/tables it writes to wouldn't exist yet).
3. No flag gating — this is an `is_dev`-role-gated ops tool, not a tenant-facing rollout.
4. **Per-tenant operational note (see Contracts & invariants):** this is not a "run once, done for every
   tenant" action. Each tenant's platform operator (or whoever administers that tenant's panel) runs
   Validate → Confirm Import separately, once per tenant, whenever they want that tenant's location data
   enriched with District/Sub-District. This is a rollout/runbook fact, not a code change.

## Out of scope

- Any change to `sc-saas-frontend`, `sc-saas-3rdparty-webservices`, `ai-startups-analyzer`,
  `sanchiconnect-saas-tenants`, `sanchiconnect-saas-tenants-admin` — no concrete need found in any of
  them; the existing Country→State→City flow they consume is unchanged.
- Any new backend API route (`AdminActionsController` or otherwise) for this feature — see Correction
  above; the corrected design has zero backend routes.
- Exposing District/Sub-District data via any new public/tenant-facing endpoint (e.g. a
  `GET /districts/:stateId` analogous to the existing `GET /states/:countryId`) — this pass is backend
  storage + admin import tooling only. A future spec can add read endpoints if a real consumer emerges.
- Backfilling `district_id`/`sub_district_id` on any pre-existing `cities` row that predates this
  feature and isn't present in a subsequently-imported payload — only rows the imported JSON can
  deterministically map get enriched; nothing else changes as a side effect of this feature shipping.
- The pre-existing `locations` table/entity (`sc-saas-backend/src/modules/global/locations/`) — a
  different, unrelated flat city+country string table; untouched.
- The Startup-Recognition-ID module's `district_master`/`city_master`/`subdivision_master` tables and
  SAN-312/313's removal of them — completely separate schema/feature; this spec's new tables are
  deliberately, permanently differently named (see Background) so the two efforts can never collide,
  regardless of deploy order between this spec and SAN-312/313.
- A retention/cleanup policy for districts/sub-districts that a later source JSON stops mentioning — per
  requirement #6 (no cascade-delete), such rows simply remain; no expiry/archival mechanism is designed
  here.

## Open questions

None blocking. This spec is approvable as drafted (re-confirmed after the 2026-08-11 architecture
correction above, which changed only where the logic runs, not any product behavior in the Acceptance
criteria).
