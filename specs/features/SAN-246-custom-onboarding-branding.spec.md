---
id: SAN-246                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # per-repo issue, SAN-246 (tenants). Full issue set: SAN-246..SAN-250.
title: Per-tenant custom branding for all 10 onboarding screens — default vs custom design mode
type: feature
status: approved                # Approved by document owner (Nirmal), 2026-08-05 — zero open questions, Linear tracking in place (SAN-246..SAN-250).
linear: https://linear.app/sanchiconnect/project/per-tenant-custom-branding-for-all-10-onboarding-screens-5876325b54ad
owner: nirmal.s@sanchiconnect.com
repos: [tenants, backend, frontend, tenants-admin, admin]   # dependency order
contracts:
  api:
    - "GET api/v1/public/global/settings (sc-saas-backend, EXISTING route — response shape extended, not a new route)"
  flags:
    - "custom_onboarding_design_enabled"
  events: []
tenant_scoped: true
depends_on: []
created: 2026-08-05
---

# Per-tenant custom branding for all 10 onboarding screens — default vs custom design mode

## Reference

Business intent comes from `BRD-Dynamic-Auth-Pages-Branding-v1.pdf` (v1.0, 4 Aug 2026, reference client
Start-Up Tripura / T-RISE). Scope, a real naming bug, and the spec's hardest open questions were all
resolved across thirteen passes with the document owner — tracked here in full so nothing gets silently
lost or re-litigated:

- **v1:** two states, not three; scope narrowed to Login + Signup only.
- **v2:** added the form card as a second surface needing its own background + heading.
- **v3:** logos corrected from an open-ended gallery to two fixed light/dark slots.
- **v4:** all eight prior open questions resolved; background color/image found to coexist rather than
  being mutually exclusive; text color found to be per-element, not per-screen.
- **v5:** scope reverted to all 8 of the BRD's original screens (Login, Signup, and the 6
  "Create Profile as…" screens), surfacing the central engineering problem: those 6 screens have no
  hero-panel layout to extend today.
- **v6:** two corrections:
  1. Logo cap raised from exactly-2-light/dark-variants to up to 4, dropping the variant model in favor
     of a simple multi-mark lockup — flagged as an unconfirmed assumption at the time.
  2. **A real bug in every prior version of this spec, found while verifying the new screens:**
     "Incubator/Accelerator" was never a real account type in this codebase — it doesn't exist in the
     `ACCOUNT_TYPE` enum. It's a sub-classification *inside* the Partner account type
     (`PartnerType.INCUBATOR` / `.ACCELERATOR`, `partners.model.ts:85-95`). Every version through v5
     silently mislabeled one of the 6 profile screens as "Incubator/Accelerator" when it should have
     been **Partner**. Combined with the document owner's request to add Service Provider and Program
     Office as additional screens, the corrected, verified list of profile screens is now **8** (not 6):
     Startup, Investor, Corporate, Mentor, **Partner**, Service Provider, Program Office, Individual —
     the exact `ACCOUNT_TYPE` enum values (`auth.model.ts:31-42`) minus `OTHER` and `JOB_SEEKER`, which
     aren't in scope. Total screens: Login + Signup + 8 profile screens = **10**.
