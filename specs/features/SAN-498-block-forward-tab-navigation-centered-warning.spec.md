---
id: SAN-498
title: Block Forward Tab Navigation Past an Incomplete Page, With Centered Warning
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/project/block-forward-tab-navigation-past-an-incomplete-page-with-centered-8c87bdfec46a
owner: mahima.s@sanchiconnect.com
repos: [frontend]                # sc-saas-frontend only — pure interaction/UI change, no endpoint or DTO involved
contracts:
  api: []                        # no endpoint added/changed — reuses the existing profile-completeness fetch already loaded for the top-bar widget/Startup's nav-links today
  flags: []                      # no flag added/changed
  events: []
tenant_scoped: false             # no new data read/write; the completeness payload this reuses is already fetched today (see findings) — this issue only changes what gates a click
depends_on: [SAN-496]
created: 2026-08-24
---

# Block Forward Tab Navigation Past an Incomplete Page, With Centered Warning

## Evidence-tagging convention used throughout this spec

- **Evidenced** — cited to `file:line` in the real `sc-saas-frontend` (and, for one backend-verification point, `sc-saas-backend`) codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation from code, not a full manual UI click-through.
- `[DESIGN DECISION PENDING]` — a genuine product/UX or architecture choice this spec deliberately does not make; routed to Open questions.

## Linear tracking

