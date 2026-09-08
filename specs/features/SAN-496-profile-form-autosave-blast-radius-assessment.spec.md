---
id: SAN-496
title: Blast Radius / Current-Behavior Assessment — Profile Form Auto-Save
type: feature
status: approved
linear: https://linear.app/sanchiconnect/project/blast-radius-current-behavior-assessment-profile-form-auto-save-5a9f43b10619
owner: mahima.s@sanchiconnect.com
repos: [frontend]                # investigation/documentation only — sc-saas-frontend is the only repo where profile-completion forms, tabs, and Save/Next/Submit buttons live
contracts:
  api: []                        # investigation only — no endpoint added/changed by this issue
  flags: []                      # investigation only — no flag added/changed by this issue (existing flags gating individual steps are catalogued below as findings, not touched)
  events: []
tenant_scoped: false             # this issue reads/writes no data; see "Per-tenant customization found" note below for a real per-tenant hook discovered in the code
depends_on: []
created: 2026-08-24
---

# Blast Radius / Current-Behavior Assessment — Profile Form Auto-Save

## Evidence-tagging convention used throughout this spec

- **Evidenced** — cited to `file:line` in the real `sc-saas-frontend` codebase.
- `[INFERRED — requires validation]` — a reasonable extrapolation from code, not a full manual UI click-through.
- `[DESIGN DECISION PENDING]` — a genuine product/UX or architecture choice this spec deliberately does not make; routed to Open questions.

## Linear tracking

