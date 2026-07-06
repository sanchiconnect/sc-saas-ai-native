---
type: frs
repo: sc-saas-frontend
updated: 2026-07-06
---

# Functional Requirement Specification — `sc-saas-frontend`

## 1. Purpose & Scope

This document specifies the functional behavior of `sc-saas-frontend`, the Angular 13 PWA that end users (startups, investors, mentors, corporates, partners, service providers, program offices, individuals, job seekers, and public visitors) use to interact with the SanchiSaaS platform. It is organized by functional domain, not by source folder, so that a reader can understand *what the product does* without first knowing the codebase layout.

Each requirement is written as `FR-<id>: <title> — <trigger> → <steps> → <outcome>`. Requirements were derived directly from the current codebase (components, routing, services) rather than from design intent, so this document reflects actual behavior, including known gaps and inconsistencies — these are called out explicitly under **Notable business rules / edge cases** so they are not mistaken for intended design.

This FRS covers the frontend only. The companion document `specs/FRS-sc-saas-admin.md` covers the PHP admin panel. Per the workspace constitution, the API contract, feature-flag names, and tenant-verification shape referenced throughout are owned by `sc-saas-backend` and `sanchiconnect-saas-tenants` respectively — this document treats them as given.

## 2. Actors

| Actor | Description |
|---|---|
| Public / anonymous visitor | No session; browses public pages, directories, job/challenge listings, registers. |
| Startup | Primary account type; applies to programs, manages pitch decks, reports growth metrics, posts jobs. |
| Investor | Org or individual investor profile; browses/connects with startups. |
| Mentor | Provides mentorship; logs/approves mentorship hours. |
| Corporate | Posts business challenges, engages with startups. |
| Partner | Institutional partner; manages its own sub-ecosystem of startups and a program team. |
| Service Provider | Offers services to startups; profile + directory listing only. |
| Program Office | Institutional program-running partner; profile + team + dashboard. |
| Individual | Non-org account type (e.g. freelancer/professional); profile + custom forms. |
| Job Seeker | Applies to job postings; may or may not hold another account type. |
| Platform admin / staff | Operates via `sc-saas-admin`; reaches the frontend only through impersonation ("backdoor login") or public-page previews. |

## 3. System-Wide Mechanics

These mechanics are shared by every module below and are not repeated per-module.

