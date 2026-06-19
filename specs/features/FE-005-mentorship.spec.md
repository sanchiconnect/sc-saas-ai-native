---
id: FE-005
title: Mentorship
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET  api/v1/mentors/mentor-information
    - PATCH api/v1/mentors/mentor-information
    - POST  api/v1/mentors/upload/logo
    - GET   api/v1/mentors/dashboard
    - PATCH api/v1/mentors/request/approval
    - GET   api/v1/mentors/profile_completeness
    - GET   api/v1/mentors/public/mentor-information/:mentorUUID
    - PATCH api/v1/mentors/engagement-information
    - GET   api/v1/mentorship
    - GET   api/v1/mentorship/stats
    - GET   api/v1/mentorship/startups
    - GET   api/v1/mentorship/mentors
    - POST  api/v1/mentorship/manual-entry
    - POST  api/v1/mentorship/auto-entry
    - PATCH api/v1/mentorship/ratings/:id
    - PATCH api/v1/mentorship/approve-hours/:id
  flags:
    - mentors
    - mentor_hours
    - logout_on_rejection
    - ecosystem_enabled
  events: []
tenant_scoped: true
depends_on:
  - FE-001
updated: 2026-06-17
---

# FE-005 — Mentorship

## Summary
Two related but distinct feature areas: (1) mentor profile management — self-service profile editing, avatar upload, approval workflow, completeness scoring, and public profile display; and (2) mentorship hour tracking — a shared tracker for mentors and startups to log sessions (manual or automated from VideoSDK), approve/reject logged hours, submit bilateral ratings, and view session stats. Video sessions are provisioned by VideoSDK and auto-logged via the tracker.

## Frontend entry points
Angular modules:
- `sc-saas-frontend/src/app/modules/mentors/` — `MentorsModule` (profile portal) and `MentorFormPreviewRoutingModule` (preview routes)
- `sc-saas-frontend/src/app/modules/tracker/` — `TrackerModule` (hours tracker, lazy-loaded at `/tracker`)

Routes:

| Route | Module | Guard | Notes |
|---|---|---|---|
| `/mentors/dashboard` | `MentorsModule` | `AuthGuard` | Mentor dashboard |
| `/mentors/edit/mentor-information` | `MentorsModule` | `AuthGuard` | Profile edit — step 1 |
| `/mentors/edit/industry-technology` | `MentorsModule` | `AuthGuard` | Profile edit — step 2 |
| `/mentors/edit/extra` | `MentorsModule` | `AuthGuard` | Extra / custom forms |
| `/mentors/edit/custom-forms/:uuid/:slug` | `MentorsModule` | `AuthGuard`, `expectedType: MENTOR` | Dynamic custom forms |
| `/mentors/profile/:profileId/:slug` | `MentorsModule` | none | Public profile page |
| `/edit-preview/mentor-information` | `MentorFormPreviewRoutingModule` | `AuthLayoutWrapper` | Preview mode |
| `/edit-preview/industry-technology` | `MentorFormPreviewRoutingModule` | `AuthLayoutWrapper` | Preview mode |
| `/tracker` | `TrackerModule` | ProtectedLayout | Mentorship hours tracker |

Services: `mentors.service.ts` (profile management), `mentorship.service.ts` (hours tracking).

NgRx:
- `core/state/mentors-dashboard/` — dashboard data, profile completeness, approval request state.
- `core/state/mentor-info/` — cached mentor profile for edit forms.

## Backend modules
- `sc-saas-backend/src/modules/mentors/module.spec.md` — mentor profile lifecycle, avatar upload, approval, profile completeness, recommended startups, application-round management
- `sc-saas-backend/src/modules/mentorship/module.spec.md` — hour logging (manual + auto), approval workflow, ratings, connected-party lists

## Data flow