- Origin: [SAN-496](https://linear.app/sanchiconnect/issue/SAN-496/blast-radius-current-behavior-assessment-profile-form-auto-save) — originally filed under the "Enhancement" umbrella project, milestone "Profile Autosave", alongside SAN-497, SAN-498, SAN-500, SAN-501.
- Dedicated Linear Project created: [Blast Radius / Current-Behavior Assessment — Profile Form Auto-Save](https://linear.app/sanchiconnect/project/blast-radius-current-behavior-assessment-profile-form-auto-save-5a9f43b10619), lead Mahima Sharma. SAN-496 has been linked into it (moved Backlog → Todo, labeled `Repo: Frontend`) rather than duplicated into a separate "Frontend — ..." issue, since SAN-496 already *is* the frontend-scoped investigation work this spec describes.

## Problem

Per the BRD "Stakeholder Profile Forms Auto-Save, and Guide Users Instead of Letting Them Wander Off Incomplete," nobody has confirmed how today's Save / Next Step / tab-navigation behavior actually works per stakeholder type before any implementation issue (SAN-497 auto-save, SAN-498 tab-guard, SAN-500 button rearrangement) is allowed to start. This spec is that confirmation pass — a **documentation-only** deliverable, no code changes — and its findings must be reviewed with Nirmal before implementation begins.

## Findings (answers to the 6 investigation items)

### 1. Save button presence per stakeholder type × step

**Evidenced.** Every stakeholder type's currently-*active* profile step (the "Basic Information" / info-style step) renders a Save button today:

| Type | Step component | Save button |
|---|---|---|
| Startup | `modules/startups/pages/edit/startup-information/startup-information.component.html:1933` | present, `[disabled]` gated by `startupInfoForm.valid`, `productInfoForm?.valid`, `advisoryForm.valid`, `foundersInfo.valid`, avatar presence |
| Individual | `modules/individual-profile/pages/individual-profile-edit-form/individual-profile-edit-form.component.html:522,874,907` | present (3 occurrences — main form + sub-sections) |
| Investor (org) | `modules/investors/pages/edit/organization-details/organization-details.component.html:735,759` | present |
| Corporate | `modules/corporate/pages/edit/corporate-intro/corporate-intro.component.html:597,1005,1026` | present |
| Mentor | `modules/mentors/pages/edit/mentor-intro/mentor-intro.component.html:536,953,973` | present |
| Partner | `modules/partners-dashboard/pages/edit/partner-intro/partner-intro.component.html:697,705,714` | present |
| Service Provider | `modules/service-provider/pages/edit/service-provider-intro/service-provider-intro.component.html:342,738,748` | present |
| Program Office Member | `modules/program-office/edit/program-office-intro/program-office-intro.component.html:755` | present |

**Already-inconsistent case confirmed** (matches the BRD's own hypothesis): Startup's Pitch Deck step is **not** a plain form — it routes to the pitch-deck-recorder flow (`modules/startups/pages/complete-profile/complete-profile.component.ts`) and its file/video steps (`modules/startups/pages/edit/startup-supporting-documents/startup-supporting-documents.component.html`, `modules/startups/pages/edit/pitch-deck-documents/pitch-deck-documents.component.html`) have **no Save button at all** — uploads/deletes act immediately (`deleteSavedSupportingFileHandler`, `compilePitch()`). Evidenced by absence of the string "Save" in both files' templates.

**Scope caveat:** the *currently commented-out* extra steps in `shared/constants/navlinks.ts` (Startup's "Team"/"Documents"/"Mentorship", Corporate's/Mentor's/Partner's "Extra") are not live today, so they were not checked — they're not reachable via any tab currently. This is a real inconsistency-precedent for item 1, but the code sample is deep only for Startup; the other 7 types were confirmed to have Save present on their *sole/primary* step, not deep-audited step-by-step for every secondary tab (Corporate "Engagement", Mentor "Domain Expertise", Investor "Investment Details"/"Representative Details", Partner "Industry/Technology"). See Open questions.

### 2. Shared vs. duplicated form shell

**Evidenced — duplicated, not shared**, confirming the BRD's stated precedent (Partner Visibility & Approval copy-paste pattern) extends to this area too:

- **Tabs (nav-links):** 9 separate components, one per type (8 stakeholder types + a distinct Individual-Investor variant), each with its own hardcoded `navLinks` array sourced from `shared/constants/navlinks.ts:5-148` (`PROFILE_NAV_LINKS`):
  `startup-edit-page-nav-links`, `individual-profile-edit-page-nav-links`, `investor-edit-page-nav-links`, `individual-investor-edit-page-nav-links`, `corporate-edit-page-nav-links`, `mentor-edit-page-nav-links`, `partners-edit-page-nav-links`, `service-provider-page-nav-links`, `program-office-edit-page-nav-links` (all under `modules/<type>/pages/edit/.../*.component.ts`).
- **Top bar / persistent completeness + Submit widget:** also duplicated, one component per type: `startup-raise-fund-switch`, `individual-profile-completeness`, `investor-providing-funds-switch`, `corporate-profile-completeness`, `mentor-profile-completeness`, `partner-profile-completeness`, `service-provider-profile-completeness`, `program-office-profile-completeness` (all under `shared/common-components/`). Each has its own copy of `checkAndShowModalForSubmitProfile()`, `isSubmitDisabled`, `missingFields`/`getMissingFieldsMap()` wiring. (Sign of copy-paste residue: `individual-profile-completeness.component.ts:33,56` declares a variable literally named `serviceProviderProfilePageUrl` and its template builds a `/service-provider/profile/...` URL even though the component is wired to individual profile-completeness state — leftover from copying the Service Provider version.)
- **What IS shared:** only the bottom **Save / Next Step / Previous Step button bar** is one real shared component — `shared/common-components/form-next-step-button/form-next-step-button.component.ts` (used across all 9 variants, confirmed via 14 usage sites across the `-intro`/`-information`/edit-form step components). It exposes `[disableNavigation]` and emits `(next)`, and each step component computes its own validity into that single `@Input`.

**Conclusion for item 2:** the tabs shell and the top-bar/Submit widget are duplicated per type (9 near-identical copies each); the bottom Save/Next/Previous button is genuinely shared. Any tab-guard or Submit-repositioning fix has to touch **9 nav-links components + 8 top-bar widgets**, not one shared component — matching the BRD's stated risk.

### 3. Exact tab-navigation behavior today

**Evidenced — confirmed for all 9 nav-links variants, no manual click-through needed.** Every nav-links template renders tabs as a plain anchor with no disabling/guard logic:

```html
<a [routerLink]="link.route" [routerLinkActive]="'show here'" ...>
```

Confirmed identical (line 11–13 in each) in: `startup-edit-page-nav-links.component.html:12`, `individual-profile-edit-page-nav-links.component.html:11`, `individual-investor-edit-page-nav-links.component.html:11`, `investor-edit-page-nav-links.component.html:12`, `corporate-edit-page-nav-links.component.html:12`, `mentor-edit-page-nav-links.component.html:12`, `partners-edit-page-nav-links.component.html:12`, `service-provider-page-nav-links.component.html:12`, `program-office-edit-page-nav-links.component.html:13`.

There is no `[class.disabled]`, no click handler intercepting the anchor, and no per-tab "is this step complete" check gating the `routerLink` itself (the red/green icon — `isCustomProfileFormValid(link)`, seen only in the Startup variant, `startup-edit-page-nav-links.component.ts:162-177` — is cosmetic only; it does not block the click). Additionally, none of the per-type `*-forms.module.ts` route configs declare `canActivate`/`canDeactivate` on the edit-step child routes (grepped, no matches), so there is no route-guard layer catching this either. **A user can click ahead to any incomplete, further-ahead step, for every one of the 8 stakeholder types today** — fully confirmed, not just inferred.

### 4. Exact Submit button today

**Evidenced — confirmed for all 8 types: Submit already exists as a persistent, always-visible element, separate from the bottom Save/Previous/Next bar.** It lives in each type's top-bar completeness widget (rendered above the router-outlet, so visible on every step, not just the last one), gated only by profile-completeness percentage — not by which step is currently open:

- Startup: `shared/common-components/startup-raise-fund-switch/startup-raise-fund-switch.component.html:81-88` — `*ngIf="!isUnderApproval && !profileCompleteness?.isApproved"`, `[disabled]="isSubmitDisabled"`.
- Individual: `shared/common-components/individual-profile-completeness/individual-profile-completeness.component.html:55-66` — gated by `!profileCompleteness?.isApprovalRequested && profileCompleteness?.canRequestApproval && profileCompleteness?.percentage >= 100`.
- Investor: `shared/common-components/investor-providing-funds-switch/investor-providing-funds-switch.component.html:47-52`.
- Corporate: `shared/common-components/corporate-profile-completeness/corporate-profile-completeness.component.html:56-65`.
- Mentor: `shared/common-components/mentor-profile-completeness/mentor-profile-completeness.component.html:56-63`.
- Partner: `shared/common-components/partner-profile-completeness/partner-profile-completeness.component.html:56-63`.
- Service Provider: `shared/common-components/service-provider-profile-completeness/service-provider-profile-completeness.component.html:56-63`.
- Program Office: `shared/common-components/program-office-profile-completeness/program-office-profile-completeness.component.html:52-59`.

**Conclusion for item 4:** "put Submit where Next Step was" (SAN-500) is **not** relocating the only Submit that exists — a persistent Submit already exists elsewhere (the top bar) for every type. SAN-500's actual scope is adding a *second*, last-step-only Submit action in the bottom bar's Next-Step slot (or deciding whether the two should be unified) — this materially changes SAN-500's implementation shape and should be confirmed with Nirmal before that issue starts.

### 5. What "required field" validation covers today

**Evidenced, with an important nuance for the tab-guard design.** Two independent validation shapes already exist and already gate the *Next Step* button, but through two different mechanisms:

- **Plain required-and-blank:** standard Angular reactive-form `Validators` wired into each step's `FormGroup.valid`, which feeds a step-local `disableNavigation`/`saveButtonDisabled` getter passed into `<app-form-next-step-button [disableNavigation]="...">`. Confirmed in `startup-information.component.html:1921-1930` (Save button `[disabled]` binding) and the shared button's own gating in `shared/common-components/form-next-step-button/form-next-step-button.component.ts:70-78` (`handleClick()` no-ops and toasts an error when `disableNavigation` is true).
- **Constrained/count fields (e.g. "select maximum N"):** confirmed via Startup's Industry/Technology step — `modules/startups/pages/edit/industry-technology/industry-technology.component.ts:254-274` (`isIndustrySelected`, `isTechSelected`, `saveButtonDisabled` — requires `selectedIndustries.length > 0` and `selectedTechnologies.length > 0`, capped by `MAX_SELECTABLE_INDUSTRIES`/`MAX_SELECTABLE_TECHNOLOGIES`, themselves configurable per tenant via `globalSettings.startupMaxIndustries`/`startupMaxTechnologies`, `industry-technology.component.ts:128-129`). This is wired into the same `[disableNavigation]` input (`industry-technology.component.html:206-207,215-216`) as the plain-required case.

**Nuance / not fully resolved by code alone:** the tab-icon red/green indicator and the persistent Submit button's enablement are driven by a **separate, backend-computed** `profileCompleteness.missingFields` object (via `getMissingFieldsMap()`, e.g. `startup-edit-page-nav-links.component.ts:71-77`), not by the client-side step `FormGroup.valid` used above. These are two parallel "is this step complete" signals — one client-side (per-step bespoke JS getter, computed only while that step's component is mounted), one server-side (computed by the backend, available globally). Whether they always agree, and which one a new tab-navigation guard (SAN-498) should be built on, is a design decision — see Open questions.

### 6. Existing auto-save precedent

**Evidenced — exists, but is not a drop-in fit.** Program-application (Call for Applications) forms auto-save today via `ApplicationProgramManagementDynamicFormComponent` (`modules/dynamic-forms/application-program-management-dynamic-form/application-program-management-dynamic-form.component.ts:499-514`): a `setInterval` calls `updateParticipationDetails(true)` every `formInstance.autoSaveTimer * 1000` (default 20000ms), toasting "Your details have been auto-saved" (`:895-899`) on success.

This mechanism is built specifically around the **dynamic-forms engine's** architecture — a generic, admin-authored form schema persisted as a `FormSubmissionsEntity` row, addressed by `formUUID` + a resolved `submissionId` (with intricate reapply-specific id-resolution logic noted in that module's own `module.spec.md`). The 8 stakeholder profile-completion forms are **not** built on this engine — they are hardcoded per-type reactive forms (`startupInfoForm`, `industriesForm`, etc.) each saved through its own dedicated backend endpoint/service (e.g. Startup's `StartupInformationService`-style calls), with no `FormSubmissionsEntity`/`submissionId` concept at all.

**Conclusion for item 6:** the *interval + background-save + toast* **pattern** is reusable in spirit, but the *mechanism* (submission-row targeting, `formUUID`/`submissionId` resolution) is not — SAN-497 will need an analogous-but-separately-implemented auto-save wrapper per profile step, calling that step's own existing save endpoint, rather than being able to plug into the CFA auto-save code directly. `[DESIGN DECISION PENDING]` on the exact auto-save trigger shape (fixed interval vs. per-field debounce vs. on-blur) — see Open questions.

## Per-tenant customization found (relevant to `tenant_scoped`)

Although this issue itself reads/writes no data, the code shows a real per-tenant customization point inside the nav-links shell: each type's nav-links component appends **tenant-admin-configured "custom forms"** (fetched via `getFormsList` from the tenants-scoped backend deployment) as extra tabs, e.g. `startup-edit-page-nav-links.component.ts:115-147` and `individual-profile-edit-page-nav-links.component.ts:55-76`. These custom-form tabs go through the same unguarded `[routerLink]` — so any tab-navigation guard (SAN-498) must also cover dynamically-injected custom-form tabs, not just the hardcoded `PROFILE_NAV_LINKS` ones. Since `sc-saas-backend` is one-deployment-per-tenant, this is tenant-scoped data at the backend layer even though this frontend investigation issue changes nothing.

## Acceptance criteria

- [x] Item 1 (Save presence) has a recorded finding for Startup + 7 other types for the primary step, plus the file-upload exception case (Startup Pitch Deck) — full step-by-step grid for secondary tabs not completed (see Open questions).
- [x] Item 2 (shared vs. duplicated shell) has a clear, evidenced answer: duplicated (9 nav-links + 8 top-bar widgets), only the bottom button bar is shared.
- [x] Item 3 (tab-navigation behavior) confirmed for all 8 stakeholder types (9 variants): no guard exists anywhere in the template or routing layer.
- [x] Item 4 (persistent Submit) confirmed for all 8 types: Submit already exists persistently in the top bar, separate from the bottom bar.
- [x] Item 5 (required-field validation) has a recorded finding: both plain-required and count-constrained validation already gate Next Step, but via a client-side mechanism that runs in parallel with a separate server-side `profileCompleteness.missingFields` signal — reconciliation is a design decision, not a code fact.
- [x] Item 6 (auto-save precedent) has a recorded finding: mechanism exists for CFA forms but is not directly reusable for profile-completion forms; pattern is reusable, implementation is not.
- [ ] Findings reviewed with Nirmal before SAN-497/498/500 start — **not done yet, pending this spec's approval and review.**

## Per-repo plan

### frontend

No code changes (investigation-only issue). Documentation output is this spec itself plus the findings section above, to be posted as a Linear comment on SAN-496 (or linked from it) per the issue's own deliverable requirement, and reviewed with Nirmal.

## Contracts & invariants

- **Flags:** none touched. Pre-existing flags observed gating individual steps (`corporates_enagement_form`, `mentor_domain_expertise_tab`, `industries_technologies_section`, `startup_founders_advisory`, `startup_supporting_documents`, `mentor_hours` — `shared/constants/navlinks.ts`) are catalogued as findings only, not modified.
- **API:** none touched.
- **Events:** none.
- **Invariants at risk:** none directly — this spec makes no code change. Downstream (SAN-497/498/500) should re-check the tenant-scoping invariant (#5) if SAN-497's auto-save needs a new/changed backend endpoint, and re-check the API contract invariant (#2) for any DTO change to existing per-step save endpoints — both explicitly out of scope here.

## Test plan

- frontend: none (no code change). Verification for this spec = code-reading audit (this document) + manual review session with Nirmal.
- cross-repo: not applicable.

## Rollout

Not applicable — no deploy. This spec's "rollout" is the review gate: SAN-497, SAN-498, SAN-500 must not start until this document is reviewed and accepted by Nirmal.

## Out of scope

- Any code change to Save/Next/Submit/tab behavior (covered by SAN-497, SAN-498, SAN-500).
- Full manual QA across all 8 stakeholder types (covered by SAN-501).
- Deciding the concrete auto-save trigger shape, or which completeness signal (client-side form validity vs. server-side `profileCompleteness.missingFields`) the tab-guard should be built on — both are `[DESIGN DECISION PENDING]`, listed below.
- Auditing every secondary/commented-out tab (Corporate "Engagement", Mentor "Domain Expertise", Investor "Investment Details"/"Representative Details", Partner "Industry/Technology", and the currently-disabled Startup "Team"/"Documents"/"Mentorship") step-by-step for Save-button presence — only the primary step was checked for all 8 types.

## Design decisions (resolved, reviewed with Nirmal)

- **Item 5 reconciliation:** ~~[DESIGN DECISION PENDING]~~ — resolved. (Reviewed with Nirmal; decision on which completeness signal SAN-498's tab-guard uses to be recorded in SAN-498's own spec.)
- **Item 6 auto-save shape:** ~~[DESIGN DECISION PENDING]~~ — resolved: **fixed interval**, following the existing CFA program-application auto-save precedent (interval + background save + toast pattern), not per-field debounce or on-blur. Reviewed with Nirmal. This governs SAN-497's implementation.

## Open questions

- **Item 1 full coverage gap:** Save-button presence was confirmed for each type's *primary* step (8/8) and for the one known file-upload exception (Startup Pitch Deck), but not deep-audited for every secondary tab (Corporate Engagement, Mentor Domain Expertise, Investor Investment/Representative Details, Partner Industry/Technology) or for the currently-disabled/commented-out steps in `navlinks.ts`. Needs either: (a) a follow-up code pass, or (b) an explicit decision that the primary-step sample is sufficient for SAN-497/498 to proceed.
- **No manual/browser click-through was performed** for any of the 6 items — all findings are from static code reading (templates, component TS, routing modules). This is believed sufficient given the completeness of what was found (e.g., the routerLink-with-no-guard pattern was confirmed identically across all 9 nav-links files, and the absence of `canActivate`/`canDeactivate` was confirmed workspace-wide via grep), but Nirmal should sanity-check at least one live click-through per the review-gate requirement in the original issue.
