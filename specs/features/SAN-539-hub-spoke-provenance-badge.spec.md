---
id: SAN-539
title: Show Hub/Spoke provenance badge on outreach-promoted programs
type: feature
status: approved                # Approved by the document owner 2026-08-30 to begin implementation. Zero
                                 # blocking Open Questions. Document owner explicitly signed off on both
                                 # recorded scope boundaries: no badge for Hub-owned-shared-via-partner this
                                 # pass, and no backfill of promoted_from_tenant_name for already-promoted
                                 # programs.
linear: https://linear.app/sanchiconnect/project/show-hubspoke-provenance-badge-on-outreach-promoted-programs-c56238511c5e
owner: nirmal.s@sanchiconnect.com
repos: [admin, backend, frontend]
                                 # Dependency order per the originating issue's own reasoning: admin defines
                                 # and populates the new column at clone time; backend must expose the new
                                 # column/derived fields before frontend can render them.
contracts:
  api:
    - "GET api/v1/public/application-programs-management (sc-saas-backend, PublicApplicationProgramsController
       → ApplicationProgramService.getAllPublicPrograms() → ApplicationProgramsRepository.getAllPublicPrograms())
       — ADDITIVE response fields only: `isPromoted` (boolean), `promotedFromName` (string | null) on every
       returned program object. No path/method/DTO-shape change."
    - "GET api/v1/application-programs-management (sc-saas-backend, ApplicationProgramController.getAllPrograms(),
       JwtAuthGuard, ?partnerId= query param → ApplicationProgramsRepository.getAllPrograms()) — same additive
       fields as above."
    - "POST api/v1/application-programs-management/applied/:email (sc-saas-backend,
       ApplicationProgramService.getAppliedApplicationsByEmail() → same repository.getAllPrograms()) — same
       additive fields flow through automatically (no separate code path); frontend does not render them here
       in this pass, see Out of scope."
  flags: []                     # No TenantUsersEntity flag gates this feature; it is presentation-only, driven
                                 # off existing `programRequestType`/`partnerId`/`promoteWithPartners` data.
  events: []
tenant_scoped: true             # sc-saas-admin writes the new column into the per-tenant client DB's
                                 # `application_programs` table (selected via `admin_domain`, invariant #5);
                                 # sc-saas-backend reads/derives it from its own one-deployment-per-tenant
                                 # `application_programs` table and its own tenant's `partners` table — no new
                                 # cross-tenant query is introduced beyond the pre-existing `tenant_users`
                                 # name-by-domain lookup pattern already used elsewhere in the same admin file
                                 # (see Evidence).
depends_on: []
created: 2026-08-30
---

# Show Hub/Spoke provenance badge on outreach-promoted programs

## Reference

Originated from Linear issue SAN-539, which itself reflects real investigative work from a prior session (a
research agent read the actual code, not guesswork). This spec independently re-verified every code claim in
that issue against the current repos (see Evidence) before writing the plan below — one framing correction and
one additional in-scope location were found; both are called out explicitly.

Related, previously-authored specs in the same "Hub/Spoke" problem space (read before drafting this one, per
spec-authoring practice #1 — check prior art first):
- **SAN-384** (Multi-Tenant Hub/Spoke Domain & White-Label Architecture, `in-progress`) — its Evidence #11
  documents that `application-program.controller.ts`'s `?partnerId=` query param (the same param this spec's
  Case 2 relies on) is **client-supplied and untrusted**, not derived from the authenticated session — a real
  data-exposure gap, tracked as its own separate bug-fix issue by explicit document-owner decision, deliberately
  **not** bundled into SAN-384's rollout. This spec builds on that same, as-is `partnerId` mechanism (it does
  not read the JWT session itself) — it neither fixes nor worsens that gap. If/when that separate fix lands
  (sourcing `partnerId` from the session instead of the query string), this spec's badge computation needs no
  rework: it consumes whatever `partnerId` value the controller already resolves, wherever that value ends up
  coming from.
