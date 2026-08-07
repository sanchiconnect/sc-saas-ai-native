---
id: SAN-253
title: Startup ID Creation Module + Program/Round Configuration Controls
type: feature
status: draft                   # NOT approvable — see Open questions
linear: https://linear.app/sanchiconnect/project/startup-id-creation-module-programround-configuration-controls-e357b1f7a805
owner: nirmal.s@sanchiconnect.com
repos: [tenants, backend, sanchiconnect-saas-tenants-admin, admin, frontend]   # dependency order per BRD rollout note
contracts:
  api:
    - "PATCH api/v1/public/global/saas/settings"     # EXISTING, unauthenticated except FeatureGuard — evidenced precedent for the new cross-application call shape (global.controller.ts:51); see Cross-Repo Contract Impact
    - "[NEW — proposed] GET/PUT api/v1/startup-id/config"            # format config read/save+preview
    - "[NEW — proposed] POST api/v1/startup-id/config/regenerate"    # confirm + async chunked regenerate-all
    - "[NEW — proposed] CRUD api/v1/startup-id/locations"             # District/Sub-Division/Hub/Spoke master
    - "[NEW — proposed] GET api/v1/startup-id/geography"              # Standard Geography registry search/match
    - "[NEW — proposed] CRUD api/v1/startup-id/card-template"         # front/back layer templates
    - "[NEW — proposed] GET api/v1/startup-id/:startupId"             # read-only summary (frontend account page, admin startup detail)
    - "[MODIFIED — proposed] existing update-round / reject-round / tentative-round admin-callback DTOs (UpdateRoundDto/RejectRoundDto/TentativeRoundDto, see FE-009 spec) — no shape change, new server-side hook only"
  flags:
    - startup_id_enabled            # NEW — tenants-owned, tenant_users column
    - startup_id_cards               # EXISTING — tenant_users.entity.ts:2127; convergence with startup_id_enabled is an open question, do NOT assume merge
  events: []                        # no domain-event bus exists anywhere in this workspace (evidenced by absence across all module specs read); async regenerate-all needs a job/poll mechanism, not an event
tenant_scoped: true                # every entity lives in the per-tenant DB; no cross-tenant Startup ID registry exists or is proposed
depends_on: []
created: 2026-08-07
---

# Startup ID Creation Module + Program/Round Configuration Controls

## Problem

Startup incubators/accelerators using SanchiConnect need a tenant-configurable, composite Startup ID
(e.g. `TR26-GOM-UDPR-000326`) issued to a startup when it is recognised in a program round, plus a
printable/downloadable Digital ID Card carrying that code — today no such mechanism exists (the only
adjacent feature is the unrelated, tenant-self-service `startup_id_cards` module already in
`sc-saas-admin`/`sc-saas-backend`, evidenced below). Separately, program/round creation needs two new
and two overlapping configuration toggles to support reapply-after-rejection cooldowns and
Startup-ID-gated program eligibility. This spec is sourced from Linear **SAN-253**, which bundles a
fully-reviewed BRD (v1.4, "Startup ID Creation Module") with a second, materially less-specified
requirement ("Program & Round Configuration Controls") that the issue itself says needs its own design
pass. This document traces both against real code per `specs/spec-authoring-practices.md` and carries
forward every unresolved decision rather than inventing answers.

## Evidence-tagging convention used throughout this spec

- **Evidenced** — cited to `file:line` in the real codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation, not directly stated in the source brief or code.
- `[NOT SPECIFIED IN SOURCE]` — a real gap; neither the BRD nor the code says either way.
- `[DESIGN DECISION PENDING]` — a genuinely new decision with no precedent to ground it in.

## Acceptance criteria

