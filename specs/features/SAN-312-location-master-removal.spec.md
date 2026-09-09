---
id: SAN-312                     # sc-saas-admin removal issue (ships first, dependency order). Backend counterpart: SAN-313. Project: see `linear:` below.
title: Location Master removal (Startup Recognition ID — District/City/Sub-Division)
type: feature
status: in-review                # Implementation complete both repos 2026-08-11 (php -l / tsc / lint / tests clean); awaiting human review + commit + deploy. Open question resolved 2026-08-11 by product owner — see Open questions
linear: https://linear.app/sanchiconnect/project/location-master-removal-c603249ade94
owner: nirmal.s@sanchiconnect.com
repos: [admin, backend]         # DEPENDENCY ORDER — admin removes references first, backend's schema drop ships second (synchronize:true risk, see Rollout)
contracts:
  api: []                       # No REST surface touched — this feature has none (per SAN-253's resolved direct-DB-access architecture); confirmed unaffected
  flags: []                     # startup_recognition_enabled / ecosystem_enabled untouched
  events: []
tenant_scoped: true             # district_master/city_master/subdivision_master + startups.* all live in the per-tenant DB in both repos
depends_on: []
created: 2026-08-11
---

# Location Master removal (Startup Recognition ID — District/City/Sub-Division)

## Evidence-tagging convention used throughout this spec
- **Evidenced** — cited to `file:line` in the real codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation, not directly stated.
- `[NOT SPECIFIED IN SOURCE]` — a real gap.
- `[DESIGN DECISION PENDING]` — a genuinely new decision with no precedent, routed to product/dev lead, never guessed.

## Linear tracking

