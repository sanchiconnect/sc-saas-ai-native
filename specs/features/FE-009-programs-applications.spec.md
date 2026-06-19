---
id: FE-009
title: Programs & Applications
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET api/v1/programs-management
    - GET api/v1/programs-management/applied/list
    - GET api/v1/programs-management/code/:programCode
    - POST api/v1/programs-management/:programUUID/apply
    - POST api/v1/programs-management/:programUUID/submit
    - GET api/v1/application-programs-management
    - GET api/v1/application-programs-management/code/:programCode
    - POST api/v1/application-programs-management/:programUUID/:submissionId/apply
    - POST api/v1/application-programs-management/submit-document
    - POST api/v1/application-programs-management/:programUUID/upload-document
    - GET api/v1/application-programs-management/fetch-documents/:programId/:submissionId/:roundId?
    - POST api/v1/application-programs-management/:programUUID/payment-reminder/:adminMd5
    - GET api/v1/vs-programs-management
    - GET api/v1/vs-programs-management/code/:programCode
    - POST api/v1/vs-programs-management/:programUUID/apply
    - POST api/v1/vs-programs-management/:programUUID/submit
    - GET api/v1/forms-management/uuid/:uuid
    - POST api/v1/forms-management/submission/:formUUID
    - POST api/v1/forms-management/submission/:formUUID/upload-file
    - POST api/v1/forms-management/submission/:submissionId/cfa/upload-pitch-document
    - GET api/v1/public/forms-management/submission/:formUUID/fetch
    - POST api/v1/public/forms-management/submission/:formUUID/submit
  flags:
    - startups
    - venture_studio
    - individuals
  events: []
tenant_scoped: true
depends_on:
  - FE-008
updated: 2026-06-17
---

# FE-009 — Programs & Applications

## Summary

Full program lifecycle for tenant members: browsing programs, submitting call-for-applications (CFA), completing multi-step dynamic forms, uploading documents, tracking round progression, and receiving outcome notifications. Three parallel program types exist — classic (`programs-management`), CFA (`application-programs-management`), and Virtual Summit (`vs-programs-management`) — each with its own Angular module, backend controller, and entity tree, but sharing a structural pattern. Dynamic forms (`form-management`) provide the question surfaces across all three flows.

## Frontend entry points

Module specs:
- `sc-saas-frontend/src/app/modules/programs/module.spec.md`

Routes (all lazy-loaded, wrapped in `ProtectedLayoutWrapperComponent`):

| Path | Component | Auth |
|---|---|---|
| `/programs` | `ProgramsComponent` | open — immediately redirects to `/call-for-applications` |
| `/programs/apply/:code/:slug` | `ProgramPublicApplyComponent` | open (guest OTP verify) |
| `/programs/details/:code/:slug` | `ProgramCodeDetailsComponent` | open |
| `/programs/applied/:id` | `ProgramsDetailsPageComponent` | AuthGuard |
| `/programs/applied/:id/payment-form` | payment tab | AuthGuard |
| `/programs/applied/:id/video-pitch` | video pitch tab | AuthGuard |
| `/call-for-applications` | `CallForApplicationsComponent` | open |
| `/call-for-applications/applied` | `CallForApplicationsAppliedComponent` | open |
| `/vs-programs/details/:code/:slug` | `VsProgramCodeDetailsComponent` | open |
| `/vs-programs/applied/:id` | `VsAppliedProgramsComponent` | open (no AuthGuard — deliberate for shared-link preview) |

The `/programs` root is a dead route in production — `ProgramsComponent.ngOnInit` immediately calls `this.router.navigate(['/call-for-applications'])`. Do not add new logic there.