- **v7 (this pass): the logo model is simplified and resolved.** Logo cap reduced from v6's "up to 4"
  to **up to 2** — plain marks, no light/dark variant, no 4-mark lockup. More importantly, the
  fallback behavior is now explicit: **if no logo is uploaded, nothing renders in the logo area at
  all** — no placeholder, no fallback to the platform's default logo. The stated reasoning: logos are
  meant to sit *on top of* a tenant's own uploaded hero background image, not to stand in for one — a
  tenant who hasn't set up a custom background hasn't set up custom logos either, so there's nothing to
  show. This resolves v6's open question about confirming the logo model; it's now a Decision (#7),
  not an open item.
- **v8:** the form-card background is corrected to color-only. Re-examining the reference screens
  confirms the page is structurally two panels — a background *image* only ever appears on the
  left/hero panel; the right/form panel's background is always a flat color. v6's Decision #9
  ("background color and image coexist") is now scoped to the **hero panel only** — the form panel
  never had an image field to begin with, on any screen. This removes the `form_bg_image` field from
  every screen's data model and simplifies the form-panel admin UI to a single color picker.
- **v9 (this pass): the route-context split is resolved — the biggest open item in the spec, closed.**
  Confirmed: route-data is the right mechanism, and "dashboard editing" means precisely *any* path to
  the 8 profile components other than the one automatic redirect immediately after signup — including a
  user logging back in later with an incomplete profile. Resolving this exposed a real implementation
  detail worth catching now: **static Angular route `data` is the wrong tool**, since it'd apply to every
  visit to that route regardless of how it was reached. The corrected mechanism uses Router navigation
  **state**, set only inside the post-signup redirect call — see the frontend per-repo plan.
- **v10:** background image size cap raised to 10MB (was 5MB). Format list unchanged (JPG, PNG, WebP,
  SVG). Pixel dimensions remain the one still-unspecified sub-item.
- **v11:** background stacking mechanics resolved. No blend, no opacity control, no admin-configurable
  mixing. It's a precedence rule: on the hero panel, if a background image is set, it renders and the
  color doesn't show at all; the color only ever renders when no image is set. Both fields stay
  independently settable (not a forced either/or toggle) — the BRD's "mutually exclusive" framing was
  closer to right than v4's "coexist and layer" language suggested, just not for the reason the BRD gave.
- **v12 (this pass): the last open question is resolved — zero remain.** No fixed max width×height at
  upload. Instead, the hero background image is resized at render time via the platform's existing
  ImageKit URL-transformation pipeline (the same mechanism `LogoRendererComponent` already uses),
  adapting to actual screen resolution rather than constraining what a tenant can upload. With Decisions
  #5 (format/size), #9 (rendering precedence), and #12 (dimensions) covering every angle of the
  background-image question, and #11 covering the route-context problem, this spec has no open items
  left — see Open questions.
- **v13:** a real repo gap, found while preparing Linear tracking. `repos:` never listed
  `sanchiconnect-saas-tenants-admin`, even though every version since v9 described the Decision #1
  operator switch as living there — it had no per-repo plan section of its own. Added one; `repos:` now
  correctly lists all 5 affected repos in dependency order.
- **v14 (this pass): Linear tracking created.** Linear Project "Per-tenant custom branding for all 10
  onboarding screens" created under the Sanchiconnect team, with one Todo issue per repo in the
  per-repo plan's dependency order: SAN-246 (tenants), SAN-247 (backend), SAN-248 (frontend), SAN-249
  (tenants-admin), SAN-250 (admin). `id` and `linear` frontmatter fields updated accordingly; file
  renamed from `DRAFT-custom-onboarding-branding.spec.md` to `SAN-246-custom-onboarding-branding.spec.md`.
  `status` intentionally left as `draft` — moving to `approved` remains an explicit call for the document
  owner.

## Problem

Every tenant today renders the same shared design across Login, Signup, and each of the eight
stakeholder-specific "Create Profile as…" screens (Startup, Investor, Corporate, Mentor, Partner,
Service Provider, Program Office, Individual) — there is no way for a tenant to apply their own brand
identity (logos, background, heading/body copy and color, on both a hero panel *and* a form card) to
any of them. Some clients (e.g. Start-Up Tripura / T-RISE) want a fully custom look across all 10
screens without engineering involvement per client. This is a presentation-only feature: no auth logic,
form field, or validation changes — and no change to which stakeholder types a tenant offers on Signup,
which is already configurable independently of this work.

## The one hard problem in this spec — resolved this pass

Everything else here generalizes cleanly across screens. This didn't, until now:

**Login and Signup already render inside a two-panel hero+form layout. The eight "Create Profile as…"
screens do not** — today they render as full-width pages inside `ProtectedLayoutWrapperComponent`, the
same dashboard chrome (sidebar, header, footer) used everywhere else in the logged-in product. There is
no hero panel there to extend. Matching the BRD's reference look for any of them is new layout
construction, not a config extension.

**All 8 are already reached as a continuation of onboarding, not general dashboard editing.**
`register.component.ts:207-299`'s `checkAndRedirectToEditPage()` sends a freshly-registered user
straight to the matching one of these 8 components immediately after signup — confirmed routes:
`/partners/edit/partner-information` (`PartnerIntroComponent`),
`/service-provider/edit/service-provider-information` (`ServiceProviderIntroComponent`),
`/program-office-members/edit/program-office-member-information` (`ProgramOfficeIntroComponent`), and
the equivalents for the other 5 types.

**Resolved (Decision #11): the route-data split is confirmed as the mechanism, and "dashboard editing"
is defined precisely.** The branded onboarding layout applies **only** to that one automatic,
uninterrupted redirect immediately following signup submission — the single request-chain
`checkAndRedirectToEditPage()` triggers. Every other way of reaching the same 8 components counts as
**dashboard editing** and stays on today's unbranded `ProtectedLayoutWrapperComponent`, with no
exceptions:
- a returning user editing a completed profile from the dashboard menu,
- a user who signed up, didn't finish their profile, logged out, and **logs back in** later — even
  though their profile is still incomplete, reaching the same screen via a *login* rather than the
  *signup* redirect makes it dashboard editing, not onboarding.

This keeps the mechanism simple and stateless: no "has this user completed onboarding" flag on the user
record, no ambiguity about partially-finished profiles — it's purely "did this render happen from the
one specific post-signup redirect, in that same flow, or not."

## Decisions

1. **Flag ownership** — platform-gated. A platform operator enables `custom_onboarding_design_enabled`
   per tenant in `sanchiconnect-saas-tenants-admin`; not tenant self-serve.
2. **CTA color** — reuse the existing global `primary_color` setting, applied to every button on all 10
   screens.
3. **Bullet input** — a structured add/remove/reorder list editor, stored as an ordered array.
4. **Partial configuration** — any screen left unconfigured while Custom is on falls back to the
   platform default.
5. **Background image constraints** — JPG, PNG, WebP, SVG; max 10MB (revised this pass, was 5MB). No
   fixed pixel dimension requirement at upload — see Decision #12.
6. **Logo lockup scope** — one shared logo lockup across all 10 screens, not per-screen.
7. **Logo count — up to 2 (final, resolved this pass).** Two independent, optional upload slots — no
   variant concept, no gallery. **Empty-state rule: if neither slot is uploaded, the logo area renders
   nothing at all** — no placeholder, no fallback to the platform's default logo asset. Logos are meant
   to sit on top of a tenant's own uploaded hero background image, not to substitute for one; a tenant
   without a custom background hasn't set up custom logos either. Each screen still has its own
   visibility toggle for the cases where logos *are* uploaded but a specific screen shouldn't show them.
8. **Primary/accent input mechanism** — two plain text fields per heading, each with its own hex color.
9. **Background rendering — precedence, not blending (finalized this pass).** Both a color and an image
   are independently settable on the **hero/left panel only** — the admin isn't forced to pick just one
   via an either/or toggle. But at render time there's no visual layering, blend, or opacity: **if a
   hero background image is set, it renders and the color is not shown at all; the color renders only
   when no image is set.** Image always wins when present — it's a fallback relationship, not a
   composite one. This resolves the last open question about stacking mechanics: there is no blend to
   configure. **The form/right panel's background is color-only, on every screen** — it never had an
   image field to begin with, so this precedence rule doesn't apply there.
10. **Text color granularity** — per text element (heading primary, heading accent, body/bullets), not
    per screen.
11. **Route-context split (resolved this pass — see "The one hard problem," above).** A route-data flag
    on the single automatic post-signup redirect is the mechanism. Reaching the same 8 components any
    other way — including logging back in later with an incomplete profile — is dashboard editing,
    unbranded. No user-record flag, no "onboarding completed" state to track.
12. **Background image pixel dimensions — no fixed upload constraint (resolved this pass).** Rather than
    enforcing a hard max width×height at upload time, the hero background image is resized dynamically
    at render time based on the actual display resolution — reusing the platform's existing ImageKit
    URL-transformation pipeline, the same mechanism `LogoRendererComponent` already uses today
    (`(logoUrl | imagekitUrlAppender) + '?h-75,cm-pad_resize,q-100'`). The admin upload only needs to
    enforce the already-set format/size limits (Decision #5); responsive sizing per screen resolution is
    handled by appending the appropriate ImageKit transform params for the hero panel's rendered
    dimensions at each breakpoint, not by constraining what the tenant is allowed to upload.
13. **Signup wizard scope — confirmed intentional (this pass).** "Signup" is the "I am" account-type
    step specifically (Decision matches the reference screens). The hero panel and form-panel
    background color are applied once at `register.component`'s top level and so persist across all 4
    wizard steps (I am → Account Information → OTP → Completed) — but the heading override is passed
    only to `<app-account-type>` (step 0). Steps 1–3 keep their own default heading text while the hero
    image/logo and form background stay custom around them. Confirmed with the document owner this is
    the desired behavior, not a gap: one consistent hero/background for the whole signup experience,
    with the heading differing only on the one step the BRD's reference screens actually showed
    branded.

## Corrections vs the BRD

1. No existing branding pipeline runs from `tenants` (cockpit) to the frontend for actual assets — only
   for boolean/string flags. Real branding rides `sc-saas-backend`'s `spa_settings` →
   `GET public/global/settings` → frontend `IGlobalSettings`.
2. `AuthLayoutWrapperComponent` renders nothing today — a bare shell.
3. Login and Signup already have separate hero images (`loginSideImage`/`registerSideImage`); none of
   the 8 profile screens has an equivalent field today.
4. **The eight "Create Profile as X" screens are not part of the auth flow's layout at all** — see "The
   one hard problem," above.
5. Admin writes are direct-to-DB (Medoo), never an API call, in either direction.
6. A "global CTA color" analog (`primary_color`) already exists — reused per Decision #2.
7. **"Incubator/Accelerator" is not an account type — it's a `PartnerType` sub-field inside Partner**
   (`partners.model.ts:85-95`, rendered as two radio options inside `PartnerIntroComponent`). Every
   version of this spec through v5 mislabeled one of the profile screens with this name; corrected this
   pass. The genuine `ACCOUNT_TYPE` enum (`auth.model.ts:31-42`) has exactly 8 stakeholder-facing values
   relevant here: `startup`, `investor`, `corporate`, `mentor`, `partner`, `service_provider`,
   `program_office`, `individual` (excludes `other` and `job_seeker`).
8. Logos resolved to a fixed-count lockup (Decision #7), not an open-ended gallery.
9. The form card is 100% hardcoded today on Login/Signup — zero styling hooks; the 8 profile screens
   don't even have a form-card *concept* yet, since they render as plain dashboard content.
10. Background color and image are both independently settable on the hero panel — the admin isn't
    forced into an either/or toggle, which is a real departure from the BRD's "mutually exclusive"
    statement. But the *rendered result* is closer to the BRD's intent than it first appeared: image
    wins whenever present, color is fallback-only — there's no visual blend (Decision #9, finalized).
    The form panel was never part of that statement to begin with; it's color-only, full stop.
11. Text color is per-element, not per-screen.

## Acceptance criteria

- [ ] A tenant has exactly one onboarding-design state: Default or Custom, flipped only by a platform
      operator.
- [ ] For **all 10 screens** — Login, Signup, Startup, Investor, Corporate, Mentor, Partner, Service
      Provider, Program Office, Individual — independently, a tenant admin can set the same field set:
      hero panel (logo-lockup visible, heading primary/accent text+color, reorderable body/bullet list
      with its own color + visible, background color + optional image) and form card (**background
      color only — no image field**, heading primary/accent text+color).
- [ ] Up to 2 logo images make up the shared lockup, applied identically wherever the logo is shown; if
      neither is uploaded, the logo area renders nothing — no placeholder, no default-logo fallback.
- [ ] The 8 profile screens render this branding **only** on the immediately-post-signup path, not when
      reached later from the dashboard for editing.
- [ ] One global CTA color applies to every screen's buttons.
- [ ] Any unconfigured screen falls back to its current appearance exactly.
- [ ] Switching Default → Custom → Default reverts every screen; Custom config is preserved, not deleted.
- [ ] Which stakeholder types appear on the Signup account-type picker is unaffected by this feature.
- [ ] No change to any form field, validation rule, or submission logic on any of the 10 screens.

## Per-repo plan

### tenants (`sanchiconnect-saas-tenants`) — Linear: SAN-246

- One boolean column on `TenantUsersEntity` (`custom_onboarding_design_enabled`, default `false`),
  added to the explicit field lists both `verify_tenant` and `getTenantSettings()` read from.
- No screen content lives here — only the on/off switch, flipped exclusively in
  `sanchiconnect-saas-tenants-admin`.

### backend (`sc-saas-backend`) — Linear: SAN-247

- Add `CUSTOM_ONBOARDING_DESIGN` to the `Feature` enum.
- Extend `spa_settings` with 2 global logo fields (`onboarding_logo_1`, `onboarding_logo_2`, each
  optional) plus, per screen key (`login`, `signup`, `startup`, `investor`, `corporate`, `mentor`,
  `partner`, `service_provider`, `program_office`, `individual` — 10 keys):
  - Hero: `<screen>_hero_logo_visible`, `<screen>_hero_heading_primary_text`,
    `<screen>_hero_heading_primary_color`, `<screen>_hero_heading_accent_text`,
    `<screen>_hero_heading_accent_color`, `<screen>_hero_body_items` (JSON array),
    `<screen>_hero_body_color`, `<screen>_hero_body_visible`, `<screen>_hero_bg_color`,
    `<screen>_hero_bg_image` (optional) — 10 fields
  - Form: `<screen>_form_bg_color` (color only — no `_form_bg_image` field exists, Decision #9),
    `<screen>_form_heading_primary_text`, `<screen>_form_heading_primary_color`,
    `<screen>_form_heading_accent_text`, `<screen>_form_heading_accent_color` — 5 fields
  - 15 fields × 10 screens + 2 global = **152 settings rows**, additive, no new tables.
- Extend `getGlobalSettings()`'s response with all of the above, on the existing
  `GET public/global/settings` route. The response layer (not just the frontend) should omit/null the
  logo fields when neither global slot is uploaded, so the frontend has a clean "nothing configured"
  signal rather than needing to infer it.

### frontend (`sc-saas-frontend`) — Linear: SAN-248

- **Login + Signup:** as in v4/v5 — extend `LoginRegisterPage`, bind the previously-hardcoded form
  headings, add a background-color binding to the form card wrapper (color only — no image/upload
  handling needed there) and a background binding to the hero panel that renders the image when set,
  falling back to the color only when no image is present (Decision #9 — a precedence check, not a
  composite/blended style). The hero background image URL is piped through the existing
  `imagekitUrlAppender` (same one `LogoRendererComponent` already uses) with resize params sized to the
  hero panel's actual rendered dimensions per breakpoint — per Decision #12, no fixed upload dimension
  is enforced; responsiveness is handled here, not at upload time.
- **Logo rendering:** a small component reading up to 2 URLs from the global settings, rendered in slot
  order. If both are absent, the component renders nothing — no markup, no reserved space, no fallback
  to the platform's default logo asset (that fallback still applies outside Custom mode, unchanged).
- **The eight profile screens — new work, not extension:**
  - **Implementation note on Decision #11:** static route `data` (e.g. `data: { onboarding: true }` on
    the route definition) is the *wrong* tool here — it would apply every time that route path is
    visited, including a later login-triggered redirect to the same URL, which Decision #11 explicitly
    excludes. Use Angular Router navigation **state** instead
    (`this.router.navigate([...], { state: { onboarding: true } })`), set only inside
    `checkAndRedirectToEditPage()`'s post-signup call — state travels with that one navigation, not with
    the route itself, so a later visit to the identical URL (e.g. via login) arrives with no such state
    and correctly falls through to dashboard editing.
  - Build one new shared two-panel layout component (hero + form card) — reviving the dead
    `RegisterSidebarComponent` as the hero half is the natural starting point — reused across Login,
    Signup, and all 8 profile screens rather than building 10 one-off layouts.
  - Each of the 8 components (`StartupInformationComponent`, `OrganizationDetailsComponent` (Investor),
    `CorporateIntroComponent`, `MentorIntroComponent`, `PartnerIntroComponent`,
    `ServiceProviderIntroComponent`, `ProgramOfficeIntroComponent`, `IndividualInvestorEditFormComponent`)
    reads the navigation state (via `Router.getCurrentNavigation()` on init, since router state isn't
    otherwise available after the fact) plus the feature flag, to decide which layout wraps it — the
    component's own form/validation logic is untouched either way.
  - Reached any other way — dashboard menu, a later login while the profile is still incomplete —
    all 8 render inside `ProtectedLayoutWrapperComponent` exactly as today, unbranded, per Decision #11.
- `AuthLayoutWrapperComponent` stays a bare shell for Login/Signup; the new profile-screen layout is a
  separate component, not a retrofit of it.

### tenants-admin (`sanchiconnect-saas-tenants-admin`) — Linear: SAN-249

- **This is the actual home of the Decision #1 operator switch** — a gap in every prior version of this
  spec, which described the switch as "flipped in `sanchiconnect-saas-tenants-admin`" without ever
  giving that repo its own per-repo plan entry. Fixed this pass.
- Expose `custom_onboarding_design_enabled` as an editable boolean on the tenant edit screen. Per this
  repo's own architecture (CLAUDE.md), every non-`spa_`-prefixed table's Add/Edit page — which includes
  `tenant_users` — is generated by one generic engine driven by `spa_data_management` field metadata,
  not bespoke per-field code. **Before estimating this as new UI work, check whether adding this column's
  metadata row is sufficient to surface it on the existing tenant edit form** (the way other boolean
  flags like `ai_credits_enabled` presumably already do) — this may be a metadata-only change, not new
  page code. Confirm against one existing boolean flag's metadata entry before scoping the ticket.
- No other content lives here — this repo only ever touches the on/off switch, never the per-screen
  hero/form content (that's `sc-saas-admin`, below).

### admin (`sc-saas-admin`) — Linear: SAN-250

- Onboarding Design module: flag status read-only; global logo lockup upload (2 slots, both optional);
  a note in the UI that leaving both empty shows nothing, by design, not as a bug; **10 tabs**, one
  per screen, each with:
  - Hero panel: logo-lockup show/hide, heading primary/accent text+color, structured bullet-list
    editor with its own color, background color + optional image (upload control shown here only).
  - Form panel: heading primary/accent text+color, background **color picker only** — no upload
    control on this panel at all, per Decision #9.
- Content-status overview: 10 rows, same "customized vs default" pattern.
- `config/config.php`: `custom_onboarding_design_enabled` constant, read-only here.

## Contracts & invariants

- **Flags:** `custom_onboarding_design_enabled` — owned by `tenants`, propagated per invariant #1,
  written only from `sanchiconnect-saas-tenants-admin`. Run `/trace-flag`.
- **API:** `GET public/global/settings` — existing route, response shape extended. Run `/audit-contract`.
- **Events:** none.
- **Invariants at risk:** unchanged from prior versions — tenant-verification contract untouched beyond
  the one boolean; screen-content settings live in the backend's own per-deployment, non-tenant-scoped
  DB (safe today, single-deployment-per-tenant).

## Test plan

- tenants/backend/admin: unchanged in kind from v5, scaled to 10 screens and 2 logo slots.
- frontend: the route-context test (same component, `onboarding: true` vs. absent) remains the key new
  coverage, now across 8 profile components instead of 6; confirm the dashboard-editing path never picks
  up onboarding branding regardless of flag state.
- cross-repo: `/audit-contract` + `/trace-flag` before `in-review`. No automated end-to-end coverage
  exists across all 4 repos today.

## Rollout

- Flag defaults to `false` — zero behavior change on deploy.
- Deploy order: `tenants` → `backend` → `frontend` → `sanchiconnect-saas-tenants-admin` (operator switch)
  → `sc-saas-admin` (content editor, deploy last).
- The eight-profile-screen layout work should land and be verified on its own before the admin UI
  exposes all 10 tabs — a sub-milestone inside `frontend`'s work, not a single atomic change.

## Out of scope

- Per-stakeholder show/hide on the Signup account-type picker — already exists, untouched.
- Any change to registration/login/profile form fields, validation, or submission logic on any screen.
- Editing the account-type tiles' icons/labels on the "I am" step within Signup.
- The `PartnerType` sub-selection (Incubator / Accelerator / Association-Organization) inside the Partner
  profile screen — that's existing form content, not part of this branding feature.
- Branding the 8 profile screens' **dashboard-editing path** (reached later from the dashboard, not
  immediately post-signup) — deliberately stays on today's unbranded dashboard chrome.
- Tenant self-service toggling of Default/Custom — platform-operator-gated only.

## Open questions

None remaining. The route-context split (Decision #11), background stacking mechanics (Decision #9),
and background image dimensions (Decision #12) — the three items that kept this spec in draft — are all
resolved. Per this workspace's own rule, an empty Open Questions list means this spec is now
**approvable** — that's a call for the document owner to make explicitly, not something this document
asserts on its own. `status` remains `draft` here; Linear tracking (this pass) does not imply approval.