**Startup ID module (Part 1)**
- [ ] `startup_id_enabled` exists on `tenant_users`, defaults `false`, is backfilled for existing tenants, and is the sole tenant-side gate surfaced to backend/frontend/admin (no separate master control).
- [ ] A tenant with the flag off sees no Startup ID UI anywhere (frontend panel hidden, admin toggles hidden/disabled, backend routes return `403`/feature-guard rejection even via direct API call).
- [ ] Format Builder (tenants-admin, platform-operator only) lets an operator add/remove/reorder any of Country Code, State Code, Year of Recognition, District, Sub-Division, Hub, Spoke, Serial No. with none locked as mandatory, and preview a sample assembled code + affected-count before saving.
- [ ] Saving a changed format triggers an async, chunked, audited regenerate-all of every existing `StartupIdEntity` row under the tenant, preserving stored source values and only reassembling the string; a segment removed from the format simply disappears from newly-assembled codes.
- [ ] The assembled code is stored in a column/property named `recognition_id`/`recognitionId`, never `startup_id`/`startupId`.
- [ ] The serial counter is atomic (locking read or `INSERT...ON DUPLICATE KEY UPDATE`+`LAST_INSERT_ID`, not `SELECT MAX()+1`), 6-digit zero-padded, continuous, and increments regardless of whether Serial No. is in the visible format.
- [ ] A `recognition_id` collision (or a format that omits Serial No.) triggers an auto-appended disambiguating suffix on write rather than a failed insert or a duplicate; the assembled-code column carries a UNIQUE index as the hard backstop.
- [ ] Round entry generates a Startup ID exactly once per startup ever, only when `generate_startup_id` is true on the triggering round AND the tenant's `startup_id_enabled` is true, checked idempotently at the shared backend round-transition layer (not per admin-UI entry point).
- [ ] `freeze_application` blocks move/reject/mark-tentative on any application already in a frozen round, enforced at the same shared backend layer.
- [ ] Every StartupIdModule mutating endpoint re-checks `Feature.STARTUP_ID_ENABLED` server-side (does not repeat the documented `startup_id_cards`-style render-time-only gating gap).
- [ ] Location Master (tenants-admin) supports District/Sub-Division registry-search-and-match against `StandardGeographyEntity` with a `manual_entry` fallback, and Hub/Spoke auto-suggest (first 3 letters) + manual edit; codes are unique per type per tenant; rows are soft-deleted (`active` flag) since issued `StartupIdEntity` rows may reference them.
- [ ] Digital ID Card Design Builder (tenants-admin) renders a true CR80 (85.6×54mm) canvas, supports static-asset and data-bound layers, and a Preview-with-Sample-Data mode; saves apply immediately with no regeneration step (presentation-only).
- [ ] All three tenants-admin `digital_id_card` screens are reachable only by `super_admin`/`developer` roles, matching the existing `ai_credits` hardcoded role-check pattern.
- [ ] `sc-saas-admin`'s existing round-edit screen gains `Generate Startup ID` (disabled + tooltip when the tenant flag is off) and `Freeze Application` toggles.
- [ ] `sc-saas-frontend`'s account page shows a read-only Startup ID + segment breakdown when the flag is on, and is absent when off.

**Program/Round configuration controls (Part 2)** — acceptance criteria intentionally deferred; see Open questions. This half is not ready for a testable-criteria pass until its own design questions are resolved.

## Per-repo plan
<Dependency order per the BRD's explicit rollout note: cockpit flag → backend module (inert until flag on) → Admin Portal builders → sc-saas-admin toggle+round-toggles → frontend panel → platform operator configures a tenant → tenant flips its toggle → program manager turns on round settings.>

### tenants (sanchiconnect-saas-tenants)
- Add `startup_id_enabled` boolean column to `TenantUsersEntity` (`sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts`), default `false`, alongside the existing `startup_id_cards` column at `tenant-users.entity.ts:2126-2132` — **Evidenced**: `startup_id_cards` already exists there (`name: 'startup_id_cards', width: 1, type: 'boolean', default: false`), confirming both the naming convention and that this is a genuinely new, second/parallel flag, not a rename of the old one.
- Backfill existing tenant rows to `false` on migration.
- This is the only tenant-side control for the whole module — no separate "master" toggle is introduced here; the round-level `generate_startup_id`/`freeze_application` booleans live on the backend's round entities, not on `tenant_users`.
- **[DESIGN DECISION PENDING]** whether `startup_id_cards` (existing) and `startup_id_enabled` (new) converge, and if so how — see Open questions.