Services: `PublicApiService` (program and form API calls), `ProgramOfficeService` (program-office profile + document management — also houses meeting feedback and event API calls that don't conceptually belong here).

## Backend modules

Module specs:
- `sc-saas-backend/src/modules/program-management/module.spec.md`
- `sc-saas-backend/src/modules/application-management/module.spec.md`
- `sc-saas-backend/src/modules/form-management/module.spec.md`
- `sc-saas-backend/src/modules/vs-programs-management/module.spec.md`

`ProgramsController` (path `programs-management`, v1): classic programs. Startup-facing apply/submit/form-access require `JwtAuthGuard` + `RolesGuard(STARTUP)` + `@Features(Feature.STARTUP)`. Admin-callback routes (`update-round`, `reject-round`, `tentative-round`, `payment-reminder`) authorized only by `:adminMd5` token — no JWT. **`payment-reminder` has `checkIsValidAdmin` commented out — it is completely unauthenticated.**

`ApplicationProgramController` (path `application-programs-management`, v1): CFA programs. `FeatureGuard` is on all controllers but NO `@Features(...)` is declared on any route — the gate is entirely inert. Admin-callback routes also use `:adminMd5`. Apply route has auth guards commented out.

`VsProgramsManagementController` (path `vs-programs-management`, v1): VS programs. `apply`/`submit`/`form-access`/`applied-list` require `JwtAuthGuard` + `RolesGuard(INDIVIDUAL)` + `@Features(Feature.INDIVIDUALS, Feature.VENTURE_STUDIO)`. Admin callbacks (update-round, reject-round, tentative-round) — JWT-less, only `:adminMd5` token. `@Features` is commented out on list/detail/public routes.

`FormsController` (path `forms-management`, v1): form definitions are public (no guard). Submission read/write and upload require `JwtAuthGuard`; `check-access` additionally requires `RolesGuard(STARTUP)`. `cfa/upload-pitch-document` has JWT guard commented out — fully public.

`PublicFormController` (path `public/forms-management`, v1): no guards — intended for externally-shared forms.

## Data flow

1. **Program listing** — `GET programs-management` or `GET application-programs-management` or `GET vs-programs-management`. All list endpoints are unauthenticated on the backend (guards removed or never added). Frontend sends token via interceptor but backend ignores it.
2. **Program detail** — `GET programs-management/code/:programCode`. Guards commented out on backend; unauthenticated. `GET application-programs-management/:programUUID` is JWT-authenticated.
3. **Apply (CFA)** — `POST application-programs-management/:programUUID/:submissionId/apply`. This route has auth/role/feature guards commented out on the backend — it is effectively public.
4. **Dynamic form submission** — `POST forms-management/submission/:formUUID` (JWT required). Frontend renders form questions fetched from `GET forms-management/uuid/:uuid` (public) and POSTs answers.
5. **Document upload** — `POST application-programs-management/:programUUID/upload-document` (multipart, 25 MB cap). `POST forms-management/submission/:formUUID/upload-file` (JWT). `POST forms-management/submission/:submissionId/cfa/upload-pitch-document` (JWT guard commented out — public).
6. **VS program round flow** — `POST vs-programs-management/:programUUID/apply` creates the `IndividualEntity.programs` entry. Admin advances via `update-round/:adminMd5`; rounds are tracked in `VsProgramIndividualRoundsEntity`.
7. **Auto-row creation bug** — `getProgram` (both `vs-programs-management` and `program-management`) auto-creates a round record on every fetch for a logged-in applicant who has not yet formally applied. A browse call silently inserts a `VsProgramIndividualRoundsEntity` / `ProgramStartupRoundsEntity` row.
8. **Guest CFA apply** — `ProgramPublicApplyComponent` uses OTP verification via `ng-otp-input`. Stores `AutoApplyProgramOffSecret` constant in `localStorage` key `auto_apply_program` to trigger apply after login redirect.

## Feature flags

- `startups` — gates `apply`, `submit`, `form-access`, and `applied/list` in `program-management`. Must exist in the cockpit. Run `/trace-flag startups`.
- `venture_studio` + `individuals` — co-gate apply/submit/form-access/applied-list in `vs-programs-management`. List and detail routes have `@Features` commented out.
- CFA module (`application-management`) has NO active feature flag gate — `FeatureGuard` is declared on controllers but no `@Features(...)` annotation is present on any route.

## API contract

- `moduleType` strings used in payment-related calls from programs (`"program"`, `"round"`) must match the values used in `payment-management`. A mismatch causes silent verification failures.
- Admin-callback DTOs: `UpdateRoundDto` (`nextRoundId`, `startupIds[]`, `approvalMessage?`), `RejectRoundDto` (`startupIds[]`, `rejectionMessage`), `TentativeRoundDto` (`startupIds[]`). VS program equivalents use `individualIds[]` instead of `startupIds[]`.
- `VsProgramsEntity.formId` column is typed `int` at the DB level but is overwritten at service layer with an array of form-metadata objects. Any code reading `formId` as a numeric FK after a `getProgram` call will see the mutated array — do not rely on `program.formId` as a number.

## Auth & security

Cross-repo security gaps:

1. **`POST application-programs-management/:programUUID/:submissionId/apply` is entirely open** — all guards commented out. Any unauthenticated caller can submit an application.
2. **`POST programs-management/:programUUID/payment-reminder/:adminMd5` has `checkIsValidAdmin` commented out** — this is a completely unauthenticated write endpoint that sends payment reminder emails. Any caller knowing the URL can trigger bulk SES emails.
3. **`application-management` FeatureGuard is inert** — no `@Features(...)` declared anywhere in the controller. CFA program routes are accessible regardless of flag state.
4. **`POST forms-management/submission/:submissionId/cfa/upload-pitch-document` is open** — `JwtAuthGuard` is commented out. Unauthenticated callers can upload files to S3 on behalf of any `submissionId`.
5. **`getProgram` (VS programs) creates DB rows on every read** for a logged-in individual — a read endpoint that performs writes is a side-effect bug. Browsing program details generates orphan `VsProgramIndividualRoundsEntity` rows for users who never formally apply.
6. **`VsProgramsManagementController.checkFormProgramAccess`** uses `user.startupId` instead of `user.individualId` — for Individual-type users `startupId` is `null`; the form-access check will fail silently or return incorrect results.
7. Admin md5 tokens appear in URL paths for all admin-callback routes (`update-round`, `reject-round`, etc.) — they may appear in server access logs, proxy logs, and browser history. Treat as deployment secrets.

## Known issues / Watch out for

- **`/programs` is a dead route.** The root `ProgramsComponent` redirects immediately to `/call-for-applications`. All new program logic must go into the CFA module.
- **`ProgramsService` / `PublicApiService` responsibility creep** — `ProgramOfficeService` also owns meeting feedback calls (`getFeedbackQuestions`, `onSubmitFeedback`, `getMeetingDetails`) and primary event data (`getPrimaryEventData`). These belong in `MeetingService`.
- **`getSingleProgram` in classic programs has N+1 queries** — one per form to calculate completeness. For programs with many forms this degrades at scale.
- **`ProgramPitchVideoRepository` is registered both in `ProgramsManagementModule` and in the power-pitch module** — two injectable instances. Cross-module use is via direct provider declaration rather than module imports. Ensure both use the same underlying `DataSource` or data will diverge.
- **`CacheModule` is imported** in `program-management` but `CACHE_MANAGER` is never injected anywhere in that module — unused.
- **`ProgramOfficeService.getProgramOfficeProfileCompleteness()`** triggers auto-logout via `setTimeout(..., 1000)` if `logout_on_rejection` is set and the profile is rejected. It reads `getBrandDetails` with `take(1)` — if the store has not yet emitted a value this fires silently as a no-op, masking the rejection state.