- Project: [Location Master Removal](https://linear.app/sanchiconnect/project/location-master-removal-c603249ade94)
- [SAN-312](https://linear.app/sanchiconnect/issue/SAN-312) — sc-saas-admin (this spec's id; ships first)
- [SAN-313](https://linear.app/sanchiconnect/issue/SAN-313) — sc-saas-backend (ships second)

## Problem

"Location Master" — `sc-saas-admin`'s District/City/Sub-Division CRUD screen for the Startup Recognition
ID feature (built as part of **SAN-253**, `specs/features/SAN-253-startup-id-creation-module.spec.md`,
status `approved` and already implemented in code) — and the `sc-saas-backend` master-data
entities/repositories/lookups backing it are being retired. Per two rounds of user clarification, the
product owner wants this specific sub-feature removed while everything else SAN-253 shipped (Format
Builder, Digital ID Card Design Builder/Template, Standard Geography, `state_master`-level generation)
continues exactly as-is. This is a scoped code-and-schema removal, not a new feature. The real risk is
(a) getting the cross-repo removal **order** right — `sc-saas-backend` runs with `synchronize: true` in
prod (**Evidenced**, `sc-saas-backend/src/core/database/database.module.ts:32`), so dropping the
`district_id`/`city_id`/`subdivision_id` columns from `StartupEntity` is a live, destructive schema
change on the next backend deploy — and (b) surfacing the one real behavior change this removal causes
(a segment that used to resolve to a code now permanently resolves to nothing) to the product owner
before shipping, rather than silently absorbing it.

## Background (verified against code during this spec's authoring)

`location_master` is not its own DB table — it is the admin UI's name for a screen
(`sc-saas-admin/modules/startup_recognition_management/location_master.php`) that does direct-Medoo CRUD
on three real, TypeORM-synced per-tenant tables: `district_master`, `city_master`, `subdivision_master`
(**Evidenced**, `sc-saas-backend/src/modules/startup-recognition-id/entities/{district,city,subdivision}-master.entity.ts`).
These three tables are also consumed by the Startup Recognition ID generation path itself — both the
backend's round-entry trigger (`StartupRecognitionIdGenerationService.generateForStartup()`) and the
admin's own PHP port of the same algorithm (`includes/startup_recognition_id_functions.php`'s
`srIdGenerateForStartup()`/`srIdRegenerateAll()`, a deliberate, documented duplication — see that
module's `module.spec.md`) — not just by the Location Master screen. Removing the tables therefore
means removing three separate consumers, not one.

**Verified: District/City/Sub-Division are already-optional, silently-omitted segments today** — both
the PHP (`srIdResolveSegmentValues()`) and TypeScript (`resolveSegmentValues()`) segment-resolvers only
push a value for these segment types `if (!empty($ctx['district']['code']))` / `if (ctx.district?.code)`
— a startup with no district set already produces a code with that segment silently absent, never a
placeholder. This existing "omit if unresolvable" behavior is what makes the removal *mechanically* safe
(no exception is thrown), but it also means removal has a real, non-hypothetical visible consequence for
any tenant currently relying on it — see Open questions.

## Acceptance criteria

- [x] `sc-saas-admin`'s Location Master screen (`modules/startup_recognition_management/location_master.php`
  and its view) is deleted; no route, nav link, or feature-card anywhere in Settings or the Startup ID
  Management module points to it. **Verified 2026-08-11**: both files deleted; repo-wide grep for
  `location_master`/`Location Master` returns zero hits outside the intentional doc comment left in
  `includes/startup_recognition_id_functions.php`.
- [ ] `sc-saas-admin`'s manual "Generate ID" action (`startup-detail.php`) and the format-change
  "regenerate all" worker (`cli/regenerate_startup_recognition_ids.php` → `srIdRegenerateAll()`) both run
  successfully end-to-end with zero code references to `district_master`/`city_master`/`subdivision_master`,
  for tenants both with and without those segment types in their saved
  `startup_recognition_id_config.segments`. **Partially verified 2026-08-11**: zero code references
  confirmed by repo-wide grep and `php -l` on every edited file; the "runs successfully end-to-end
  against a live tenant DB" half of this criterion was NOT exercised (no test framework in this repo, no
  DB access in this environment) — deferred to the Rollout section's post-deploy smoke test.
- [x] `sc-saas-backend`'s `StartupRecognitionIdGenerationService` (the round-entry trigger, called from
  `program-management.service.ts`) runs successfully with `DistrictMasterRepository`/`CityMasterRepository`/
  `SubdivisionMasterRepository` and their entities fully removed; `state_master`-based Country
  Code/State Code resolution is unaffected. **Verified 2026-08-11**: all 11 tests in
  `startup-recognition-id-generation.service.spec.ts` and all 10 tests in
  `program-management.service.spec.ts` pass with the three repositories/case-blocks removed; `tsc --noEmit`
  clean; `npm run lint` shows zero new errors/warnings introduced (18 pre-existing errors, all in
  unrelated files).
- [ ] `startups.district_id`/`city_id`/`subdivision_id` columns no longer exist in the schema once
  `sc-saas-backend` has deployed (via `synchronize: true`), with zero SQL errors in either repo once both
  repos' changes have landed **in the specified order** (admin, then backend). **Not yet verified** — this
  is an actual-deploy-time criterion (`synchronize: true` runs against a real MySQL DB); nothing has been
  deployed as part of this implementation pass. Deferred to the Rollout section's post-deploy smoke test.
- [x] Format Builder, Digital ID Card Design Builder, `digital_id_card_template`, `standard_geography`
  (+ its `searchStandardGeography` AJAX action), `state_master`, `startup_recognition_id_config`, and
  `startup_recognition_id_sequence` are all verified unchanged — zero diffs to those files/tables.
  **Verified 2026-08-11** via `git status`/`git diff` in both repos: `format_builder.php`,
  `card_design_builder.php` (admin, both controller+view), `digital-id-card-template.entity.ts`,
  `standard-geography.entity.ts`, `startup-recognition-id-config.entity.ts`,
  `startup-recognition-id-sequence.entity.ts`, and `state-master.repository.ts` show zero edits by this
  change. `state-master.entity.ts` required the one consequential edit named in the Per-repo plan (removing
  the now-dangling `districts` relation + import) — its own `name`/`countryCode`/`stateCode` columns and
  the `state_master` table itself are untouched.
