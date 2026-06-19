---
id: FE-003
title: Job Board
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - POST api/v1/jobs
    - GET  api/v1/jobs
    - GET  api/v1/jobs/:jobUUID
    - PATCH api/v1/jobs/:jobUUID/details
    - PATCH api/v1/jobs/hiring-profile
    - GET  api/v1/public/search/jobs
    - GET  api/v1/public/jobs/:jobUUID
    - POST api/v1/jobs/:jobUUID/apply
    - POST api/v1/jobs/apply/:applicationUUID/upload/resume
    - POST api/v1/public/resumes/submit
    - POST api/v1/public/resumes/upload
    - GET  api/v1/jobs/applied/list
    - POST api/v1/jobs/upload/attachment
    - GET  api/v1/jobs/interviews/job-seeker
    - GET  api/v1/jobs/interviews/job-applicant
    - PATCH api/v1/jobs/:jobUUID/application/:applicationUUID/actions
    - POST api/v1/jobs/application/:applicationUUID/schedule-interview
  flags:
    - jobs
    - job_seekers
  events: []
tenant_scoped: true
depends_on:
  - FE-001
updated: 2026-06-17
---

# FE-003 — Job Board

## Summary
Full job-board domain spanning two roles: employer-side users (startups, corporates, investors, partners, service-providers, program-office members) post and manage jobs; job-seeker users search, apply, upload resumes, track applications, and schedule interviews. Public-facing routes expose job listings and detail without authentication. The feature is gated by `jobs` (employer surface) and `job_seekers` (seeker-only routes) flags.

## Frontend entry points
Angular modules:
- `sc-saas-frontend/src/app/modules/hire/` — `HireModule` (employer management)
- `sc-saas-frontend/src/app/modules/job-details/` — `JobDetailsModule` (recruiter detail + applicant management)
- `sc-saas-frontend/src/app/modules/job-search/` — `JobSearchModule` (public/authenticated job search)
- `sc-saas-frontend/src/app/modules/job-public-details/` — `JobPublicDetailsModule` (public detail + apply flow)
- `sc-saas-frontend/src/app/modules/applied-jobs/` — `AppliedJobsModule` (job-seeker applied-list + interview tracking)
- `sc-saas-frontend/src/app/modules/job-interview/` — `JobInterviewModule` (standalone interview page)

Routes:

| Route | Module | Guard | Notes |
|---|---|---|---|
| `/jobs` | `HireModule` | ProtectedLayout (implicit auth) | Employer job list |
| `/jobs/create` | `HireModule` | `AuthGuard` | Job creation form |
| `/jobs/:id/edit` | `HireModule` | none explicit | Job edit form |
| `/jobs/:id/details` | `JobDetailsModule` | none explicit | Recruiter detail view |
| `/job-interview/:id` | `JobInterviewModule` | none | Bare page — no layout shell |
| `/search/jobs` | `JobSearchModule` | none | Public job search |
| `/search/jobs/:id` | `JobPublicDetailsModule` | none | Public job detail + apply |
| `/applied/jobs` | `AppliedJobsModule` | none explicit | Job-seeker applied list |

Services: `jobs.service.ts`, `job-details.service.ts`.
NgRx: `core/state/jobs/` — `jobsList`, `jobsLoading`, `jobsError`.

## Backend modules
- `sc-saas-backend/src/modules/job/module.spec.md` — complete job lifecycle: posting, search, application management, interview scheduling, public routes, and public resume intake

## Data flow

### Job creation (employer)
1. Employer navigates to `/jobs/create`; `AuthGuard` enforces authentication.
2. `JobFormComponent` renders a reactive form (multi-select for skills/industry via `NgSelectModule`).
3. Optional attachment upload: `POST api/v1/jobs/upload/attachment` (multipart, 2 MB max) — returns S3 key.
4. On submit: `jobs.service.ts` → `POST api/v1/jobs` with `CreateJobDto`.
5. Backend: `FeatureGuard (@Features(Feature.JOBS))` + `JwtAuthGuard` + `RolesGuard(STARTUP|INVESTOR|CORPORATE|PARTNER|SERVICE_PROVIDER|PROGRAM_OFFICE)`.
6. Backend creates the `jobs` row; returns `{ message, data: JobEntity }`.
7. If a hiring profile is incomplete, `CompleteHiringProfileModalComponent` prompts: `PATCH api/v1/jobs/hiring-profile` is called (see Known issues — this is a no-op).
8. On success, NgRx `GetJobsList` is dispatched to refresh the employer list.

### Job publishing and editing
1. Employer edits an existing job: `PATCH api/v1/jobs/:jobUUID/details` with `UpdateJobDto`.
2. Job status transitions: `ACTIVE → CLOSED` via the details PATCH; `CLOSED → REACTIVE` by sending `jobStatus: REACTIVE`. A non-`CLOSED` job cannot be set to `REACTIVE` — the backend enforces this constraint.
3. No delete route exists; jobs can only be closed.