### backend (sc-saas-backend)
- New `StartupIdModule` (mirrors the existing module layout convention — controller/service/dto/entities/repositories, per `sc-saas-backend/CLAUDE.md`'s module map).
- **Entities** (all new, per-tenant DB, no existing equivalents found — **Evidenced** by a full-workspace grep for `StartupId`/`recognition_id`/`startup_id_enabled` returning zero code hits before this spec):
  - `StartupIdConfigEntity` — one row/tenant, ordered segment list (JSON: segment type + fixed value for Country/State), delimiter, version.
  - `StartupIdLocationEntity` — District/Sub-Division/Hub/Spoke master; District/Sub-Division optionally FK to `StandardGeographyEntity` + `manual_entry` flag; Hub/Spoke auto-suggested code, no registry.
  - `StandardGeographyEntity` — platform-seeded, read-only reference data (ISO 3166-1/3166-2 + national district codes e.g. India's LGD), seeded per tenant DB at provisioning.
  - `DigitalIdCardTemplateEntity` — one active row/tenant/side (front/back); layer list as JSON.
  - `StartupIdEntity` — one row per issued ID ever; startup ref, triggering round, resolved per-segment source values (all nullable), optional disambiguating suffix, assembled `recognition_id` (UNIQUE index), gen/regen timestamps.
  - `StartupIdSerialCounterEntity` — single row/tenant, atomic increment. **Evidenced anti-pattern to avoid**: `specs/features/FA-001-application-evaluation.spec.md:83` documents a real, live race condition in `sc-saas-admin`'s `generateMentorApplicationNo()` using `SELECT MAX(application_no) + 1` with no DB uniqueness constraint — this module must use `INSERT...ON DUPLICATE KEY UPDATE`+`LAST_INSERT_ID` (or an equivalent locking read) instead, exactly as the companion design doc specifies.
  - `StartupIdRegenerationLogEntity` — append-only audit (actor, timestamp, old/new format snapshot, affected count).
- **Existing entities modified**:
  - `startups` table (`sc-saas-backend/src/modules/startup/entities/startup.entity.ts`): new `sub_division_id` FK column. **Evidenced correction to the source brief**: the brief describes this as "cascading from District exactly like existing Country→State→District," but `startup.entity.ts:59-78` shows the *actual* existing cascade is **Country → State → City** (`registeredCountryId`/`registeredStateId`/`registeredCityId`, joined to `CountriesEntity`/`StatesEntity`/`CitiesEntity` in `sc-saas-backend/src/modules/global/{countries,states,cities}`) — there is **no District level anywhere in the current data model or frontend form**. See Open questions.
  - Round entities: two new booleans, `generate_startup_id` + `freeze_application`. **Evidenced complication**: there are at least **two independent Round entity families** in this codebase, not one — `ApplicationProgramRoundsEntity`/`application_program_rounds` (paired with `ApplicationProgramSubmissionRoundsEntity`, used by the "Call for Applications" flow) and `ProgramRoundsEntity`/`program_rounds` (paired with `ProgramStartupRoundsEntity`, used by the regular Program flow) — confirmed at `sc-saas-backend/src/modules/application-management/entities/application-program-rounds.entity.ts` and `sc-saas-backend/src/modules/program-management/entities/program-rounds.entity.ts`, both independently defining near-identical boolean-flag sets. A third, individual-scoped family exists for Venture Studio (`vs-program-individual-rounds.entity.ts`). See Open questions on scope.
- **Naming constraint** (hard rule, evidenced): do not name the new assembled-code column/property `startup_id`/`startupId` — grep confirms this is the universal FK-to-`startups.id` convention (e.g. `ProgramStartupRoundsEntity.startupId` at `program-startup-rounds.entity.ts:15-16`, `ApplicationProgramSubmissionRoundsEntity` joins on `submissionId` but the pattern recurs 30+ times workspace-wide). Use `recognition_id`/`recognitionId`.
- **Round-transition hooks**: the existing update-round/reject-round/tentative-round admin-callback flow (`UpdateRoundDto`/`RejectRoundDto`/`TentativeRoundDto`, documented in `specs/features/FE-009-programs-applications.spec.md:112`) must be extended, at the shared service layer (not per admin-UI entry point), to (a) generate a Startup ID exactly once, idempotently, when `generate_startup_id` + tenant `startup_id_enabled` are both true, and (b) block move/reject/mark-tentative when `freeze_application` is set on the application's current round.
- **Feature guard**: add `Feature.STARTUP_ID_ENABLED = 'startup_id_enabled'` to the `Feature` enum (`sc-saas-backend/src/core/constants/enum.ts:1021-1101`, currently ending at `AI_CREDITS_ENABLED`). Gate every mutating route with `@Features(Feature.STARTUP_ID_ENABLED)` + `@UseGuards(FeatureGuard)` (`sc-saas-backend/src/core/guards/feature-guard.ts` — confirmed the guard reads `saasFeatures[feature]` set at bootstrap, so a new flag must exist upstream in the cockpit first). **Evidenced precedent for the exact bug to avoid**: `specs/FRS-sc-saas-admin.md:171` documents that the existing `startup_id_cards` flag "is only checked at render time, not re-validated on the POST handler" — every StartupIdModule mutating endpoint must re-check server-side.
- **Format-change flow**: preview (before/after sample + affected count) → confirm → async, chunked, audited regenerate-all (source values preserved; only the assembled string changes; a removed segment's portion disappears).
- **Collision safety**: UNIQUE index on `recognition_id` as hard backstop; auto-append a short disambiguating suffix on write if a format excludes Serial No. (or otherwise collides) rather than fail or duplicate.
- **Cross-application API surface**: format/location/card-template/regenerate endpoints must be callable by both the tenant's own `sc-saas-admin` and the separate `sanchiconnect-saas-tenants-admin` ("Admin Portal"). See Cross-Repo Contract Impact — the only existing precedent for this call shape (`resetAPISaaSSettings()` → `PATCH api/v1/public/global/saas/settings`) is currently **unauthenticated** beyond the class-level `FeatureGuard` (`sc-saas-backend/src/modules/global/global.controller.ts:37-57`, no `@UseGuards(JwtAuthGuard)` on the controller or the `updateSAASSettings` handler; confirmed independently by `sc-saas-backend/src/modules/global/module.spec.md:9,140` — "no auth"). Replicating this pattern for mutating Startup ID config endpoints would be a new instance of the workspace's own documented "unauthenticated-endpoint pattern" guardrail. **[DESIGN DECISION PENDING]**.

### sanchiconnect-saas-tenants-admin ("Admin Portal")
- New `modules/digital_id_card/` — a fifth repo touched, distinct from `sc-saas-admin`, reachable only via the platform operator's tenant switcher (no tenant login reaches it), calling into that tenant's own `sc-saas-backend` StartupIdModule endpoints.
  - **Format Builder**: drag-and-drop, Available Segments palette ↔ Selected Format tray, live preview, no segment locked/mandatory.
  - **Location Master**: CRUD for District/Sub-Division (registry-search-and-match against `StandardGeographyEntity`) and Hub/Spoke (auto-suggest + edit); code uniqueness per type per tenant; soft-delete via `active` flag (Startup IDs reference these rows historically).
  - **Digital ID Card Design Builder**: 3-panel layer editor (Layers list, live Canvas at true CR80 85.6×54mm, Properties panel); static-asset vs bound-field layers; Preview with Sample Data; saves apply immediately, no regeneration needed (presentation-only).
- **Role gate — evidenced precedent confirmed**: all three screens must use the exact same hardcoded role check already protecting `modules/ai_credits/` — `$_SESSION['admin_roles']['code'] == super_admin_role_id || ... == developer_role_id`, confirmed verbatim at `sanchiconnect-saas-tenants-admin/modules/ai_credits/{orders,task_rates,grants,packages}.php:5` and `setup_menu.php:11`; both role-id constants are `define()`d from `$_ENV` in `sanchiconnect-saas-tenants-admin/config/config.php:125-138`. This is **not** the repo's normal flag-based permission system — it is a hardcoded bypass of it, same as `ai_credits`.
- **[DESIGN DECISION PENDING]** the exact service-to-service auth mechanism for these calls into the tenant backend (see backend section + Cross-Repo Contract Impact).

### admin (sc-saas-admin, tenant side only — no format/location/card-design work here)
- Single "Digital ID Card" toggle on the existing Settings/Modules screen (ordinary Settings permission, no new permission needed) that reads/writes the cockpit `startup_id_enabled` flag — same shape as other tenant-side module toggles already on that screen (`sc-saas-admin/config/config.php` flag-constant convention).
- Two new round-configuration toggles beside the existing round-edit controls: **Generate Startup ID** (rendered disabled with a tooltip when the tenant flag is off) and **Freeze Application**. Anchor point: `sc-saas-admin/themes/default/html/edit_program_round.php`, which already renders round-level checkboxes for related booleans (e.g. `jury_can_view_overall_ratings` at line 387, the jury auto-allotment toggle `toggleJuryAutoAllotment` at line 458, backed by `ProgramRoundsEntity.autoAllotJury`/`ApplicationProgramRoundsEntity.autoAllotJury`) — **note**: the source brief's "existing jury call-request control" could not be independently confirmed by that exact name; the nearest evidenced analog is this jury-auto-allotment toggle, cited here rather than the unverified name.
- Read-only Startup ID display on the startup detail page.
- **Convergence note (evidenced, important)**: this repo already ships a fully independent, tenant-**self-service** ID card system — `modules/id_card_builders/` (visual template designer, `module.spec.md` confirms it "writes design settings... into `spa_settings`") + `modules/id_cards/` (issuance/verification, gated on `Feature.STARTUP_ID_CARDS` per `sc-saas-backend/src/modules/id-cards/id-cards.controller.ts:43,57,70` and `sc-saas-backend/src/core/constants/enum.ts:1097`), both gated on the **existing** `startup_id_cards` flag, which is **also already present in `sc-saas-frontend`'s `IFeatures`** (`sc-saas-frontend/src/app/core/domain/brand.model.ts:38`). This new BRD introduces a **second, platform-operator-only** Digital ID Card Design Builder (in tenants-admin) gated on the **new** `startup_id_enabled` flag. These are two different control models (tenant self-service vs. platform-operator-controlled) for what a user would perceive as the same capability. **[DESIGN DECISION PENDING]** — see Open questions.

### frontend (sc-saas-frontend)
- Add `startup_id_enabled` to `IFeatures` (`sc-saas-frontend/src/app/core/domain/brand.model.ts:33-93`, which already declares the sibling flag `startup_id_cards?: boolean` at line 38 — confirms the interface's naming convention to follow).
- Read-only Startup ID summary panel + segment breakdown on the account page, hidden when the flag is off.
- New Sub-Division dropdown on the registration/profile form, visible only when the flag is on. **Evidenced correction**: the source brief describes this as cascading "exactly like existing Country→State→District," but the actual current cascade (`step-one-company-info.component.ts:64-109`) is **Country → State → City** (`registeredCountryId` → `getStates()` → `registeredStateId` → `getCities()` → `registeredCityId`); there is no District selector in the frontend today to cascade a Sub-Division picker from. See Open questions — this may mean a District field must also be newly introduced here, which is not in the source brief's scope list.

## Contracts & invariants

- **Flags:** `startup_id_enabled` (new, owned by `tenants`, propagates to backend `Feature` enum + frontend `IFeatures` + admin `config.php` per invariant #1). `startup_id_cards` (existing, `tenant-users.entity.ts:2127`) is touched only in the sense that its convergence with the new flag is an open question — no code change to it is proposed by this spec.
- **API:** New `StartupIdModule` surface in `sc-saas-backend` (proposed paths listed in frontmatter `contracts.api`, marked `[NEW — proposed]` since no such module exists yet — confirmed by a zero-hit grep for `StartupId` across the workspace prior to this spec). Existing round admin-callback DTOs (`UpdateRoundDto`/`RejectRoundDto`/`TentativeRoundDto`) gain no new fields, only a new internal hook — still a change to backend-owned contract territory (invariant #2), run `/audit-contract` before implementation. `PATCH api/v1/public/global/saas/settings` is cited as the existing precedent for the tenants-admin→backend call shape, not itself modified.
- **Events:** None. No domain-event/message-bus mechanism exists anywhere in this workspace's seven repos (confirmed by the absence of one in every module spec read during this investigation); the async regenerate-all job needs a polling or job-status mechanism, not an event emission.
- **Invariants at risk:**
  - **#1 (flag names owned by tenants):** `startup_id_enabled` is new and must propagate consistently to all four consumers before any repo gates on it — run `/trace-flag` before backend work starts.
  - **#2 (API contract owned by backend):** the entire new `StartupIdModule` surface, plus the round-transition hook change — run `/audit-contract` before frontend/admin/tenants-admin start consuming it.
  - **#4 (auth is JWT):** the cross-application (tenants-admin → tenant backend) call shape is unresolved and its only real precedent is unauthenticated — this is the single highest-risk open item in this spec from an auth-invariant standpoint.
  - **#5 (tenant scoping):** every new entity lives in the per-tenant DB; there is no cross-tenant Startup ID registry, consistent with `sc-saas-backend`'s one-deployment-per-tenant model (`sc-saas-backend/CLAUDE.md` "Tenancy model") — no query here should ever reference another tenant's config/host. `StandardGeographyEntity` is platform-seeded reference data *within* each tenant's own DB (seeded at provisioning), not a shared cross-tenant table.

## Cross-Repo Contract Impact

1. **Backend `Feature` enum + FeatureGuard** — adding `STARTUP_ID_ENABLED` is a contract addition consumers must react to (frontend `IFeatures`, admin `config.php`). No existing route signature changes.
2. **Round admin-callback DTOs** (`UpdateRoundDto`/`RejectRoundDto`/`TentativeRoundDto`) — no field-shape change, but a new server-side side effect (Startup ID generation, freeze enforcement) is added to handlers those DTOs already drive. Any consumer relying on prior handler behavior (e.g., assuming a round transition never fails due to a freeze) must be re-checked — run `/audit-contract`.
3. **Cross-application auth (tenants-admin → tenant backend)** — this is a **new** contract, not a change to an existing one, but it is being modeled on an existing, unauthenticated precedent (`resetAPISaaSSettings()`/`PATCH .../saas/settings`). Per this workspace's own "Unauthenticated-endpoint pattern" guardrail (root `CLAUDE.md`), this must be a deliberate, stated decision before implementation, not a silent copy of the existing gap. **[DESIGN DECISION PENDING]** — see Open questions.
4. **`startup_id_cards` (existing flag/module family) vs `startup_id_enabled` (new)** — no code change to the existing family is proposed, but the two now coexist in the same product surface (ID cards for startups) with different control models. Any future decision to merge/retire one is itself a cross-repo contract change touching `tenants`, `sc-saas-backend` (`id-cards` module), `sc-saas-admin` (`id_card_builders`/`id_cards`), and `sc-saas-frontend` (`IFeatures.startup_id_cards`) — flagged here so it isn't missed later, not resolved now.

## Test plan

- **tenants:** migration test for `startup_id_enabled` column add + backfill; unit test for the entity change.
- **backend:** jest unit tests for `StartupIdConfigService` (format save/preview/regenerate), `StartupIdSerialCounterService` (concurrency test proving no duplicate serials under parallel generation — the exact race class this design is meant to avoid), collision-suffix logic, round-transition hook idempotency (generate exactly once) and freeze enforcement; `/audit-contract` and `/trace-flag` gates before merge.
- **frontend:** karma unit test for the Startup ID panel's visibility toggling on `IFeatures.startup_id_enabled`; manual check of the new Sub-Division field once its cascade design question is resolved.
- **admin:** `php -l` on every edited file; manual verification of toggle visibility/disabled-state logic (Generate Startup ID tooltip when tenant flag off).
- **tenants-admin:** `php -l`; manual verification of the `super_admin`/`developer` role gate on all three new screens (attempt access as a non-privileged role and confirm rejection).
- **cross-repo:** end-to-end smoke — platform operator configures format+locations+card template for a test tenant → tenant flips `startup_id_enabled` on via `sc-saas-admin` → program manager enables `generate_startup_id` on a round → a test startup enters that round → verify a `recognition_id` is generated exactly once, matches the configured format, and the Digital ID Card renders correctly; repeat entry attempt confirms idempotency (no second ID).

## Rollout

1. `tenants`: ship `startup_id_enabled` column, default `false`, backfilled — no behavior change yet.
2. `backend`: ship `StartupIdModule` inert behind the flag (still `false` everywhere) — deploy-safe, no tenant sees any change.
3. `sanchiconnect-saas-tenants-admin`: ship the three Admin Portal builder screens, role-gated — usable by platform operators to pre-configure a tenant ahead of go-live, still invisible to that tenant until its flag flips.
4. `sc-saas-admin`: ship the tenant-side toggle + round-config toggles — the round toggles are meaningless until the tenant flag is on, so ship safely in advance.
5. `sc-saas-frontend`: ship the read-only panel + Sub-Division field, gated on `IFeatures.startup_id_enabled` — safe to ship ahead of any tenant flipping the flag.
6. Platform operator configures a tenant's format/locations/card template ahead of go-live (via tenants-admin).
7. Tenant admin flips `startup_id_enabled` on (via `sc-saas-admin` Settings/Modules).
8. Program manager turns on `generate_startup_id`/`freeze_application` per round as needed.

## Out of scope

- Public QR verification page for a Startup ID / Digital ID Card — **confirmed out of scope this phase** per the source brief.
- Freeze Application "unfreeze" admin override — **confirmed not built this phase**; correction is by direct DB edit only.
- Backfill/bulk-generation tooling to mint Startup IDs for startups approved before the module was enabled — **not committed this phase**.
- Any change to the existing `startup_id_cards` flag, `id_card_builders`, or `id_cards` modules — this spec only notes the overlap; it does not propose merging, retiring, or modifying them.
- Per-program/per-round Digital ID Card template variants — this phase is one active template per tenant per side (front/back) only.
- Delimiter customization beyond a fixed `-` — not part of this phase's Format Builder.
- Part 2's two net-new toggles (Reapply-after-rejection cooldown; Restrict-to-Startup-ID-holders) are explicitly **not** designed to implementation-readiness by this spec — see Open questions; they need their own BRD/design pass at comparable rigor to Part 1 before a per-repo plan can be written for them.

## Open questions
<Non-empty — this spec is NOT approvable until these are resolved by product/dev lead. Carried forward from SAN-253's BRD §13, the Program/Round rough requirement, and code-evidenced findings surfaced while drafting this spec. Do not guess at any of these.>

**Carried from BRD §13 (Startup ID module):**
- [DESIGN DECISION PENDING] Hub/Spoke capture mechanism at generation time — no profile field exists for either today (unlike District/Sub-Division, which at least have a proposed FK); how does the system determine a startup's Hub/Spoke at the moment its ID is generated?
- [NOT SPECIFIED IN SOURCE] Which countries/regions get seeded Standard Geography data in Phase 1 (India/LGD is confirmed; others are not), and what is the fallback experience for an unseeded region — manual entry only, or blocked entirely?
- [DESIGN DECISION PENDING] Should ID generation block for a legacy startup with no Sub-Division on file, or proceed with that segment simply omitted from the assembled code?
- [DESIGN DECISION PENDING] Should a format combining District/Sub-Division with Hub/Spoke in the same code be warned against, blocked outright, or left entirely to admin discretion?
- [DESIGN DECISION PENDING] Serial-counter overflow behavior past `999,999` — hard stop (generation fails/alerts) vs. silently extending to a 7th digit (which would break the "6-digit zero-padded" assumption baked into the format)?
- [NOT SPECIFIED IN SOURCE] Delimiter customization beyond the fixed `-` — confirmed out of scope this phase (see Out of scope), but not designed even conceptually for a possible future phase.
- [DESIGN DECISION PENDING] Exact cross-application (tenants-admin Admin Portal → tenant `sc-saas-backend`) service-to-service auth mechanism. **Evidenced finding sharpening this question**: the only existing precedent for this exact call shape — `resetAPISaaSSettings()` calling `PATCH api/v1/public/global/saas/settings` — is currently unauthenticated beyond a feature-flag guard (`global.controller.ts:37-57`, confirmed no `JwtAuthGuard`; `global/module.spec.md:9` explicitly notes "no auth"). Replicating that pattern for mutating Startup ID config/location/card-template endpoints would create a new set of unauthenticated, cross-tenant-callable, mutating endpoints — a direct instance of the workspace's own documented "Unauthenticated-endpoint pattern" guardrail. This needs a deliberate decision (shared secret header, signed request, scoped service API key, or similar), not a silent copy of the existing gap.
- [DESIGN DECISION PENDING] One-card-template-per-tenant-only limitation — confirmed as this phase's design, but is it an acceptable permanent limitation or a known Phase 2 gap (no per-program/per-round variants)?
- [NOT SPECIFIED IN SOURCE] Card asset upload constraints — file formats, size/resolution limits, RGB vs. CMYK — not specified anywhere in the source material.
- [DESIGN DECISION PENDING] Whether the pre-existing `startup_id_cards` flag/module family (`sc-saas-admin`'s `id_card_builders`+`id_cards`, `sc-saas-backend`'s `id-cards` module, `sc-saas-frontend`'s `IFeatures.startup_id_cards`) converges with the new `startup_id_enabled` family, is retired in favor of it, or is deliberately kept running in parallel as a legacy, tenant-self-service alternative. **Evidenced**: these are two structurally different control models (tenant self-service today vs. platform-operator-only in this new design) for what looks like the same end-user capability — see Cross-Repo Contract Impact item 4.
- [NOT SPECIFIED IN SOURCE] Whether the other 5 Admin Portal roles (reviewer, recruitment_partner, jury, program_manager, analyst) genuinely have zero business need for any part of this module's screens — assumed by the source brief but not validated against real usage.
- Public QR verification page — **resolved**: confirmed out of scope this phase (see Out of scope); listed here only for traceability per the source brief's own framing.
- Freeze Application "unfreeze" override — **resolved**: confirmed not built this phase, direct DB correction only (see Out of scope); listed here only for traceability.
- Backfill/bulk-generation tooling for pre-existing startups — **resolved**: not committed this phase (see Out of scope); listed here only for traceability.

**Code-evidenced findings raised during this spec's drafting (not in the original brief):**
- [DESIGN DECISION PENDING] The source brief assumes an existing Country→State→**District** cascade to hang the new Sub-Division field off of. The actual current cascade, in both `sc-saas-backend/src/modules/startup/entities/startup.entity.ts:59-78` and `sc-saas-frontend`'s `step-one-company-info.component.ts:64-109`, is Country→State→**City** — there is no District level anywhere in the existing data model or UI. Does this feature also need to introduce a first-class District field (backend + frontend) that doesn't exist today, or does Sub-Division need to resolve independently (e.g., a flat registry-search picker, not a cascading dropdown)? This is not answerable from the source material and materially affects the frontend/backend per-repo plans above.
- [DESIGN DECISION PENDING] Which Round entity family/families get the new `generate_startup_id`/`freeze_application` columns? The codebase has at least two independent, structurally parallel Round families — `application_program_rounds` (Call for Applications flow) and `program_rounds` (regular Program flow) — plus a third, individual-scoped Venture Studio family (`vs-program-individual-rounds`) that is presumably out of scope since Startup IDs are company-scoped, not individual-scoped. Confirm both of the first two need the new columns (or just one), and confirm Venture Studio is genuinely excluded.

**Program & Round Configuration Controls (Part 2) — needs its own dedicated design pass, not resolved here:**
- [DESIGN DECISION PENDING] Reapply-after-rejection: is the cooldown enforced at the frontend (gate the reapply button) or the backend (validate at submit time)? Given this workspace's documented precedent of flag/permission checks being bypassable when only enforced client-side, backend enforcement is the safer default — but this is not yet decided.
- [NOT SPECIFIED IN SOURCE, partially evidenced] What tracks the rejection timestamp + cooldown window? **Evidenced prior art**: both existing round-submission entities already carry `rejectedOn`/`rejected_on` (`ApplicationProgramSubmissionRoundsEntity.rejectedOn`, `application-program-submission-rounds.entity.ts:46-47`; `ProgramStartupRoundsEntity.rejectedOn`, `program-startup-rounds.entity.ts:34-35`) plus an existing `isReapplied` boolean on the latter (`program-startup-rounds.entity.ts:68-69`) — these look like a plausible foundation to compute eligibility from, but no column exists yet for a configurable delay period, and it is not decided whether reusing these columns vs. adding new ones is the right approach.
- [DESIGN DECISION PENDING] Is the reapply delay scoped per-program or per-round?
- [DESIGN DECISION PENDING] Restrict-to-Startup-ID-holders: exact UI flow when the applicant is logged out — redirect-to-login vs. an inline prompt?
- [NOT SPECIFIED IN SOURCE, partially evidenced] Where is the admin/program-manager-configured dynamic error message stored? **Evidenced prior art**: both round-submission entities already carry a free-text `rejectionMessage`/`rejection_message` column set per-round by an admin (`application-program-submission-rounds.entity.ts:52-53`, `program-startup-rounds.entity.ts:40-41`) — a plausible precedent for "admin-configured message string stored per program/round," but it is not decided whether to reuse/extend that pattern or add a new column, nor which entity/level (program vs. round) it belongs on.
- [DESIGN DECISION PENDING] Is the Startup-ID-holder gate frontend-only or also backend-enforced? This workspace has a documented, real precedent of a flag (`startup_id_cards`) being checked only at render time and bypassable via direct API call (`specs/FRS-sc-saas-admin.md:171`) — that precedent is a strong argument for requiring backend enforcement here, but it has not been decided, and this spec does not assert it as already resolved.
- This entire second toggle pair (reapply cooldown + Startup-ID-holder restriction) needs its own requirements/design pass — data model, access control, edge cases, cross-repo impact — at comparable rigor to the BRD covering Part 1, before any per-repo implementation plan can be written for it.