- [x] Format Builder's segment palette no longer offers District/City/Sub-Division as selectable segment
  types — both admin's picker UI and its server-side "invalid segment" validation (both driven by the
  single function `srIdSegmentTypes()`) and the backend's `StartupRecognitionIdSegmentType` enum have
  those three entries removed. `StandardGeographyLevel` (a separate enum for the unrelated,
  out-of-scope Standard Geography feature) is verified unchanged. **Verified 2026-08-11**: both edits made;
  `StandardGeographyLevel`'s own `STATE`/`DISTRICT`/`CITY`/`SUBDIVISION` values confirmed untouched by
  direct read of `enum.ts`.
- [x] Any tenant's already-saved `startup_recognition_id_config.segments` that still contains a
  `district`/`city`/`subdivision` entry continues to generate/regenerate IDs with zero errors — that
  segment is now silently omitted via the existing `default: break` fallback in
  `resolveSegmentValues()`/`srIdResolveSegmentValues()`, the same "omit if unresolvable" behavior as the
  rest of this spec, not a new failure mode. No data migration of saved configs is required or performed.
  **Verified 2026-08-11 by code inspection** (not a live-DB run): both switch statements' `default: break`
  fallback is intact post-edit, and the PHP ctx array passed into `srIdResolveSegmentValues()` no longer
  carries `district`/`city`/`subdivision` keys at all (rather than passing now-undefined PHP variables),
  matching the Background section's "notice-suppressing missing-key access" reasoning exactly.

## Per-repo plan

Dependency order: **admin ships first** (stop reading/writing the tables and columns), **backend ships
second** (delete the entities/repositories and drop the `startups` columns — the actual destructive
schema change under `synchronize: true`). Shipping backend first would leave admin's PHP still trying to
`INSERT`/`SELECT` against columns/tables that error mid-request. See Rollout.

### admin (sc-saas-admin) — Linear SAN-312

- Delete `modules/startup_recognition_management/location_master.php` (controller) and
  `themes/default/html/startup_recognition_management/location_master.php` (view) in full.
- `modules/startup_recognition_management/settings.php`: remove the line setting
  `$tpl->canAccessSrIdCore = srIdCheckRole();` (**Evidenced**, `settings.php:38`) — its only consumer
  (the Location Master feature-card gate) is being deleted below, so this becomes dead code otherwise.