- Origin: [SAN-498](https://linear.app/sanchiconnect/issue/SAN-498/block-forward-tab-navigation-past-an-incomplete-page-with-centered) — "Enhancement" project, milestone "Profile Autosave", currently assigned to Mahima Sharma, priority High.
- Depends on [SAN-496](https://linear.app/sanchiconnect/issue/SAN-496/blast-radius-current-behavior-assessment-profile-form-auto-save) (done, approved) — this spec builds directly on its item 3 and item 5 findings rather than re-deriving them; see `specs/features/SAN-496-profile-form-autosave-blast-radius-assessment.spec.md`.
- Related: [SAN-497](https://linear.app/sanchiconnect/issue/SAN-497/remove-save-button-and-add-auto-save-to-profile-completion-form) (implemented) — see `specs/features/SAN-497-remove-save-button-add-autosave-profile-form.spec.md`. No functional overlap (SAN-497 is save mechanics; this is tab-navigation gating) but both touch the same 9 nav-links/step-component family.
- Dedicated Linear Project created: [Block Forward Tab Navigation Past an Incomplete Page, With Centered Warning](https://linear.app/sanchiconnect/project/block-forward-tab-navigation-past-an-incomplete-page-with-centered-8c87bdfec46a), lead Mahima Sharma. SAN-498 linked into it (moved Backlog → Todo, labeled `["Feature", "Repo: Frontend"]`, priority High) rather than duplicated into a separate issue, since SAN-498 already *is* the frontend-scoped work this spec describes.

## Problem

Per the BRD "Stakeholder Profile Forms Auto-Save, and Guide Users Instead of Letting Them Wander Off Incomplete," and confirmed by SAN-496 (item 3): every one of the 9 profile-form nav-links variants renders its tabs as a plain `<a [routerLink]>` with zero guard logic — a user can click ahead to any incomplete, further-ahead step today, for every stakeholder type. Meanwhile "Next Step" already blocks forward progress on an incomplete current page, showing a small corner toast. This issue closes that gap: tab clicks must be blocked the same way, with the warning shown centered instead of in the corner.

## Findings (this issue's own investigation, building on SAN-496)

### 1. Does nav-links have existing access to a step's live client-side FormGroup validity (signal a)? What's the actual component relationship?

**Evidenced — no shared-state plumbing exists, and it is not a "layout hosts both nav-links and router-outlet" relationship as originally hypothesized.** `<app-startup-edit-page-nav-links>` is not rendered by a shared layout/wrapper alongside a `<router-outlet>`; it is embedded as a **child element directly inside each step component's own template** — confirmed via 12 separate embed sites for the Startup type alone: `startup-information.component.html:16`, `industry-technology.component.html:14`, `product-information.component.html:8`, `financials-details.component.html:13`, `pitch-deck-documents.component.html:7`, `startup-supporting-documents.component.html:12`, `mentorship.component.html:8`, `extra-info-startup.component.html:8`, `hire-info-edit-page.component.html:13`, `founders-list.component.html:7`, `supporting-documents.component.html:10`, `pitch-deck-management.component.html:17`. Each routed step component is, itself, nav-links' DOM parent — but no `@Input`/`@Output` binding currently passes anything between them (confirmed: `startup-edit-page-nav-links.component.ts` has no `@Input`, and none of the 12 embed sites bind one in). There is no separate `*-forms.module.ts` wrapper hosting both; `startup-forms.module.ts` (`/Users/mahimasharma/Desktop/SanchiSaaS/sc-saas-frontend/src/app/modules/startups/startup-forms.module.ts`) is a plain `NgModule` declaration list, not a shared parent component.

**Consequence:** signal (a) — a step's own `FormGroup`/count-selection validity (e.g. `industry-technology.component.ts:254-274`'s `saveButtonDisabled`) — is *reachable* from nav-links only by adding a brand-new `@Input` and wiring it at **every one of these embed sites, per type** (≈12 sites just for Startup; the other 8 types were not individually counted here but follow the same "nav-links embedded inside each step template" pattern per SAN-496 item 2's file list, so a comparable multiplication applies). This is real new plumbing, not a cheap wiring change.

### 2. What does `getMissingFieldsMap()` / `profileCompleteness.missingFields` (signal b) actually contain, and does it already exist inside nav-links uniformly?

**Evidenced — granularity matches "is this tab complete" exactly, but the subscription is NOT uniformly present across all 9 nav-links variants today; this corrects an implicit assumption in SAN-496's own phrasing.**

- **Shape:** `getMissingFieldsMap()` (`shared/utils/common-methods.ts:468-511`) takes the backend's `profileCompleteness.forms` object (per-section `{ total, completed, percentage, missingFields: string[] }`, `core/domain/startup-investor-dashboard.model.ts:57-94`) and re-groups every missing field string by `groupTitle` — the **nav-link/tab title** the field's section maps to (via `MissingFormKeyToUrlMapping`/`getTitleFromNavLink`, `shared/constants/constants.ts:31,54`). The output is `[{ key: <tab title>, value: [<missing field descriptions>] }]` — i.e. **already keyed per-tab**, exactly the granularity a "is THIS tab complete" check needs, for every tab, not just the current one.
- **Already present, and already used to gate a per-link check, in Startup's nav-links only:** `startup-edit-page-nav-links.component.ts:71-77` subscribes to `profileService.profileCompleteness$` and computes `this.missingFields = getMissingFieldsMap(...)`; `isCustomProfileFormValid(link)` (`:162-177`) already implements a genuinely reusable **per-link** completeness check: `this.missingFields.find(group => group.key === link.title)` — today used only to color the tab icon red/green, never to block a click. This is the exact primitive a tab-guard needs, already written, for one type.
- **Confirmed ABSENT for Individual's nav-links:** `individual-profile-edit-page-nav-links.component.ts` has **zero** references to `missingFields`, `profileCompleteness`, or `getMissingFieldsMap` (grepped, no matches) and its template (`individual-profile-edit-page-nav-links.component.html`) has no completeness-driven icon at all — the signal instead lives only in that type's separate top-bar widget, `individual-profile-completeness.component.ts:10,29,31,67,80` (which, per SAN-496's own copy-paste note, still types itself as `ServiceProviderProfileCompleteness` — leftover residue, cosmetic only, doesn't affect the data shape used).
- **The other 7 nav-links variants (Investor org, Individual-Investor, Corporate, Mentor, Partner, Service Provider, Program Office) were not individually re-checked in this pass** — flagged in Open questions rather than assumed uniform.
- **Count-constrained case (SAN-496's open item):** verified against the actual backend calculation, `calculateCompleteness()` (`sc-saas-backend/src/core/utils/app.utils.ts:59-91`) — it is **purely presence-based** (`eval('data?.'+key)` truthy → complete), with no max-count logic at all. Startup's `startupIndustries`/`startupTechnologies` are gated in `criteria.industryTechnologyBusiness` (`sc-saas-backend/.../startup.repository.ts:1888-1901`) only on non-empty presence. Since the client-side `MAX_SELECTABLE_INDUSTRIES`/`MAX_SELECTABLE_TECHNOLOGIES` cap (SAN-496 item 5) only restricts selecting *more* than N, and never requires reaching exactly N, both signals agree for this specific case: "at least one selected" is the only real completeness condition either side enforces. No divergence found for this case — but this is one case, not an exhaustive reconciliation of every step.

**Conclusion for item 2:** signal (b) is the right shape and, unlike signal (a), needs no new cross-component plumbing to be introduced generically — but it does need to be **ported into the 8 nav-links components that don't yet have it** (a modest, well-precedented one-file-per-type change, copying the exact pattern already proven in Startup's own nav-links and in every other type's own top-bar widget), not assumed to already exist everywhere.

### 3. Current-page-only vs. target/range check — does the simpler framing satisfy every AC bullet?

Worked through against the issue's literal acceptance criteria:

- The given worked example (user on page 3/5, completed 1–2, current page 3 is itself incomplete, clicks tab 5 → blocked; clicks tab 1 or 2 → not blocked) is satisfied by **either** framing below, because in the example the current page happens to be the first incomplete page. It does not disambiguate the two options.
- The AC's own more general wording — "a tab for a page **further ahead than the user has actually completed**" — is phrased in terms of the user's completed *progress*, not literally "the page currently on screen." These are the same thing only when the user is viewing the furthest page they've reached. They diverge if a user navigates *backward* to review an already-complete earlier page, then tries to tab forward past a *different*, still-incomplete page that isn't the one currently on screen.

**Two genuinely different options, both now similarly cheap to build** (because signal (b) already holds full per-tab data for every tab, not just the current one — see finding 2):

- **Option A — current-page-only.** Block a forward click only if the tab **currently being viewed** is itself incomplete (maximal literal parity with `FormNextStepButtonComponent.handleClick()`, `form-next-step-button.component.ts:70-78`, which also only ever checks the current step). Satisfies the worked example exactly. Risk: a user on a *complete* current page can still tab-jump past a different incomplete page lying between current and target (e.g. current=3 complete, 4 incomplete, jump 3→5) with no warning at all — this under-delivers relative to the BRD's own "don't let them wander off incomplete" framing and the AC's more general wording.
- **Option B — first-incomplete-tab.** Compute the first incomplete tab in `navLinks` order using signal (b) across the *whole* list (trivial extension of the per-link check that already exists for Startup, `isCustomProfileFormValid`, `startup-edit-page-nav-links.component.ts:162-177` — just applied across the array instead of one link) and block any click whose target index is beyond it, regardless of which tab is currently mounted. Closes the gap Option A leaves open; matches the AC's literal wording more precisely; still satisfies the worked example exactly. Marginal extra engineering cost over Option A is small, since the same per-tab data (signal b) already has to be loaded either way.

Because Option B is barely more expensive once signal (b) is in place, this is a **product/UX decision, not an engineering-cost-driven one** — this spec does not choose between them; see Open questions.

### 4. Would signal (a) require a new shared service, or is there a cheap wrapper point?

**Evidenced — no cheap existing wrapper; a new shared service (or ported per-component subscription) is required either way.** As found in item 1, nav-links and its step component are parent/child within one template, per step, with **no persistent shared instance** across steps — each navigation destroys the old step (and its embedded nav-links instance) and creates a new one. There is no `*-forms.module.ts`-level or router-level wrapper component that persists across step navigations for any type (grepped `startup-forms.module.ts`, confirmed a plain `NgModule`, not a component). So:
- Signal (a) would need either a brand-new `@Input` wired at every embed site (item 1), or a brand-new shared Angular service (e.g. an injectable `FormValidityBridgeService` that each step component pushes its own validity into, and nav-links reads from) — genuinely new infrastructure, not a reuse of anything existing.
- Signal (b) needs only the same `ProfileService.profileCompleteness$` subscription pattern already proven working in 8 of the 9 relevant components (Startup's nav-links + all 8 types' top-bar widgets) ported into the one or two nav-links components missing it.

This reinforces finding 2/3's conclusion: signal (b) is the lower-cost, lower-risk foundation regardless of which scope option (A/B) is chosen for item 3.

### 5. Does a centered/modal alert pattern already exist, versus the corner toast Next Step uses today?

**Evidenced — yes, trivially reusable; no new UI library or component needed.** `ToastAlertService.showToast()` (`shared/utils/toast.service.ts:19-36`) — what `FormNextStepButtonComponent.handleClick()` calls today (`form-next-step-button.component.ts:77,88`) — is a `Swal.mixin({ toast: true, position: 'top-end', ... })`: SweetAlert2's small corner-toast mode. Elsewhere in the same codebase, `Swal.fire({...})` is called **directly, without `toast: true`** (`event-forms.component.ts:438-446` — title/text/icon, `showCancelButton: false`, `confirmButtonText: 'Ok'`), which renders SweetAlert2's **default centered modal**, dismissed by an explicit confirm button. `sweetalert2` is already an installed dependency, already imported in `toast.service.ts:2` and directly in other components. Producing a centered warning is therefore a matter of adding one more method (e.g. `ToastAlertService.showCenteredAlert(message)` wrapping a plain `Swal.fire({icon:'warning', text: message, confirmButtonText:'Ok'})`) or calling `Swal.fire()` inline at the guard's block site — not a new UI pattern.

### 6. Coverage scope

Following SAN-497's precedent (its decision 3): recommend this pass covers the **9 primary-step nav-links variants** (8 stakeholder types + the Individual-Investor variant) and, because tenant-admin custom-form tabs are pushed into the *same* `navLinks` array each nav-links component already renders (`startup-edit-page-nav-links.component.ts:115-147`'s `fetchFormsLinks()`, and the equivalent in `individual-profile-edit-page-nav-links.component.ts:55-76`), guarding at the nav-links click-handler level **automatically covers custom-form tabs too, for free** — a materially lower blast radius than SAN-497 needed for its own save-button removal (which required visiting 10 separate save call sites). Secondary/non-primary tabs (Corporate Engagement, Mentor Domain Expertise, Investor Investment/Representative Details, Partner Industry/Technology, and any disabled/commented-out steps in `navlinks.ts`) are **out of scope**, matching SAN-497's own explicit exclusion, not silently dropped.

## Acceptance criteria

(Restated from the Linear issue; unchanged from its own wording, since this spec does not weaken or reinterpret them — the open design decisions above are about *how* to satisfy them, not whether to.)

- [ ] Clicking "Next Step" behaves exactly as it does today — only proceeds if the current page's required fields are complete; shows the existing (corner-toast) warning if they aren't. `FormNextStepButtonComponent` itself is not modified.
- [ ] Clicking a tab for a page further ahead than the user has actually completed is blocked the same way Next Step is blocked today — tabs cannot be used to skip past an incomplete page. (Exact scope of "further ahead than actually completed" is Open question 1/2 below.)
- [ ] Clicking a tab for a page the user has already completed — going backward, or to an earlier finished page — still works freely, exactly as it does today.
- [ ] When forward tab-navigation is blocked, the message carries the same content already used for Next Step's warning, but shown **centered** in front of the user (reusing the existing `Swal.fire()` centered-modal pattern, finding 5), not the small corner `ToastAlertService.showToast()` notification.
- [ ] A user on page 3 of 5, having completed only pages 1–2, who clicks the tab for page 5 sees this warning, exactly as if they'd clicked Next Step from an incomplete page 3.
- [ ] That same user clicking the tab for page 1 or 2 is not blocked and sees no warning.
- [ ] A user who completes every page, then goes back and clears a required field on an earlier page, has Submit become disabled again immediately — this is existing top-bar Submit-button behavior (SAN-496 item 4) and must not regress; this issue's own code does not need to implement it, only avoid breaking it.
- [ ] Coverage: all 9 primary-step nav-links variants (8 stakeholder types + Individual-Investor) plus tenant-admin custom-form tabs (covered automatically per finding 6); secondary/non-primary tabs out of scope (see Out of scope).

## Per-repo plan

### frontend

Dependency order (single repo):

1. **Establish signal (b) uniformly.** Per decision 4's audit table: port the `ProfileService.profileCompleteness$` subscription + `getMissingFieldsMap()` pattern (proven in `startup-edit-page-nav-links.component.ts:71-77`) into the 6 nav-links components that don't yet have it — `investor-edit-page-nav-links`, `individual-investor-edit-page-nav-links`, `program-office-edit-page-nav-links`, `individual-profile-edit-page-nav-links`, `partners-edit-page-nav-links`, `service-provider-page-nav-links`. The other 3 (Startup, Corporate, Mentor) already have this. No new backend call anywhere — this data is already fetched today for the top-bar widget in all 9 types.
2. **Generalize the per-link completeness check + add first-incomplete-index (decision 2, Option B).** Promote Startup's existing `isCustomProfileFormValid(link)` (`startup-edit-page-nav-links.component.ts:162-177`) from "cosmetic icon-only" to the shared primitive the guard uses; add the equivalent method to the other 8 nav-links components. Add a `getFirstIncompleteIndex()`-style helper reusing this same per-link check across the ordered `navLinks` array, in all 9 components.
3. **Guard the tab click.** Replace the plain `<a [routerLink]="link.route">` in all 9 nav-links templates with a click-intercepting handler: compute whether the click is "forward" (target index in `navLinks` > current index, using `activeItem`/`this.router.url` the same way `CommonService.goToNextPage()` already does, `core/service/common.service.ts:31-39`), and if forward **and** target index beyond the first-incomplete index (decision 2), call `event.preventDefault()`, show the centered warning (step 4), and leave the user on their current page (decision 3 — no redirect). Tenant-admin custom-form tabs are covered automatically since they live in the same `navLinks` array (finding 6) — no separate code path needed for them.
4. **Add the centered-warning method.** Add `ToastAlertService.showCenteredAlert(message)`, wrapping a plain `Swal.fire({ icon: 'warning', text: message, confirmButtonText: 'Ok' })` (decision 6) — reusing the existing `sweetalert2` dependency and the pattern already used at `event-forms.component.ts:438-446`. Message text: reuse `FormNextStepButtonComponent`'s default string verbatim (decision 5 — confirmed single generic string, no per-step overrides exist).
5. **Manual verification** across all 9 primary-step variants (re-confirm at implementation time whether the pre-existing, unrelated karma bundling breakage noted in SAN-497's implementation record has been fixed) plus at least one tenant-admin custom-form tab, matching the AC's worked example precisely.

Not touched: `FormNextStepButtonComponent` itself (Next Step's own behavior is explicitly unchanged); any secondary/non-primary tab (finding 6); any backend endpoint or DTO (no data shape changes — same payload already fetched today is simply read by one more component).

## Contracts & invariants

- **Flags:** none touched.
- **API:** none touched — no new endpoint or DTO; the profile-completeness payload this reuses is already fetched today (for the top-bar widget in 8/9 types, and already in nav-links for Startup).
- **Events:** none.
- **Invariants at risk:** none of the 6 hard workspace invariants are implicated — no flag name, no API/DTO change, no tenant-verification-shape change, no auth change, no PowerPitch involvement, and no *new* tenant-scoped data access (invariant #5): this issue widens which existing, already-tenant-scoped-and-already-fetched completeness payload gets read to gate a click, it does not add a new query or write.

## Test plan

- frontend: karma/jasmine coverage for the new per-link completeness check and the guarded click handler (forward + current/target incomplete → `preventDefault` called, centered-alert method invoked, no navigation; forward + complete → navigation proceeds normally; backward → always navigates, no check performed at all). Per SAN-497's own implementation record, `ng test` was found to fail to bundle workspace-wide for pre-existing, unrelated reasons at that time — this should be re-verified at `/spec-implement` time rather than assumed still broken or still working.
- cross-repo: not applicable — frontend-only change, no other repo consumes anything changed here.

## Implementation record (2026-08-24)

All 5 per-repo plan steps implemented on `ai_native_setup_mahima`. Shared `getFirstIncompleteNavLinkIndex()`/`isForwardTabNavigationBlocked()` added to `shared/utils/common-methods.ts`; `ToastAlertService.showCenteredAlert()` added. All 9 nav-links components wired: Startup/Corporate/Mentor already had the completeness subscription (decision 4's audit table); the other 6 got it newly ported.

**Deviation found and fixed during implementation:** Corporate's nav-links was miscategorized in decision 4's audit table as "already has it" (grep found 4 references to `missingFields`/`profileCompleteness`) — but the actual `profileService.profileCompleteness$` *subscription* that populates `missingFields` was missing, so `isCustomProfileFormValid()` silently always returned `true`. Fixed by porting the subscription in, same as the other 6. Documented in `corporate/module.spec.md`.

**Deviation from literal spec wording:** the click guard calls `event.stopImmediatePropagation()` in addition to `event.preventDefault()` (not specified in the per-repo plan). Necessary because Angular's `RouterLinkWithHref` triggers navigation via its own `router.navigateByUrl()` call inside a click listener on the same element, not the browser's default anchor action — `preventDefault()` alone doesn't reliably stop it. Documented in `shared/module.spec.md`.

**Post-implementation review (performed by me, not the implementing agent):**
- Hand-traced the `isForwardTabNavigationBlocked()` truth table against the spec's worked example and the Option A/B distinguishing case (current page complete, an earlier different page incomplete) — confirmed correct: blocks only strictly beyond the first incomplete tab, allows navigating *to* the first incomplete tab itself (to go complete it), always allows backward navigation.
- Confirmed all 9 templates actually bind `(click)="onNavLinkClick($event, link)"` (grepped).
- Confirmed `activeItem` (used as the guard's "current tab" reference) is pre-existing, correctly-maintained state in every component (set on init, updated on route change) — not something this issue needed to add.
- Removed one stray pre-existing `console.log('this.profileData', ...)` in `investor-edit-page-nav-links.component.ts` (logs the current user's own profile data — not a leak, but flagged as a drive-by cleanup opportunity by the `/check-isolation` gate since this file was already being edited).
- `npx tsc -p tsconfig.app.json --noEmit` — clean, both after the implementer's changes and after my own edit.
- `ng test` — still fails to bundle workspace-wide for the same pre-existing, unrelated reasons recorded in SAN-497's implementation record. New spec files (`nav-link-forward-guard.spec.ts`, `toast.service.spec.ts`) are logically reviewed by me and believed correct but not confirmed by an actual run.
- **Not done — requires a human/browser:** manual click-through verification (the AC's worked example, backward navigation, all 9 types + a custom-form tab). Out of scope for me; this is SAN-501's job.

**`/check-isolation` gate (run before implementation):** isolation holds, 0 blockers. Two non-blocking notes: (1) a pre-existing `ProfileService` stale-buffer-replay edge case during an in-session profile-type switch (unrelated to tenant isolation — same user throughout; not introduced by this issue, just present in 3 more components now) — worth a "no regression" manual check, not a blocker; (2) the stray console.log above, now removed.

## Critical fix (2026-08-24, found via live testing) — click-interception did not actually block navigation

**The user live-tested this feature and found the block did not work**: the centered warning appeared correctly (proving the completeness logic was right), but the tab navigation proceeded anyway. Root cause: `event.preventDefault()`/`event.stopImmediatePropagation()` inside the nav-link `(click)` handler cannot reliably stop `[routerLink]`'s own click-triggered navigation. `RouterLink`'s `@HostListener('click', ...)` calls `router.navigateByUrl()` inside its own handler body *before* returning a value Angular uses to call `preventDefault()` — if that listener fires (which it did here, apparently before or independent of our own `(click)` binding on the same element), the navigation call has already executed by the time our handler runs. `stopImmediatePropagation()` can only stop listeners that haven't fired *yet*; it cannot undo a function call that already happened.

**Fix: moved enforcement from a DOM click handler to Angular's routing pipeline.** Added `IncompleteStepForwardGuard implements CanActivate` (`shared/guards/incomplete-step-forward.guard.ts`) — the Router always resolves `CanActivate` guards before completing any navigation, regardless of how it was triggered (click, browser back/forward, a `router.navigate()` call elsewhere), so this is immune to the DOM event-ordering issue entirely. Mirrors the same architectural pattern already proven working for `UnsavedProfileLeaveGuard` (`CanDeactivate`, SAN-499).

**Design of the guard:**
- Resolves which type's ordered tab list applies to a navigation attempt purely by matching the *target* URL against every array in `PROFILE_NAV_LINKS` (`shared/constants/navlinks.ts`) — no dependency on `route.data.expectedType`, which elegantly handles the Investor org-vs-individual split for free (their routes are disjoint strings, so whichever array contains a match is authoritative).
- Filters out any tab behind a feature flag that's off for the current tenant (`storageService.getObject(StorageService.storageKeys.brandDetails)?.features`), matching the same filter every nav-links component already applies — so a flag-gated tab like Corporate's "Engagement" (`corporates_enagement_form`) doesn't skew the first-incomplete-index calculation for tenants that don't have it.
- Reuses `ProfileService.profileCompleteness` (a plain synchronous field, not the `$` observable) + `getMissingFieldsMap()` — same completeness source the removed click-guard used.
- If the target URL isn't found in any `PROFILE_NAV_LINKS` array at all (dashboard, custom-form tabs, any unmodeled route) → default allow, preserving prior behavior for anything not explicitly covered.
- Wired as `canActivate: [IncompleteStepForwardGuard]` onto every route already carrying `canDeactivate: [UnsavedProfileLeaveGuard]` (SAN-499) across all 8 routing files — i.e. every real primary/secondary `edit/*` route, appended into each route's existing `canActivate` array (not overwriting `AuthGuard`/`DisableStartupProfileUpdateGuard`).

**Custom-form-tab coverage (closed 2026-08-24, same day, per explicit user request):** initially shipped with a known gap — tenant-admin custom-form tabs weren't covered, since they're fetched asynchronously and aren't part of the static `PROFILE_NAV_LINKS` map. Closed by having the guard build the exact same combined list every nav-links component builds: `PROFILE_NAV_LINKS` entries for the resolved prefix, filtered by feature flag, followed by that prefix's custom-form tabs read from the `global` store's `getFormsList` selector (filtered identically to every nav-links component's own `fetchFormsLinks()`). Because this list is rebuilt fresh on every navigation attempt rather than hardcoded, a tenant admin adding a new custom form — or a developer adding a new static tab to `PROFILE_NAV_LINKS` with this guard on its route — is automatically covered with no further code change, which was the explicit ask: "if an additional page is added to the profile, it also needs this same check that all earlier required fields are filled before entering it."

**Also found and fixed while investigating:**
- `mentor-edit-page-nav-links.component.ts` passed `'startups'` as `getMissingFieldsMap()`'s custom-form-URL-prefix argument instead of `'mentors'` — copy-paste residue. Fixed. (Low impact: this argument only affects custom-form missing-field URL construction, not the static-tab matching the new guard or the existing per-link icon check rely on.)
- `partners-dashboard.module.ts` and `individual-profile.module.ts` each had one `edit/*` route (`edit/partner-information`, `edit/startups`, `edit/industry-technology` for Partner; `edit/individual-information` for Individual) with **no `canActivate` array at all** — not even `AuthGuard`. Added `IncompleteStepForwardGuard` to each; did **not** add `AuthGuard` to them, since that's a separate, pre-existing gap (possibly intentional, possibly not) outside this fix's scope — flagging for the team to confirm rather than silently changing auth behavior as a side effect.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all changes, including the custom-form-tab extension. `incomplete-step-forward.guard.spec.ts` covers: the exact reported bug (blocks Basic Info → Industry/Technology when Basic Info is incomplete), allows navigating to the first incomplete tab itself, allows everything once complete, default-allows unmodeled URLs, fails open when completeness hasn't loaded, resolves the Investor individual variant via URL alone, correctly excludes a flag-gated tab from the index calculation, and 3 cases for the custom-form-tab extension (blocks entry when an earlier static tab is incomplete; allows entry once all static tabs are complete; ignores a form that fails the same status/useFormAs filter `fetchFormsLinks()` applies). Not run (same pre-existing `ng test` bundling breakage as SAN-497/499).

**Not addressed in this pass:** the original per-nav-link `(click)="onNavLinkClick($event, link)"` handlers were left in place rather than removed. They're now redundant (the `CanActivate` guard is the real enforcement) but not harmful beyond a possible duplicate-modal flash in the blocked case, since Angular Router still runs the guard even if the click handler's own `preventDefault()` has no effect. Worth removing in a follow-up for cleanliness, not urgent.

## Fix (2026-08-24, requested via live testing) — "freeze" the tab strip while the warning is showing, for all 8 types

**The user asked for the tab strip (and rest of the page) to appear visually frozen for the duration of the centered warning**, confirmed to mean: only while the modal itself is open, not persistently whenever a step is incomplete. The page behind the modal is already dimmed by SweetAlert2's own backdrop (confirmed via screenshot — sidebar, tabs, and buttons all uniformly grayed already), but `ToastAlertService.showCenteredAlert()` had no `allowOutsideClick`/`allowEscapeKey` overrides, meaning SweetAlert2's default (`allowOutsideClick: true`) let a click on the dimmed backdrop — including on a tab — silently dismiss the warning without the user ever clicking "Ok".

**First fix (insufficient on its own):** added `allowOutsideClick: false, allowEscapeKey: false` to `showCenteredAlert()`. This stops the *modal itself* from being dismissed by a backdrop click/Escape — but the user re-tested live and confirmed the tab strip **stayed clickable underneath** the modal regardless. SweetAlert2's backdrop visually dims the page but does not reliably block pointer-events on every element rendered behind it in this app (whatever the exact reason — z-index/stacking-context specifics of this app's own CSS, most likely), so `allowOutsideClick` alone (which only governs whether the *backdrop click* itself dismisses the modal) never actually addressed clicks landing on the tabs.

**Actual fix, second pass, same day:** explicit, direct control instead of relying on SweetAlert2's own backdrop behavior. `showCenteredAlert()` now toggles a `body.tabs-frozen-during-warning` class — added immediately before `Swal.fire()`, removed once its promise resolves (Ok clicked). A new global CSS rule in `src/styles.scss` scopes `pointer-events: none` (plus a dimmed/disabled visual treatment) to `<a>` elements specifically inside all 9 nav-links component selectors (`app-startup-edit-page-nav-links a`, `app-investor-edit-page-nav-links a`, etc. — one rule per variant, covering all 8 stakeholder types + the Individual-Investor variant). Because this targets the tab links directly rather than depending on backdrop stacking, it's guaranteed to block clicks regardless of any z-index quirk. `showLeaveConfirm()` (SAN-499's Stay/Discard prompt) remains untouched — that modal's own design already treats a backdrop-click/Escape as an intentional "Stay" choice, unrelated to this fix. The Previous/Next Step buttons (a separate shared component) were deliberately left unfrozen — the user's request was specifically about the tab strip.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` and the spec-config type-check both clean. Added tests confirming the body class is added before `Swal.fire()` and removed after its promise resolves.

## Fix (2026-08-26, found via live testing) — forward navigation still succeeded past a live-invalid, unsaved tab

**Reported live**: on Investor Organization's Investment Details tab, the user broke the "Ticket Size (Max) must be greater than Ticket Size (Min)" cross-field validator (and/or cleared a required field) without saving. Clicking forward still showed the "Please fill in all the required information" warning correctly, but navigation to Representative Details went through anyway — the modal fired for show, but nothing was actually blocked.

**Root cause**: `IncompleteStepForwardGuard` (the `CanActivate` guard added in the fix above) and the legacy nav-link `onNavLinkClick` check both determine "is this tab complete" purely from `ProfileService.profileCompleteness` — a **backend-fetched snapshot** that only refreshes as a side effect of a successful save (`patchInvestorOrgInvestmentInfo(...).pipe(tap(() => this.getProfileCompleteness()))`, itself an async NgRx dispatch, not synchronous with the PATCH). Neither check ever consults the *live* Angular form on the component currently on screen. So the sequence was: Investment Details was previously saved complete → snapshot says "complete" → user edits the form invalid without re-saving → snapshot is untouched → user clicks a later tab → guard reads the stale "complete" snapshot and allows it, even though the on-screen form is visibly invalid right now.

**Fix**: added a second, complementary guard — `LiveStepValidityGuard implements CanDeactivate<unknown>` (`shared/guards/live-step-validity.guard.ts`). `CanDeactivate` guards are the one point in the Router pipeline that receive a live reference to the *outgoing* component instance, so this guard can ask the component itself, in real time, "are you valid right now" — instead of trusting a snapshot that can go stale the moment the user types.

- New optional interface `ProfileStepLiveValidity` (`shared/interfaces/profile-step-live-validity.interface.ts`): `isCurrentStepValid(): boolean`. A component opts in by implementing it; components that don't implement it are invisible to this guard and fail open (mirrors `IncompleteStepForwardGuard`'s own missing-data fail-open) — purely additive, can never newly block an unaudited tab.
- The guard only fires for a genuine **forward** move within the same type's own edit flow (same index math as `IncompleteStepForwardGuard`: static `PROFILE_NAV_LINKS` + tenant custom-form tabs, feature-flag filtered). Backward/Previous navigation and leaving the edit area entirely (`UnsavedProfileLeaveGuard`'s job, SAN-499) are always let through unconditionally — this does not reintroduce the "Previous button blocked" bug fixed earlier in this same milestone.
- On a forward move where the outgoing component reports `isCurrentStepValid() === false`, shows the same `showCenteredAlert(' Please fill in all the required information.')` and returns `false` — this time a *real* `CanDeactivate` block, not a click-handler race.
- Wired as `canDeactivate: [UnsavedProfileLeaveGuard, LiveStepValidityGuard]` (order: leave-confirm first, then live-validity) across all 8 stakeholder module files, alongside the existing guard wiring.
- `isCurrentStepValid()` implemented on all 11 primary profile-edit-step components across every stakeholder type, delegating to whatever live-validity signal each already had (no new validation logic invented): `investments-details` → `!saveButtonDisabled`; `financials-details` (Startup's actual Submit tab) → `!saveButtonDisabled`; `organization-details` / `individual-investor-edit-form` → `organizationForm.valid`; `startup-information` → `startupInfoForm.valid` (matches its own template's existing `[disableNavigation]="!startupInfoForm.valid"` gate); `corporate-intro` / `mentor-intro` / `service-provider-intro` / `program-office-intro` / `individual-profile-edit-form` → `corporateForm.valid`; `partner-intro` → `partnerForm.valid`.
- Tabs not in this list of 11 (e.g. Startup's other sub-pages, Pitch Deck, Representative Details) are not yet audited for this specific live-validity hook and simply fail open for now — same conservative default as everywhere else in this guard, not a regression.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all changes (new guard, new interface, 11 component edits, 8 module-file wiring edits).

## Fix (2026-08-26, same day, found via live testing) — Investor Representative Details had the same gap, plus 5 more secondary tabs closed proactively

**Reported live**: on Investor Organization's Representative Details (the last static tab before the tenant's custom form), the warning fired correctly but the tab still switched anyway. Root cause: `RepresentativeDetailsComponent` was not in the list of 11 components that got `isCurrentStepValid()` in the fix above — it was missed because it wasn't one of the original 9 "primary" SAN-497 tabs, even though it's a real, required-field-bearing step in the Investor flow. `LiveStepValidityGuard` correctly fails open for any component that doesn't implement the interface, so with no hook to call it just let the navigation through — exactly the same failure shape as the Investment Details bug, just on a different, previously-unaudited component.

**Fix**: added `isCurrentStepValid()` to `RepresentativeDetailsComponent` (`representativeInfoForm.valid`).

**Proactively audited the rest of the surface** rather than wait for each remaining tab to be reported one at a time: every component sitting on a route wired with `canDeactivate: [UnsavedProfileLeaveGuard, LiveStepValidityGuard]` across all 8 stakeholder module files was checked for whether it has a genuine, already-established validity signal (a `saveButtonDisabled` getter or a `xxxForm.valid` check already driving that page's own `[disableNavigation]` binding on `<app-form-next-step-button>`, confirmed against each component's own template before reusing it). Closed for 5 more:

- `IndustryTechnologyComponent` (Startup) → `!saveButtonDisabled`
- `CorporateEngagementComponent` → `engagementForm.valid`
- `PartnerIndustryTechnologyComponent` → `!saveButtonDisabled`
- `MentorTechnologyIndustryComponent` → `!saveButtonDisabled`
- `ProgramOfficeTechnologyIndustryComponent` → `!saveButtonDisabled`

Checked and deliberately left alone:
- `ServiceProviderIndustriesComponent` — its `industriesForm` has no `Validators.required` on any control and its own template has no `[disableNavigation]` binding at all today (Next Step is never locally blocked here either) — adding a guard-level block would be new behavior not backed by any existing local gate, so left as-is rather than invented.
- `IndividualInvestmentDetailsComponent` (Investor individual's "Investment Thesis" tab) — confirmed to be an empty stub (`ngOnInit(): void {}`, no form, no fields) — nothing to validate yet; matches the pre-existing flagged gap in SAN-500's record.
- The various `Extra*`/custom-forms dynamic-renderer components (`ExtraInfoCorporateComponent`, `ExtraInfoStartupComponent`, `ExtraInfoPartnersComponent`, `ExtraInfoIndividualComponent`, `ExtraInfoServiceProviderComponent`, `ExtraIntroMentorsComponent`, `ExtraInfoInvestorComponent`) and Startup's several other sub-pages (Product Info, Pitch Deck, Founders, Advisory Board, etc.) were not audited in this pass — they fail open under `LiveStepValidityGuard` exactly like every other not-yet-implementing component, which is the same conservative, non-regressing default the guard was designed around. Flagging as the known remaining gap rather than rushing an unverified validity getter onto components not yet read carefully.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all changes.

## Critical fix (2026-08-26, same day) — `PROFILE_NAV_LINKS` prefix collision silently broke every Investor Organization/Syndicate index calculation

**Reported live**: even with `isCurrentStepValid()` added to `RepresentativeDetailsComponent` (previous fix, same day), the tab still switched after the warning fired. Root cause was one level deeper and much bigger than that one component.

`PROFILE_NAV_LINKS` has **two separate arrays sharing the same URL prefix**: `INVESTOR_INDIVIDUAL` (`/investors/edit/individual-details`, `/investors/edit/individual-investments-details` — 2 tabs, no Representative Details) and the org/syndicate array under the `[ACCOUNT_TYPE.INVESTOR]` key (`/investors/edit/organization-details`, `/investors/edit/investments-details`, `/investors/edit/representative-details` — 3 tabs). Both live under the `/investors/...` segment. Every prefix-resolution helper in this feature (`IncompleteStepForwardGuard.getStaticLinksForPrefix`, `LiveStepValidityGuard.getCombinedLinksForPrefix`, `ProfileStepPositionService.getStaticLinksForPrefix` — all three copies of the same logic, one per file per this codebase's existing duplication convention) resolved a URL to "whichever `PROFILE_NAV_LINKS` array shares this path's leading URL segment" — and since `INVESTOR_INDIVIDUAL` is declared *first* in the object (JS iterates own string keys in insertion order), it silently won for **every** `/investors/...` path, including ones that only exist in the 3-tab org array.

Concretely: for any Investor Organization/Syndicate navigation, all three helpers resolved to the wrong 2-tab Individual array. `'representative-details'` isn't in that array at all, so `IncompleteStepForwardGuard`'s target-index lookup came back `-1` (silently not-modeled, always allowed) and `LiveStepValidityGuard`'s current-index lookup also came back `-1` (fails open by design). This bug has existed since `IncompleteStepForwardGuard` was first written earlier this same day, and `ProfileStepPositionService` inherited the exact same flaw when it was built afterward — meaning Investor Org's Submit-button placement (`isLastStep`) could also have been silently wrong, not just this guard. It went undetected because the guard's own pre-written spec test ("blocks forward navigation within the Investor org variant using its own real form key", targeting exactly `/investors/edit/representative-details`) was asserting the *correct* behavior all along but was never actually executed (`ng test`'s pre-existing bundling breakage, same issue noted throughout SAN-497/498/499) — so a real, reproducible bug sat behind a test that would have caught it immediately if the suite could run.

**Fix**: replaced segment-only matching with `resolveStaticLinksAndPrefix(path)` in all three files — it first tries to find the specific `PROFILE_NAV_LINKS` array that has an **exact matching entry** for the given path (disambiguates `INVESTOR_INDIVIDUAL` vs. the org array correctly, since `'representative-details'` only exists in one of them), and only falls back to the old segment-based resolution when no static array has an exact match at all (the one case that still needs it: the path is itself a custom-forms route, which by definition isn't in any static array — same pre-existing limitation, unchanged, not a regression).

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean. Traced the existing (never-executed) spec test by hand against the new logic: `getTitleFromNavLink()` (used by `getMissingFieldsMap()` to label missing-field groups) was already unaffected by this bug, since it matches by exact route equality, not by segment — so with the guard fix, the trace now correctly reproduces the test's expected `false`/blocked result for the Investor org scenario it describes.

## Critical fix (2026-08-26, found via live testing) — "Next Step" silently did nothing, even with every required field filled

**Reported live**: on Mentor's Basic Information tab, after filling every visible required field (Name, Headline, About You) plus the required-but-off-screen Country field, clicking "Next Step" did nothing at all — no navigation, no error toast, no console output.

**Root cause — unrelated to validity gating, a pre-existing race in the nav-links components' own feature-flag filtering.** `MentorEditPageNavLinksComponent`, `CorporateEditPageNavLinksComponent`, and `StartupEditPageNavLinksComponent` (the 3 of the 8 nav-links variants that have any feature-flag-gated tab at all — Mentor's 'Domain Expertise'/`mentor_domain_expertise_tab`, Corporate's 'Engagement'/`corporates_enagement_form`, Startup's 'Financials'/`financials_form` and 'Industry-Technology'/`industries_technologies_section`) each had:
```ts
getFilteredNavLinks(): void {
  this.navLinks = this.navLinks.filter(link => !link.featureKey || this.brandDetails?.features[link.featureKey]);
}
```
— filtering `this.navLinks` **in place, over its own current value**, using `this.brandDetails`, which is populated by a separate, unordered async store subscription (`getBrandDetails`) racing against whatever first calls `getFilteredNavLinks()`. If that call landed before `brandDetails` had loaded (a real, unguarded race — no resolver blocks route activation on it, and `TenantService.getTenantDetails()` is fired unguarded from `app.component.ts`'s `ngOnInit`), `this.brandDetails?.features[link.featureKey]` evaluated to `undefined` → falsy → the feature-gated tab was filtered **out**. Because the filter always re-filters `this.navLinks` itself rather than a pristine original list, once removed, that tab could **never come back** for the rest of the page's lifetime — every later re-run just re-filtered the already-shrunk array, a no-op, even once `brandDetails` did arrive moments later.

This silently truncated `CommonService.editPageLinks` (the shared, singleton list `goToNextPage()` reads) down to a single entry for the affected type. `FormNextStepButtonComponent`'s `handleClick()` → `commonService.goToNextPage()`:
```ts
goToNextPage() {
  this.editPageLinks$.pipe(take(1)).subscribe((res) => {
    const foundRoute = res.findIndex((e) => e.route === this.router.url);
    if (foundRoute >= 0 && res[foundRoute + 1]) {  // res[1] undefined on a 1-entry list -- silently false
      this.router.navigate([res[foundRoute + 1].route])
    }
  })
}
```
— `foundRoute` correctly resolves to `0` (Basic Information matches), but `res[1]` is `undefined` on the truncated list, so the `if` is false and **nothing happens at all** — no navigation, no error, no log. This is completely independent of `disableNavigation`/form validity (which was correctly `false` once every required field was filled, per the earlier `.valid`-gating fixes in this and the SAN-497 spec) — the button was fully willing to proceed, but the route list it needed to find "what's next" from had already been corrupted on page load, possibly minutes before the user finished filling the form.

**Fix**: all 3 components now keep a pristine `allNavLinks` (static tabs + fetched custom forms, never mutated by feature-flag filtering) separate from `navLinks` (the currently-displayed/exported list). `getFilteredNavLinks()` now always re-derives `this.navLinks = this.allNavLinks.filter(...)` fresh from the pristine source, so a call that runs before `brandDetails` loads simply produces a temporarily-conservative (but self-correcting) result — the next call, whenever `brandDetails` does arrive, recomputes correctly from the untouched original instead of compounding an already-destructive filter. Also hardened `this.brandDetails?.features[link.featureKey]` → `this.brandDetails?.features?.[link.featureKey]` (the `?.` on `brandDetails` doesn't protect a `undefined.features` read) as defensive hardening, though the primary fix (non-destructive re-derivation) is what actually resolves the bug.

**Scope**: the other 5 nav-links variants (Investor org, Investor individual, Partner, Service Provider, Program Office, Individual Profile) have no feature-flag-gated tabs in `PROFILE_NAV_LINKS` today, so this specific race was latent/inert for them — not fixed since there's currently nothing for it to affect, but the same destructive-filter shape may resurface if a flag-gated tab is ever added to one of those types' arrays. Two other files matched the same `getFilteredNavLinks` pattern (`program-details-edit-page-links.component.ts`, `vs-program-details-edit-page-links.component.ts`) but belong to the unrelated Programs/VS-Programs features, not the 8-stakeholder profile-edit flow this spec covers — not investigated or touched.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all 3 file changes.

## Fix (2026-08-26, same day) — CommonService's URL matching had no protection against query params/fragments

**Reported live, after the fix above**: still reproduced on Mentor — but this time the "...updated successfully" toast correctly fired (confirming the form WAS valid and the save genuinely succeeded), yet no navigation happened. This ruled out both the validity-gating fixes and the destructive-filter fix above; the remaining suspect was `CommonService` itself.

**Root cause**: all 4 of `CommonService`'s route-lookup methods (`goToNextPage`, `goToPreviousPage`, `getNextRoute`, `getPreviousRoute`) compared the raw `this.router.url` against each `editPageLinks` entry's `.route` with strict string equality (`e.route === this.router.url`). `PROFILE_NAV_LINKS` routes are always bare paths with no query string or fragment — but `Router.url` reflects whatever is actually in the browser's address bar, which can legitimately carry a query param or fragment (tracking params, a redirect artifact, etc.). If it ever does, the exact-match comparison silently fails, `foundRoute` comes back `-1`, and every one of these methods just does nothing — no error, no log, no feedback of any kind. Every other route-matching helper built during this same milestone (`IncompleteStepForwardGuard`, `LiveStepValidityGuard`, `ProfileStepPositionService`) already strips query/fragment before comparing; `CommonService` — the oldest of the group, predating all of this milestone's work — never did.

**Fix**: added a private `currentPath()` helper (`this.router.url.split('?')[0].split('#')[0]`) and routed all 4 methods through it instead of the raw `this.router.url`, matching the same defensive pattern already used everywhere else in this feature.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after the change.

## Critical fix (2026-08-26, same day) — save-then-navigate raced against the backend completeness re-fetch

**Reported live, for both Partner and Mentor, after every earlier fix in this document**: fill in every required field, see "...information updated successfully", click Next Step -- and it still doesn't move. No error toast (a temporary debug message added mid-investigation confirmed `CommonService.goToNextPage()` itself was finding a valid next route and calling `router.navigate()` -- the block was happening somewhere in the Router's own guard resolution, silently, with no visible message this time).

**Root cause**: `IncompleteStepForwardGuard` (`CanActivate`, runs on the target route) decides whether a tab is "complete" purely from `ProfileService.profileCompleteness` -- a snapshot that only refreshes via an async re-fetch (`tap(() => this.getProfileCompleteness())`) dispatched as a side effect of a successful save. `FormNextStepButtonComponent.handleClick()` fires the save (`next.emit()`) and the navigation attempt (`commonService.goToNextPage()`) essentially together, not sequenced -- so the `CanActivate` guard resolution for that same click typically runs *before* the completeness re-fetch's HTTP round-trip has actually landed in the store. Net effect: a user can fill in every required field, get a genuine "saved successfully" response from the backend, click Next -- and still get silently blocked, because the guard is still reading the *pre-save* snapshot that says this exact tab is incomplete. This is completely independent of every fix earlier in this document (form validity, the `PROFILE_NAV_LINKS` prefix collision, the destructive nav-links filter, the `CommonService` query-param stripping) -- all of those were real, necessary fixes, but none of them touched this specific race, which is why it kept reproducing after each one.

**Fix**: new `LiveCompletionOverrideService` (`shared/utils/live-completion-override.service.ts`) -- a small in-memory record of `(prefix, tab title)` pairs confirmed complete *live*. `LiveStepValidityGuard` (`CanDeactivate`, runs on the page being left, and Angular always resolves `CanDeactivate` before `CanActivate` for the same navigation) now calls `markComplete(prefix, currentLink.title)` the moment it confirms the outgoing page is valid. `IncompleteStepForwardGuard`'s own `isLinkComplete()` check now also accepts `liveCompletionOverride.isConfirmedComplete(prefix, link.title)` as an alternative to the stale backend snapshot -- so a tab just confirmed complete moments ago is never blocked purely because the async re-fetch hasn't caught up yet, without ever needing to delay navigation waiting on a network round-trip, and without weakening the guard for tabs that genuinely haven't been confirmed.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after the new service and both guard changes. The temporary debug toast/console logging added to `CommonService.goToNextPage()` mid-investigation (to rule out a stale-bundle/caching red herring) was removed once this fix landed.

## Critical fix (2026-08-26, same day) — the "in-flight save" flag was doubling as the live-validity signal, racing itself on every click

**Reported live, after every fix above**: Basic Information → Domain Expertise now navigated correctly (confirmed by the user's own screenshot, both tabs showing green checkmarks). But Domain Expertise → the tenant custom form still didn't move: a genuine "Updates saved!" toast fired (save succeeded), yet the URL never changed, with no visible error at all.

**Root cause, found by a fresh, dedicated investigation of exactly this one hop** (`mentor-technology-industry.component.ts`, and identically in `industry-technology.component.ts` (Startup), `partner-industry-technology.component.ts`, `program-office-technology-industry.component.ts`): `saveButtonDisabled` folded two unrelated conditions into one boolean — "is the current data actually valid" and "is a save currently in flight" (`this.loader`) — and `isCurrentStepValid()` (the exact signal `LiveStepValidityGuard` relies on) reused that same combined getter. `handleSave()` sets `this.loader = true` *synchronously*, as its very first statement, before the `PATCH` request's network round-trip even starts. `FormNextStepButtonComponent.handleClick()` then calls `commonService.goToNextPage()` in that same synchronous call stack — Angular's Router resolves guards on the very next microtask, which is *always* before a real HTTP round-trip can possibly have completed. So `LiveStepValidityGuard.canDeactivate()` runs `isCurrentStepValid()` while `loader` is still `true` from this exact click's own save — sees "disabled" — and blocks with its own centered warning, genuinely cancelling the navigation. A moment later the save's own success callback fires, clearing `loader` and showing "Updates saved!" via the same shared `Swal` instance the centered warning was just using — SweetAlert2 only shows one popup at a time, so the success toast silently replaces the just-shown block, leaving no visible trace that anything was ever stopped. This is not an intermittent race — `loader` being `true` at guard-resolution time is *guaranteed* by this exact call ordering, which is why it reproduced 100% of the time on this specific hop, unlike every earlier fix in this document (form validity, tab lists, `CommonService`, the stale-completeness override) which all check out clean and were correctly ruled out as the cause here.

**Why the Basic Information → Domain Expertise hop was unaffected**: `MentorIntroComponent.isCurrentStepValid()` is a plain `!!this.corporateForm?.valid` — Angular's own reactive-form validity, with no reference to any in-flight-save flag. Only the 4 "industry/technology"-style secondary tabs build their own custom `saveButtonDisabled` getter with a `this.loader ||` term baked in, which is exactly why this surfaced specifically on Domain Expertise and not the primary Basic Information step.

**Fix**: split each affected component's validity computation into a new private `isFormDataValid` getter (data only, no loader), and `saveButtonDisabled` now reads `this.loader || !this.isFormDataValid` (the Save/Next-Step button still correctly disables while a save is genuinely in flight) while `isCurrentStepValid()` now reads `this.isFormDataValid` directly (no longer cares whether a save happens to be running). Applied identically to all 4 affected components — `mentor-technology-industry`, `industry-technology` (Startup), `partner-industry-technology`, `program-office-technology-industry`. The other `isCurrentStepValid()` implementations built earlier in this document (`organization-details`, `individual-investor-edit-form`, `investments-details`, `financials-details`, `representative-details`, and the 6 `corporate-intro`-style single-form components) were individually checked and confirmed clean — none of them mix an in-flight flag into their validity signal, so this fix is scoped to exactly the 4 components that had it.

**Verification:** `npx tsc -p tsconfig.app.json --noEmit` clean after all 4 component changes.

## Rollout

Single-repo (`sc-saas-frontend`) deploy, no backend coordination needed (no contract changes). No flag gating planned (contracts.flags is empty). Ship the 9 nav-links variants together, following the same "small, self-contained, ship-together" approach SAN-497 used.

## Out of scope

- Save/auto-save mechanics (SAN-497, already implemented).
- The "leaving without completing your profile" dialog — this is about navigation blocked *within* the form, not leaving it entirely (SAN-499, separate issue).
- Last-page Submit button rearrangement (SAN-500, separate issue).
- Any backend endpoint/DTO change.
- Secondary/non-primary tabs (Corporate Engagement, Mentor Domain Expertise, Investor Investment/Representative Details, Partner Industry/Technology, and any currently-disabled/commented-out steps in `navlinks.ts`) — matches SAN-497's own explicit exclusion for consistency, not silently dropped; candidate for its own follow-up issue if any of these turn out to need independent tab-guard treatment.
- Full manual QA across all 8 stakeholder types (covered by SAN-501).

## Design decisions (resolved 2026-08-24)

1. **Completeness signal: signal (b)** — the backend-computed `profileCompleteness.missingFields`/`getMissingFieldsMap()`. Confirmed over signal (a) per findings 1/2/4: signal (a) has no existing plumbing into nav-links and would need a brand-new `@Input` wired at every step-template embed site across all 9 types; signal (b) needs only a one-file-per-type subscription port, already proven working in 3 of the 9 nav-links components.

2. **Guard scope: Option B (first-incomplete-tab).** Block any tab click whose target is beyond the first incomplete tab anywhere in `navLinks` order, computed via signal (b) across the whole list — not just a check of the currently-viewed tab. Closes the "jump past a different incomplete page" gap Option A would have left open, and better matches the AC's "further ahead than actually completed" wording and the BRD's intent.

3. **On block: stay on the current page.** No auto-redirect to the first incomplete tab — just show the centered warning and leave the user where they were, matching how Next Step's own block behaves today (warn, don't navigate anywhere).

4. **Nav-links signal-(b) wiring audit — confirmed for all 9 variants (2026-08-24):**

   | Nav-links component | Has `missingFields`/`profileCompleteness` today? |
   |---|---|
   | `startup-edit-page-nav-links.component.ts` | **Yes** (10 refs) — reuse as-is |
   | `corporate-edit-page-nav-links.component.ts` | **Yes** (4 refs) — reuse as-is |
   | `mentor-edit-page-nav-links.component.ts` | **Yes** (9 refs) — reuse as-is |
   | `investor-edit-page-nav-links.component.ts` | No — needs porting |
   | `individual-investor-edit-page-nav-links.component.ts` | No — needs porting |
   | `program-office-edit-page-nav-links.component.ts` | No — needs porting |
   | `individual-profile-edit-page-nav-links.component.ts` | No — needs porting |
   | `partners-edit-page-nav-links.component.ts` | No — needs porting |
   | `service-provider-page-nav-links.component.ts` | No — needs porting |

   6 of 9 nav-links components need the `ProfileService.profileCompleteness$` subscription + `getMissingFieldsMap()` porting (following the pattern already proven in the other 3); the other 3 only need the per-link/first-incomplete-index check (finding 2's per-repo plan step 2) added on top of what they already have.

5. **Next Step's warning message: confirmed to be a single generic string, no per-step overrides exist anywhere.** `disableNavigationMessage` is declared with its default (`' Please fill in all the required information.'`) only inside `form-next-step-button.component.ts:22` itself; grepped across the entire `src/app` tree for any consuming template binding `[disableNavigationMessage]` — zero matches. Safe to reuse this exact string directly in the centered-warning path without needing any per-step message lookup.

6. **Centered-warning dismiss behavior:** standard `Swal.fire()` confirm-button pattern (reusing `event-forms.component.ts:438-446`'s existing usage), dismissed by an explicit "Ok" button — not a timed auto-dismiss.

7. **Assignee: Mahima Sharma** (matches SAN-496/SAN-497).

## Open questions

None — all resolved above (2026-08-24).