### Mentor profile load and edit
1. Authenticated mentor navigates to `/mentors/dashboard`.
2. NgRx `GetMentorDashboard` → `mentors.service.ts` → `GET api/v1/mentors/dashboard`.
3. Backend `MentorsController`: `@Features(Feature.MENTORS) + JwtAuthGuard + RolesGuard(MENTOR)`.
4. Dashboard response populates the `mentors-dashboard` NgRx slice.
5. Mentor navigates to `/mentors/edit/mentor-information`; profile loaded from `GET api/v1/mentors/mentor-information` into `mentor-info` NgRx slice.
6. Mentor edits fields; `PATCH api/v1/mentors/mentor-information` with `MentorInformationDto`.
7. On success: backend conditionally calls `EcoSystemService.updateMentor(uuid)` if `ECOSYSTEM_ENABLED` is true AND the mentor is approved AND `isSearchResults` is true. **This call is NOT best-effort** — a cockpit failure throws and propagates, failing an otherwise-successful profile edit.
8. After save, `mentors.service.ts` calls `getProfileCompleteness()` → `GET api/v1/mentors/profile_completeness`.

### Avatar upload
1. Mentor uploads a logo from the edit page.
2. `mentors.service.ts` → `POST api/v1/mentors/upload/logo` (multipart/form-data).
3. Backend stores file under `LogoFolders.MENTOR_FOLDER/<uuid>` via `UploadService`, updates `MentorsEntity.avatar` and the `UserRepository` user avatar.
4. If `Feature.CHAT` is enabled and chat type is `COMET_CHAT`, backend propagates the avatar update to the CometChat SDK.
5. Frontend re-dispatches `GetProfile` if `refetchProfile=true` and calls `getProfileCompleteness()`.

### Approval request
1. Mentor submits for admin review: `mentors.service.ts` → `PATCH api/v1/mentors/request/approval`.
2. Backend sends SES email (profile-under-review) and conditionally a WhatsApp message (if `Feature.WA_SEND_MESSAGES` is active).
3. NgRx `SendRequestApproval` / `SendRequestApprovalSuccess` / `SendRequestApprovalFault` update the approval request state.
4. On approval/rejection by admin, the application-round management endpoints are called by the admin panel (`POST api/v1/mentor-application-management/update-round/:adminMd5`, etc.).

### Profile completeness and `logout_on_rejection`
1. `GET api/v1/mentors/profile_completeness` → `GetProfileCompleteness` NgRx action.
2. On `GetProfileCompletenessSuccess`: if `isRejected: true` in the response AND `brandDetails.features.logout_on_rejection` is truthy, the effect triggers `authService.logout({ ignoreRedirect: true })` after a `setTimeout(1000)`.
3. `logout_on_rejection` flag must be defined in the cockpit. The `setTimeout(1000)` delay exists to avoid double-navigation from concurrent logout flows across dashboard services.

### Public profile
1. Any user navigates to `/mentors/profile/:profileId/:slug` (no auth guard).
2. `mentors.service.ts` → `GET api/v1/mentors/public/mentor-information/:mentorUUID`.
3. Backend: `@Features(Feature.MENTORS) + FeatureGuard` only — **no `JwtAuthGuard`**.
4. View count increment: a separate `GET api/v1/mentors/increment_views/:mentorUUID` endpoint exists but the corresponding call (`incrementViews`) is commented out in `getMentorInformationPublicly` on the backend. View counts are not incremented.

### Manual hour logging (mentor or startup)
1. Mentor or startup opens `TrackerComponent` at `/tracker`.
2. Startup opens the connected-mentors dropdown: `mentorship.service.ts` → `GET api/v1/mentorship/mentors`.
3. Mentor opens the connected-startups dropdown: `GET api/v1/mentorship/startups`.
4. Both lists are derived from `ConnectionsRepository` accepted connections, then bulk-fetched — two sequential queries, no join.
5. User opens `AddHoursModalComponent` and submits: `POST api/v1/mentorship/manual-entry` with `{ startupId, mentorId, date, timeFrom, timeTo, mode, type }`.
6. Backend validates `timeTo > timeFrom` (service layer, not DTO), creates a `MentorshipEntity` row, and sends an SES approval-request email with a token-authenticated deep-link to the startup.
7. Tracker updates via `GET api/v1/mentorship` on next load.

