---
id: SAN-343                     # sc-saas-backend issue (ships first — schema/enum change; admin's UI depends on it). Admin counterpart: SAN-344. Project: see `linear:` below.
title: Reapplication — Immediate Duration Option
type: feature
status: done                    # Implemented and pushed to ai_native_setup in both repos before this spec was authored — filed retroactively per this workspace's standing Linear-tracking practice.
linear: https://linear.app/sanchiconnect/project/reapplication-immediate-duration-option-3d859525522e
owner: nirmal.s@sanchiconnect.com
repos: [backend, admin]         # DEPENDENCY ORDER — backend's enum value ships first, admin's UI (which sends that value) ships second
contracts:
  api: []                       # No REST route/DTO shape changed — reapplicationDurationType is a pre-existing TypeORM enum column, not a class-validator-guarded DTO field; MySQL's own enum constraint (synchronize:true) is the only validation layer, and it now accepts a 4th value
  flags: []                     # No feature flag involved — Allow Re-application is a per-program boolean column, not a tenant flag
  events: []
tenant_scoped: true             # programs/application_programs rows live in the single tenant DB this deployment is scoped to
depends_on: []
created: 2026-08-14
---

# Reapplication — Immediate Duration Option

## Evidence-tagging convention used throughout this spec
- **Evidenced** — cited to `file:line` in the real codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation, not directly stated.
- `[NOT SPECIFIED IN SOURCE]` — a real gap.

## Linear tracking