- **Tenant resolution**: on boot, the app calls the cockpit (`sanchiconnect-saas-tenants`) `GET api/v1/public/global/verify_tenant/{hostname}`. The response (`IBrandDetails`, including `features: IFeatures` and the tenant's dynamic `apiUrl`) is stored in the NgRx `global` store and `localStorage`. All business API calls thereafter go to that per-tenant `apiUrl` (`sc-saas-backend`), not to the cockpit.
- **Session/auth carrier**: the real authenticated-request credential is an httpOnly `accessToken` cookie set by the backend. The `Auth` object is also kept in `localStorage['user']` and the NgRx `auth` store for client-side session/UI state (guards, `accountType` decoding) — not as the actual bearer credential.
- **Route guards**: `AuthGuard` checks that `localStorage['user']` exists and, if the route declares `data.expectedType`, that `user.accountType` matches (else redirect to that type's dashboard). `NonAuthGuard` redirects an already-logged-in user away from `/auth/**`. Neither guard verifies JWT expiry against the server — a stale but structurally valid `user` object in `localStorage` still passes.
- **Layouts**: `AuthLayoutWrapperComponent` (chrome-free — auth pages, renderer pages), `ProtectedLayoutWrapperComponent` (main nav shell — hides the sidebar on a fixed allow-list of URLs for visitors with no profile), `PublicLayoutWrapperComponent` / `-v2` (marketing/public directory pages).
- **No passwords anywhere** — login and registration are entirely OTP-based (mobile, email, or WhatsApp, depending on tenant flags).
- **"Logout on rejection"**: across nearly every role dashboard (startup, mentor, investor, corporate, partner, service provider, program office, individual), if a profile's completeness check reports it was rejected by an admin and `features.logout_on_rejection` is on, the app force-logs-out the user ~1 second after the completeness poll.
- **Feature-flag enforcement is inconsistent across modules**: some route/component pairs actively check `brandDetails.features.<flag>` in `ngOnInit` and hard-redirect to `/errors/404` when disabled (e.g. the challenges family, tracker, growth-metrics); others rely solely on nav-menu visibility with no component-level guard (e.g. the jobs family, market-insights) — direct URL navigation can reach these pages even when the tenant's flag is off, and the backend is the only real gate. This inconsistency recurs throughout the document and is not repeated at every occurrence beyond the first mention per module.

## 4. Functional Requirements by Domain

---

### 4.1 Authentication, Account & Profile Infrastructure

*Modules: `auth`, `account`, `individual-profile`, `individuals`, `notifications`, `admin-actions`, `share-links`, `static-form-field`, `dashboard-v2`, `utilities`, `inline-styles-csp`, `page-not-found`.*

#### 4.1.1 auth

**Purpose**: All entry/exit points to the platform — OTP-based login, multi-type registration wizard, email verification, admin impersonation, external/import sign-in.

**Actors**: Public visitor; any account type; platform admin (via backdoor login).

1. `FR-AUTH-01: Mobile/email OTP login` — Visitor enters email or mobile + country code → `POST public/auth/mobile/login` sends OTP → visitor enters the OTP → `POST public/auth/mobile/login/verify` (OTP md5-hashed client-side) → on success, `Auth` is stored and the user is redirected to their account-type dashboard.
2. `FR-AUTH-02: Registration wizard` — Visitor picks account type → fills profile info → sends OTP(s) per enabled flags (`mobile_otp_verification`, `email_otp_verification`) → verifies → `POST public/auth/register/{userType}` creates the account → user is auto-logged-in and redirected to type-specific profile completion.
3. `FR-AUTH-03: Invite-only gate` — If `features.registration_invite_only` is on and no `inviteCode` is cached, visitor is redirected to `/auth/login`; a valid invite code is validated and cached.
4. `FR-AUTH-04: Enterprise "market access" upsell` — Startup registrant on step 1, with `features.registration_enterprise_sales_popup` on and "customer_access" not yet selected, sees an upsell prompt; accepting appends `customer_access` to the services list.
5. `FR-AUTH-05: Email verification via link` — User clicks the emailed verification link (`/verify/email/:uid/:email`) → `POST public/auth/verify/email` → success/fail message shown.
6. `FR-AUTH-06: WhatsApp/external OTP login` — When `external_sign_in_enabled` is on, a visitor can authenticate via `POST auth-external/login[/verify/import]` to import/link an external profile without full registration.
7. `FR-AUTH-07: Logout` — Dispatches `LogOut`; if `single_session_login_enabled`, calls `GET users/logout` to kill the server session; clears local state and redirects to login.
8. `FR-AUTH-08: Account deactivate/delete` — User confirms via dialog → `PATCH users/deactivate_account` (sleep mode) or `DELETE users/delete_account`, then force-logout after a fixed 5s timer regardless of the delete call's actual result.
9. `FR-AUTH-09: Admin backdoor login` — Admin panel deep-links to `/backdoor-login/:id/:uuid` → `POST admin-actions/backdoor-login` → local state cleared and rebuilt from the impersonation payload → redirect to `/startups/dashboard` or `/investors/dashboard` based on account type.

**Dependencies**: `public/auth/mobile/login[/verify]`, `public/auth/register[/startup|/job-seeker|/other]`, `public/auth/verify/mobile/:num`, `public/auth/verify/email[-token]/:token`, `users/logout`, `users/delete_account`, `users/deactivate_account`, `public/auth-external/login[/verify/import]`, `public/otp_verifications/send|verify[/whatsapp]`, `admin-actions/backdoor-login`. Flags: `job_seekers`, `startups`, `single_session_login_enabled`, `external_sign_in_enabled`, `mobile_otp_verification`, `email_otp_verification`, `whatsapp_otp_verification`, `registration_invite_only`, `registration_enterprise_sales_popup`.

**Notable business rules / edge cases**: OTP codes are always md5-hashed client-side. `DeleteAccountModalComponent` unconditionally logs the user out after a hard-coded 5-second timer without checking the delete response — a failed delete can present as a successful one. `VerifyEmailComponent`'s route lives outside `AuthRoutingModule`, so it renders without the auth chrome. Backdoor-login redirect only branches on `STARTUP` vs. everything-else-as-`investor` — impersonating a mentor/corporate/partner/service-provider/program-office/individual lands on `/investors/dashboard` regardless of actual type.

#### 4.1.2 account

**Purpose**: Self-service "Account Settings" — profile fields, notification preferences, certificates, ID cards, membership/plan history, invoices, account lifecycle — shared across all account types.

**Actors**: Any authenticated user.

1. `FR-ACC-01: Edit profile` — Edits name/designation/mobile/WhatsApp (email read-only) → `PATCH users/profile`.
2. `FR-ACC-02: Avatar upload` — Image ≤512KB, cropped → `POST users/upload/avatar`.
3. `FR-ACC-03: Social links` — LinkedIn (required, URL pattern) and X/Twitter (required, `x.com/...` pattern) → `PATCH users/profile/social-links`.
4. `FR-ACC-04: Newsletter toggle` — Auto-saves on change → `PATCH users/profile/subscribe-to-newsletter`.
5. `FR-ACC-05: Notification preferences` — Per-channel (WhatsApp/email) toggles for meeting/funding requests and new chats → `PATCH users/profile/notification-settings`.
6. `FR-ACC-06: Email-only notification settings page` — Separate page toggling `allEmailsEnabled`/`promotionalEmailsEnabled` → `PATCH users/profile`.
7. `FR-ACC-07: One-click unsubscribe` — Visiting `/account/edit/email/notification/:email` (from an email footer, no auth) auto-fires `POST users/update/notification` on page load.
8. `FR-ACC-08: Deactivate/reactivate account` — Confirm dialog → `PATCH users/deactivate_account`.
9. `FR-ACC-09: Delete account` — Same flow as FR-AUTH-08.
10. `FR-ACC-10: Certificates list & download` — Gated by `certificates` flag; `GET users/certificates`; "download" is a client-side DOM-to-PNG render, not server-generated.
11. `FR-ACC-11: ID card view/generate` — Gated by `startup_id_cards`; `GET users/id-cards`; "Generate" calls `POST users/id-cards/generate`.
12. `FR-ACC-12: Membership/plan history` — Active plan, purchase history, latest order status, gated until both calls resolve.
13. `FR-ACC-13: Membership upgrade request (moderated)` — If `membership_moderation_enabled`, an upgrade must be admin-approved before the plan picker unlocks.
14. `FR-ACC-14: Renew plan reminder` — "Renew" CTA auto-appears at ≤30 days remaining; blocked while a pending/recently-failed order exists.
15. `FR-ACC-15: Proforma invoices` — Lists admin-generated invoices; download fetches the S3 file as a blob; expired invoices flagged client-side.
16. `FR-ACC-16: Team management entry` — Embeds team add/remove UI for multi-user account types.

**Dependencies**: `users/profile[/social-links|/subscribe-to-newsletter|/notification-settings]`, `users/update/notification`, `users/upload/avatar`, `users/certificates[...]`, `users/id-cards[...]`, `users/deactivate_account`, `users/delete_account`, payments endpoints for plan/order/upgrade. Flags: `certificates`, `startup_id_cards`, `membership_moderation_enabled`, `membership_enabled`, `payment_currency`.

**Notable business rules / edge cases**: `users/update/notification` has no JWT guard on the backend — any caller who knows an email can flip that email's notification flags. Payment-order gating hardcodes a 30-minute grace window assuming a backend cron reconciles gateway callbacks in that time. Certificate/invoice "download" is client-rendered, not a true generated PDF.

#### 4.1.3 individual-profile

**Purpose**: Dashboard, profile edit, custom-form completion, and public profile for the `INDIVIDUAL` account type.

1. `FR-INDP-01: Individual dashboard` — `GET individuals/dashboard`, embeds the shared dashboard shell.
2. `FR-INDP-02: Edit individual profile` — Name, description, social links, cascading country/state/city → `PATCH individuals/information`.
3. `FR-INDP-03: Avatar upload` — Max 10MB (larger than the generic account limit) → `POST individuals/upload/logo`.
4. `FR-INDP-04: Custom/extra-info forms` — Tenant-defined forms; unknown UUID redirects to `/not-found`; submission triggers a completeness recheck.
5. `FR-INDP-05: Approval request` — `PATCH individuals/request/approval`, one-shot (backend 409s on repeat).
6. `FR-INDP-06: Public individual profile` — No-auth `GET individuals/public/individual-information/:uuid`; view count incremented once per load unless viewer is on the profile's own team.
7. `FR-INDP-07: Locked/limited-access redirect` — If `profiles_locked` or `limited_access` is on and viewer isn't the owner, redirect to `/`.

**Notable business rules / edge cases**: Same "logout on rejection" pattern as other roles. The edit-form route has no route-level guard of its own — it relies on the parent layout. The public info endpoint requires no JWT; the frontend must avoid forwarding internal fields it doesn't need.

#### 4.1.4 individuals (cross-cutting profile & team services)

**Purpose**: Cross-cutting profile services and team-member management consumed by every account type (no dedicated routed module — code lives in `individual-profile` + `team` + `profile.service.ts`).

1. `FR-INDS-01: Multi-profile creation` — Gated by `multiple_profiles`; `POST users/profile-types`.
2. `FR-INDS-02: Profile-type switching` — `POST users/profile-types/switch`; backend re-issues a JWT that must be captured into stored credentials.
3. `FR-INDS-03: Team member invite` — `POST users/team-members` (general) or a partner-scoped equivalent.
4. `FR-INDS-04: Team member removal` — `DELETE users/team-members/:uuid` (or partner-scoped equivalent).
5. `FR-INDS-05: Team roster listing` — `GET users/team-members` (general) or partner-scoped equivalent, chosen by account type.
6. `FR-INDS-06: Profile-completeness dispatch` — Cross-cutting service auto-dispatches the correct role-specific completeness action on profile-store changes.
7. `FR-INDS-07: Profile-viewers modal` — "Who viewed my profile" via `GET users/profile-views/:profileType/:profileId`.

**Notable business rules / edge cases**: Profile completeness silently no-ops if called before profile state is hydrated. Profile-page URL construction is centralized; components must not re-derive it.

#### 4.1.5 notifications

**Purpose**: Authenticated notification feed + navbar badge, combining REST pull with WebSocket push.

1. `FR-NOTIF-01: View notification feed` — Opening `/notifications` immediately marks everything read server-side (`MarkAllReadNotifications`) while independently paginating (`GET notifications/?pageNumber=&limit=`) — the list always renders as already-read.
2. `FR-NOTIF-02: Badge count refresh` — A WebSocket push or a successful mark-all-read triggers a re-fetch of `GET notifications/count` — never an inline increment/decrement.
3. `FR-NOTIF-03: Platform broadcast (admin-originated)` — `POST notifications/platform`.
4. `FR-NOTIF-04: Pagination` — Default page size 5.

**Notable business rules / edge cases**: Errors on count-fetch and mark-all-read are silently swallowed; a failed mark-all-read can render an empty/zero badge that masks still-unread items. The list itself does not live-update on a push — only the badge does.

#### 4.1.6 admin-actions

**Purpose**: Hosts the "backdoor login" impersonation flow reached from the admin panel — see FR-AUTH-09 for the full flow.

**Notable business rules / edge cases**: No confirmation step; the security boundary is entirely the signed link's server-side validity.

#### 4.1.7 share-links

**Purpose**: Reusable social-share + copy-link widget used across public/profile/detail pages. No backend calls — pure client-side URL construction and `window.open`.

1. `FR-SHARE-01: Share via social network` — Opens a network-specific share URL in a sized popup.
2. `FR-SHARE-02: Copy link to clipboard` — `navigator.clipboard.writeText` + toast.
3. `FR-SHARE-03: Configurable widget chrome` — Consumers can hide the copy button or the title.

#### 4.1.8 static-form-field

**Purpose**: Decorative preview-only fragment (company/applicant name, email, mobile) shown inside the dynamic form-preview page — not an independently routed feature and has no submit handler.

#### 4.1.9 dashboard-v2

**Purpose**: Shared "home" dashboard shell embedded by every role's routing module.

1. `FR-DASH-01: Load dashboard user data` — `GET dashboards/user` (notification counts, upcoming meetings/events).
2. `FR-DASH-02: Load dashboard content feed` — `GET dashboards/content` (reports, news, webinars).
3. `FR-DASH-03/04/05: Pending tasks, recommendations, sidebar nav` — Role-aware widgets sourced from role-specific store slices.

**Notable business rules / edge cases**: Declares no router config of its own — a pure component library; changing its `@Input`/`@Output` contract breaks every role dashboard simultaneously.

#### 4.1.10 utilities

**Purpose**: Cross-cutting grab-bag: dynamic form engine, certificate/ID-card renderers, public-page shell, misc widgets.

1. `FR-UTIL-01/02/03: Form preview / authenticated submission / public submission` — `/form-preview/:formId` (no auth), `/form/submit/:formId` (`POST forms-management/submission/:formUUID`), and fully public submission (`POST public/forms-management/submission/:formUUID/submit`).
2. `FR-UTIL-04: Form access check` — `GET forms-management/:formUUID/check-access`.
3. `FR-UTIL-05/06: Certificate/ID-card rendering` — No-JWT-guard renderer routes driven entirely by query params/parent navigation.
4. `FR-UTIL-07: Certificate listing & verification` — Includes a public certificate-number verification lookup.
5. `FR-UTIL-08: Public directory & landing pages` — Unauthenticated profile/directory/landing/glossary pages.
6. `FR-UTIL-09: CSP-safe inline styles` — Stamps a fixed nonce on injected `<style>` tags.
7. `FR-UTIL-10: 404 fallback` — Wildcard route → `/errors/404`.

**Notable business rules / edge cases**: Form-definition GETs are unauthenticated on the backend — treat all form metadata as effectively public. The certificate/ID-card renderer routes carry no JWT guard and may render personal data. `savePublicFormsSubmission` has a lingering `console.log` that can leak submitted form data (potentially PII) to the browser console. Route naming has two long-standing typos (`cerificates`, `growth-matrics`) that must not be "fixed" opportunistically without a coordinated router update.

#### 4.1.11 inline-styles-csp

**Purpose**: Infrastructure-only module patching Angular's style-injection service to stamp a CSP nonce on every dynamically-created `<style>` tag.

**Notable business rules / edge cases**: The nonce value is a hard-coded literal, not truly randomized per request — it only satisfies a CSP policy that allow-lists that exact literal.

#### 4.1.12 page-not-found

**Purpose**: 404 fallback, rendered inside the standard protected layout chrome even for anonymous visitors.

---

### 4.2 Startups, Programs & Applications

*Modules: `startups`, `call-for-applications`, `dynamic-forms`, `startup-kit`, `pitch-deck-management`, `pitch-deck-recorder`, `program-office`, `program-office-team`, `programs`, `vs-programs`, `tracker`, `milestones`, `growth-matrics`, `growth-matrics-print`.*

#### 4.2.1 startups

**Purpose**: Self-service portal for the startup account type — full profile lifecycle, all pitch-deck variants, supporting documents, dashboard, fund-raise status.

1. `FR-STU-01: Company profile completion` — Company info, industry/technology/business model, product info, team/founders, advisory board — each section PATCHes its own endpoint; completeness recalculated after every save.
2. `FR-STU-02: Financials & funding info` — Funding stage, target funds, ongoing commitments.
3. `FR-STU-03: Pitch deck management (3 modes)` — Upload a document/video, record via Loom-embedded PowerPitchDeck, or connect the external PowerPitch recorder; `submitPitch(type)` marks it submitted for evaluation.
4. `FR-STU-04: Supporting documents` — Named uploads per pitch type, individually deletable.
5. `FR-STU-05: Approval request & fund-raise toggle` — Requests admin approval; toggles a public "raising funds" badge.
6. `FR-STU-06: Profile-completeness gated logout` — See system-wide "logout on rejection" mechanic.
7. `FR-STU-07: Public profile & compare` — Public profile page; authenticated compare of up to N startups side-by-side.
8. `FR-STU-08: Custom/extra forms` — Tenant-defined extra questions via the dynamic form engine.
9. `FR-STU-09: Preview mode` — Admin-triggered read-only preview of any edit section (save calls suppressed).

**Dependencies**: `sc-saas-backend` `startup` module; `power-pitch-sanchiconnect-api` (proxied `power-pitch/*`); flags `startups`, `startup_supporting_documents`, `logout_on_rejection`.

**Notable business rules / edge cases**: `DisableStartupProfileUpdateGuard` locks all edit routes once a startup is approved/locked by tenant config. `powerPitchAccessToken` is kept in raw `localStorage` (not the app's storage service) and appended as a plain URL query param — visible in browser history/logs. Several distinct save methods PATCH the same endpoint with different partial payloads.

#### 4.2.2 call-for-applications

**Purpose**: Unified applicant-facing discovery & apply surface fanning out across three parallel program tracks (Startup Programs, VS-Programs, CFA).

1. `FR-CFA-01: Unified discovery` — Fetches all three program-type lists in parallel, tags each `ProgramType`, filters by account type, splits into active/closed.
2. `FR-CFA-02: Apply navigation by type` — Routed based on `ProgramType` to the correct apply flow.
3. `FR-CFA-03: Guest registration URL auto-apply` — A shared, pre-filled apply link stashes intent, redirects to register, and auto-applies on return.
4. `FR-CFA-04: Startup Program application flow` — Apply → dynamic form (auto-saving) → pay if required → submit → status SUBMITTED.
5. `FR-CFA-05: CFA application flow` — Public form submit (no auth) → creates a submission round → documents → payment.
6. `FR-CFA-06: Round-based payment gating` — Submit enabled only when payment succeeds or isn't required for the round.
7. `FR-CFA-07: Application status check without login` — By email, single or bulk.
8. `FR-CFA-08: Document re-upload after rejection` — Dedicated re-upload route for rejected document types.
9. `FR-CFA-09: Applied programs list` — Merged "My Applications" across program types.

**Dependencies**: backend `application-management`, `program-management`, `vs-programs-management`, `form-management`, `payments`; flags `programs_public_view`, `vs_programs_public_view`, `programs_payment_enabled`, `business_challenges`, `startups`.

**Notable business rules / edge cases**: `/programs` and `/vs-programs` root routes are dead code — they immediately redirect to `/call-for-applications`. Startup accounts never see VS-Programs and vice versa; CFA is visible to both. Signed document S3 URLs expire and must be re-fetched, never cached. Form completion progress is client-computed only and can drift ahead of the backend record after a failed save.

#### 4.2.3 dynamic-forms

**Purpose**: Generic, schema-driven form rendering engine shared by every program/application/custom-form surface in the platform.

1. `FR-DYN-01: Render a form from schema` — Sections → fields, many field types, built as a reactive form.
2. `FR-DYN-02: Conditional field visibility` — Per-field visibility rules toggle validators dynamically.
3. `FR-DYN-03: Multi-value (repeatable) sections` — Rendered as `FormArray`.
4. `FR-DYN-04: Auto-save / draft` — Background-saves on an interval until explicit submission.
5. `FR-DYN-05: Public preview iframe` — Read-only embeddable preview.
6. `FR-DYN-06: Video-pitch capture inside a form` — Embeds the PowerPitch connect flow, tagged to the specific application/round.
7. `FR-DYN-07: CFA payment/document layer` — Wraps the generic form with payment status polling and document upload.
8. `FR-DYN-08: Master-data-sourced options` — Some fields fetch their option list live rather than from static schema.

**Notable business rules / edge cases**: Required-field completion is calculated client-side only. Video Pitch panel visibility is driven purely by matching option label text (case-insensitive) — a schema author renaming that option silently breaks the gating. Identity fields (email/name) are force-disabled once patched from profile data.

#### 4.2.4 startup-kit

**Purpose**: Marketplace/catalog of third-party partner perks eligible startups can apply for.

1. `FR-SKT-01: Browse catalogue` — `GET public/startup-kit`, filterable by category.
2. `FR-SKT-02: View service detail` — Detail + similar-services in the same category.
3. `FR-SKT-03: Apply for a service` — Confirm dialog → `POST startup-kit/service/:id`; duplicate-apply prevented by a check call.
4. `FR-SKT-04: Eligibility gating` — Disabled with a reason if not logged in / not approved / already applied / ineligible incubation stage.

**Notable business rules / edge cases**: Eligibility is entirely client-checked with no visible server-side re-validation beyond the apply POST itself. The `startup_kit` flag exists in `IFeatures` but the actual component-level gate is commented out — the catalogue is reachable regardless of the flag.

#### 4.2.5 pitch-deck-management

**Purpose**: Manages a startup's pitch-deck **video** specifically — mode selection between live PowerPitch recorder, PowerPitchDeck Loom embed, and raw file upload.

1. `FR-PDM-01: Mode selection` — Driven by `features.video_types`.
2. `FR-PDM-02/03: Connect / edit PowerPitch` — Opens the connect modal; edit reopens the video editor.
3. `FR-PDM-04: Loom-URL mode` — Startup pastes a Loom URL, displayed via oembed.
4. `FR-PDM-05: File upload mode` — mp4/webm ≤100MB; re-upload requires deleting the prior file first.
5. `FR-PDM-06: Submit for evaluation` — Confirmation → `submitPitch('video_pitch')`.
6. `FR-PDM-07: Default pitch type` — Marks which pitch type is "primary."

**Notable business rules / edge cases**: `isVideoPitchEnabled` = admin-requested OR `video_pitch_mandatory`. `powerPitchAccessToken` exposure issue same as `startups`.

#### 4.2.6 pitch-deck-recorder (legacy)

**Purpose**: Legacy in-app webcam/screen recording UI. Its route is commented out and not reachable via normal navigation — superseded by the external PowerPitch connect flow.

#### 4.2.7 program-office

**Purpose**: Profile management & dashboard for the Program Office account type.

1. `FR-PO-01: Complete profile` — Intro/bio, industry/technology → `PATCH program_office_members/program-office-member-information`.
2. `FR-PO-02: Logo upload`.
3. `FR-PO-03: Request approval` — Same logout-on-rejection pattern as other roles.
4. `FR-PO-04: Dashboard` — `GET program_office_members/dashboard`.
5. `FR-PO-05: Public profile` — Read-only, no auth.
6. `FR-PO-06: Engagement info` — Captures how the office wants to engage with startups.

#### 4.2.8 program-office-team

**Purpose**: Public directory of an individual Program Office's team members.

1. `FR-POT-01: List team members`.
2. `FR-POT-02: Add a team member` — Inline form, not separately routed.

**Notable business rules / edge cases**: No dedicated NgRx state; data is component-local and can go stale across navigations.

#### 4.2.9 programs

**Purpose**: Original tenant-programs module — now effectively a routing shell redirecting to `call-for-applications`, but still owns the live component tree CFA uses for Startup-Program-type applications.

1. `FR-PRG-01: Dead root redirect` — Immediately navigates to `/call-for-applications`.
2. `FR-PRG-02: Program detail & apply (live path)` — Guest OTP verification then apply.
3. `FR-PRG-03: Applied-program detail tabs` — Profile-Form / Payment-Form / Video-Pitch tabs.
4. `FR-PRG-04: Reminder scheduling` — Email reminder before a round deadline.
5. `FR-PRG-05: Check status without login`.
6. `FR-PRG-06: Required-details inline form` — Collects missing mandatory profile fields inline during application.

**Notable business rules / edge cases**: `/programs` is an alias — do not add new discovery logic here. No NgRx cache — every route re-entry re-fetches the full program list.

#### 4.2.10 vs-programs

**Purpose**: Structural mirror of `programs` for Individual/VS (venture-studio) programs.

1. `FR-VSP-01: Discovery & apply` — Mirrors the Startup-Program apply flow one-to-one against the `vs-programs-management` backend module.
2. `FR-VSP-02: Applied list & detail`.
3. `FR-VSP-03: Preview mode`.

**Notable business rules / edge cases**: Any new endpoint added to `programs-management` should be checked for a matching `vs-programs-management` counterpart — drift risk. Route-level auth is looser here than in `programs`.

#### 4.2.11 tracker (Mentor Hours)

**Purpose**: Logging, review, approval, and rating of mentor↔startup mentorship sessions.

1. `FR-TRK-01: Flag gate` — `!features.mentor_hours` → redirect to 404.
2. `FR-TRK-02: Log a session` — Role-aware form; new session enters `pending`, never auto-approved.
3. `FR-TRK-03: Approve/reject a session` — Mentor-only action; approve always opens the rating modal (no skip).
4. `FR-TRK-04: Rate a session` — Star rating + optional comment.
5. `FR-TRK-05: Filter sessions` — Server-side filters plus a client-side-only "programs" filter.
6. `FR-TRK-06: Deep-link add` — `?add=true` auto-opens the add-hours modal.

**Notable business rules / edge cases**: `pageSize: 1000` is hardcoded with no real pagination — will silently truncate past 1000 sessions, and the client-side program filter then also silently misses records beyond that page. Approval authority is a UI convention only; the backend must enforce it.

#### 4.2.12 milestones

**Purpose**: Structured goal tracking for a startup — qualitative and quantitative milestones, notes, message thread, reviewer assignment.

1. `FR-MIL-01: Create a milestone` — Mixed qualitative + quantitative sub-items with a target date.
2. `FR-MIL-02: Track progress` — Qualitative toggle-complete; quantitative running-value update with full history log.
3. `FR-MIL-03: Set/adjust target date`.
4. `FR-MIL-04: Notify toggle`.
5. `FR-MIL-05: Assign reviewers`.
6. `FR-MIL-06: Notes & messages` — Private notes with file uploads; thread messages.
7. `FR-MIL-07: Delete a milestone`.

**Notable business rules / edge cases**: Backend blocks qualitative/quantitative updates once `targetDate` has passed. **Security gap**: ownership checks on notes, messages, and the info-fetch endpoint are reportedly disabled on the backend — any authenticated user with the flag on who knows/guesses a milestone UUID can read/write another startup's notes and messages; milestone UUIDs should not be exposed in shareable links until this is fixed.

#### 4.2.13 growth-matrics (Growth Metrics)

**Purpose**: Startup self-reported KPI tracking over time, with table/chart views, reviewer sharing, and connection-based access control.

1. `FR-GRM-01: Flag gate` — `!features.growth_metrics` → 404.
2. `FR-GRM-02: Report metrics for a period` — One control per active metric type; new entries POST, existing PATCH.
3. `FR-GRM-03: Program-scoped metrics` — A startup only sees/edits metrics for programs it's enrolled in.
4. `FR-GRM-04: Table & chart views` — Toggle with a cumulative-value option.
5. `FR-GRM-05: Request edit on locked metrics` — Free-text reason submitted for review.
6. `FR-GRM-06: Reviewer sharing` — Add/remove reviewers from existing connections, or invite a new external reviewer by email.
7. `FR-GRM-07: Reviewer's view of a startup's metrics` — Read-only for non-startup accounts.
8. `FR-GRM-08: Quarterly vs. monthly period formatting` — Respects the tenant's financial-year start month.
9. `FR-GRM-09: Share/print link` — Builds a `/growth-metrics-print` URL for a read-only, auto-printing snapshot.
10. `FR-GRM-10: Export a chart` — PNG (canvas) and CSV.

**Notable business rules / edge cases**: Radio/checkbox metric types are excluded from chart view. Reviewer removal always recomputes the full reviewer set client-side (no partial-delete endpoint).

#### 4.2.14 growth-matrics-print

**Purpose**: Standalone, print-optimized rendering of a startup's growth metrics — the destination of the share/print link from 4.2.13.

1. `FR-GMP-01/02: Read share-link params / auto-select startup+program`.
2. `FR-GMP-03: Auto-print` — `window.print()` fires ~2.5s after chart data loads.
3. `FR-GMP-04: Combined metric list for print`.
4. `FR-GMP-05: Same flag gate` as growth-matrics.

**Notable business rules / edge cases**: No route guard/layout wrapper, but still depends on NgRx profile/startup state being present — a fully logged-out visitor will not see real data despite the route's "public-looking" shape; this is not a genuine anonymous-access path.

---

### 4.3 Challenges & Hiring

*Modules: `challenges`, `challenge-details`, `challenge-public-details`, `challenge-public-view`, `challenge-search`, `challenge-collection`, `hire`, `job-details`, `job-interview`, `job-public-details`, `job-search`, `applied-jobs`.*

#### 4.3.1 challenges (corporate challenge management)

**Purpose**: Corporate/startup poster creates, edits, and manages the lifecycle of "business challenges," including a public CFA submission variant.

1. `FR-CHL-LIST: View my challenges` — Paginated list of the poster's own challenges with status badges.
2. `FR-CHL-CREATE: Create a challenge` — Full form → `POST challenges/` → enters "under review" state.
3. `FR-CHL-EDIT: Edit a challenge` — Pre-filled form → `PATCH challenges/:id`.
4. `FR-CHL-STATUS: Toggle challenge status` — Confirmation → `PATCH challenges/:id`.
5. `FR-CHL-CFA-SUBMIT: Public CFA submission` — Unauthenticated extended form (with logo upload) → `POST public/challenges/`.
6. `FR-CHL-CFA-COLLECTION: Submit challenge attached to a collection` — Via `?collection=<id>`.
7. `FR-CHL-ELEVATE: Corporate backdoor access ("elevation")` — Opens an impersonation-style login into the corporate context for a CFA-origin challenge.

**Dependencies**: flag `business_challenges` gates nav visibility only — no route-level redirect on the create/list pages themselves.

**Notable business rules / edge cases**: A `PATCH jobs/hiring-profile` call embedded in this flow is a confirmed no-op on the backend. The public CFA form's logo requirement is enforced only by custom submit-time logic, not an Angular validator.

#### 4.3.2 challenge-details

**Purpose**: Corporate-facing detail screen for one challenge, showing full info and the list of startup participants.

1. `FR-CHD-VIEW: View challenge detail`.
2. `FR-CHD-PARTICIPANTS: View participant submissions`.

**Notable business rules / edge cases**: The backend's participants controller reportedly has no feature guard — apply/list/update participant endpoints bypass the `business_challenges` flag server-side; this page is the only gate and it enforces none of its own beyond normal auth routing.

#### 4.3.3 challenge-public-details

**Purpose**: Public (in-app-shell) detail page where a startup/visitor reviews a challenge and applies.

1. `FR-CPD-VIEW: View challenge`.
2. `FR-CPD-APPLY-LOGGEDIN: Apply while authenticated` — External link or in-app application modal → `POST participants/:id/apply`.
3. `FR-CPD-APPLY-ANON: Apply while logged out` — Login modal → register → resume the apply flow automatically post-registration.
4. `FR-CPD-SHARE: Social share`.

**Notable business rules / edge cases**: "Already applied" suppresses the apply modal entirely — no re-apply/edit path is exposed.

#### 4.3.4 challenge-public-view

**Purpose**: Public browse/landing page listing publicly discoverable challenges and curated collections.

1. `FR-CPV-BROWSE: Browse challenges`.
2. `FR-CPV-COLLECTIONS: Filter by collection` — Single-select, resets pagination.
3. `FR-CPV-REDIRECT-TO-COLLECTION`.
4. `FR-CPV-APPLY-REDIRECT: Apply/redirect on card click` — External platform opens in new tab with analytics beacon; else hands off to `/programs/apply/:code/:slug`.
5. `FR-CPV-404-GATE: Flag gate` — `business_challenges` falsy → 404.

#### 4.3.5 challenge-search

**Purpose**: Slimmer sibling of challenge-public-view without the "collections" concept.

1. `FR-CHS-SEARCH: Search/filter challenges`.
2. `FR-CHS-APPLY-REDIRECT`.
3. `FR-CHS-404-GATE`.

**Notable business rules / edge cases**: Near-duplicate implementation of challenge-public-view's rendering logic — a maintenance/consistency risk (two divergently-maintained copies of the same business logic).

#### 4.3.6 challenge-collection

**Purpose**: Detail page for one curated challenge collection.

1. `FR-CHC-VIEW: View collection`.
2. `FR-CHC-APPLY-REDIRECT`.
3. `FR-CHC-404-GATE` — Requires both `business_challenges` and `business_challenge_collections_enabled`.
4. `FR-CHC-BACK`.

#### 4.3.7 hire (job posting / employer-side)

**Purpose**: Employer-side job board — create, list, manage postings; gated behind an "approved hiring profile."

1. `FR-HIR-LIST: View my jobs` — With an embedded interview calendar.
2. `FR-HIR-ADD-GATE: Gate job creation` — Blocks with a message if the poster's profile isn't approved.
3. `FR-HIR-CREATE: Create job` — Full form → `POST jobs/`, optional attachment.
4. `FR-HIR-EDIT: Edit job` — `PATCH jobs/:id/details`.
5. `FR-HIR-STATUS: Reactivate/close job`.
6. `FR-HIR-HIRING-PROFILE: Complete hiring profile` — Confirmed no-op on the backend.

**Notable business rules / edge cases**: No route-level 404 redirect on the `jobs`/`job_seekers` flags found anywhere in this family — access control relies on nav-menu visibility only, unlike the challenges family.

#### 4.3.8 job-details

**Purpose**: Employer's per-job detail screen — applicants, shortlist/reject, interview scheduling.

1. `FR-JBD-VIEW: View job + applicants`.
2. `FR-JBD-SHORTLIST: Shortlist a candidate` — Optionally schedules a video interview in the same action.
3. `FR-JBD-REJECT: Reject a candidate` — Two independent UI paths call the same backend action.
4. `FR-JBD-INTERVIEW-STATUS: Update post-interview status`.

**Notable business rules / edge cases**: Scheduling computes both local-display time and a separate UTC payload with explicit timezone/offset fields — a conversion bug here directly mis-schedules interviews.

#### 4.3.9 job-interview

**Purpose**: Standalone (no shell) video interview room using VideoSDK.live, plus a personal notes panel.

1. `FR-JIV-JOIN: Join interview` — No navbar/sidebar; embedded video call starts from meeting config.
2. `FR-JIV-NOTES: Personal interview notes` — Debounced autosave plus manual save.
3. `FR-JIV-RESPONSIVE: Notes panel auto-collapse` on narrow viewports.

**Notable business rules / edge cases**: The "fetch existing notes" call exists but its invocation is commented out — a reload never repopulates previously-saved notes, only newly-typed ones get saved.

#### 4.3.10 job-public-details

**Purpose**: Public job detail with inline apply (resume upload) and similar-jobs suggestions.

1. `FR-JPD-VIEW: View job`.
2. `FR-JPD-APPLIED-CHECK: Applied-status check` — For logged-in job seekers.
3. `FR-JPD-APPLY-LOGGEDOUT: Apply while logged out` — Redirects to login.
4. `FR-JPD-APPLY-LOGGEDIN: Apply while logged in` — Cover letter + required resume (pdf/doc/docx ≤5MB) → `POST jobs/:id/apply` then resume upload.

#### 4.3.11 job-search

**Purpose**: Public job discovery with rich filters, a "post a job" CTA, and a resume-submission campaign entry point.

1. `FR-JBS-SEARCH: Search/filter jobs`.
2. `FR-JBS-APPLIED-CHECK`.
3. `FR-JBS-SUBMIT-RESUME-CAMPAIGN: Submit-resume campaign` — Triggered by `?campaign=submit_resume`; the underlying endpoints are fully unauthenticated (rate-limited only).
4. `FR-JBS-POST-JOB: "Post a Job" CTA` — Blocks non-startup accounts with an error.

#### 4.3.12 applied-jobs

**Purpose**: Job-seeker's dashboard of applied jobs plus interview calendar.

1. `FR-APJ-LIST: View applied jobs`.
2. `FR-APJ-INTERVIEWS: View interview calendar`.
3. `FR-APJ-SUBMIT-RESUME-CAMPAIGN` — Duplicated logic from job-search.
4. `FR-APJ-FILTERS: Filter scaffolding` — UI exists but the apply-handler is commented out — a half-finished, currently non-functional feature.

**Cross-cutting observations for this domain**: The challenges family actively flag-gates with hard redirects; the jobs family does not — direct URL navigation reaches jobs pages even when the tenant's `jobs`/`job_seekers` flag is off. `/search/challenges` and `/search/jobs` each have two top-level module registrations at the same path; only the first-registered module's route wins.

---

### 4.4 Community, Networking & Communication

*Modules: `community-feed`, `connections` (+ `connections-v3`, `connection-v4`, `connection-approve-reject-page`, `connection-request-action-email`), `mentors`, `investors`, `corporate`, `partners` (+ `partners-dashboard`, `partners-details`), `team`, `service-provider`, `chat`, `global-search-page`, `search`.*

#### 4.4.0 Connections — version note

Three generations coexist: `connection-v4` is the active top-level route; it synchronously imports `connections-v3` as its child renderer; the plain `connections/` folder is model-only (types only, no component/route) and must not be re-activated as a standalone route or it will shadow `connection-v4`.

#### 4.4.1 community-feed

**Purpose**: Member-facing social feed (posts/comments/reactions/polls) plus the platform notification inbox, gated by `community_feed`.

1. `FR-FEED-VIEW/POST/EDIT-DELETE/COMMENT/REACT/POLL-VOTE` — Standard social-feed CRUD and engagement actions against `community-wall/posts*`.
2. `FR-FEED-MY-ACTIVITY / FR-FEED-USER-FILTER` — Filtered views of own or another user's activity.
3. `FR-FEED-SHARE: Share a single post` — Public shareable link backed by an unauthenticated read endpoint.
4. `FR-NOTIF-INBOX / FR-NOTIF-REALTIME` — Paginated inbox plus WebSocket push toasts and live badge updates.

**Notable business rules / edge cases**: Three backend routes (`weekly-post`, `upload-file`, `poll/vote`) bypass the `community_feed` flag entirely. File upload capped at 25MB.

#### 4.4.2 connections / connections-v3 / connection-v4

**Purpose**: Peer-to-peer connection request lifecycle, a "saved for later" wishlist, and email-link accept/reject.

1. `FR-CONN-SEND/ACCEPT/REJECT/REMOVE` — Standard connection lifecycle; accepting with reason "Schedule call" auto-creates a meeting.
2. `FR-CONN-LIST` — Overview + online status; typed/paginated lists (active/pending/sent/rejected) with search and sort.
3. `FR-CONN-DOC-UPLOAD` — Attach a document to a request (25MB backend limit).
4. `FR-CONN-WISHLIST: Save for later` — Gated separately by `connections_wishlist`.
5. `FR-CONN-EMAIL-ACCEPT-REJECT` — No-login accept/reject via emailed link.
6. `FR-CONN-EMAIL-DEEPLINK-LOGIN` — Broader magic-link landing page shared by connection/profile/message/meeting/mentorship/document/video-pitch/growth-metrics email actions.
7. `FR-CONN-BASIC-LIST-CACHE` — Cached "is connected" lookup to avoid a network round-trip per profile card.

**Dependencies**: flag `connections` gates all authenticated endpoints **and** the public email-link endpoint — a disabled flag returns 403 even for email-link accept/reject. `direct_accept_connection_enabled` skips the accept-reason modal.

**Notable business rules / edge cases**: Sending a connection request from an investor uses a distinct fast-path endpoint with different backend behavior (auto-creates/returns a chat group) — must not be conflated with the general send-request endpoint.

#### 4.4.3 mentors

**Purpose**: Mentor self-service portal plus the shared mentorship-hours tracker.

1. `FR-MENTOR-DASHBOARD/EDIT-PROFILE/LOGO/APPROVAL/PUBLIC-PROFILE` — Standard profile lifecycle (see system-wide mechanics for the approval/logout-on-rejection pattern).
2. `FR-MENTOR-TRACKER-LOG/APPROVE/RATE` — See tracker module (4.2.11) for full detail; mentors are one side of that flow.

**Notable business rules / edge cases**: `mentorship/auto-entry` (auto-logged from a completed video meeting) uses the browser's detected timezone, not the meeting's actual timezone — cross-timezone sessions can log incorrect durations.

#### 4.4.4 investors

**Purpose**: Investor self-service portal (org or individual) plus a side-by-side comparison tool.

1. `FR-INV-DASHBOARD/EDIT-ORG/EDIT-INDIVIDUAL/LOGO-DOC/APPROVAL/FUNDING-TOGGLE/PUBLIC-PROFILE` — Standard profile lifecycle, branching on `investorType`.
2. `FR-INV-COMPARE: Compare investors` — Side-by-side comparison grid.

#### 4.4.5 corporate

**Purpose**: Corporate self-service portal for companies engaging with startups.

1. `FR-CORP-DASHBOARD/EDIT/LOGO/APPROVAL/PUBLIC-PROFILE` — Standard profile lifecycle.

#### 4.4.6 partners / partners-dashboard / partners-details

**Purpose**: Public partner directory, authenticated partner self-service hub, and public partner detail/contact page.

1. `FR-PARTNER-DIRECTORY/DETAIL/CONTACT` — Public browse, detail (with event gallery and program-office people), and a rate-limited contact form.
2. `FR-PARTNER-DASHBOARD/EDIT/LOGO/APPROVAL` — Standard self-service lifecycle.
3. `FR-PARTNER-STARTUP-ADD/INVITE` — Onboard a single startup or bulk-invite via CSV.
4. `FR-PARTNER-TEAM: Manage program team members` — Distinct from the personal team-member module (4.4.7); not gated by the `partners` flag on the backend.

**Notable business rules / edge cases**: Contact-form submission is server-side rate-limited. `addStartup` is not idempotent — guard against double submission.

#### 4.4.7 team

**Purpose**: Manage the authenticated organization's own internal team member list (distinct from partner program-team management above).

1. `FR-TEAM-LIST/ADD/DELETE` — `GET/POST/DELETE users/team-members`.

**Notable business rules / edge cases**: No pagination on the fetch. The underlying service class also carries the unrelated partner-program-team methods — do not conflate the two member lists.

#### 4.4.8 service-provider

**Purpose**: Service-provider self-service (profile, dashboard, public profile), gated by `service_providers`.

1. `FR-SVC-DASHBOARD/EDIT/LOGO/APPROVAL/PUBLIC-PROFILE` — Standard profile lifecycle.

#### 4.4.9 chat

**Purpose**: In-app messaging with two mutually-exclusive per-tenant implementations selected by the `chat_type` setting: CometChat (third-party SDK) or in-house REST + Socket.IO.

1. `FR-CHAT-ENTRY: Open conversations` — Reads `chat_type` and renders the matching implementation.
2. `FR-CHAT-COMETCHAT: CometChat mode` — Entirely SDK-driven, no backend REST calls.
3. `FR-CHAT-INHOUSE-LIST/SEND/REALTIME/MARK-READ/DELETE/GROUP-MANAGE` — Full in-house conversation feature set with WebSocket delivery.
4. `FR-CHAT-NOTIFY-FANOUT: Off-band alerts` — Email/push fan-out for a group chat.

**Notable business rules / edge cases**: `upload-logo`, `messages-file`, and `reply-file` are missing feature metadata on the backend despite the class-level guard — reachable by any authenticated user even when the `chat` flag is off for the tenant.

#### 4.4.10 global-search-page + search

**Purpose**: Platform-wide discovery — nine stakeholder-type directories, a global typeahead/omni-search page, and IP/patent search.

1. `FR-SEARCH-DIRECTORY/FILTERS/SAVE-FILTER/TYPEAHEAD` — Per-stakeholder-type directories with advanced filters and saved-filter reuse; typeahead branches between Elasticsearch and plain-text search per tenant setting.
2. `FR-GLOBAL-SEARCH: Global omni-search` — Fans a single query across all stakeholder types plus news/reports/videos.
3. `FR-SEARCH-LIVE-DEALS`.
4. `FR-IP-SEARCH/CONNECT/REQUEST-THREAD` — Browse patents, request to connect with a holder/TTO, and manage the resulting message thread.

**Notable business rules / edge cases**: No NgRx state exists for search or IP — all state is component-local.

---

### 4.5 Learning, Events & Content

*Modules: `learning-management`, `webinars`, `event-agenda`, `meetings`, `calender`, `public-events`, `deeptech-news`, `market-insights`, `glossary`, `resources`, `resource-reports`, `product-updates`, `slider`, `public`/`public-shared`, `ad-viewer`.*

#### 4.5.1 learning-management

**Purpose**: Tenant LMS — course catalogue, enrollment, lesson playback, quiz attempts, reviews.

1. `FR-LMS-CATALOG/DETAIL: Browse and view a course`.
2. `FR-LMS-ENROLL: Enroll in a course` — Paid courses route through the checkout module first.
3. `FR-LMS-PLAY/PROGRESS: Play a lesson & track completion` — Progress posted on a debounce; 100% triggers backend certificate generation.
4. `FR-LMS-QUIZ: Take a quiz` — Max 3 attempts per enrollment, backend-enforced.
5. `FR-LMS-REVIEW: Rate a course`.

**Notable business rules / edge cases**: The signed video-URL endpoint has no auth/feature guard on the backend — access control is frontend-route-only. Only `STARTUP` accounts can enroll/learn/quiz; other roles can only browse.

#### 4.5.2 webinars

**Purpose**: Lists tenant webinars (YouTube-hosted) with an in-app player modal, gated by `webinar_videos`.

1. `FR-WEB-LIST/PLAY/DEEPLINK/GATE`.

#### 4.5.3 event-agenda

**Purpose**: Authenticated multi-day agenda/venue/booth view for the tenant's single "primary event."

1. `FR-EVA-LOAD/SEARCH/BOOTH/EXPORT`.

**Notable business rules / edge cases**: No explicit route-level guard/flag check in the component — gating relies on the backend 403 plus the protected layout.

#### 4.5.4 meetings

**Purpose**: In-meeting experience — video call join, feedback, job-interview meeting handling. Intentionally has no route guard for the join page (invite-link access).

1. `FR-MTG-JOIN/SCHEDULE/RESPOND/PROPOSE/NOTES/FEEDBACK/INTERVIEW`.

**Notable business rules / edge cases**: The public meeting-fetch endpoint exposes the full meeting entity with no JWT guard.

#### 4.5.5 calender

**Purpose**: Authenticated schedule overview, availability settings, shared notes, events view.

1. `FR-CAL-GRID/AVAIL/NOTES/EVENTS/GATE`.

**Notable business rules / edge cases**: Event visibility filtering is client-side only, with no guaranteed backend enforcement.

#### 4.5.6 public-events

**Purpose**: Unauthenticated landing/registration page for a single public event.

1. `FR-PEV-VIEW/REGISTER/REDIRECT/SPEAKER-LINK`.

**Notable business rules / edge cases**: Already-authenticated visitors are redirected to the authenticated `calender/events` view rather than seeing the public page.

#### 4.5.7 deeptech-news

**Purpose**: Curated news feed with per-user category preferences and infinite scroll, gated by `news`.

1. `FR-NEWS-FEED/SCROLL/SEARCH/FILTER/PREF`.

**Notable business rules / edge cases**: All four backend news endpoints, including the preference write, are unauthenticated — any caller can overwrite any profile's preferences by guessing IDs; the frontend must only ever call with the current user's own IDs.

#### 4.5.8 market-insights

**Purpose**: Read-only wrapper around embedded Power BI dashboards.

1. `FR-MI-NAV/EMBED`.

**Notable business rules / edge cases**: No `AuthGuard` or feature-flag check exists anywhere in this module. Most leaf pages are functionally empty scaffolding (chrome only, no wired dashboard) — should be treated as incomplete, not delivered, when scoping acceptance criteria.

#### 4.5.9 glossary

**Purpose**: A–Z terminology reference, gated by `glossary`.

1. `FR-GLOS-LIST/DETAIL/SUGGEST`.

#### 4.5.10 resources

**Purpose**: Downloadable business-document library with in-app preview, gated by `resources_downloads`.

1. `FR-RES-BROWSE/VISIBILITY/VIEW/DOWNLOAD`.

**Notable business rules / edge cases**: The email-delivery fallback endpoint (for `accountType === OTHER`) has no feature guard on the backend.

#### 4.5.11 resource-reports

**Purpose**: Curated report-downloads library, gated by `reports_downloads` — a distinct content type and flag from `resources`.

1. `FR-RREP-LIST/FILTER/GATE`.

#### 4.5.12 product-updates

**Purpose**: Platform release-notes/changelog feed. No feature flag observed anywhere in the module.

1. `FR-PU-LIST`.

**Notable business rules / edge cases**: The video/file click handler is entirely commented out — currently a dead click target.

#### 4.5.13 slider

**Purpose**: Pure presentational carousel primitive, not independently routed — a dependency of other modules, not a standalone FRS subject.

#### 4.5.14 public / public-shared

**Purpose**: Shared library of public-facing page/section components (glossary, resources, startup-kit, login/register modals, job-apply modals) declared and routed by *other* feature modules.

1. `FR-PUB-SKLIST/SKDETAIL/SKAPPLY: Startup-kit browse/detail/apply` (see also 4.2.4).
2. `FR-PUB-LOGINGATE: Inline auth on protected actions` — Chained login → register modals rather than a page redirect.
3. `FR-PUB-JOBAPPLY` — Apply/resume modals consumed by `job-public-details`.

**Notable business rules / edge cases**: `PublicModule`'s own routing is effectively an empty shell — treat as a component library, not a routed feature. FAQ section components exist but are not declared in any module — currently orphaned/dead code.

#### 4.5.15 ad-viewer

**Purpose**: Shared, placement-driven advertising widget embedded into other screens. No feature flag — gating is purely by which host pages choose to embed it.

1. `FR-AD-LOAD/FILTER/DISPLAY/MODAL/CLICK`.

**Notable business rules / edge cases**: Modal-dismiss dedup state lives only in `localStorage`, so it is per-browser, not per-account.

---

### 4.6 Facilities, Finance, Certificates & Support

*Modules: `facilities-management`, `external-facilities-management`, `ip-request`, `ip-search`, `payment`, `payment-gateways`, `membership`, `cerificates`, `sc-certificate-renderer`, `sc-id-card-renderer`, `tickets`.*

#### 4.6.1 Facilities Management

**Purpose**: Browse, book, check in/out of, and rate bookable physical spaces/equipment; plus browse cross-tenant ("ecosystem") facilities.

1. `FR-FAC-LIST/DETAIL/BOOK/MYBOOKINGS/CHECKIN/CANCEL/RATE` — Full booking lifecycle, with paid bookings routed through the checkout module.
2. `FR-FAC-KIOSK: Public/QR kiosk check-in` — Unauthenticated check-in/rating via a booking UUID + session token.
3. `FR-FAC-ECOSYSTEM: Browse ecosystem facilities` — Read-only cross-tenant browsing.

**Notable business rules / edge cases**: `/external-facilities`'s auth guard is commented out and reachable unauthenticated; the backend controller also lacks a JWT guard. A legacy booking endpoint still exists alongside the active one — only the new path is live. The kiosk `sessionToken` is the sole identity credential for unauthenticated check-in/rating and must not be logged or shared beyond the booked user.

#### 4.6.2 IP Request & IP Search

**Purpose**: Discover published/granted patents and manage a startup's connect-request conversation thread with the TTO.

1. `FR-IPSCH-LIST/DETAIL/CONNECT: Browse patents and send a connect request`.
2. `FR-IPREQ-LIST/DETAIL/MSG/ATTACH: Manage a connect-request thread` — Messaging + 25MB/file attachments.

**Notable business rules / edge cases**: The request-thread page gates on the wrong flag (`ticket_management` instead of an IP-specific flag) — tenants with IP enabled but tickets disabled are incorrectly redirected to 404, and vice versa.

#### 4.6.3 Payment

**Purpose**: Core embedded checkout widget — gateway selection, coupons, GST, orders, success/fail landing — used across facilities, membership, applications, and LMS.

1. `FR-PAY-CHECKOUT/PRICE/COUPON/GATEWAY/FREE/RESULT/ORDERS/INVOICE`.

**Notable business rules / edge cases**: Nearly all backend payment routes are effectively unauthenticated (guards disabled server-side) to support pre-login checkout — there is no server-side ownership validation on order creation/verification; `moduleType` is a free-text key that must match exactly between order-creation and verification calls.

#### 4.6.4 Payment Gateways (dev harness)

**Purpose**: A standalone developer/test harness for Stripe/PayPal/Razorpay — **not part of any production user flow**, not linked from navigation.

**Notable business rules / edge cases**: Hardcodes `http://localhost:3000` and embeds test API keys directly in source — must never ship to production traffic.

#### 4.6.5 Membership

**Purpose**: Plan-picker where a user subscribes to or upgrades a paid membership tier.

1. `FR-MEM-LIST/SUBSCRIBE/UPGRADE/REMEMBER`.

**Notable business rules / edge cases**: Membership `history`/`last`/`types` endpoints are unauthenticated server-side — do not treat their response as proof of subscription.

#### 4.6.6 Certificates (`cerificates` — note the codebase-wide spelling)

**Purpose**: Public certificate-number verification and PDF download page.

1. `FR-CERT-VERIFY/DOWNLOAD` — Verification is a public, unauthenticated lookup keyed only by certificate number; the download is a client-rendered PDF, not server-generated.

#### 4.6.7 SC Certificate Renderer & SC ID Card Renderer

**Purpose**: Themeable, printable certificate/ID-card rendering, used both standalone (verify/preview) and embedded in the account flows.

1. `FR-CR-TEMPLATE/VERIFY/PREVIEW/QR` and `FR-ID-TEMPLATE/VERIFY/PREVIEW/QR`.

**Notable business rules / edge cases**: Neither route carries a JWT guard — both render personal data (name, photo, signature) directly from query/verify responses and should not be cached or indexed. Preview mode never calls the backend, so preview and production rendering can silently diverge if the shapes drift apart.

#### 4.6.8 Tickets

**Purpose**: Member-facing support-ticket system, gated by `ticket_management`.

1. `FR-TIX-LIST/CREATE/DETAIL/CONVERSE/UPDATE`.

**Notable business rules / edge cases**: The list fetch hardcodes `limit: 500` with no real pagination UI. File-type allow-listing on attachments is enforced client-side only.

## 5. Consolidated Known Issues (Cross-Cutting)

These recur across multiple modules and are worth tracking centrally rather than only per-module:

- **Inconsistent flag enforcement**: some modules (challenges, tracker, growth-metrics, LMS role-gating) actively redirect to `/errors/404` when their flag is off; many others (jobs, market-insights, community-feed route level, chat file endpoints) rely solely on nav-menu visibility or backend 403s, meaning direct URL navigation can reach a disabled feature's UI shell.
- **Multiple unauthenticated write endpoints** exist where an authenticated-looking flow is actually backed by a backend route with no JWT guard: `users/update/notification`, milestone notes/messages, news preferences, membership history/types, several payment-management routes, and the connections `check_user_online_status` lookup. The frontend must be disciplined about only ever calling these with the current user's own identifiers, since the backend will not stop a caller from supplying someone else's.
- **`powerPitchAccessToken` exposure**: stored in raw `localStorage` and passed as a plain URL query parameter in both `startups` and `pitch-deck-management` — visible in browser history and referrer headers.
- **Client-rendered "documents"**: certificates, ID cards, and invoices are all rendered/exported client-side (DOM-to-image or blob-fetch) rather than server-generated — visual fidelity depends on the browser, and there is no server-side PDF of record for any of these artifacts.
- **Legacy/duplicate route registrations**: `/search/challenges` and `/search/jobs` each have two competing top-level lazy-module registrations; `/programs` and `/vs-programs` are dead redirects; `connections/` (legacy) coexists with `connection-v4`/`connections-v3` as inert model-only code.
- **Two long-standing folder/route typos** — `cerificates` (certificates) and `growth-matrics` (metrics) — are load-bearing in routing and must not be "fixed" without a coordinated, cross-cutting router change.
