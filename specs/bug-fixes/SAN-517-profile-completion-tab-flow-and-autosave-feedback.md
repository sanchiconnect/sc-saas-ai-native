---
id: SAN-517
title: "Profile-completion tab flow (tab-switch race, stale green/red ticks) + auto-save user feedback, across all stakeholder edit-profile forms"
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-517
sentry: []
repos: [frontend]
commit: none — all changes below are uncommitted as of this update
created: 2026-09-10
updated: 2026-09-10
---

# SAN-517 — Profile-completion tab flow + auto-save feedback — all stakeholder edit-profile forms

## How this started
Reported live against `mentor-intro.component.ts` (Basic Information tab): with Photo/Logo genuinely missing, the user could still click through to the next tab. Root-causing that one report uncovered five independent, previously-undiagnosed bugs, all sharing the same underlying architecture (the multi-tab "edit profile" flow every stakeholder type uses: a `*-edit-page-nav-links` component driving the tab strip's red-!/green-check icons and forward-navigation guard, fed by `ProfileService.profileCompleteness$`). Each was traced to a real mechanism (not guessed), verified against the actual `@angular/forms`/RxJS behavior where possible, and then checked across **every** stakeholder type and **every** tab — not just the one first reported — since the same shared architecture meant the same bug class was very likely to recur, and largely did.

## Bug 1 — tab-switch click bypassed the forward-navigation block
**Symptom:** clicking a later tab succeeded even though the current tab was genuinely incomplete, despite the block logic (`isForwardTabNavigationBlocked`, from SAN-498) correctly computing `true`.

**Root cause:** `onNavLinkClick()` called `event.preventDefault()`/`stopImmediatePropagation()` to cancel the click — but Angular's `RouterLink` directive has its own click handler on the same `<a>` that calls `router.navigateByUrl()` directly, without checking whether some other handler already called `preventDefault()`. Confirmed live with diagnostic console logging on `mentor-edit-page-nav-links.component.ts`: the block computed `true`, yet the browser still navigated.

**Fix:** stopped relying on cancelling a navigation `RouterLink` already triggered. `[routerLink]` is now bound to a `getRouterLinkFor(link)` method that returns `null` for a currently-blocked target — `RouterLink` treats `null`/`undefined` as "nothing to link to" and does nothing on click, so there's no navigation to race against. `onNavLinkClick()` now only shows the "please complete required fields" toast.

**Applied to all 9 nav-links components:**
`startup-edit-page-nav-links`, `mentor-edit-page-nav-links`, `corporate-edit-page-nav-links`, `service-provider-page-nav-links`, `program-office-edit-page-nav-links`, `partners-edit-page-nav-links`, `investor-edit-page-nav-links`, `individual-investor-edit-page-nav-links`, `individual-profile-edit-page-nav-links`.

Also corrected `src/app/shared/utils/nav-link-forward-guard.spec.ts`, which had asserted the old (disproven) `preventDefault()`-is-sufficient contract as the "component-level contract" — it now documents and tests the `getRouterLinkFor()`-returns-null contract instead.

## Bug 2 — green/red tick and the block itself never refreshed after a save
**Symptom:** filling in every required field and saving didn't turn a red tab green, and didn't unblock forward navigation — even though the data was genuinely complete.

**Root cause:** each stakeholder type's `GetProfileCompleteness()` (or `GetIndividualProfileCompleteness()`) action was dispatched exactly **once**, in `ngOnInit()`. Nothing ever re-dispatched it after a save succeeded, so `missingFields` (shared across a stakeholder type's tabs via `ProfileService.profileCompleteness$`, a live store subscription) stayed frozen at whatever was true on initial page load.

**Fix:** re-dispatch the relevant completeness action inside each save's success callback.