### Public job search (job-seeker / anonymous)
1. User navigates to `/search/jobs` (no auth required, `ProtectedLayout` provides optional JWT context).
2. `jobs.service.ts` → `GET api/v1/public/search/jobs` (maps to `GET api/v1/public/search/jobs` via `JOBS_PUBLIC` endpoint key) with filter params.
3. Backend `SearchController`: `@Features(Feature.JOBS)`, **no `OptionalJwtAuthGuard`** — fully public, no personalization.
4. Response: paginated job list; `JobSearchComponent` renders `PublicJobCardComponent` cards.
5. User clicks a job card → `/search/jobs/:id` → `JobPublicDetailsComponent` → `GET api/v1/public/jobs/:jobUUID` (fully unauthenticated, no JWT required).

### Job application flow (job-seeker)
1. Authenticated job-seeker on the public detail page clicks Apply.
2. `ApplyJobModalComponent` collects cover letter and resume.
3. Resume upload (if file selected): `POST api/v1/jobs/apply/:applicationUUID/upload/resume` (multipart, 2 MB max). Note: `applicationUUID` must be obtained from a prior `POST :jobUUID/apply` response.
4. `jobs.service.ts` → `POST api/v1/jobs/:jobUUID/apply` with `JobApplyDto`.
5. Backend `JobController`: `JwtAuthGuard` present but **`RolesGuard` is NOT in `@UseGuards` for this method** — any authenticated user (regardless of role) can call this endpoint. The `@Roles(Role.JOB_SEEKER)` decorator is present but unenforced.
6. On success, application row is created with `application_status: PENDING`.
7. For unauthenticated users: `SubmitResumeModalComponent` → `POST api/v1/public/resumes/submit` + `POST api/v1/public/resumes/upload` — fully unauthenticated, rate-limited (2 req/60 s), no `FeatureGuard`.

### Application management (employer)
1. Employer navigates to `/jobs/:id/details` → `JobDetailsComponent`.
2. `job-details.service.ts` → `GET api/v1/jobs/:jobUUID` (recruiter job details including applicants list).
3. Employer shortlists or rejects: `PATCH api/v1/jobs/:jobUUID/application/:applicationUUID/actions` with `JobApplicationActionDto`.
4. Interview scheduling: `POST api/v1/jobs/application/:applicationUUID/schedule-interview` with `JobInterviewDto`.
5. Backend calls `VideoSDKervice.createMeeting()` to provision a VideoSDK room, then creates a `MeetingsEntity` via `MeetingsRepository.createJobInterviewMeeting()` and updates `job_applications.meeting_interview_id`.
6. SES email sent to the candidate with the interview link.

### Interview page (job-seeker)
1. `jobs.service.ts` → `GET api/v1/jobs/interviews/:path` where `path` is `'job-seeker'` or `'job-applicant'` (determined by `ACCOUNT_TYPE` in the component).
2. For job-seekers: gated by `@Features(Feature.JOBS, Feature.JOB_SEEKERS)` — both flags must be active.
3. `/job-interview/:id` renders `JobInterviewComponent` with no layout shell — no navbar/sidebar; intended as a bare interview scheduling/video page.

### Applied jobs list (job-seeker)
1. `jobs.service.ts` → `GET api/v1/jobs/applied/list`.
2. Backend: `JwtAuthGuard` but **no `RolesGuard`** — any authenticated user can access this endpoint.
3. Response: list of `JobApplicationEntity` records; `AppliedJobsComponent` renders them alongside interview info.

## Feature flags
- `jobs` — backend: gates `POST /jobs`, `GET /jobs`, `PATCH /jobs/*`, `GET interviews/job-applicant`, `GET public/jobs/:jobUUID`, and `GET public/search/jobs`; frontend: employer dashboard visibility. Both sides must be on for the employer surface to function.
- `job_seekers` — backend: additionally co-gates `GET interviews/job-seeker` (alongside `jobs`); frontend: seeker-only registration tab visibility and seeker-specific UI elements. Also gates `POST api/v1/public/auth/register/job-seeker` in the auth module.
- Both flags map to `IBrandDetails.features.jobs` and `IBrandDetails.features.job_seekers` in the frontend NgRx global store.

## API contract

### `POST api/v1/jobs`
Request: `CreateJobDto` — title, description, location, industry, required/good-to-have skills (JSON arrays), salary range, job type, attachment (S3 key optional).
Response: `{ message, data: JobEntity }`.

### `POST api/v1/jobs/:jobUUID/apply`
Request: `JobApplyDto` — cover letter, resume file key (optional).
Response: `{ message, data: JobApplicationEntity }` — `applicationUUID` needed for subsequent resume upload.