- **SAN-392** / **SAN-395** — Spoke Broadcast/partner-visibility features in the same Hub/Spoke ecosystem, but
  confirmed unrelated data paths (`program_promotions`/`application_programs` vs. `associated_partners` on
  stakeholder tables) — no overlap, cited only for the workspace's shared conventions (email-notification
  patterns, `rejection_message`-style column naming), which this spec does not need.

## Evidence — current code state (re-verified this session)

1. **Cross-tenant clone path confirmed, one correction to the issue's framing.** `sc-saas-admin/modules/outreach_requests/list.php`'s `approveRequest` handler (`submitAction == "approveRequest"`, ~line 269) recomputes `approval_status`, then at ~line 353-357 sets `$createProgram = true` only when `is_requested_by_partner === 0 && requested_to_partner_id === null` (a pure tenant-to-tenant request). Inside that block (~line 385-397), when **not** a business challenge, it inserts a new `application_programs` row with `"program_request_type" => "external"` and `"promotion_request_id" => $_POST['recordId']` — exactly as the issue describes. **Correction:** the outer branch guard is `$promotion['is_business_challenge'] === 1` (strict **int** comparison), while the row it inserts on the non-challenge path itself sets `"program_type" => $promotion['is_business_challenge'] === "1" ? "business_challenge" : "normal"` (strict **string** comparison) two lines later. Medoo/PDO typically returns MySQL column values as strings, so `=== 1` is very likely always false in practice — meaning the `challenges`-table clone branch (~line 359-384) is probably dead code today, and **all** clones — including ones meant to be business challenges — land in `application_programs` with `program_type` correctly set to `business_challenge` via the second (string) comparison. This is a pre-existing latent bug, **not fixed by this spec** (out of scope — not requested, and fixing it is a separate, isolated concern), but it matters here: it means a promoted program can plausibly carry `isProgramChallengeType == 'business_challenge'` **and** be outreach-promoted at the same time in the very code path this spec touches, which is part of why the new ribbon must be visually distinct and positioned separately from the existing "Challenge" ribbon (see Frontend plan).
2. **Partner-shared path confirmed exactly as described.** Same handler, ~line 433-512: when `is_accepted_by_partner === 1` and `requested_to_partner_id` is set, no new row is created — the existing `application_programs` row (looked up by `promotion.program_id`) has the requesting partner's id appended to its `promote_with_partners` JSON column (idempotent, checked for existing entries) plus a `partner_promotions` audit array. `sc-saas-backend`'s `ApplicationProgramsRepository.getAllPrograms(includeTestMode, approvalStatus, partnerId)` (`repositories/application-programs.repository.ts:99-154`) confirmed matching this via `programs.partnerId = :partnerId OR (JSON_VALID(...) AND JSON_CONTAINS(programs.promoteWithPartners, ...))` when a `partnerId` is supplied, else filtering strictly to `programs.partnerId IS NULL`. `ApplicationProgramsEntity.promoteWithPartners` (`entities/application-programs.entity.ts:296-297`) confirmed mapped to DB column `promote_with_partners`.
3. **No third path found.** `outreach_requests`'s own `module.spec.md` states this module operates only on `application_programs`/`challenges`, distinct from the unrelated `associated_partners` mechanism (SAN-395) and the unrelated `connections`/`community-connections` module. Grepping the repository and service layer found no other code path that marks a program as foreign.
4. **Which endpoint the frontend actually calls, and when each path is reachable.** `sc-saas-frontend`'s `call-for-applications.component.ts:226` and `active-programs.component.ts:76` both call `PublicApiService.fetchApplicationProgramManagement('true', isPublic, partnerId)` (`public-api.service.ts:129-143`), which routes to **`GET public/application-programs-management`** (unauthenticated `PublicApplicationProgramsController.getAllPublicPrograms()` → `getAllPublicPrograms()` repository method, which **always** filters `partnerId IS NULL`, no `promoteWithPartners` matching at all) whenever `isPublic !== false`, and to the **authenticated** `GET application-programs-management?partnerId=X` (`ApplicationProgramController.getAllPrograms()`, `JwtAuthGuard`, `req.query.partnerId`) only when `isPublic === false`. **Consequence, not stated in the issue:** Case 1 (cross-tenant clone, `program_request_type == 'external'`) is visible on the fully public/anonymous programs page, but Case 2 (partner-shared, `promoteWithPartners`) is **only ever visible to a logged-in partner-portal session** (`profileDetails.partnerId` set) hitting the authenticated endpoint — never to an anonymous visitor or a non-partner logged-in user. This does not change the design, but does scope when Case 2's badge can ever actually render.
5. **Column design confirmed feasible exactly where the issue says.** `sc-saas-admin/modules/application_management/program.php` already resolves a tenant's display `name` from `requested_by_source_domain` via `$mainDatabase->get("tenant_users", "name", ["domain" => $val['requested_by_source_domain']])` in multiple places (e.g. lines 124, 727-729, 1700) — the exact same `$mainDatabase`/`tenant_users` main-DB lookup pattern this spec's admin change needs, just not yet done inside `list.php`'s `approveRequest` clone block. No new endpoint or live cross-service call is required.
6. **`ApplicationProgramsEntity` confirmed to have no such column today** (`entities/application-programs.entity.ts`, full file read) — `promoted_from_tenant_name` would be a genuinely new column, not a rename/reuse. `sc-saas-backend`'s TypeORM datasource runs with `synchronize: true` always on (`core/database/database.module.ts:32`), the same mechanism already used to materialize every other recently-added column in this repo (e.g. `partner-branding`, `startup-recognition-id`) — adding the new `@Column` is sufficient to create it on the next backend deploy, no manual migration needed.
7. **`IProgram` (frontend) already carries several related-but-insufficient fields**: `programRequestType`, `promotionRequestId`, `partnerId`, `partner?: {uuid, name, logo}`, `promoteWithPartners`. None of these are populated as a ready-to-render "is this foreign and who owns it" pair by the list endpoints today — `partner` is only populated on single-program detail fetches (`application-program.service.ts:667,777,892,929,1022`, via `partnerRepository.getPartnerById(program.partnerId)`), never in the list/grid responses this spec's card components consume. `isPromoted`/`promotedFromName` are genuinely new, additive fields.
8. **Card/ribbon pattern precisely re-read.** `call-for-applications-card.component.html` has exactly **one** true corner-ribbon: `<div class="corner-ribbon" *ngIf="program.isProgramChallengeType=='business_challenge'">Challenge</div>`, present in both the `grid` (line 2) and `list` (line 91) template blocks. **Correction to the issue's framing:** "Draft"/"Rejected"/"Unauthorized" are **not** the same `.corner-ribbon` pattern — they render as a plain absolutely-positioned `<span class="badge ... unauth-badge">` (top:8px, left:8px, no rotation; `.scss:17-21`), a visually distinct element. Only "Challenge" is a rotated corner-ribbon (`.scss:39-55`: `width:150px; position:absolute; top:15px; left:-40px; transform:rotate(-45deg)`).
9. **A second, real in-scope location found, not named in the issue.** `sc-saas-frontend/src/app/shared/common-components/active-programs/active-programs.component.html:28` renders the **identical** pattern — `<div class="corner-ribbon" *ngIf="program.isProgramChallengeType=='business_challenge'">Challenge</div>` — inside its own `.program-image` card, sourced from the same `fetchApplicationProgramManagement()` call (`active-programs.component.ts:76`), with its own duplicate `.corner-ribbon` CSS block (`active-programs.component.scss:134-150`, byte-identical geometry to the card component's). This is a genuine "related program-listing view" per the issue's own scope language and must get the same treatment for visual consistency.
10. **"My Applications" is structurally incompatible with the ribbon pattern.** `call-for-applications-applied.component.html` ("My Applied Programs") renders programs as `<table>` rows (`<tr *ngFor="let milestone of allPrograms">`), not `.card`/`.corner-ribbon` markup — there is no ribbon element to extend here at all; the same underlying data (via `fetchApplicationProgramManagementApplied()` → `getAppliedApplicationsByEmail()` → the same repository method) will carry the new `isPromoted`/`promotedFromName` fields once the backend change ships, but rendering them requires net-new table UI (e.g. a badge next to the title or a new column), a different design task. See Decisions/Out of scope.
11. **`programs`/`program-card` and `vs-programs`/`vs-program-card`** render `ProgramsEntity`/vs-programs data — entities the `outreach_requests` promotion mechanism never touches (confirmed by that module's own `module.spec.md`: it operates only on `application_programs`/`challenges`). The provenance concept does not apply there; no code path could ever set these fields on that data.
12. **`PartnerEntity.name`** confirmed (`modules/partner/entities/partner.entity.ts:42-43`, `@Column('varchar', {name: 'name'})`) — the field to resolve for Case 2's owning-partner name.

## Decisions (made this session, with evidence — not left as open questions)

1. **New column:** `application_programs.promoted_from_tenant_name` (`varchar`, `nullable: true`) — TypeORM entity property `promotedFromTenantName`. Populated only for Case 1 (cross-tenant clone) rows, at clone time, in `sc-saas-admin`.
2. **New API fields (both list endpoints):** `isPromoted: boolean` and `promotedFromName: string | null`, computed as follows (backend, per row):
   - `isPromoted = true, promotedFromName = row.promotedFromTenantName` when `row.programRequestType === ProgramRequestType.EXTERNAL` (Case 1 — value already denormalized at clone time, no extra lookup needed at read time).
   - Else, **only when the request supplied a `partnerId`** (i.e. only ever reachable from the authenticated, partner-portal-context endpoint — see Evidence #4) **and** `row.partnerId` is non-null **and** `row.partnerId !== partnerId` (i.e. the row matched via `promoteWithPartners`, not direct ownership): `isPromoted = true, promotedFromName` = the owning partner's `name`, resolved via a single batched `PartnerEntity` lookup over the distinct owning-partner-ids present in the result set (no N+1, no live cross-service call).
   - Else `isPromoted = false, promotedFromName = null` — this is every native/inner-community row, by construction.
3. **Deliberately narrower boundary than the theoretical full Case 2:** when a program is Hub-owned (`row.partnerId IS NULL`) but matched via `promoteWithPartners` (a Hub sharing its own program directly to a partner's portal, with no intermediate clone), this spec does **not** badge it in this pass. Resolving "the Hub's own display name" would require either a new bootstrap-config field on `AppConfigService` or a live cross-service call back to the cockpit — evidence search found no existing local source for a tenant's own display name inside `sc-saas-backend` today, and the resolved design decision for this feature explicitly rules out new cross-service calls at read time. Recorded as a scope boundary (see Out of scope), not a blocking open question — it can be picked up as a small, well-defined follow-up (e.g. add `tenantName` to the bootstrap `tenant-settings` payload, mirroring how `hub_spoke_domain_enabled` was added to that same hand-maintained field list in SAN-384) if the document owner wants full Case 2 coverage later.
4. **Frontend scope resolved with evidence, per Evidence #8-11 (was the issue's one flagged open question):**
   - **In scope:** `call-for-applications-card.component.html`/`.scss` (both `grid` and `list` template blocks) and `active-programs.component.html`/`.scss` (the dashboard "Active Programs" widget) — both already render the identical Challenge corner-ribbon over the same `application_programs`-sourced data, so both need the new ribbon variant for visual consistency.
   - **Out of scope (this pass):** `call-for-applications-applied.component.html` ("My Applications") — table-based rendering with no ribbon/card structure to extend; would need distinct new UI (e.g. a table badge/column), not a copy of the ribbon markup. Flagged as a natural follow-up, not bundled in here to keep this change's blast radius contained to the one existing visual pattern it's extending.
   - **Out of scope (definitively, not applicable):** `programs`/`vs-programs` modules — different entities, the promotion mechanism cannot ever apply to them.
5. **Ribbon visual distinction (issue's point 4):** the new "Promoted" ribbon is placed in the **opposite corner** (top-right, mirrored transform) from the existing "Challenge" ribbon (top-left), in a distinct color, so a program that is simultaneously a business challenge *and* outreach-promoted (a real, reachable combination per Evidence #1's dead-branch finding) shows both without visual collision or ambiguity. Label text is the resolved `promotedFromName`, truncated with CSS ellipsis (rotated ribbon + fixed 150px width cannot reliably fit an arbitrary tenant/partner name) with a native `title` attribute carrying the full name for on-hover/long-press disclosure.

## Problem

Today, a program that a Hub/Spoke community sees only because another community's outreach-promotion request
was accepted — either cloned in wholesale (`program_request_type == 'external'`) or shared in place via
`promoteWithPartners` — renders identically to a program native to the viewer's own community in the public
Programs list and the dashboard's Active Programs widget. Neither list carries any indication of where the
program actually came from, so end users cannot tell a Hub/Spoke-shared program apart from their own
community's programs. This spec adds a small, additive corner-ribbon badge naming the owning community, shown
only for the two confirmed outreach-visibility paths, never for native/inner-community programs.

## Acceptance criteria

- [ ] A cross-tenant-cloned program (`application_programs.program_request_type == 'external'`) returned by
      either `GET public/application-programs-management` or `GET application-programs-management` carries
      `isPromoted: true` and `promotedFromName` equal to the source tenant's `tenant_users.name` at the time it
      was cloned.
- [ ] A native program (no clone, no `promoteWithPartners` entry, or a partner viewing their own
      `partnerId`-owned program) carries `isPromoted: false` and `promotedFromName: null` in the same responses
      — never badged.
- [ ] A partner-portal session (`partnerId` supplied) viewing a program owned by a **different** partner
      (matched via `promoteWithPartners`, not `programs.partnerId = partnerId`) receives `isPromoted: true` and
      `promotedFromName` equal to that owning partner's `partners.name`.
- [ ] Approving a Hub-to-tenant outreach request in `sc-saas-admin`'s `outreach_requests/list/received` view
      (`approveRequest`) populates the new `application_programs.promoted_from_tenant_name` column on the
      cloned row at the moment of cloning, using the same `tenant_users`-by-`requested_by_source_domain`
      lookup pattern already used elsewhere in this repo — no new endpoint, no live cross-service call.
- [ ] `call-for-applications-card.component.html` (both `grid` and `list` views) shows a "Promoted" ribbon,
      positioned and colored distinctly from the existing "Challenge" ribbon, for any program with
      `isPromoted === true`, and shows neither/either ribbon correctly (independently) for a program that is
      simultaneously `isProgramChallengeType == 'business_challenge'` and `isPromoted === true`.
- [ ] `active-programs.component.html`'s dashboard widget shows the same ribbon under the same condition, using
      the same visual treatment (color/position) as the card component, for consistency.
- [ ] `call-for-applications-applied.component.html` ("My Applications") is **not** modified in this pass — the
      new fields are present in its data but not rendered (explicit decision, not an oversight).
- [ ] No existing consumer of either endpoint (frontend or any other caller) breaks — the change is
      purely additive (two new optional response fields, one new nullable DB column).
- [ ] `php -l` passes clean on the changed admin file; backend `npm run build`/`npm test` and frontend
      `npm run build`/`npm test` (scoped to changed files, see Test plan) pass.

## Per-repo plan

### admin

- `modules/outreach_requests/list.php`, inside `approveRequest`'s `createProgram === true` branch (~line
  385-398, the non-business-challenge `application_programs` insert): immediately before building
  `$insertData`, add `$sourceTenantName = $mainDatabase->get("tenant_users", "name", ["domain" =>
  $promotion['requested_by_source_domain']]);` (mirrors the existing pattern in
  `application_management/program.php`, Evidence #5) and add `"promoted_from_tenant_name" =>
  $sourceTenantName` to `$insertData`.
- No change to the `is_business_challenge === 1` (`challenges`-table) branch — per Evidence #1, this branch is
  very likely unreachable dead code today (a pre-existing bug, out of scope to fix here); if it ever does
  become reachable, extending the same lookup into the `$challengeData` array is a natural, separate follow-up
  but is not required for this spec's acceptance criteria (the `challenges` table/UI is not part of this
  spec's scope).
- No change to the `promote_with_partners`/`partner_promotions` block (~line 433-512, Case 2) — that data
  needs no new admin-side column; the name resolution for Case 2 happens entirely in `sc-saas-backend` from
  the already-existing `partners` table.
- `php -l modules/outreach_requests/list.php` before done.

### backend

- `src/modules/application-management/entities/application-programs.entity.ts` — add:
  ```ts
  @Column('varchar', { name: 'promoted_from_tenant_name', nullable: true })
  promotedFromTenantName?: string;
  ```
- `src/modules/application-management/repositories/application-programs.repository.ts` — in both
  `getAllPrograms()` and `getAllPublicPrograms()`, after the existing `.map()` post-processing, add the
  `isPromoted`/`promotedFromName` derivation described in Decisions #2-3:
  - For `getAllPublicPrograms()`: no `partnerId` parameter exists on this method, so only the Case 1 branch
    (`programRequestType === ProgramRequestType.EXTERNAL`) ever applies — no partner lookup needed here at
    all.
  - For `getAllPrograms(includeTestMode, approvalStatus, partnerId)`: apply both branches from Decision #2.
    Collect distinct `row.partnerId` values where `row.partnerId != null && row.partnerId !== partnerId`
    across the result set, batch-fetch via `this.partnerRepository.find({ where: { id: In(ownerIds) } })`
    once, build an id→name map, then attach `promotedFromName` per row from that map (or from
    `row.promotedFromTenantName` for Case 1 rows) — no N+1 query pattern.
- No DTO changes needed — these list endpoints return repository-shaped objects directly (no
  class-transformer allowlist restricting the response), so the two new fields pass through additively; the
  `TransformInterceptor` wraps the whole payload unchanged.
- No controller/route signature changes — `application-program.controller.ts`'s `getAllPrograms()` and
  `public-application-program-management.controller.ts`'s `getAllPublicPrograms()` are unchanged.
- `npm run build` + relevant Jest coverage for `ApplicationProgramsRepository` (new/updated unit test for the
  `isPromoted`/`promotedFromName` derivation, covering: native row, Case 1 row, Case 2 row where viewer owns
  the program, Case 2 row where viewer does not, and the `getAllPublicPrograms()` Case-1-only behavior).

### frontend

- `src/app/core/domain/program.model.ts` (`IProgram`) — add:
  ```ts
  isPromoted?: boolean
  promotedFromName?: string | null
  ```
- `src/app/modules/call-for-applications/call-for-applications-card/call-for-applications-card.component.html`
  — in both the `grid` (near line 2) and `list` (near line 91) blocks, add a second ribbon alongside the
  existing Challenge one:
  ```html
  <div class="corner-ribbon corner-ribbon-promoted" *ngIf="program.isPromoted" [title]="program.promotedFromName">
    {{ program.promotedFromName }}
  </div>
  ```
- `.../call-for-applications-card.component.scss` — add a mirrored variant of the existing `.corner-ribbon`
  block:
  ```scss
  .corner-ribbon-promoted {
    left: auto;
    right: -40px;
    transform: rotate(45deg);
    background: var(--bs-info, #6f42c1); /* distinct from Challenge's var(--color-theme) */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 6px;
  }
  ```
- `src/app/shared/common-components/active-programs/active-programs.component.html` (line ~28) — same
  `*ngIf="program.isPromoted"` ribbon markup added alongside the existing Challenge ribbon inside
  `.program-image`.
- `.../active-programs.component.scss` — same `.corner-ribbon-promoted` block added (this file already
  duplicates the card component's `.corner-ribbon` block independently, per Evidence #9 — no shared
  stylesheet exists between the two components today, so this mirrors that existing duplication rather than
  introducing a new shared-style refactor out of scope for this spec).
- No change to `call-for-applications-applied.component.html`/`.ts`, `programs/program-card`, or
  `vs-programs/vs-program-card` — see Decisions #4 and Out of scope.
- karma/jasmine: extend `call-for-applications-card.component.spec.ts` with cases for `isPromoted` true/false
  and simultaneous `isProgramChallengeType === 'business_challenge'` + `isPromoted === true`; add an
  equivalent case if `active-programs.component.spec.ts` exists, else a manual verification note.

## Contracts & invariants

- **Flags:** none touched or added.
- **API:** two existing `sc-saas-backend` GET-family responses gain two additive, optional fields
  (`isPromoted`, `promotedFromName`). No path, method, or existing-field shape changes on
  `application-programs-management` (public or authenticated) or on the `applied/:email` endpoint that shares
  the same repository method. This is workspace invariant #2 (API contract, owned by `sc-saas-backend`) at its
  lowest-risk category — additive-only — but must still be checked against consumers before `in-review`: run
  `/audit-contract` to confirm no frontend/admin caller does strict/allowlisted response-shape validation that
  an unexpected new field could break (none found during this session's evidence pass — `IProgram` is a
  plain TS interface, not a runtime validator).
- **Events:** none.
- **Tenant scoping (invariant #5):** the new admin write happens inside the already-tenant-scoped
  `approveRequest` flow (per-tenant client DB selected via `admin_domain`, unchanged); the new
  `tenant_users` name lookup is a read against the shared main/tenants DB by `domain` — the same
  cross-tenant-by-design pattern `outreach_requests` already uses elsewhere for tenant display names (Evidence
  #5), not a new isolation gap. The new backend partner-name resolution is a same-tenant `PartnerEntity`
  lookup, fully within the one-deployment-per-tenant model. No new query anywhere reads or writes another
  tenant's *tenant-scoped business data* (only a public display name, already an established exception in
  this exact module).
- **Cross-repo contract impact (spec-authoring practice #4):** the backend's two response shapes are consumed
  by `sc-saas-frontend`'s `IProgram` model and nowhere else (confirmed — no other repo calls these two routes;
  `sc-saas-admin` does not consume `application-programs-management` as a client). This is a genuinely
  two-hop, three-repo change (admin populates → backend exposes → frontend renders) but each hop is additive,
  and the frontend hop is inert until the backend hop ships (an absent field renders no ribbon, not an error).
- **Related, deliberately unaffected invariant:** SAN-384's Evidence #11 (`?partnerId=` being client-supplied,
  not session-derived) is a real, separately-tracked gap this spec's Case 2 depends on as-is. This spec does
  not touch, fix, or worsen it.

## Test plan

- admin: `php -l modules/outreach_requests/list.php`. Manual walkthrough: submit + approve a tenant-to-tenant
  outreach request in staging, confirm the cloned `application_programs` row has
  `promoted_from_tenant_name` set to the requesting tenant's `tenant_users.name`.
- backend: Jest unit tests on `ApplicationProgramsRepository.getAllPrograms()`/`getAllPublicPrograms()`
  covering the five cases listed in the Per-repo plan; `npm run build`.
- frontend: karma/jasmine additions per the Per-repo plan; `npm run build`. Manual visual check: a program
  with both `isProgramChallengeType === 'business_challenge'` and `isPromoted === true` shows both ribbons,
  non-overlapping, on both the CFA card and the Active Programs widget, in both grid and list view.
- cross-repo smoke check: with the backend deployed but before the admin change ships, confirm
  `promoted_from_tenant_name` is simply `null` for all existing rows (column exists, no data yet) and no
  ribbon renders — i.e. the three-repo rollout is safe in any partial-deployment order except the specific
  ordering constraint below.

## Rollout

Although `repos:` lists `[admin, backend, frontend]` in the design/narrative dependency order (admin defines
what the column means; backend must then expose it; frontend then renders it), the **actual safe deploy
order is backend first**: `sc-saas-backend` owns the `application_programs` schema via TypeORM
`synchronize: true` (Evidence #6) — the `promoted_from_tenant_name` column only exists in a given tenant's DB
once that tenant's backend deployment has restarted with the new entity. Deploying the admin change first
would make `list.php`'s `approveRequest` try to write a column that doesn't exist yet, which Medoo will
surface as a hard insert error on every tenant-to-tenant outreach approval until the backend catches up — a
real regression, not hypothetical, given `sc-saas-admin` and `sc-saas-backend` share the same per-tenant
database. Sequencing: **backend deploy (schema materializes, API starts returning the two new
always-additive fields, defaulting to `isPromoted: false` until any row has the new column populated) → admin
deploy (new approvals start populating the column) → frontend deploy (ribbon starts rendering)** — each step
independently safe to hold at, no partial-deployment window produces broken behavior (only a temporarily
un-badged program, never an error), except the admin-before-backend ordering called out above, which must be
avoided per-tenant.

No feature flag is needed — the change is inert (no ribbon, `isPromoted: false`) until: (a) the backend column
exists, and (b) at least one program has actually been cloned/shared since. No backfill is proposed for
programs promoted before this ships — `promoted_from_tenant_name` will be `null` for pre-existing cloned rows
(they simply won't show the ribbon until re-promoted), which is acceptable given the small, cosmetic nature of
this feature; call this out to the document owner as an explicit, low-risk simplification rather than silently
deciding it.

## Out of scope

- Fixing the likely-dead `is_business_challenge === 1` / `=== "1"` type-comparison bug in `list.php`
  (Evidence #1) — pre-existing, unrelated to this spec's acceptance criteria, flagged for a separate ticket.
- Badging a Hub-owned program (`partnerId IS NULL`) shared to a partner via `promoteWithPartners` with the
  Hub's own name (Decision #3) — no local source for a tenant's own display name exists in `sc-saas-backend`
  today without a new bootstrap field or a live cross-service call, both excluded by the resolved design
  decision. Candidate follow-up: add `tenantName` to the cockpit's `getTenantSettings()` hand-maintained field
  list (the same mechanism SAN-384 used to add `hub_spoke_domain_enabled`), then this boundary can close
  without any further design change here.
- Rendering the new fields in `call-for-applications-applied.component.html` ("My Applications") — different
  template structure (table, not card/ribbon); a real follow-up, not bundled in to keep this change's surface
  area contained to the one existing visual pattern it extends (Decision #4).
- Any change to `programs`/`vs-programs` modules — the promotion mechanism does not and cannot apply to that
  data (see Evidence #11 above — the `programs`/`vs-programs` one, not SAN-384's own, differently-numbered
  Evidence #11 cited in Reference — the two documents' evidence lists are independent).
- Fixing SAN-384's Evidence #11 (`?partnerId=` client-supplied/untrusted) — explicitly out of scope, tracked
  separately, referenced only for context (see Reference).
- Backfilling `promoted_from_tenant_name` for programs cloned before this feature ships (see Rollout).
- Any change to the `challenges` table/UI or the `challenges/list.php` clone branch.

## Open questions

None. The issue's one flagged open question (whether "My Applications" and other listing views should get the
badge) is resolved with evidence in Decision #4: two additional real, structurally-compatible views were found
in scope (`call-for-applications-card` grid+list, `active-programs` widget); "My Applications" and the
`programs`/`vs-programs` modules are explicitly out of scope for concrete, evidenced reasons (structural
incompatibility and non-applicable data model, respectively), not left ambiguous.