### Auto hour logging from VideoSDK
1. After a video session ends, mentor calls `POST api/v1/mentorship/auto-entry` with `{ startupId, meetingId, timeZone, offset }`.
2. `mentorship.service.ts` auto-populates `timeZone` (via `moment.tz.guess()`) and `offset` (minutes from UTC) before sending.
3. Backend `VideoSDKervice.getMeetingSessions(:meetingId)` fetches the meeting session; converts UTC start/end times to the caller's timezone via `moment-timezone`.
4. Creates a `MentorshipEntity` row. **Email and WhatsApp notifications are commented out** in `createAutoHourEntry` — the startup receives no notification when hours are auto-logged.
5. **Return value mismatch:** `createAutoHourEntry` returns the raw VideoSDK session data, not the created `MentorshipEntity` record. The frontend caller receives VideoSDK metadata, not the created row.

### Hour approval (startup)
1. Startup reviews pending hours in `TrackerComponent`.
2. `mentorship.service.ts` → `PATCH api/v1/mentorship/approve-hours/:id` with `{ actionType: 'APPROVE'|'REJECT', rejectMessage? }`.
3. Backend: `@Features(Feature.STARTUP, Feature.MENTOR_HOURS) + JwtAuthGuard + RolesGuard(STARTUP)` — startup-only.
4. On approval, bilateral ratings become available.

### Session ratings
1. Either party opens `RatingModalComponent`.
2. `mentorship.service.ts` → `PATCH api/v1/mentorship/ratings/:id` with `{ rating, comments? }`.
3. Backend branches on `user.accountType`: if mentor, writes `startupRatings`; if startup, writes `mentorRatings`. The field naming is counter-intuitive — the mentor's rating is stored in `startupRatings` (the field the startup sees).
4. Both `Feature.MENTORS` and `Feature.STARTUP` and `Feature.MENTOR_HOURS` must all be active for this endpoint.

### Session stats
1. `TrackerComponent` fetches `GET api/v1/mentorship/stats`.
2. Backend iterates all rows for the current user; computes `total_minutes`, `total_approved_minutes`, `avg_ratings`. Logic branches by caller role (mentor vs startup).

## Feature flags
- `mentors` — backend: gates all `MentorsController` authenticated routes and all `MentorshipController` routes except `approve-hours`; frontend: controls mentor portal visibility. Disabling it disables both the profile portal AND all hour tracking for the mentor role.
- `mentor_hours` — backend: co-gates all `MentorshipController` routes alongside `mentors` or `startup`; both must be active for the tracker. Frontend must check this flag before showing the tracker navigation.
- `logout_on_rejection` — frontend only (technically); determines whether `authService.logout()` is called when `profile_completeness` returns `isRejected: true`.
- `ecosystem_enabled` — backend: checked at runtime in `editMentorInformation` and `deleteMentorInformationById` to conditionally trigger ecosystem sync.

## API contract

### `PATCH api/v1/mentors/mentor-information`
Request: `MentorInformationDto` — bio, areas of expertise, sector interests, availability, etc.
Response: `{ message, data: MentorsEntity }`.
Side-effect: if `ecosystem_enabled` and approved and `isSearchResults`, `EcoSystemService.updateMentor()` is called (NOT best-effort — throws on cockpit failure).

### `POST api/v1/mentorship/manual-entry`
Request: `CreateManualEntryDto` — `{ startupId, mentorId, date, timeFrom, timeTo, mode, type }`.
Validation: `timeTo > timeFrom` enforced at service layer, not DTO.
Response: `{ message, data: MentorshipEntity }`.

### `POST api/v1/mentorship/auto-entry`
Request: `AutoHoursEntryDto` — `{ startupId, meetingId, timeZone }`.
Response: **returns raw VideoSDK session payload**, not the created `MentorshipEntity`. Frontend must not assume the response shape matches a mentorship record.

### `PATCH api/v1/mentorship/approve-hours/:id`
Request: `ApproveHoursDto` — `{ actionType: 'APPROVE' | 'REJECT', rejectMessage?: string }`.
Response: `{ message, data: MentorshipEntity }`.

### `PATCH api/v1/mentors/engagement-information`
Frontend endpoint key `ENGAGEMENT_INFO` resolves to `corporates/engagement-information` in `ApiEndpointService`, not a mentors-specific path. The backend `mentors` module spec lists no `engagement-information` route. **This is a cross-domain bug** — `patchEngagementInfo` in `mentors.service.ts` calls the corporate endpoint.