### `PATCH api/v1/jobs/hiring-profile`
Request: `HiringProfileDto`.
Response: HTTP 200 with success message. **No data is persisted** — service body is commented out (no-op).

### `POST api/v1/jobs/application/:applicationUUID/schedule-interview`
Request: `JobInterviewDto` — proposed date/time, interview type.
Response: `{ message, data: { meetingId, meetingUrl, ... } }` — VideoSDK meeting details.

### `GET api/v1/public/jobs/:jobUUID`
Response: full job detail including `organizationName`, `organizationLogo`. Fully unauthenticated. `requiredSkillIds` population has a copy-paste bug — see Known issues.

**Shape mismatch:** `getJobDetails` on the backend fetches `goodToHaveSkillIds` twice using the same condition (`goodToHaveSkillIds?.length > 0`), so `requiredSkillIds` is only populated when `goodToHaveSkillIds` is also non-empty. If a job has required skills but no good-to-have skills, the `requiredSkillIds` field will be empty in the response. The frontend model must tolerate this.

## Auth & security

**Frontend:**
- Role-based branching (employer vs seeker) is done client-side inside components; no server-side role check is enforced on the apply endpoint.
- `AuthGuard` is only on `/jobs/create`; the edit, detail, applied-jobs, and interview routes have no explicit guard. Unauthenticated users reaching those routes via direct URL get the protected layout, which should redirect them, but there is no explicit route-level guard.

**Backend:**
- All `JobController` routes: `@Features(Feature.JOBS) + JwtAuthGuard + RolesGuard` (except `applied/list` and `:jobUUID/apply` — `RolesGuard` missing for both).
- `PublicJobController` `GET public/jobs/:jobUUID`: `@Features(Feature.JOBS)`, **no JWT** — exposes org name, logo, full job description without authentication.
- `PublicResumesController` `POST public/resumes/upload` and `POST public/resumes/submit`: **no `FeatureGuard`**, **no JWT** — always reachable regardless of the `jobs` flag state, rate-limited to 2 req/60 s only.
- `validateJobResource` in the backend service checks that the job's `userId` is within the requesting user's team member IDs — prevents cross-org job management.

**Gaps:**
- `GET applied/list` and `POST :jobUUID/apply` use `JwtAuthGuard` but not `RolesGuard` — any authenticated user (startup, corporate, mentor, etc.) can call these job-seeker-only endpoints.
- `POST public/resumes/upload` and `/submit` are entirely open even when the `jobs` flag is disabled.

## Known issues / Watch out for

- **`PATCH jobs/hiring-profile` is a no-op.** The `updateHiringProfile` service method runs validation but the actual update is commented out. The frontend calls this from both `jobs.service.ts` and `challenge.service.ts` (the challenge form shares this endpoint); both calls succeed (HTTP 200) but nothing is persisted. Any UI that relies on a hiring profile being complete will never progress via this endpoint.
- **Missing `RolesGuard` on job-seeker routes (security gap).** `GET api/v1/jobs/applied/list` and `POST api/v1/jobs/:jobUUID/apply` declare `@Roles(Role.JOB_SEEKER)` but the `RolesGuard` is absent from `@UseGuards`. Any authenticated user can list job applications or submit a job application regardless of their account type. The frontend is the only role enforcement on these paths.
- **`requiredSkillIds` copy-paste bug.** In `getJobDetails`, `requiredSkillIds` is populated only when `goodToHaveSkillIds?.length > 0` due to a copy-paste error. Jobs with required skills but no good-to-have skills will return an empty `requiredSkillIds` array.
- **`/applied/jobs` imports `JobSearchComponent` from a sibling module.** `AppliedJobsModule` imports `JobSearchComponent` from `job-search.module.ts` — a cross-module component import. Any structural change to `JobSearchComponent` (inputs, outputs, template) can silently break `AppliedJobsModule`.
- **`/job-interview/:id` has no layout shell.** No navbar, sidebar, or global styles apply. Intended for a bare interview video/scheduling page, but the route has no auth guard — a direct URL access by an unauthenticated user is not blocked by Angular routing.
- **`/search/jobs` and `/search/jobs/:id` route ordering.** Both are registered as children of the same lazy-load path. Angular matches the empty-path child first. If route ordering changes, both could collide and only one may be reachable.
- **`getPublicJobDetails` silent redirect on 404.** `jobs.service.ts` navigates to `/search/jobs` on a 404 response without surfacing an error to the user. This swallows "job not found" cases silently.
- **`scheduleJobInterview` logs `LOG_ENTER` twice, no `LOG_EXIT`.** Minor dead code in the backend service; not functional but indicates incomplete copy-paste.