- `themes/default/html/startup_recognition_management/settings.php`: remove the Location Master
  `<a class="sr-feature-card">` block (currently lines 117-123), the now-unused
  `$canAccessSrIdCore = $this->canAccessSrIdCore;` local (line 10), and the "Location Master" mentions in
  the hero/disabled-state descriptive prose (currently lines ~68 and ~95-97 — "Format Builder, **Location
  Master**, Digital ID Card Design Builder, ...").
- `modules/startup_recognition_management/module.spec.md`: remove the `location_master` bullet from
  "Public surface" (currently lines 63-70), the "Location Master's soft-delete is `status`, not `active`"
  bullet under "Watch out for" (lines 127-129), and drop `{state,district,city,subdivision}_master` →
  `state_master` only in the `tenant_scoping` frontmatter line and the "Purpose" paragraph's table list
  (drop `district`/`city`/`subdivision`, keep `state`).
- `includes/startup_recognition_id_functions.php`:
  - `srIdGenerateForStartup()`: remove the three `$database->get("district_master"/"city_master"/"subdivision_master", ...)`
    lookups (currently lines 315-317) **and** the `district_id`/`city_id`/`subdivision_id` keys from
    `$updateData` (currently lines 349-351) — leaving those in `$updateData` would attempt to write
    columns backend is about to drop.
  - `srIdRegenerateAll()`: remove the same three lookups inside the per-startup loop (currently lines
    423-425). No `$updateData` write to remove here — regenerate-all never wrote those three columns back
    (only `recognition_id`/`recognition_suffix`/`recognition_regenerated_at`/`recognition_regeneration_count`).
  - `srIdResolveSegmentValues()`'s `district`/`city`/`subdivision` `case` blocks are **not** on the
    task's explicit removal list and are left in place as harmless dead code — once callers above stop
    populating `$ctx['district']`/`$ctx['city']`/`$ctx['subdivision']`, `!empty($ctx['district']['code'])`
    safely evaluates false with no PHP notice (multi-level array access inside `empty()` is
    notice-suppressing by language design), so the segment is simply always omitted. Deleting these case
    blocks too is optional follow-up cleanup, not required for correctness — flagging so it isn't mistaken
    for an oversight.
- `modules/startup-detail.php` / `themes/default/html/startup-detail/startup-detail.php` — **verified,
  no edit required**. The controller's manual "Generate ID" AJAX handler
  (`srIdGenerateForStartup($database, $brandSettings, $startupId, ...)`, line 178) and the view's
  read-only display block (lines 427-449, showing only `recognition_id`/`recognition_year`/`serial_no`/
  `recognition_suffix`/`recognition_generated_at`) have **zero** direct reference to
  district/city/subdivision — that dependency is fully encapsulated inside the shared library function
  edited above. The task brief anticipated a possible edit here; code inspection shows none is needed.
- `cli/regenerate_startup_recognition_ids.php` — **verified, no edit required**. This file only calls
  `srIdRegenerateAll($database, $brandSettings, $newConfig, 200)` (line 122); it holds no direct reference
  to district/city/subdivision itself. Editing the shared function above fully resolves this file's
  dependency with zero changes to the file.
- Re-grepped `district_master`/`city_master`/`subdivision_master`/`district_id`/`city_id`/`subdivision_id`
  across this repo: the only real hits beyond the files above are `location_master.php`'s own AJAX
  handlers (deleted with the file) and `registered_city_id` / general per-stakeholder `city_id` fields on
  mentor/investor/individual/corporate/partner/service-provider/program-office-member (**Evidenced**,
  e.g. `sc-saas-backend/src/modules/mentors/entities/mentor.entity.ts:64` `registered_city_id`) — a
  distinct, unrelated general-address concept backed by the pre-existing `cities`/`states`/`countries`
  registration tables, not `city_master`. **Must not be touched.**
- `includes/startup_recognition_id_functions.php`'s `srIdSegmentTypes()` (**Evidenced**, lines 30-41):
  remove the `"district" => "District"`, `"city" => "City"`, `"subdivision" => "Sub-Division"` entries
  from the returned array. This is Format Builder's entire segment palette — a single source of truth
  consumed by `format_builder.php` both for the tenant-facing picker UI (`$tpl->segmentTypes =
  srIdSegmentTypes()`, line 173) and for server-side "invalid segment" validation
  (`array_keys(srIdSegmentTypes())`, lines 79-82) — so this one edit removes District/City/Sub-Division
  from both the picker and the validator with no changes needed to `format_builder.php` itself.
  **Verified — no data migration needed**: `segments` is stored as a JSON blob per tenant row; removing
  these keys from the palette function only affects new saves (rejected by the now-stricter
  `array_keys()` validation) and what the picker offers — it does not touch already-saved rows containing
  `district`/`city`/`subdivision`, which continue to be silently omitted at generation time (see backend
  plan below).

### backend (sc-saas-backend) — Linear SAN-313

- Delete `src/modules/startup-recognition-id/entities/district-master.entity.ts`, `city-master.entity.ts`,
  `subdivision-master.entity.ts`.
- Delete `src/modules/startup-recognition-id/repositories/district-master.repository.ts`,
  `city-master.repository.ts`, `subdivision-master.repository.ts`.
- `entities/state-master.entity.ts`: remove the `@OneToMany(() => DistrictMasterEntity, (data) => data.state) districts`
  relation and its now-dangling `import { DistrictMasterEntity } from './district-master.entity'`
  (**Evidenced**, `state-master.entity.ts:1-31`) — a consequential edit not explicitly named in the
  task's scope list but required once `DistrictMasterEntity` is deleted; `state_master`'s own
  `name`/`countryCode`/`stateCode` columns and table stay untouched, per the explicit out-of-scope list.
- `startup-recognition-id.module.ts`: remove `DistrictMasterEntity`/`CityMasterEntity`/`SubdivisionMasterEntity`
  from `TypeOrmModule.forFeature([...])` and `DistrictMasterRepository`/`CityMasterRepository`/
  `SubdivisionMasterRepository` from `providers` (**Evidenced**, current lines 57-81); update the
  module-level doc-comment, which currently reads "Format config, Location Master
  (District/City/Sub-Division), Standard Geography, and the Digital ID Card template are plain
  admin-configured data" (lines 26-28) — drop the "Location Master (District/City/Sub-Division)"
  parenthetical.
- `services/startup-recognition-id-generation.service.ts`:
  - Remove the `DistrictMasterRepository`/`CityMasterRepository`/`SubdivisionMasterRepository` imports and
    constructor injections (current lines 12-14, 45-47).
  - Remove the `Promise.all([...])` district/city/subdivision lookup block in `generateForStartup()`
    (current lines 83-97).
  - Drop `district`/`city`/`subdivision` from the `ctx` object passed into `resolveSegmentValues()`
    (lines 124-132) and from the `StartupEntity.update()` payload's `districtId`/`cityId`/`subdivisionId`
    keys (lines 147-149) — those properties won't exist on `StartupEntity` once the columns are dropped
    below.
  - Remove the `DISTRICT`/`CITY`/`SUBDIVISION` `case` blocks in the private `resolveSegmentValues()`
    (lines 197-208) — unlike the PHP port, there is no reason to leave this dead code in the canonical
    TypeScript original; also remove `district`/`city`/`subdivision` from that method's `ctx` type
    signature (lines 169-177).
  - **Verified — `state_master` validation is cleanly separable**: `stateMasterRepository`/
    `config.stateMasterId` resolution (lines 77-81) is an entirely independent code path from the three
    repositories being removed; no shared logic, shared query, or shared transaction ties them together.
- `services/startup-recognition-id-generation.service.spec.ts`: update `baseStartup` to drop
  `districtId`/`cityId`/`subdivisionId` (current lines 74-76); remove the
  `districtMasterRepository`/`cityMasterRepository`/`subdivisionMasterRepository` mocks and their three
  constructor args passed into `new StartupRecognitionIdGenerationService(...)` (lines 40-42, 87-95,
  104-106) — none of the test assertions in this file exercise district/city/subdivision behavior, so no
  test cases themselves need to change, only the setup.
- `program-management.module.ts`: remove the `DistrictMasterRepository`/`CityMasterRepository`/
  `SubdivisionMasterRepository` imports (lines 47-49) and their `providers` entries (lines 106-108).
  **Verified — no call-site signature change needed**: `program-management.service.ts` never references
  district/city/subdivision directly anywhere (confirmed by grep); it only calls
  `this.startupIdGenerationService.generateForStartup(startup, { roundId: nextRound.id })` (line 600),
  whose signature is unaffected by this removal — these three repositories were only ever wired into this
  module's DI graph to satisfy `StartupRecognitionIdGenerationService`'s own constructor, never used
  directly by `ProgramsService` itself.
- `src/modules/startup/entities/startup.entity.ts`: remove the `district_id`/`city_id`/`subdivision_id`
  `@Column` definitions and their `districtId`/`cityId`/`subdivisionId` properties (current lines
  217-224). `recognition_id`/`recognition_year`/`state_id`/`serial_no`/`recognition_suffix`/
  `recognition_round_id`/`recognition_generated_at`/etc. all stay untouched.
- `src/core/constants/api-error-message.ts` — **verified, no change needed**. The
  `StartupRecognitionIdErrors`-related comment near line 417-421 already documents that the Format
  Builder/Location Master/Card Template/manual-"Generate ID" error messages were retired earlier (when
  this feature's API-controller layer was deleted during SAN-253's own architecture correction — see that
  spec's Per-repo plan → backend, "No API surface"). No live, district/city/subdivision-specific error
  message exists in `StartupRecognitionIdErrors` today to clean up.
- Re-grepped `DistrictMasterEntity`/`CityMasterEntity`/`SubdivisionMasterEntity`/`district_master`/
  `city_master`/`subdivision_master` across this repo: no hits outside the files listed above.
- `src/core/constants/enum.ts`: remove `DISTRICT = 'district'`, `CITY = 'city'`, `SUBDIVISION =
  'subdivision'` from the `StartupRecognitionIdSegmentType` enum (**Evidenced**, lines 1795-1804) — this
  is the backend-side mirror of admin's `srIdSegmentTypes()` palette, typing
  `StartupRecognitionIdConfigSegment.type`
  (`entities/startup-recognition-id-config.entity.ts:16`). Consistent with the `resolveSegmentValues()`
  case-block removal already planned above. **Must not touch** the separate `StandardGeographyLevel` enum
  immediately below it (lines 1806+, its own unrelated `STATE`/`DISTRICT`/`CITY`/`SUBDIVISION` values for
  the out-of-scope Standard Geography feature).
  **Verified — no data migration and no new failure mode**: `segments` is a `type: 'json'` column with no
  DTO/class-validator layer in front of it (this module has no controller), so TypeORM never validates
  stored JSON against this TS enum at read time — removing enum members only affects compile-time typing
  of new code. At generation time, `resolveSegmentValues()`'s `switch` already has a `default: break;`
  fallback (**Evidenced**, lines 217-218) for any segment `type` it doesn't recognize — once the
  `DISTRICT`/`CITY`/`SUBDIVISION` cases are removed, a tenant's pre-existing saved config containing one
  of those types simply falls through to `default` and is silently skipped, identical in effect to
  today's "omit if unresolvable" behavior. No exception, no migration, no new open question.

## Contracts & invariants

- **Flags:** none touched — `startup_recognition_enabled` and `ecosystem_enabled` are unaffected; no
  flag is added, renamed, or removed.
- **API:** none — this feature has no REST surface at all today (per SAN-253's resolved, direct-DB-access
  architecture: `sc-saas-admin` reads/writes these tables directly via Medoo, `sc-saas-backend` ships no
  `StartupRecognitionIdController`). This removal stays entirely inside direct-DB-access code in both
  repos; nothing for `/audit-contract` to check here.
- **Events:** none — no event/message-bus mechanism exists anywhere in this workspace.
- **Invariants at risk:** none of the six named cross-repo invariants (flag names / API contract /
  tenant-verification shape / auth / tenant scoping / PowerPitch contract) is directly touched — this is
  a removal inside two repos' pre-existing, already-tenant-scoped direct-DB-access code, not a new query
  or endpoint. The real risk here is a **genuine cross-repo deployment-order/schema hazard**, not one of
  the six invariants:
  - `sc-saas-backend` runs with `synchronize: true` in prod (**Evidenced**,
    `src/core/database/database.module.ts:32`). Removing the `district_id`/`city_id`/`subdivision_id`
    `@Column`s from `StartupEntity` will make TypeORM **drop those three columns from the live `startups`
    table** on the next backend deploy — this is the actual destructive schema operation, not a
    hypothetical migration to author separately.
  - If that backend deploy lands **before** admin's removal ships, `sc-saas-admin`'s
    `srIdGenerateForStartup()`/`srIdRegenerateAll()` (which still reference `district_master`/
    `city_master`/`subdivision_master` and still write `district_id`/`city_id`/`subdivision_id` into
    `$updateData` until admin's own changes ship) will start throwing "Unknown column" SQL errors on
    every manual Generate-ID and regenerate-all action, for every tenant, until admin catches up. This is
    why `repos:` is ordered `[admin, backend]` and Rollout below is sequenced accordingly.
  - **TypeORM will not auto-drop the physical `district_master`/`city_master`/`subdivision_master`
    tables themselves** — `synchronize: true`'s schema builder only manages tables it has live entity
    metadata for; once `DistrictMasterEntity`/`CityMasterEntity`/`SubdivisionMasterEntity` are deleted,
    those three tables simply become unmanaged/stale in each tenant DB, not auto-dropped. Only the three
    `startups` columns are destructively affected by this specific change. Physically dropping the three
    orphaned tables, if ever wanted, is a separate, explicit follow-up (see Out of scope).

## Test plan

- **admin:** `php -l` on every edited `.php` file; manual verification: (a) the Location Master
  nav/feature-card is gone from Settings and direct URL access to
  `startup_recognition_management/location_master` errors cleanly (file deleted, no dangling route
  reference); (b) manual "Generate ID" on a startup with no prior `recognition_id` still succeeds and
  assembles a code with any District/City/Sub-Division segment simply omitted, for a tenant whose saved
  format still includes those segment types; (c) Format Builder's existing "save → regenerate all" flow
  still completes with zero SQL errors against a format that lists District/City/Sub-Division as
  configured segments.
- **backend:** `tsc --noEmit` and `npm run lint` clean; update and re-run
  `startup-recognition-id-generation.service.spec.ts` (collision-suffix, serial-padding, idempotency, and
  Spoke-omission suites must all still pass with the three repositories/case-blocks removed); re-run
  `program-management.service.spec.ts` (round-transition generation-idempotency/freeze suites, to confirm
  the DI-wiring change in `program-management.module.ts` doesn't break module bootstrap).
- **cross-repo:** after both repos deploy **in the specified order**, smoke-test: a round-entry trigger
  and a manual Generate-ID action each produce a `recognition_id` matching the tenant's configured
  format, with District/City/Sub-Division segments (where present in that tenant's saved format) silently
  absent; zero SQL/500 errors in either repo; confirm via direct DB inspection that `startups` no longer
  has `district_id`/`city_id`/`subdivision_id` columns post-backend-deploy.

## Rollout

1. **`sc-saas-admin` ships first (SAN-312).** Delete the Location Master screen/nav link/feature-card;
   update `startup_recognition_id_functions.php` to stop reading `district_master`/`city_master`/
   `subdivision_master` and stop writing `district_id`/`city_id`/`subdivision_id`; remove
   District/City/Sub-Division from `srIdSegmentTypes()`, which simultaneously drops them from Format
   Builder's picker and its validation. Startup Recognition ID generation (manual + round-entry, still
   backend-side pending step 2) continues to work identically for every tenant — segments that were never
   resolvable become uniformly unresolvable (the pre-existing "omit" behavior, now permanent) rather than
   erroring. Deploy-safe on its own; does not depend on backend having shipped yet. The palette edit has
   no cross-repo dependency of its own (pure admin-side picker/validation change, no backend API involved)
   so it ships in this same batch rather than needing independent sequencing.
2. **`sc-saas-backend` ships second (SAN-313), only after step 1 is confirmed live in production.**
   Delete the three entities/repositories, remove them from `startup-recognition-id.module.ts` and
   `program-management.module.ts`, drop the three columns from `StartupEntity`, and remove
   `DISTRICT`/`CITY`/`SUBDIVISION` from the `StartupRecognitionIdSegmentType` enum (alongside the
   `resolveSegmentValues()` case-block removal already planned). Because `synchronize: true`
   is always on in prod, **this deploy IS the destructive schema change** (drops
   `startups.district_id`/`city_id`/`subdivision_id`) — it must not land before step 1, or every admin
   Generate-ID/regenerate-all action will error against a still-referencing PHP codebase in the window
   between the two deploys.
3. No flag gating applies (no invariant/flag is touched) and no explicit migration script needs authoring
   — `synchronize: true` performs the schema change automatically on backend deploy. No data migration of
   already-saved `startup_recognition_id_config.segments` rows is needed either — see Per-repo plan for
   why the `default: break` fallback makes this safe.
4. Physical removal of the now-orphaned `district_master`/`city_master`/`subdivision_master` tables
   themselves is out of scope for this rollout (see below) — they become inert, unmanaged tables in each
   tenant DB after step 2, untouched by either repo going forward.

## Out of scope

- Format Builder (any code under `startup-recognition-id` related to ID format configuration) —
  untouched.
- Digital ID Card Design Builder / `digital_id_card_template` table/entity — untouched.
- Standard Geography (`standard_geography` table/entity, `searchStandardGeography` AJAX action) —
  untouched.
- `state_master` table/entity/repository — state-level data and validation stays exactly as-is; only
  district/city/subdivision are removed.
- `startup_recognition_id_config`, `startup_recognition_id_sequence` tables/entities — untouched.
- Physically dropping the orphaned `district_master`/`city_master`/`subdivision_master` tables from each
  tenant DB — `synchronize: true` will not do this automatically once the entities are deleted (see
  Contracts & invariants); a deliberate follow-up if ever wanted, not designed or committed here.
- Optional cleanup of the now-permanently-dead `district`/`city`/`subdivision` `case` blocks in the PHP
  `srIdResolveSegmentValues()` — left in place as harmless dead code per the Per-repo plan → admin note;
  may be tidied in a later pass.

## Open questions

- **[RESOLVED 2026-08-11 by product owner, nirmal.s@sanchiconnect.com]** — decision: **option 2**. Format
  Builder's segment palette also drops District/City/Sub-Division as selectable segment types (see
  Per-repo plan for the resulting `srIdSegmentTypes()` and `StartupRecognitionIdSegmentType` edits), so a
  tenant can no longer re-select a segment that can never resolve to anything. The visible ID-format
  change for tenants who already had these segments configured (below) is accepted as a consequence.
  Follow-up investigation confirmed no data migration of already-saved configs is needed — see Per-repo
  plan → backend for why. Original question text, preserved for context:

- Does the Startup Recognition ID's visible format change
  once District/City/Sub-Division segments are dropped? **Verified from code, not hypothetical:** Format
  Builder (explicitly out of scope, left untouched) still offers District/City/Sub-Division as selectable
  segment types in a tenant's saved `startup_recognition_id_config.segments`. Both segment-resolvers
  already omit a segment silently whenever its value is unresolvable (e.g. a startup with no district
  set) — that "omit, never a placeholder" behavior is pre-existing, not new. Once this spec's removal
  ships, **any tenant that currently (a) has District and/or City and/or Sub-Division included in their
  saved format, AND (b) has startups whose `district_id`/`city_id`/`subdivision_id` currently resolve to
  a real code**, will see that segment silently and permanently disappear from every subsequently
  generated/regenerated `recognition_id` — because the lookup tables and the `startups` columns backing
  them are gone, so the segment becomes unconditionally unresolvable rather than just usually
  unresolvable. This is a real, confirmed behavior change in the ID's rendered string for any tenant
  using those segments today, not merely a theoretical edge case. This investigation had no means to
  check whether any live tenant currently has these segments configured and/or populated (no DB/data
  access) — that data point, plus a decision, are both needed before this spec is approvable:
  1. Is it acceptable for these segments to simply and permanently render empty going forward for any
     tenant currently using them (accepting the visible ID-format change), with **no** companion change to
     Format Builder itself (which stays untouched per this spec's scope)? — or
  2. Should Format Builder's segment palette **also** drop District/City/Sub-Division as selectable
     segment types (a scope change beyond what this spec currently authorizes), so a tenant can no longer
     re-select a segment that can now never resolve to anything?

  Do not guess an answer — route to the product owner before approving this spec.
