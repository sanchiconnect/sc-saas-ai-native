---
id: SAN-497
title: Remove Save Button and Add Auto-Save to Profile-Completion Form
type: feature
status: approved                # all open questions resolved below (decisions recorded 2026-08-24)
linear: https://linear.app/sanchiconnect/project/remove-save-button-and-add-auto-save-to-profile-completion-form-85677eea7fcb
owner: mahima.s@sanchiconnect.com
repos: [frontend]                # sc-saas-frontend only — backend contracts are untouched per acceptance criteria; all save calls reuse existing endpoints
contracts:
  api: []                        # no endpoint added/changed — every save call reuses an existing per-type/per-form endpoint (see Per-repo plan)
  flags: []                      # no flag added/changed — pre-existing gates on individual steps/sections (e.g. industries_technologies_section) are untouched
  events: []
tenant_scoped: true              # the reused save endpoints write per-tenant profile data on the tenant's own one-deployment-per-tenant backend (invariant #5); auto-save doesn't add new tenant-scoped surface but it does fire more writes against existing tenant-scoped data than today's manual-Save flow
depends_on: [SAN-496]
created: 2026-08-24
---

# Remove Save Button and Add Auto-Save to Profile-Completion Form

## Evidence-tagging convention used throughout this spec

- **Evidenced** — cited to `file:line` in the real `sc-saas-frontend` codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation from code, not a full manual UI click-through.
- `[DESIGN DECISION PENDING]` — a genuine product/UX or architecture choice this spec deliberately does not make; routed to Open questions. (None remain open in this revision — see "Design decisions" below.)

## Linear tracking