## Auth & security

**Frontend:**
- All mentor edit/dashboard routes: `AuthGuard` enforced.
- `/mentors/profile/:profileId/:slug`: no guard — public profile is accessible without login.
- `/tracker`: `ProtectedLayout` (implicit auth).
- No Angular `FeatureGuard` wired in routing; flag checks are component-level.

**Backend:**
- All `MentorsController` authenticated routes: `@Features(Feature.MENTORS) + JwtAuthGuard + RolesGuard(MENTOR)`.
- `GET mentors/public/mentor-information/:mentorUUID`: `@Features(Feature.MENTORS) + FeatureGuard` only — no JWT.
- `GET mentors/public/elastic-search/mentor-information` and `GET mentors/increment_views/:mentorUUID`: **no guards at all** — fully public, no feature flag, no JWT. The elastic-search endpoint returns all mentor records.
- `MentorApplicationManagementController`: `@UseGuards(FeatureGuard)` at class level but **no `@Features` decorator** — FeatureGuard runs but no flag is checked; routes are effectively ungated. Auth is only the `:adminMd5` path token.
- `MentorshipController`: `JwtAuthGuard + RolesGuard` per route, all co-gated by `Feature.MENTOR_HOURS`.

**Gaps:**
- `GET mentors/public/elastic-search/mentor-information` exposes all mentor records without any auth or flag gate.
- `MentorApplicationManagementController` has no effective flag gate.
- Ecosystem sync on mentor profile edit is NOT best-effort — a cockpit outage will fail the profile edit.

## Known issues / Watch out for

- **`patchEngagementInfo` calls the corporate endpoint (cross-domain bug).** `mentors.service.ts` uses the `ENGAGEMENT_INFO` constant which resolves to `corporates/engagement-information` in `ApiEndpointService`. The backend `mentors` module has no `engagement-information` route. Any mentor engagement update is silently routed to the corporate endpoint. Verify if mentors should have their own engagement endpoint, then update `ApiEndpointService` accordingly.
- **Ecosystem sync on mentor edit is NOT best-effort.** Unlike the platform convention (ecosystem updates wrapped in try/catch that logs but does not rethrow), `editMentorInformation` propagates ecosystem sync errors directly. A cockpit outage while a mentor edits their profile will return a 500 to the user and fail the save, even though the local DB write may have succeeded. Wrap in try/catch per the platform convention.
- **`auto-entry` returns VideoSDK payload, not the created mentorship record.** `createAutoHourEntry` returns the raw `getMeetingSessions` response. Frontend callers expecting a `MentorshipEntity` shape will silently receive VideoSDK data. The created record must be fetched separately via `GET api/v1/mentorship`.
- **Auto-entry notifications are commented out.** The startup receives no email or WhatsApp notification when hours are auto-logged from a VideoSDK session. This is likely a TODO, not intentional. Manual entry does send an SES email.
- **Tracker route registration conflict risk.** The original `// path: 'track'` stub inside `MentorsModule` must not be re-enabled. `TrackerModule` is independently registered at `path: 'tracker'` in `app-routing.module.ts`. Re-enabling the stub would create two route registrations for different paths pointing to the same module.
- **`MentorsDashboardComponent` (v1) is dead code.** The active dashboard route uses `MentorDashboardWrapperComponent`. Do not add new logic to `MentorsDashboardComponent`.
- **Ratings field naming is counter-intuitive.** A mentor's submitted rating is stored in `startupRatings` (the value the startup sees) and vice versa. When reading mentorship records, interpret field names relative to the viewer, not the submitter.
- **Browser timezone vs meeting timezone drift.** `mentorship.service.ts` auto-populates `offset` and `timeZone` using the browser's current timezone (`moment.tz.guess()`), not the meeting's actual timezone. If the user's device TZ differs from the meeting TZ, auto-logged session durations will be incorrect.
- **`console.log` leaks in backend.** `getMentorshipStats` logs the full session data to stdout; `getConnectedStartups` logs connection count. Both expose user IDs and session metadata in production logs.