- Project: [Reapplication: Immediate Duration Option](https://linear.app/sanchiconnect/project/reapplication-immediate-duration-option-3d859525522e)
- [SAN-343](https://linear.app/sanchiconnect/issue/SAN-343) — sc-saas-backend (this spec's id; ships first)
- [SAN-344](https://linear.app/sanchiconnect/issue/SAN-344) — sc-saas-admin (ships second)

## Problem

Both "Startup Programs" (Program-rounds) and "Custom Programs" (Call for Applications) already support an
"Allow Re-application" toggle: once a startup is rejected from a program, it's normally blocked from
reapplying to the *same* program unless this toggle is on, in which case a configurable cooldown
(`ReapplicationDurationTypes`: `DAY`/`MONTH`/`YEAR` + a numeric duration value) determines how long the
startup must wait before reapplying. Product wants a way to allow reapplication with **zero** wait — an
"Immediate" option — for both program types, without touching the existing Day/Month/Year behavior.

## Acceptance criteria

- [x] `ReapplicationDurationTypes` (`sc-saas-backend/src/core/constants/enum.ts`) has a 4th value,
  `IMMEDIATE = 'immediate'`, alongside `DAY`/`MONTH`/`YEAR`.
- [x] All 3 duplicated activation-date helpers — `ProgramsService.getReapplyActivationDate()`
  (`program-management.service.ts`), `ApplicationProgramService.getReapplyActivationDate()`
  (`application-program.service.ts`), and `ProgramReapplyReminderService.getActivationDate()`
  (`cron/program-reapply-reminder.service.ts`) — treat `IMMEDIATE` as a no-op: the `switch` falls through
  with no date arithmetic, so the returned date equals the rejection date itself. Since the downstream
  check is always `activationDate > new Date()`, an unchanged (already-past) date makes this condition
  false, and the reapplication cooldown is satisfied immediately. `reapplicationTime`/`re_application_duration`
  is not read for this case.
- [x] Both admin pages (`create-program.php` for Program-rounds, `application_management/program.php` for
  CFA) offer "Immediate" as a 4th Duration Type option, hide the Duration Value input when it's selected,
  and always submit `re_application_duration = 0` for that case regardless of whatever value was left in
  the (now hidden) input from a prior Day/Month/Year selection.
- [x] Selecting Immediate does not block form submission. See Watch out for — this required more than
  hiding the input.
- [x] The CFA admin page's duration box no longer has a grey `alert-secondary` background (cosmetic
  cleanup requested alongside the functional fix; the Program-rounds page's box never had this class).

## Per-repo plan

### backend
- `src/core/constants/enum.ts`: added `ReapplicationDurationTypes.IMMEDIATE = 'immediate'`.
- `src/modules/program-management/program-management.service.ts`,
  `src/modules/application-management/application-program.service.ts`,
  `src/modules/cron/program-reapply-reminder.service.ts`: each of the 3 duplicated
  `getReapplyActivationDate()`/`getActivationDate()` methods gained a
  `case ReapplicationDurationTypes.IMMEDIATE: break;` arm.
- `programs`/`application_programs`' `re_application_duration_type` columns are TypeORM `type: 'enum'`
  (MySQL ENUM) — `synchronize: true` auto-migrates the new value on next deploy, no manual migration.
- No DTO change: `reapplicationDurationType` is written via direct entity update, not a class-validator-
  checked request body field — confirmed via repo-wide grep, zero `*.dto.ts` files reference
  `ReapplicationDurationTypes`.

### admin
- `themes/default/html/create-program.php` and `themes/default/html/application_management/program.php`
  (identical duplicated-UI pattern, same as the underlying backend duplication):
  - Added `<option value="immediate">Immediate</option>` to the `#re_application_duration_type` select.
  - Wrapped the Duration Value input in a new `#re_application_duration_value_container` div; hidden
    (initial PHP-rendered state + a `change` handler + the "Allow Re-application" switch's toggle-on
    handler) whenever `immediate` is selected.
  - On submit, `re_application_duration` is now computed as `reApplicationDurationType === 'immediate' ? 0
    : $('#re_application_duration').val()` rather than reading the raw field value — see Watch out for on
    why *hiding* it wasn't sufficient to guarantee a clean `0`.
  - `application_management/program.php` only: removed `alert alert-secondary` from the `#duration`
    wrapper div (grey background, cosmetic).

## Contracts & invariants

- **Flags:** none — Allow Re-application is a per-program column, not a tenant flag.
- **API:** none — no controller/DTO shape changed.
- **Invariants at risk:** none of the 6 workspace invariants apply (no flag, no API contract, no
  tenant-verification shape, no auth, and while this is tenant-scoped data, it's read/written through the
  pre-existing per-deployment scoping, no new query pattern introduced).

## Test plan

- backend: `tsc --noEmit` clean. No new jest tests added — pure enum + no-op switch-case addition, no new
  branching logic beyond what the existing `activationDate > new Date()` check already covers; the 3
  helpers' `DAY`/`MONTH`/`YEAR` cases already have coverage via the existing reapply-cooldown test suites
  (`application-program.service.spec.ts`, `program-management.service.spec.ts`).
- admin: `php -l` clean on both edited files. No test framework exists in this repo (per standing
  convention) — verified manually via live testing during implementation (see Watch out for).
- cross-repo: none — this feature has no cross-repo contract (no flag, no API surface).

## Rollout

Additive-only on both sides (new enum value, new UI option) — existing Day/Month/Year programs are
completely unaffected. `synchronize: true` applies the schema change automatically on the backend's next
deploy; the admin UI changes are effective immediately on deploy (no migration, no data backfill).
Already deployed and live as of this spec's authoring.

## Out of scope

- No change to the `DAY`/`MONTH`/`YEAR` behavior, the `StartupReapplicationHistoryRepository` tracking
  mechanism, or the reapply-reminder cron's scheduling logic beyond the one no-op case added.
- No frontend (`sc-saas-frontend`) change — the reapplication cooldown is entirely backend/admin-side;
  the startup-facing apply flow doesn't display or configure duration type.

## Watch out for

- **Hiding the Duration Value input was not enough to stop it blocking submission.** This admin's bundled
  Parsley build (`themes/default/js/parsley.min.js`) has `excluded: "input[type=hidden]"` — it does
  **not** skip `:hidden` or `:disabled` fields by default, contrary to the common assumption that hiding
  or disabling a field removes it from validation. The input's native `min="1"` HTML5 attribute kept
  being validated even while its container was hidden and the field was `disabled`, so if any leftover
  value (e.g. a stale `0` from switching duration types) sat in the field, submission silently failed with
  "This value should be greater than or equal to 1" and no visible error near the (hidden) field. The
  actual fix required **removing the `min` attribute itself** (not just hiding/disabling) whenever
  Immediate is selected, restoring it when switching back — done in the initial PHP render and both JS
  toggle points (dropdown `change`, and the "Allow Re-application" switch's toggle-on handler) in both
  admin files. Anyone adding a similarly conditional Parsley-validated field in this admin should budget
  for this from the start rather than discovering it via a live "submission silently fails" report.
- The 3 `getReapplyActivationDate()`/`getActivationDate()` copies are an established, deliberate
  duplication (not a shared helper) — this spec's `IMMEDIATE` case had to be added to all 3 independently;
  a future change to this logic must remember to touch all 3 again (see each module's own spec for the
  duplication rationale).
