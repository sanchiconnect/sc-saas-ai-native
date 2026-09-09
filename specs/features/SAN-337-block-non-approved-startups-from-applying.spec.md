---
id: SAN-337
title: "Global switch: block non-approved startups from applying to any program"
type: feature
status: done                     # implemented, reviewed, and pushed to ai_native_setup across all 3 repos 2026-08-13
linear: https://linear.app/sanchiconnect/project/global-switch-block-non-approved-startups-from-applying-to-any-program-a9f3954035d2
owner: vishali.k@sanchiconnect.com
repos: [tenants, backend, frontend]   # dependency order
contracts:
  api: []                       # no route shape changes — existing routes gain a guard/service-level check, no new endpoints, no DTO changes
  flags: ["approved_startups_can_apply_on_programs"]
  events: []
tenant_scoped: true             # reads tenant_users flag column (tenants) + startup.isApproved (backend, per-deployment tenant DB)
depends_on: []
created: 2026-08-13
---

# Global switch: block non-approved startups from applying to any program

## Problem

Today, a startup whose profile has not been approved by the tenant's admin team can still apply to
any program — both the Program-rounds flow (`program-management.service.ts`'s `startupApply()`) and
the Call-for-Applications (CFA) flow (`application-program.service.ts`'s `applyForProgram()`). Some
tenants want a global, opt-in switch that blocks unapproved startups from applying (to either flow)
and shows an "approval pending" message in place of the apply action.

Nothing like this exists today: no flag, no backend guard/check on either apply path, and no frontend
gating beyond an unrelated per-program "complete your profile" nudge (the `withWithoutProfile: 'with'`
config, checked against `profileCompleteness` — active in `call-for-applications-card.component.ts`,
`program-public-apply.component.ts`, `program-card.component.ts`, and `program-details-modal.component.ts`;
commented out/dead in `program-code-details.component.ts`, `programs.component.ts`,
`call-for-applications.component.ts`, `vs-programs.component.ts`, and two more `vs-program-*`
components). That nudge is about profile *completeness*, not admin *approval* status, and is
per-program (a program setting), not a tenant-wide switch — a related but distinct mechanism from
what this spec adds.

A reusable `ApprovedUserGuard` (`sc-saas-backend/src/core/guards/approved-user.guard.ts`) already
exists and is wired, unconditionally, to three routes (Community Wall comment, Connections
send-request, Meetings-v2 create) — it re-reads the caller's own profile from the DB by
`session.accountType` and throws `Forbidden` if `!isApproved`, regardless of account type. It is
**not** flag-gated and is **not** account-type-aware beyond "whatever type the caller's session says
they are" — it cannot be wired as-is to the CFA route, which serves investor/mentor/corporate/
program_office/service_provider/individual applicants too, not just startups (confirmed in
`application-program.controller.ts`'s own comment, added when this route's `Roles`/`Features`
restriction was deliberately *not* restored during the unrelated SAN-336 auth fix). Applying
`ApprovedUserGuard` there unmodified would block every unapproved non-startup stakeholder too,
which is out of scope for this ask ("block non-approved **startups**").

## Acceptance criteria
- [ ] A new tenant-owned boolean flag `approved_startups_can_apply_on_programs` exists on `TenantUsersEntity`,
      defaults to `false` (off), and is propagated to backend `Feature` enum + `saasFeatures` map and
      frontend `IFeatures`.
- [ ] When the flag is **off** (default), behavior is unchanged for every stakeholder type on both
      apply flows.
- [ ] When the flag is **on**: a startup whose `startup.isApproved` is `false` cannot successfully call
      Program-rounds `POST /:programUUID/apply` (`program-management.controller.ts`) — the backend
      rejects with a new, dedicated `ApiErrors` entry (not reusing `USER_PROFILE_IS_NOT_APPROVED`).
- [ ] When the flag is **on**: a startup whose `startup.isApproved` is `false` cannot successfully call
      CFA `POST /:programUUID/:submissionId/apply` (`application-program.controller.ts`) when the
      resolved submitter is a startup (via `formSubmission.userId` → `user.startupId`) — same rejection
      behavior as above.
- [ ] When the flag is **on**: every other CFA stakeholder type (investor/mentor/corporate/
      program_office/service_provider/individual) is completely unaffected — this is verified
      explicitly in the test plan, since the CFA route resolves applicants generically.
- [ ] When the flag is **on** and a startup is unapproved: browsing/searching the program listing is
      **unaffected** (Open question #1 resolved: block only the Apply action, not the whole programs
      area). The Apply button/link itself renders inline as a disabled/greyed state with the
      approval-pending message shown in its place — no modal/toast, no full-page state (Open question
      #3 resolved). This applies on **both** the Program-rounds and CFA surfaces (Open question #4
      resolved: both flows are in scope).
- [ ] Admin panel (`sc-saas-admin`) is unaffected — this spec's `repos` list intentionally excludes
      `admin`; confirm during implementation that no admin-side apply/preview path needs the same gate
      (admin does not submit applications on behalf of startups via these two routes today — verify
      before closing).

## Per-repo plan

### tenants
- Add one new boolean column to `TenantUsersEntity`
  (`sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts`),
  `name: 'approved_startups_can_apply_on_programs'`, `default: false`, `width: 1`, `type: 'boolean'`. Note:
  `synchronize: true` is on in all envs for this repo — adding a column is safe/additive, but be
  deliberate; this is a pure addition, no rename/removal.
- **CORRECTED post-implementation (this assumption was wrong):** `verifyTenant()` and
  `getTenantSettings()` in `global.service.ts` do NOT generically pass through every
  `TenantUsersEntity` column — each builds its response via an explicit field list. Adding the column
  to the entity alone is not sufficient; the flag must also be added to:
  - `verifyTenant()`'s TypeORM query-builder `.select([...])` list AND its hand-built `features`
    object (two separate places, ~lines 307/629) — this is what the frontend's `tenant.service.ts`
    calls.
  - `getTenantSettings()`'s `select: [...]` list (~line 857 area) — this method auto-classifies any
    *selected* boolean column into `features` generically, so the select-list entry alone is enough
    here. This is what the backend's `sanchiconnect.service.ts` calls at bootstrap.
  Missing this step silently ships a flag that exists in the DB and is wired everywhere else, but
  never actually reaches either consumer — confirmed live: `features` in the API response omitted
  the key entirely (not `false`) until this was fixed (SAN-337 follow-up, 71e4a41).

### backend
- Add the flag to `Feature` enum in `src/core/constants/enum.ts`, matching the tenants column name
  exactly (snake_case string value).
- **Program-rounds flow** (`src/modules/program-management/program-management.service.ts`,
  `startupApply()`): the method already resolves `user` and `startup` (incl. `startup.isApproved`)
  before any mutation, at lines ~290–294. Add a guard clause immediately after the `startup` null-check:
  if `saasFeatures[Feature.APPROVED_STARTUPS_CAN_APPLY_ON_PROGRAMS]` is on and `!startup.isApproved`, throw `ForbiddenException`
  with a dedicated `ApiErrors` message (see Open question #3). This mirrors the existing
  `restrictToRecognitionIdHolders` style of inline service-level gate used in the sibling CFA service.
  The controller (`program-management.controller.ts`) already restricts this route to
  `@Roles(Role.STARTUP)` + `@Features(Feature.STARTUP)`, so every caller here is already guaranteed to
  be a startup — no extra account-type resolution needed.
- **CFA flow** (`src/modules/application-management/application-program.service.ts`,
  `applyForProgram()`): the method already resolves `submittingUser`/`submittingStartup` from
  `formSubmission.userId` (added under SAN-253, lines ~375–384), reused by the existing
  `restrictToRecognitionIdHolders` check right below it. Add an analogous guard clause: if
  `saasFeatures[Feature.APPROVED_STARTUPS_CAN_APPLY_ON_PROGRAMS]` is on **and** `submittingStartup` is non-null (i.e. the applicant
  resolved to a startup) **and** `!submittingStartup.isApproved`, throw `ForbiddenException`. Do
  **not** touch this route's `@UseGuards`/`@Roles`/`@Features` decorators — per the existing comment in
  `application-program.controller.ts`, this route deliberately serves multiple stakeholder types and a
  blanket account-type restriction here would be a regression (SAN-336 territory). Do **not** wire
  `ApprovedUserGuard` to this route — it isn't account-type-aware and would incorrectly block
  unapproved non-startup applicants too.
- Add a new `ApiErrors` entry, `STARTUP_APPROVAL_REQUIRED_TO_APPLY = 'Your startup profile is pending
  approval. You will be able to apply once your profile has been approved.'`, in
  `src/core/constants/api-error-message.ts`, following the existing
  `RESTRICTED_TO_STARTUP_ID_HOLDERS` / `USER_PROFILE_IS_NOT_APPROVED` pattern.
- No DTO or route-shape changes — no `contracts.api` entries. Confirm at implementation time whether
  `saasFeatures` (populated in `src/modules/global/global.service.ts`) needs any change to pick up a
  new boolean key — existing flags suggest it's a passthrough map keyed by `Feature` enum values, so
  likely no service change beyond the enum entry.

### frontend
- Add the flag to `IFeatures` in `src/app/core/domain/brand.model.ts`, matching the backend/tenants
  name exactly.
- Browsing/searching the program listing is **unaffected** regardless of flag/approval state (Open
  question #1 resolved) — no route or section-level gate; only the Apply action itself changes.
- Gate the Apply action **inline** (Open question #3 resolved — no modal/toast, no full-page state) on
  every currently-active, non-dead-code apply entry point for a startup account, on both surfaces:
  - CFA: `call-for-applications-card.component.ts` — audit for any other currently-active CFA apply
    entry point at implementation time; the `withWithoutProfile === 'with'` check around lines
    ~216–235 shows the existing pattern for a similar per-applicant gate, but that one is a Swal popup
    — this new gate instead swaps the Apply button/link itself for a disabled/greyed state with the
    approval-pending message shown in its place (mirrors the message copy chosen for the backend
    `STARTUP_APPROVAL_REQUIRED_TO_APPLY` error, adapted for inline display).
  - Program-rounds: `program-public-apply.component.ts` (lines ~462–533 show the same
    `withWithoutProfile` pattern for reference) and `program-card.component.ts`.
- Only render the inline disabled/pending state when `profileData.accountType === ACCOUNT_TYPE.STARTUP`
  — every other account type's Apply button is unaffected by this flag, consistent with the
  backend-side startup-only scoping.
- No change to `api-endpoint.service.ts` — no new endpoints are being called; this is pure client-side
  gating plus the pre-existing backend rejection as the real enforcement layer.

## Contracts & invariants

- **Flags:** one new tenant-owned boolean flag, `approved_startups_can_apply_on_programs`, added to
  `TenantUsersEntity` → propagated to backend `Feature` enum/`saasFeatures` → frontend `IFeatures`.
  Per workspace invariant #1, `admin`'s `config.php` constants would normally also need this flag —
  but `admin` is **not** in this spec's `repos` list because nothing investigated in `sc-saas-admin`
  today consumes or needs to consume this particular flag (admins aren't blocked from viewing/managing
  applications by approval status). Flag this explicitly for `/trace-flag` review during
  implementation to confirm no admin-side gate is actually needed before treating the 3-repo
  propagation as complete.
- **API:** no route/DTO/contract shape changes. Both affected routes
  (`POST api/v{n}/program-management/:programUUID/apply` and
  `POST api/v{n}/application-programs/:programUUID/:submissionId/apply` — exact versioned paths to
  confirm against the controllers' `@Controller()` base path at implementation time) keep their
  existing signatures; only their internal service logic gains a conditional rejection.
- **Events:** none.
- **Invariants at risk:**
  - *Flag names (#1)* — new flag must land in all three repos in this spec's `repos` list before the
    tenants-side default is flipped on for any tenant; verify with `/trace-flag` before `in-review`.
  - *Tenant scoping (#5)* — backend is one-deployment-per-tenant; `saasFeatures[Feature.APPROVED_STARTUPS_CAN_APPLY_ON_PROGRAMS]` is
    loaded at bootstrap like every other flag, so no new cross-tenant risk. The `isApproved` check
    reads the *current* tenant's own `startup`/`user` rows only (via the existing
    `startupRepository`/`userRepository`, already tenant-scoped by the one-deployment-per-tenant
    model) — no new query pattern introduced.
  - *API contract (#2)* — not touched (no shape change), but flagged here because this spec adds new
    rejection behavior to two routes frontend and (potentially) other clients depend on; document the
    new `ForbiddenException` case in each route's Swagger `@ApiOperation`/error docs.
  - Auth (#4), verification contract (#3), and PowerPitch (#6) — not touched.

## Test plan
- tenants: manual — confirm the new column appears in `verify_tenant`/`tenant-settings` responses with
  the correct default (`false`) for an existing tenant, and that setting it `true` directly in the DB
  round-trips through those endpoints.
- backend: jest unit tests for both `startupApply()` (program-management) and `applyForProgram()`
  (application-management) — flag off/on × approved/unapproved × (CFA only) startup/non-startup
  applicant, asserting the correct accept/reject outcome each time. Explicitly assert non-startup CFA
  applicants are never rejected by this check regardless of flag state.
- frontend: karma/jasmine for the gating logic in the affected apply components (mock
  `brandDetails.features.<new_flag>` on/off, mock startup approval state) — plus manual verification of
  the message copy/placement once Open questions #1/#3 are resolved.
- admin: not applicable — `admin` is out of `repos` for this spec (see Contracts & invariants).
- cross-repo: manual end-to-end smoke on a test tenant with the flag on — attempt CFA apply as an
  unapproved startup (rejected + message shown), attempt CFA apply as an unapproved investor/mentor
  (succeeds, unaffected), attempt Program-rounds apply as an unapproved startup (rejected + message
  shown), then flip the flag off and confirm both flows behave exactly as they do today.

## Rollout
- Ship the tenants column first (default `false`, inert until read) → then backend (flag enum +
  service-level checks, still inert while every tenant's flag value is `false`) → then frontend
  (gating UI, also inert while the flag reads `false`/`undefined`). Enable the flag only for a tenant
  that explicitly requests this behavior, after product confirms the Open questions below.
- No migrations beyond the additive `TenantUsersEntity` column (auto-applied by `synchronize: true`
  per that repo's existing pattern — no manual migration step).

## Out of scope
- Any change to the `withWithoutProfile`/profile-completeness nudge (separate, pre-existing,
  per-program mechanism — not touched by this spec).
- Any change to `sc-saas-admin` — no admin-side consumer of this flag has been identified (see
  Contracts & invariants; revisit if implementation surfaces one).
- Any change to the CFA route's `@Roles`/`@Features`/auth decorators, or to SAN-336's guard
  restoration — this spec adds a service-level, account-type-aware check instead of touching route
  guards, specifically to avoid re-litigating that route's multi-stakeholder auth model.
- Per-program override of this switch — the issue asks for a **global** (tenant-wide) switch; no
  per-program opt-out is being built unless product says otherwise in Open question #4.

## Open questions

All resolved 2026-08-13 (product owner sign-off in conversation, not re-derived by the implementer):

- **(#1) Scope — RESOLVED: block only the Apply action.** Browsing/searching the program listing is
  unaffected when unapproved; no route/section-level gate. Only the Apply button/link itself changes.
- **(#2) Flag name — RESOLVED: `approved_startups_can_apply_on_programs`.**
- **(#3) Message placement/copy — RESOLVED: inline**, replacing the Apply button/link with a
  disabled/greyed state and the pending message in its place — no modal/toast, no full-page state.
  Backend gets its own dedicated `ApiErrors.STARTUP_APPROVAL_REQUIRED_TO_APPLY` copy (not reusing
  `USER_PROFILE_IS_NOT_APPROVED`): "Your startup profile is pending approval. You will be able to
  apply once your profile has been approved." Frontend inline copy may be a shorter adaptation of the
  same message (e.g. "Approval pending") given the smaller UI footprint — finalize exact frontend
  copy length at implementation time against each component's actual layout.
- **(#4) Flows covered — RESOLVED: both.** Program-rounds and CFA are both in scope. CFA's startup-vs-
  other-stakeholder resolution (per Contracts & invariants and the per-repo plan above) still applies
  in full — this is not relaxed by resolving this question.