- Origin: [SAN-497](https://linear.app/sanchiconnect/issue/SAN-497/remove-save-button-and-add-auto-save-to-profile-completion-form) — "Enhancement" project, milestone "Profile Autosave".
- Depends on [SAN-496](https://linear.app/sanchiconnect/issue/SAN-496/blast-radius-current-behavior-assessment-profile-form-auto-save) (done, approved) — this spec builds directly on its findings rather than re-deriving them; see `specs/features/SAN-496-profile-form-autosave-blast-radius-assessment.spec.md`.
- Dedicated Linear Project created: [Remove Save Button and Add Auto-Save to Profile-Completion Form](https://linear.app/sanchiconnect/project/remove-save-button-and-add-auto-save-to-profile-completion-form-85677eea7fcb), lead Mahima Sharma. SAN-497 has been linked into it (moved Backlog → Todo, labeled `["Feature", "Repo: Frontend"]`, priority High) rather than duplicated into a separate "Frontend — ..." issue, since SAN-497 already *is* the frontend-scoped work this spec describes.
- Assignee: Mahima Sharma (confirmed, matches current Linear assignee on SAN-497).

## Problem

Per the BRD "Stakeholder Profile Forms Auto-Save, and Guide Users Instead of Letting Them Wander Off Incomplete," every stakeholder type's profile-completion form requires an explicit Save click today, and SAN-496 confirmed this is duplicated per-type (not shared) UI. Users lose in-progress edits if they navigate away or close the tab without clicking Save. This issue removes the Save button everywhere in the profile-completion form and replaces it with a fixed-interval auto-save (plus a best-effort tab-close save) that reuses each step's existing save call.

## Findings (this issue's own investigation, building on SAN-496)

### A. How each type's Save button currently triggers its save call

**Evidenced** for all 8 stakeholder types plus a 9th variant SAN-496 flagged but did not code-check (Individual-Investor). In every case, the "Save" button is a plain `type="submit"` button that is a **sibling of**, not inside, the shared `<app-form-next-step-button>` — confirming item 2's ambiguity is resolved: **Save is rendered outside the shared component, per type** (see finding B). The shared component itself (`shared/common-components/form-next-step-button/form-next-step-button.component.ts`) has no Save-related code at all — it only emits `(next)` / drives `handlePreviousClick()`, both calling `CommonService.goToNextPage()`/`goToPreviousPage()`. It requires no change to become "Next/Previous-only" — **it already is**.

| Type | Step component | Save trigger mechanism | Save handler → service call | Also called by Next Step? |
|---|---|---|---|---|
| Startup | `modules/startups/pages/edit/startup-information/startup-information.component.html:1917-1943` (`.ts:627`) | plain `(click)="onSubmit()"` on the Save `<button>` (not inside a `<form>`) | `onSubmit()` — dispatches `StartupActions.SaveStartUpInfo`, then `startUpService.saveProductInfo()`, `pitchDeckService.updateElevetorPitch()`, `handleBusinessModelSave()`, `onSaveAdvisory()`, `onSaveFounders()` — **5 separate side-calls bundled into one Save click** (`.ts:627-679`) | Yes — `handleNext()` (`.ts:760-763`) calls `goToNextPage()` then `onSubmit()` |
| Individual | `modules/individual-profile/pages/individual-profile-edit-form/individual-profile-edit-form.component.html:868-880` (`.ts:148`) | `<form [formGroup]="corporateForm" (ngSubmit)="onSubmit()">` (`.html:20`) — button has no `(click)`, submits via form `type="submit"` | `onSubmit()` → `individualProfileService.patchInvididualProfileInfo()` (`.ts:148-160`) | Yes — `handleNext()` (`.ts:294-295`) |
| Investor (org) | `modules/investors/pages/edit/organization-details/organization-details.component.html:754-767` (`.ts:269`) | `(ngSubmit)="onSubmit()"` on the form | `onSubmit()` → `investorService.patchInvestorOrganizationInfo()`, then **unconditionally `this.router.navigate(['investors/edit/investments-details'])` inside the success callback** (`.ts:269-289`) | Yes — `handleNext()` (`.ts:339-340`) |
| Investor (individual-investor variant) | `modules/investors/pages/edit/individual-investor-edit-form/individual-investor-edit-form.component.html:15` (`.ts:251`) — a 9th step component SAN-496 flagged (item 2) but did not code-check for Save presence | `(ngSubmit)="onSubmit()"` | `onSubmit()` → `investorService.patchInvestorOrganizationInfo()` — **no navigate call** (`.ts:251-260`) | Yes — `handleNext()` (`.ts:323-324`) |
| Corporate | `modules/corporate/pages/edit/corporate-intro/corporate-intro.component.html:1014-1039` (`.ts:156`) | `(ngSubmit)="onSubmit()"` (`.html:31`) | `onSubmit()` → `corporateService.patchCorporateInfo()` (`.ts:156-178`) | Yes — `handleNext()` (`.ts:374-375`) |
| Mentor | `modules/mentors/pages/edit/mentor-intro/mentor-intro.component.html:963-979` (`.ts:154`) | `(ngSubmit)="onSubmit()"` (`.html:25`) | `onSubmit()` → `mentorService.patchMentorInfo()` (`.ts:154-166`) | Yes — `handleNext()` (`.ts:303-304`) |
| Partner | `modules/partners-dashboard/pages/edit/partner-intro/partner-intro.component.html:708-724` (`.ts:221`) | `(ngSubmit)="onSubmit()"` (`.html:41`) | `onSubmit()` → `partnerService.patchPartnerInfo()` (`.ts:221-230`) | Yes — `handleNext()` (`.ts:292-293`) |
| Service Provider | `modules/service-provider/pages/edit/service-provider-intro/service-provider-intro.component.html:742-758` (`.ts:147`) | `(ngSubmit)="onSubmit()"` (`.html:22`) | `onSubmit()` → `serviceProviderService.patchServiceProviderInfo()` (`.ts:147-159`) | Yes — `handleNext()` (`.ts:299-300`) |
| Program Office | `modules/program-office/edit/program-office-intro/program-office-intro.component.html:747-758` (`.ts:153`) | `(ngSubmit)="onSubmit()"` (`.html:16`) | `onSubmit()` → `programOfficeService.patchProgramOfficeInfo()` (`.ts:153-165`) | Yes — `handleNext()` (`.ts:304-305`) |

**Critical finding — a real landmine for the naive approach:** Investor (org)'s `onSubmit()` unconditionally navigates the user to `/investors/edit/investments-details` inside its save success callback (`organization-details.component.ts:282`). If auto-save simply re-invokes `onSubmit()` on a timer, it will **forcibly navigate the user off the page every interval tick** — clearly wrong. Resolved below: this method is split into a pure "persist" call and a navigate step. No other type's `onSubmit()` navigates.

**Startup's `onSubmit()` is not a single call** — it bundles five separate service/store calls. Resolved below: auto-save decomposes this into targeted per-section calls rather than re-firing all five every tick.

### B. Shared form-next-step-button — confirmed Next/Previous-only already

**Evidenced.** `form-next-step-button.component.ts`/`.html` contain no Save button, no save-related method, and no `@Input`/`@Output` referencing save. Save is rendered by each type's own step template as a sibling `<button>`/form-submit, never inside this shared component. **No change needed to this shared component's scope** — it already is Next/Previous-only. This resolves SAN-496's open ambiguity on item 2 (whether Save is inside or outside the shared component): it is **outside**, confirmed for all 9 step variants.

### C. Tenant-admin-configured "custom form" tabs — DO have their own Save button (not fully surfaced by SAN-496)

**Evidenced — a real 10th site SAN-496 flagged only as a tenant-scoping note, not as a Save-button site.** Every stakeholder type's nav-links dynamically injects tenant-admin-configured custom forms as extra tabs (SAN-496 §"Per-tenant customization found"). Each such tab routes to a per-type wrapper component (`extra-info-startup`, `extra-info-service-provider`, `extra-info-partners`/`extra-intro-mentors`, `extra-info-investor`, `extra-info-individual`, `extra-info-corporate` — one per type, duplicated wrappers, confirmed via `Glob`), but **all of them render the same shared `<app-event-forms [formInstance]="form" [profileForm]="true">` component** (`modules/dynamic-forms/event-forms/event-forms.component.ts`).

`EventFormsComponent` has a live Save button, gated by `isDisabled` (`!dynamicFormGroup.valid`), wired to `updateParticipationDetails()` (`event-forms.component.html:151-161`, `.ts:263-282`), which calls `formManagemenetService.saveFormsSubmission(formInstance.uuid, { data, formUUID })` — an **existing endpoint, already reused** by the "Next Step" click (`handleNext()` at `.ts:158-161` calls the same `updateParticipationDetails()` after navigating). This component does **not** already auto-save (unlike its sibling `ApplicationProgramManagementDynamicFormComponent`, which SAN-496 item 6 found does auto-save via `setInterval`) — `EventFormsComponent.handleSubmit()` is a dead stub (`.ts:367-369`, just `console.log`s) and is not wired to the live template.

**Conclusion for item C:** because all 8 types' custom-form tabs funnel through this one shared `EventFormsComponent`, removing its Save button and adding the fixed-interval auto-save here is a **single-component fix that covers all 8 types' custom tabs at once** — much lower blast radius than the 9 duplicated primary-step components in finding A. Confirmed in-scope for SAN-497.

### D. CFA precedent detail relevant to auto-save behavior (extends SAN-496 item 6)

**Evidenced.** `ApplicationProgramManagementDynamicFormComponent`'s `setInterval` (`.ts:511-515`) calls `updateParticipationDetails(true)` unconditionally on every tick, with no dirty-check, defaulting to 20000ms via `formInstance.autoSaveTimer`. The interval is cleared on unmount/submit (`.ts:499-501`, `:870-874`, `:890-892`) and re-armed each time `initiateParticipation()` runs. Resolved below: SAN-497 matches the 20s duration for consistency, but adds a dirty-check the CFA precedent doesn't have (product decision, see "Design decisions").

## Design decisions (resolved 2026-08-24)

All open questions from the draft revision of this spec are resolved as follows:

1. **Tab-close safety.** In addition to the fixed interval, add a best-effort save triggered on `beforeunload`/`visibilitychange` (fired when the tab is hidden/closed), so a user who fills a field and immediately closes the tab is actually covered — satisfying the literal acceptance criterion rather than relying on the interval alone.
2. **Dirty-check.** Auto-save only fires when the relevant form/section is dirty since the last successful save (own or auto), not unconditionally every tick — this deliberately diverges from the CFA precedent (finding D) to avoid redundant writes across 9 step components plus the shared custom-form-tab component. Mark the form pristine (`markAsPristine()`) after each successful save (manual-equivalent or auto) so the dirty check has an accurate baseline.
3. **Coverage scope.** This pass covers only what's code-verified in findings A/C: the 9 primary-step variants (8 stakeholder types + the Individual-Investor variant) and `EventFormsComponent` (tenant custom-form tabs). Secondary tabs — Corporate Engagement, Mentor Domain Expertise, Investor Investment/Representative Details, Partner Industry/Technology, and any other non-primary step SAN-496 didn't audit — are explicitly **out of scope** for SAN-497 (see Out of scope) and are recorded as a follow-up, not silently dropped.
4. **Startup's bundled `onSubmit()`.** Decompose into targeted per-section auto-save calls — `SaveStartUpInfo`/`saveProductInfo`/`updateElevetorPitch`/`handleBusinessModelSave`/`onSaveAdvisory`+`onSaveFounders` each fire independently, gated by their own sub-form's dirty state, rather than re-firing all five together every tick. The manual "Save"-equivalent path (now the Next-Step and beforeunload paths) may still invoke the full aggregate.
5. **Interval scope.** Per mounted step/tab component — the timer starts on mount and is cleared on destroy (matching the existing routed-component lifecycle where each step is its own component instance), not a single session-wide timer surviving navigation.
6. **Interval duration.** 20 seconds (20000ms), matching the CFA precedent (`ApplicationProgramManagementDynamicFormComponent`'s default `autoSaveTimer`), for consistency across the codebase's two auto-save implementations.
7. **Investor org navigate-on-success landmine.** `organization-details.component.ts`'s `onSubmit()` is split into a persist-only method (called by auto-save, the beforeunload hook, and internally by the existing manual path) and a separate navigate step that runs only after a successful save triggered from the explicit Next-Step click (`handleNext()`) — auto-save and the tab-close hook never navigate.
8. **Assignee.** Mahima Sharma (matches current Linear assignee on SAN-497), for the whole project (single-repo scope).

## `/check-isolation` gate (run 2026-08-24)

Tenant-isolation review found no cross-tenant leak: auth is a browser-managed httpOnly cookie attached by a globally-registered interceptor to every `HttpClient` call regardless of trigger (click, timer, or `beforeunload`), so firing existing save calls more often doesn't bypass any tenant-context guard. It did surface 5 concrete implementation requirements, folded into the per-repo plan and acceptance criteria below rather than left as a separate report:

1. The `beforeunload`/`visibilitychange` save **must** call through the same existing `HttpClient`-backed service methods used today — never a raw `fetch()`/`navigator.sendBeacon()`, either of which risks silently dropping the cross-origin auth cookie (no `credentials:'include'` by default on `fetch`; `sendBeacon` can't set `credentials` at all).
2. `EventFormsComponent.updateParticipationDetails()` (§C) needs an in-flight guard — nothing today stops the interval tick, the `beforeunload` save, and `handleNext()` from racing to the same submission once auto-save is wired in.
3. Each of Startup's 5 decomposed per-section auto-saves (decision 4) needs the same in-flight guard, for the same reason.
4. The Investor-org persist/navigate split (decision 7) must be verified so `router.navigate` is reachable only from `handleNext()`'s explicit path, never from the persist-only method used by the timer/`beforeunload`.
5. Two `console.log` sites that echo save payloads/responses (`event-forms.component.ts:115,276`, `startup-information.component.ts:618`) must be removed as part of this change — today they log once per manual Save click; left in place, they'd echo PII-bearing data to the console roughly every 20s instead.

## Acceptance criteria

- [ ] Save button (the plain submit button described in finding A) no longer renders in any of the 9 primary-step components (8 stakeholder types + the Individual-Investor variant).
- [ ] Save button no longer renders in `EventFormsComponent` (finding C), covering all 8 types' tenant-admin-configured custom-form tabs.
- [ ] Each removed Save button's save call is preserved and now fires on a 20-second fixed interval while its step/tab is mounted, using the same existing endpoint/service call as today (no new endpoints) — per finding A's table and finding C — but only when the relevant form/section is dirty since the last successful save (decision 2).
- [ ] A best-effort save fires on `beforeunload`/`visibilitychange` (tab hidden/closed) in addition to the interval, so a user who edits a field and immediately closes the tab does not lose that edit (decision 1).
- [ ] Startup's auto-save fires its five sub-form saves independently, gated by each sub-form's own dirty state, rather than re-firing the full bundled `onSubmit()` aggregate every tick (decision 4).
- [ ] Investor (org)'s `onSubmit()` is refactored so the navigate-to-next-step call is no longer coupled to the save action — auto-save and the beforeunload hook persist without ever navigating; only the explicit Next-Step click navigates after a successful save (decision 7).
- [ ] The auto-save interval is cleared on component destroy/navigation-away for every step/tab (mirroring the CFA precedent's `clearInterval` on unmount, scoped per decision 5), so no orphaned timers keep firing after the user leaves a step.
- [ ] No new backend endpoint or DTO is introduced; every auto-save call reuses the exact service method the corresponding manual Save button called today (finding A/C).
- [ ] The `beforeunload`/`visibilitychange` save calls through the same `HttpClient`-backed service methods as the interval/manual paths — no raw `fetch`/`sendBeacon` bypassing the auth interceptor (`/check-isolation` gate, item 1).
- [ ] `EventFormsComponent.updateParticipationDetails()` and each of Startup's 5 decomposed sub-form saves have an in-flight guard so the interval, `beforeunload`, and `handleNext()` can't race to the same save target (`/check-isolation` gate, items 2–3).
- [ ] The two PII-echoing `console.log` sites (`event-forms.component.ts:115,276`, `startup-information.component.ts:618`) are removed (`/check-isolation` gate, item 5).
- [ ] No change to how the backend stores or recalculates profile completeness — this remains a frontend interaction change only.
- [ ] Manual verification: for each of the 9 primary-step types and at least one tenant-admin custom-form tab, (a) typing into a field and waiting one interval period results in the value being present after a full page reload without any explicit save action, and (b) typing into a field and immediately closing the tab (before 20s elapse) also results in the value being present on return.

## Per-repo plan

### frontend

Dependency order within this single repo (no cross-repo work — see Contracts & invariants):

1. **Shared auto-save utility.** Add one small reusable helper (e.g. an interval-based directive/service, or a mixin method) implementing: a 20s fixed interval (decision 6), scoped to the mounting component's lifecycle and cleared on destroy (decision 5), a dirty-check gate before each tick's save call (decision 2, using `FormGroup.dirty` + `markAsPristine()` after success), and a `beforeunload`/`visibilitychange` listener performing one best-effort save attempt if the form is dirty at that moment (decision 1). Mirrors the pattern already proven in `ApplicationProgramManagementDynamicFormComponent` (`setInterval` + `clearInterval` on destroy) but decoupled from that component's `FormSubmissionsEntity`-specific bits, per SAN-496 item 6's conclusion that the pattern is reusable but the mechanism is not. Location: a new file under `shared/utils/` or `shared/common-components/`, not a new backend-facing service.
2. **`EventFormsComponent`** (`modules/dynamic-forms/event-forms/event-forms.component.ts`/`.html`) — remove the live Save button (§C, `.html:151-161`); wire the new interval helper (dirty-gated, 20s, per-mount, plus beforeunload) to call the existing `updateParticipationDetails()`; the component already has `ngOnDestroy()` (`.ts:257-259`) — extend it to tear down the new timer/listener, reusing the existing `destroyed$` Subject pattern. Covers all 8 types' custom-form tabs in one change.
3. **Startup** — `modules/startups/pages/edit/startup-information/startup-information.component.ts`/`.html` — remove the Save `<button>` (`.html:1917-1943`); per decision 4, decompose the auto-save wiring into independent, dirty-gated calls to `SaveStartUpInfo` (store dispatch), `saveProductInfo()`, `updateElevetorPitch()`, `handleBusinessModelSave()`, and `onSaveAdvisory()`/`onSaveFounders()`, each keyed off its own sub-form's `dirty` state; keep the full aggregate available for the explicit Next-Step/beforeunload paths.
4. **Individual** — `modules/individual-profile/pages/individual-profile-edit-form/individual-profile-edit-form.component.ts`/`.html` — remove the Save button (`.html:868-880`); wire interval+dirty-check+beforeunload to `onSubmit()` (single call, no decomposition needed).
5. **Investor (org)** — `modules/investors/pages/edit/organization-details/organization-details.component.ts`/`.html` — remove Save button (`.html:754-767`); per decision 7, split `onSubmit()` into a persist-only method and a navigate step; wire interval+dirty-check+beforeunload to the persist-only method; keep navigation only in `handleNext()`'s explicit path after a successful persist.
6. **Investor (individual-investor variant)** — `modules/investors/pages/edit/individual-investor-edit-form/individual-investor-edit-form.component.ts`/`.html` — remove Save button; wire interval+dirty-check+beforeunload to `onSubmit()` (no navigate landmine here).
7. **Corporate** — `modules/corporate/pages/edit/corporate-intro/corporate-intro.component.ts`/`.html` — remove Save button (`.html:1014-1039`); wire interval+dirty-check+beforeunload to `onSubmit()`.
8. **Mentor** — `modules/mentors/pages/edit/mentor-intro/mentor-intro.component.ts`/`.html` — remove Save button (`.html:963-979`); wire interval+dirty-check+beforeunload to `onSubmit()`.
9. **Partner** — `modules/partners-dashboard/pages/edit/partner-intro/partner-intro.component.ts`/`.html` — remove Save button (`.html:708-724`); wire interval+dirty-check+beforeunload to `onSubmit()`.
10. **Service Provider** — `modules/service-provider/pages/edit/service-provider-intro/service-provider-intro.component.ts`/`.html` — remove Save button (`.html:742-758`); wire interval+dirty-check+beforeunload to `onSubmit()`.
11. **Program Office** — `modules/program-office/edit/program-office-intro/program-office-intro.component.ts`/`.html` — remove Save button (`.html:747-758`); wire interval+dirty-check+beforeunload to `onSubmit()`.

Not touched (per SAN-496, already have no Save button / act immediately): Startup's `startup-supporting-documents` and `pitch-deck-documents` components. Not touched (out of scope, decision 3): any secondary/non-primary tab.

## Contracts & invariants

- **Flags:** none touched. This spec does not add, rename, or gate anything behind a new flag.
- **API:** none touched. Every auto-save call reuses the exact existing service method the removed Save button called (finding A's table, finding C).
- **Events:** none.
- **Invariants at risk:**
  - **Invariant #2 (API contract)** — not touched; no controller/DTO change. `/audit-contract` should still be run mechanically as a gate before `in-review`, expected to show zero diffs.
  - **Invariant #5 (tenant scoping)** — not newly at risk (no new query/endpoint added), but auto-save materially **increases the frequency** of writes against the existing tenant-scoped save endpoints (each on the tenant's own one-deployment-per-tenant backend), partially offset by the dirty-check gate (decision 2). Implementers should sanity-check with `/check-isolation` that the reused endpoints still correctly scope by the calling tenant's session under repeated/rapid calls (e.g. no request racing across a fast interval or the beforeunload path firing concurrently with an in-flight interval save).
  - No other invariant (#1, #3, #4, #6) is implicated — no flag, no tenant-verification-shape change, no auth change, no PowerPitch involvement.

## Test plan

- frontend: karma/jasmine unit coverage for the new interval helper (mount → dirty form → interval fires → correct save method called; pristine form → interval tick skips the call; destroy → interval and beforeunload listener cleared, no further calls) and for Investor's split persist/navigate methods (persist alone does not navigate; navigate only follows a successful persist from the Next-Step path). Automated coverage for the 9 step components' full save/auto-save wiring is not currently blocked by tooling (karma is configured, `npm test`), but given the "guardian" skill referenced in the workspace's standing process is not yet available, actual test-writing depth should be confirmed at `/spec-implement` time and stated explicitly if reduced to manual verification for some components. `beforeunload`/`visibilitychange` behavior is inherently hard to unit-test fully (browser-dependent); manual verification (acceptance criterion's part (b)) is the primary check for that path.
- cross-repo: not applicable — frontend-only change, no other repo consumes anything changed here.

## Implementation record (2026-08-24)

All 11 per-repo plan steps implemented on `ai_native_setup`. New shared `shared/utils/auto-save.service.ts` (+ `auto-save.service.spec.ts`) implements the interval/dirty-check/beforeunload mechanics once; all 10 call sites (9 primary-step components + `EventFormsComponent`) wire into it. Investor-org persist/navigate split, Startup's 5-way decomposition with per-section in-flight guards, and the `EventFormsComponent` in-flight guard + console.log removal were all implemented as specified.

**Post-implementation review caught and fixed one real gap not addressed by the original implementation pass:** `EventFormsComponent.initiateParticipation()`'s pre-existing refetch-and-`patchForm()` cycle (previously only reachable after a deliberate manual Save/Next click) now also runs after every silent 20s auto-save tick. Since the save+refetch round trip takes nonzero time, a user typing during that window could have had new keystrokes silently overwritten by the stale server response on repatch — directly contradicting this issue's own "nothing is lost" acceptance criterion. Fixed by skipping `patchForm()` when `dynamicFormGroup.dirty` is true when the refetch resolves; covered by two new spec cases in `event-forms.component.spec.ts`.

Also reverted, before landing: unrelated local-dev-only scaffolding (a `proxy.conf.js`, plus edits to `angular.json`/`app.component.ts`/`tenant.service.ts`/`environment.local.ts`) that the implementing agent had added to `ng serve` against a real dev tenant backend for manual verification — out of scope for this spec and never intended to ship.

**Verification performed:**
- `npx tsc -p tsconfig.app.json --noEmit` — clean, no compile errors, both before and after the post-review fix.
- Manual diff review of every changed file against the per-repo plan and the `/check-isolation` gate's 5 requirements — all confirmed present (in-flight guards, `HttpClient`-only save paths, persist/navigate split, console.log removal).
- Karma/Jasmine: **could not be executed** — `ng test` fails to bundle at all, workspace-wide, due to pre-existing TypeScript errors in unrelated files (`jobs.component`/`startups.component`/`dashboard.component` missing exports, several pipes/directives with wrong constructor arg counts, a CometChat class-name mismatch). None of these touch any file this spec changed; confirmed by running the same failing build before this issue's changes were applied. The new/updated spec files (`auto-save.service.spec.ts`, `event-forms.component.spec.ts`) are logically reviewed and believed correct but **not confirmed by an actual test run** — this should be re-verified once the pre-existing karma breakage is fixed (separate, unrelated issue).
- **Not done — requires a human/browser:** the acceptance criteria's manual verification bullet (reload-survives-edit, immediate-tab-close-survives-edit, for each of the 9 step types + a custom-form tab). This is explicitly out of scope for me to perform and is exactly what SAN-501 (QA across all 8 stakeholder types) exists for.

## Fix (2026-08-24, found via live testing) — auto-save was showing user-facing side effects on every silent tick

**The user reported the "saved" toast repeating** every ~20s during normal editing — clearly disruptive for something meant to be invisible background auto-save. Root cause: every one of the 8 types' `onSubmit()`/`persistOrganizationInfo()`-equivalent save methods (plus `EventFormsComponent.updateParticipationDetails()`) shows a success toast (`this.toastAlertService.showToast(response.message)` or similar) unconditionally on save success — and since SAN-497 reused these exact methods as the `AutoSaveService`'s `save` callback, the toast fired on every dirty-gated interval tick, not just on a deliberate action. Startup was already unaffected (its decomposed per-section save methods already had their success toasts commented out, apparently pre-empting this exact issue). Investor individual's `onSubmit()` had a second, even more disruptive side effect: an unconditional smooth-scroll to `#investment-details-section` on every save — which would have jerked the page around every 20s during active typing.

**Fix:** added a `silent: boolean = false` parameter to every affected save method (`onSubmit`/`persistOrganizationInfo`/`updateParticipationDetails` across Individual, Investor org, Investor individual, Corporate, Mentor, Partner, Service Provider, Program Office, and `EventFormsComponent`). The `AutoSaveService` registration's `save:` callback now passes `true` (and, since `beforeUnloadSave` defaults to `save` when not separately specified, the beforeunload/visibilitychange path is silent too — correctly so, since there's no time for the user to see a toast before a tab closes anyway). `handleNext()`'s explicit call keeps the default `false`, so the deliberate Next-Step action still shows its confirmation (and, for Investor individual, still scrolls) exactly as before.

**Also fixed in the same pass, reported alongside:** `FormNextStepButtonComponent.handlePreviousClick()` had been sharing `handleClick()`'s (Next's) `disableNavigation` gate — meaning a user on an incomplete current page couldn't click Previous at all, and saw the "please fill in required fields" error instead of navigating back. This is unrelated to auto-save mechanically but was reported in the same message and is the same category of bug as SAN-498's tab-guard already solved for tabs: backward navigation must never depend on the page you're leaving being complete. Fixed to call `commonService.goToPreviousPage()` unconditionally.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after every change. Added test coverage in `form-next-step-button.component.spec.ts` for the Previous-button fix (navigates back even when `disableNavigation` is true; never shows the error toast). The `silent` parameter additions themselves are logically straightforward (single added `if (!silent)` guard per call site) and were verified by direct code reading of every affected file, not a new automated test — `ng test` still can't run workspace-wide for the same pre-existing, unrelated reasons noted above.

## Fix (2026-08-24, found via live testing) — auto-save attempted saves the backend correctly rejects while required fields are still blank

**The user reported a live "Error while saving organizzation info!" toast on Investor org's Basic Information page**, repeating every ~20s. Traced to `sc-saas-backend`'s `InvestorInformationDto`: `aboutUs` is genuinely required (`@IsNotEmpty()`), and Angular sends `aboutUs: ''` explicitly (not omitted) while that quill-editor field is untouched — so the backend correctly rejects the auto-save attempt for as long as it stays blank.

**Why this matters specifically because of auto-save:** before SAN-497, "Save" was one deliberate click — a user would generally only click it once they'd already filled in required fields, so hitting this validation was rare. After SAN-497, the exact same save call fires silently every 20s via `AutoSaveService` regardless of whether the form is complete — turning a rare, one-off validation error into a repeating, visible error toast for the entire time a user hasn't yet reached "About Us".

**Considered and reverted: loosening the backend DTO.** An initial fix removed `aboutUs`'s `@IsNotEmpty()` to match the sibling `CorporateInformationDto` (where every field is `@IsOptional()`, accepting partial payloads by design). **The user explicitly rejected this direction** — required fields must stay required at the backend; the fix belongs on the frontend. That backend edit was reverted (confirmed via `git diff` showing no changes to `investor-information.dto.ts` — it's back to its original, unmodified state).

**Actual fix: auto-save now waits for form validity, not just dirtiness, before attempting a save.** `AutoSaveService`'s `isDirty` check for Investor org (`organization-details.component.ts`) and Investor individual (`individual-investor-edit-form.component.ts` — confirmed both variants call the same `patchInvestorOrganizationInfo()` endpoint, so both needed the fix) now requires `this.organizationForm.valid` in addition to `.dirty`. This exactly mirrors a rule that already existed for Next Step (`[disableNavigation]="!organizationForm.valid"` already refuses to proceed while invalid) — auto-save simply adopts the same rule, so it never attempts a save the backend would reject, and resumes normally the moment the form becomes valid.

**Proactive audit of the other 7 types' DTOs for the same pattern** (since the user's concern implied this could recur elsewhere): `CorporateInformationDto`, `MentorInformationDto` (actually `mentor-information.dto.ts`), `PartnerInformationDto`, `ServiceProviderInformationDto`, `ProgramOfficeInformationDto`, and `IndividualInformationDto` all have **zero** `@IsNotEmpty()` fields — every field is `@IsOptional()`, so none of these 6 types can hit this issue regardless of frontend validity. **`StartupInformationDto`** (backing `saveStartupInfoSection()`, one of Startup's 5 decomposed auto-save calls) does have 2 fields matching this exact pattern — `companyName`/`yearOfIncorporation`, both `@IsNotEmpty()` and both mirrored by `Validators.required` on the frontend form — so the same fix was applied there too: `autoSaveStartupInfoSection()` now also checks `this.startupInfoForm?.valid` before attempting that section's save. Startup's other 4 decomposed sections use separate DTOs; `startup-product.dto.ts` (Product Information) was checked and is clean (no `@IsNotEmpty()` at all); the pitch-deck/founder/advisory-board/business-model DTOs backing the remaining 3 sections were **not** audited in this pass — flagged as unaudited, not assumed clean.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after every change, including the backend revert confirmation. No new automated test added for this specific fix (a straightforward added boolean condition in each `isDirty`/section-gate check) — verified by direct code reading and by tracing the exact DTO validation rule each affected form field maps to, not by running the app.

## Fix (2026-08-26, found via live testing) — raw backend validation text ("organizationTypeId must be a number conforming to the specified constraints") shown directly to the user

**Reported live**: clicking Next on an incomplete Investor profile form (e.g. `organizationTypeId`, the Organization Type radio group, left unselected) surfaced the backend's raw class-validator message verbatim in a corner error toast — technical, English-only, and not something an end user should ever see. Explicit constraint: fix on the frontend only, backend validation itself must not change.

**Root cause**: unrelated to the `isDirty`/`.valid` gating fix above (that fix reduces how often invalid saves are *attempted*, but doesn't change what happens when one still reaches the backend and fails). `InvestorService`'s three org-info PATCH methods (`patchInvestorOrganizationInfo`, `patchInvestorOrgRepresentativeInfo`, `patchInvestorOrgInvestmentInfo` — `investors.service.ts`) each had a `catchError` that displayed `GlobalService.getErrorMessage(fault, ...)` unconditionally on *any* failed save — which, for a 400 (class-validator rejection), returns the backend's own field-level validation string straight from the response body. This is also the same code path behind the earlier-reported "Error while saving organizzation info!" default fallback text.

**Fix**: for these 3 methods only, a `fault.status === 400` response now shows a fixed, friendly message — "Please fill in all the required information before you can move ahead." — instead of the raw extracted backend text. Any other status (network failure, 500, etc.) still falls through to the existing `getErrorMessage()`-based generic message, unchanged. `GlobalService.getErrorMessage()` itself was deliberately left untouched, since it's a shared utility used by ~15 unrelated services across the app (feedback, wishlist, news, uploads, etc.) — scoping the fix to just these 3 call sites avoids any blast radius beyond the Investor org flow this was reported on. No backend file touched.

**Not investigated in this pass**: why this particular save attempt reached the backend at all given `organizationTypeId` has `Validators.required` on its `FormControl` and the page's own `[disableNavigation]="!organizationForm.valid"` should refuse to fire it locally. Possible causes not yet traced: a timing race with the async organization-types dropdown data, or an auto-save tick firing before the guard reflects a just-changed invalid state. The message fix above means this no longer surfaces confusing raw text either way, but closing the underlying "why did an invalid save even fire" gap would still be worth a follow-up if it keeps happening after this fix.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after the change.

## Fix (2026-08-26, found via live testing) — the 6 remaining types' auto-save showed "success" while required fields were still blank

**Reported live**: on Mentor's Basic Information tab, with only "Name" filled in (Current Organization, Designation, Headline, About You all still blank, tab showing a red "!" incomplete indicator), auto-save fired and showed "Mentor information updated successfully" — a save that visually contradicts the same page's own incomplete-profile warning right next to it.

**Root cause**: the earlier proactive audit in this same spec (above) correctly found that `CorporateInformationDto`, `MentorInformationDto`, `PartnerInformationDto`, `ServiceProviderInformationDto`, `ProgramOfficeInformationDto`, and `IndividualInformationDto` have **zero** `@IsNotEmpty()` fields — so the *backend* never rejects a partial save for these 6 types, meaning the "auto-save attempts a save the backend will reject" failure mode (the original reason for `.valid`-gating `isDirty` on the Investor components) genuinely can't happen here. But that's not the only way an unfilled-required-field auto-save can go wrong: these 6 components' own templates already gate "Next Step" on `[disableNavigation]="!corporateForm.valid"` (or `partnerForm.valid`) — i.e. the *frontend itself* already treats these fields as required, even though the backend DTO doesn't. `isDirty` for all 6 was still only checking `.dirty`, not `.valid`, so auto-save would happily PATCH a half-filled form (the backend accepts it) and show a plain "saved successfully" toast — misleading on a tab the UI's own nav indicator still flags incomplete.

**Fix**: added the same `&& this.corporateForm.valid` (`.partnerForm.valid` for Partner) condition to `isDirty` on all 6 remaining components (`corporate-intro`, `mentor-intro`, `partner-intro`, `service-provider-intro`, `program-office-intro`, `individual-profile-edit-form`), exactly mirroring the Investor components' existing gate and each page's own already-established Next-Step gate. Auto-save now waits for the same frontend validity these pages already enforce before showing any success toast, for all 8 stakeholder types uniformly.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all 6 changes.

## Critical fix (2026-08-26, found via live testing) — Next Step's own click-time validity message was being silently overwritten by a redundant, ungated save

**Reported live**: on an incomplete Mentor form, clicking "Next Step" briefly showed "Please fill in all the required information" (correct), but it was gone by the time the user actually looked — appearing as if the message "wasn't showing" at all.

**Root cause, much bigger than Mentor:** `FormNextStepButtonComponent`'s Previous/Next/Submit buttons (`form-next-step-button.component.html`) were all `type="submit"`, and every one of this shared component's 9 host pages wraps it in `<form [formGroup]="..." (ngSubmit)="onSubmit()">` — a leftover from before SAN-497 removed the dedicated Save button, back when a `type="submit"` Save button's native form submission was the intended way to trigger `onSubmit()`. A `type="submit"` button inside a `<form>` **always** fires the form's native submit event on click, completely independently of whatever a `(click)` handler on that same button does — there is no way for a `(click)` handler to suppress it after the fact. So every click on Next Step fired **two things simultaneously**:
1. `handleClick()` (the button's own `(click)` handler) — correctly checks `disableNavigation` and, when the form is invalid, shows the "please fill in required information" toast and does nothing else.
2. The form's native submit event → Angular's `(ngSubmit)="onSubmit()"` binding → the host component's own `onSubmit()` — which has **no validity check at all** and saves unconditionally. For all 6 types with zero required backend fields (this same spec's earlier proactive audit), that redundant save succeeds even on a fully blank form, and shows its own "...updated successfully" toast — which, being the async HTTP response, lands a beat after the synchronous click-time warning and overwrites it (SweetAlert2 toasts replace one another rather than stacking).

This means the exact "auto-save shows success on an incomplete form" symptom the fix above targeted had a **second, independent source** — not just the periodic auto-save tick, but every single Next Step click too, on all 9 forms carrying this button (all 8 stakeholder types' primary step + Investor org's Representative Details), regardless of today's `.valid`-gating fixes to `isDirty`.

**Fix**: `form-next-step-button.component.html`'s 3 buttons changed from `type="submit"` to `type="button"` — each already has a complete `(click)` handler (save, navigate, or emit), so nothing relied on native form submission. Additionally removed the now-fully-vestigial `(ngSubmit)="onSubmit()"` binding from all 9 host `<form>` tags (`organization-details`, `individual-investor-edit-form`, `representative-details`, `corporate-intro`, `mentor-intro`, `partner-intro`, `service-provider-intro`, `program-office-intro`, `individual-profile-edit-form`) — Angular's `[formGroup]` directive already prevents native submission/page navigation on its own (a `@HostListener('submit')` baked into `FormGroupDirective` itself, independent of whether `(ngSubmit)` is bound), so this wasn't needed to avoid a page reload; it was only ever there to invoke `onSubmit()`, and removing it closes the *same* redundant-save bug via a second trigger — pressing Enter inside any single-line text `<input>` in these forms would native-submit the form even without any submit-type button, hitting the identical bug through a different door. The legitimate save path (`handleClick()` → `next.emit()` → the host's own `handleNext()` → `onSubmit()`/persist method) is a normal method call, not a native browser event, so it's completely unaffected by either change.

**Known follow-up, not done in this pass**: `organization-details.component.ts`'s own `onSubmit(): void { this.persistOrganizationInfo(); }` (line 386) had no other caller besides the now-removed `(ngSubmit)` binding (its `handleNext()` calls `persistOrganizationInfo()` directly, not `onSubmit()`) — it's now dead code. Left in place rather than deleted, to keep this fix scoped to the reported bug; safe to remove in a follow-up cleanup pass.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all 10 file changes (1 shared component + 9 host templates). Confirmed by reading, for each of the 9 affected `.ts` files, that `onSubmit()` still has a live call site via `handleNext()` (or, for `organization-details.component.ts`, that the real save path `persistOrganizationInfo()` is unaffected) — none of them lost their save trigger.

## Rollout

Single-repo (`sc-saas-frontend`) deploy, no backend coordination needed since no contract changes. No flag gating is planned (contracts.flags is empty) — ship all 9 step components + `EventFormsComponent` together since the per-repo plan is small and self-contained.

## Out of scope

- Tab-navigation blocking (SAN-498).
- The "leaving without completing profile" dialog (SAN-499).
- Last-page button rearrangement (SAN-500).
- Any backend endpoint/DTO change — all auto-save calls reuse existing endpoints as-is.
- **Secondary/non-primary tabs** (decision 3, follow-up candidate, not silently dropped): Corporate Engagement, Mentor Domain Expertise, Investor Investment/Representative Details, Partner Industry/Technology, and any currently-disabled/commented-out steps in `navlinks.ts` (Startup Team/Documents/Mentorship). SAN-496 did not audit Save-button presence on these, and this spec's per-repo plan only covers the primary-step files SAN-496 explicitly named plus the newly-discovered `EventFormsComponent`. If any of these turn out to have their own independent Save button not funneled through one of the components in the per-repo plan, they need their own follow-up issue.

## Open questions

None — all prior open questions were resolved on 2026-08-24 (see "Design decisions" above).