**Applied to all 9 "first tab" components** (`startup-information` via its NgRx effect `startup.effect.ts`, since its save is a fire-and-forget dispatch with no component-level callback; the other 8 directly) **and all 7 secondary-tab components**, once the same gap was found there too (see "Same bug, other tabs" below): `financials-details`, `industry-technology` (startup), `corporate-engagement`, `mentor-technology-industry`, `partner-industry-technology`, `representative-details` (investor org), `investments-details` (shared by both investor variants' Investment Details/Thesis tab).

## Bug 3 — "N field(s) not complete" badge not clickable (or missing entirely)
**Symptom:** the badge either didn't call out what was missing at all, or was styled as clickable (`cursor-pointer`) but had no `(click)` handler — unlike `startup-information.component.ts`'s own badge, the reference implementation, which marks every control touched and scrolls to the first invalid one.

**Fix:** added `checkInvalidFields()` (marks controls touched) + `scrollToFirstInvalidControl()` + `invalidCheckRequested` flag, matching `startup-information.component.ts` exactly, then wired `(click)="checkInvalidFields()"` and the "Click here to know!" copy into the badge markup.

**Applied to all 9 first-tab components, plus all 7 secondary-tab components** — 3 of the latter (`mentor-technology-industry`, `partner-industry-technology`, `representative-details`) had no badge infrastructure at all and needed it built from scratch, following the same pattern as the existing ones.

## Bug 4 — Basic-Information tab stuck red forever once a bundled sibling tab has its own unmet fields
**Symptom:** with every one of Basic Information's own fields (Name, Photo, Country, Headline, About You) genuinely filled in, the tab still showed red — reported live on Mentor.

**Root cause:** the backend bundles a second tab's completeness fields into the **same** completeness bucket as Basic Information — Mentor's Domain Expertise ("Domain areas are missing", "Industry specialisations are missing") and Corporate's Engagement (4 messages) both live inside the `mentorInformation`/`corporateInformation` bucket, not their own. The frontend already had a special case correctly *excluding* those messages when checking the **sibling** tab's own status (`isCustomProfileFormValid({title: 'Domain Expertise'/'Engagement'})`) — but no reciprocal exclusion when checking **Basic Information**'s own status, so any unmet sibling-tab field kept Basic Information red indefinitely.

**Fix:** added the reciprocal exclusion — when checking Basic Information, only count messages that are *not* in the sibling tab's own message list.

**Applied to the only 2 components with this bundled-tab pattern:** `mentor-edit-page-nav-links`, `corporate-edit-page-nav-links`. The other 7 nav-links components don't bundle any tab's fields together, so this bug class structurally doesn't apply to them.

## Bug 5 — Investor-specific: Investment Thesis tab always green, and two required fields never enforced
Found while re-verifying Bug 1/2 against the individual investor variant specifically.

**5a — title mismatch, always green regardless of fill state.** `MissingFormKeyToUrlMapping['investmentInformation']` only maps the **org** investor's route (`/investors/edit/investments-details`), so the shared `getTitleFromNavLink()` resolution always labels the completeness group "Investment Details" — but the **individual** investor's own nav link is titled "Investment Thesis". The generic `missingFields.find(group => group.key === link.title)` lookup in `individual-investor-edit-page-nav-links.component.ts` therefore never found a match and defaulted to "complete", unconditionally. Fixed with a title reroute (`'Investment Thesis' → 'Investment Details'`) mirroring Bug 4's pattern.

**5b — `saveButtonDisabled` never checked two fields marked required in the template.** "I invest in"/"We invest in" (`businessModelIds`) and "Investability Metrics" (`investAbilityMetricsIds`) both carry a red `*` in `investments-details.component.html`, but `saveButtonDisabled` never checked either array's length — Next Step/Submit could be clicked with neither selected. Added both checks, then built `countInvalidFields`/badge/highlight on top of the corrected logic.

**Cross-repo note, not fixed here:** checked `sc-saas-backend`'s `investor.repository.ts` completeness criteria directly — it tracks `investmentMechanismIds`, `investmentPreferenceIds`, `investmentStageIds`, `ticketSizeMin/Max`, `turnAroundTime`, but **not** `businessModelIds`, `investAbilityMetricsIds`, or even `sectoralInterestIds` (explicitly commented out in the criteria array). So the backend's own "Profile completion %" can still read 100% with those three genuinely empty, independent of every frontend fix above. That's a backend contract gap (frontend requires more than backend tracks) — flagged, not changed, since it's a cross-repo decision (`/audit-contract`-worthy) about what the backend should consider required, not a frontend bug.

## Bug 6 (found last) — auto-save was completely silent
**Symptom (explicit ask, not a live repro):** users who rely on auto-save (SAN-497/SAN-508's 20s-interval + debounced-edit pattern, which removed the manual Save button across every one of these pages) got zero feedback that their edits were actually persisted — `silent=true` suppressed the toast entirely for every auto-save path (interval tick, debounced-edit save, beforeunload).

**Fix:** auto-save now shows a distinct, lighter toast — `"Changes saved automatically"` at `top-end` (top-right), 2s — instead of staying fully silent. Kept deliberately different from the explicit-save toast's own message so the two remain distinguishable, and (on `individual-investor-edit-form.component.ts`) kept the existing scroll-into-view side effect tied to the explicit save only, since auto-scrolling the page during a background save would be disruptive.

**Applied to all 9 first-tab components** (`startup-information` shows one toast per auto-save *cycle* rather than per-section, since its decomposed 5-section auto-save architecture — the only one of the 9 that's structured this way — could otherwise stack up to 5 toasts from one tick) **and all 7 secondary-tab components**.

## Same bug, other tabs — why the scope grew from 9 to 16 files
Bugs 2/3/5b/6 were each first found and fixed only on the "Basic Information"-equivalent (first) tab per stakeholder type. Investigating the Investment Thesis report surfaced that **every stakeholder type has a second (sometimes third) tab with its own, fully independent auto-save** — Domain Expertise (mentor), Engagement (corporate), Industry/Technology (partner, and separately startup), Financials (startup), Representative Details + Investment Details (investor) — and none of them had received any of these fixes. Audited and fixed all 7:

| Secondary tab | Component | Had completeness re-dispatch? | Had clickable badge? |
|---|---|---|---|
| Startup — Financials | `financials-details.component.ts` | No → fixed | Already had it (badge existed, wasn't wired to completeness) |
| Startup — Industry/Technology | `industry-technology.component.ts` | No → fixed | Already had it |
| Corporate — Engagement | `corporate-engagement.component.ts` | No → fixed | Badge existed, wasn't clickable → fixed |
| Mentor — Domain Expertise | `mentor-technology-industry.component.ts` | No → fixed | None → built from scratch |
| Partner — Industry/Technology | `partner-industry-technology.component.ts` | No → fixed | None → built from scratch |
| Investor (org) — Representative Details | `representative-details.component.ts` | No → fixed | None → built from scratch |
| Investor (both variants) — Investment Details/Thesis | `investments-details.component.ts` | No → fixed | None → built from scratch (plus Bugs 5a/5b above) |

**Deliberately not touched:** Startup's Pitch Deck tab (`noStepButton: true` — an upload flow with no form/Save-button slot, structurally different, doesn't fit this pattern) and `step-one-company-info.component.ts` (the edit-profile-*modal* stepper step — no Photo/Logo field and no "field(s) not complete" badge at all; a different UI paradigm from the routed multi-tab pages this doc covers).

## Verification
`npx tsc -p tsconfig.app.json --noEmit` — clean after every round of changes, most recently after the full 16-file sweep. `ng test`/Karma remains broken workspace-wide by pre-existing, unrelated TS errors in other `.spec.ts` files (confirmed while investigating, not fixed here — out of scope). Bug 1's mechanism (RouterLink races preventDefault) and Bug 2's mechanism (`updateValueAndValidity()`/completeness staleness) were each verified directly against the real `@angular/forms`/RxJS behavior standalone in Node, not simulated.

**Live-tested:** only `mentor-intro.component.ts` (Basic Information tab) — the original report — confirmed fixed by the user after Bugs 1, 2, and 4 landed. Every other component listed above (8 more first-tab pages, all 7 secondary-tab pages, both investor-specific fixes) is unverified in a live browser as of this update — flagging explicitly rather than claiming a full pass.

## Outstanding
- Linear issue SAN-517 covers this work — Linear MCP was disconnected for this entire session, so no comment/status update has been posted there yet; do that once reconnected.
- Nothing committed yet — recommend committing promptly once live-tested, given this session's own prior experience losing uncommitted multi-round fixes to an upstream merge (see `specs/bug-fixes/SAN-730-state-city-conditional-required.md`'s History section for that incident).
- Bug 5's backend gap (`businessModelIds`/`investAbilityMetricsIds`/`sectoralInterestIds` not in the investor completeness criteria) is unresolved — needs a `sc-saas-backend` change and a cross-repo decision, not just a frontend fix.
- `service-provider-intro` and `partner-intro` (first tabs) don't mark their own logo/photo field as required at all (no asterisk, not counted in `countInvalidFields`) — flagged during the badge propagation pass, left alone since it's unclear whether that's intentional or a gap; needs a product-owner call, same as Bug 5's backend gap.
