---
id: FE-001
title: Auth Flow
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - POST api/v1/public/auth/mobile/login
    - POST api/v1/public/auth/mobile/login/verify
    - POST api/v1/public/auth/register/startup
    - POST api/v1/public/auth/register/job-seeker
    - POST api/v1/public/auth/register/other
    - POST api/v1/public/auth/register
    - GET  api/v1/public/auth/verify/mobile/:mobileNumber
    - GET  api/v1/public/auth/verify/email/:email
    - POST api/v1/public/auth/verify/email
    - GET  api/v1/public/auth/verify/email-token/:token
    - POST api/v1/public/otp_verifications/send
    - POST api/v1/public/otp_verifications/verify
    - POST api/v1/public/otp_verifications/send/whatsapp
    - POST api/v1/public/otp_verifications/verify/whatsapp
    - POST api/v1/public/auth-external/login
    - POST api/v1/public/auth-external/login/verify/import
    - GET  api/v1/users/logout
    - DELETE api/v1/users/delete_account
    - PATCH  api/v1/users/deactivate_account
    - GET  api/v1/admin-actions/backdoor-login/:userId/:adminMd5
  flags:
    - job_seekers
    - startups
    - single_session_login_enabled
    - external_sign_in_enabled
    - external_sign_in_server_enabled
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-001 — Auth Flow

## Summary
Covers every entry and exit from the platform: two-step mobile-OTP login, registration variants (startup, job-seeker, event, generic/other), email-address verification, admin backdoor impersonation, and cross-tenant profile import (`auth-external`). The JWT received on OTP verify is stored in localStorage under `user` and hydrated into the NgRx `auth` store on app bootstrap; subsequent calls carry it as a Bearer token.

## Frontend entry points
Angular module: `sc-saas-frontend/src/app/modules/auth/`

Routes (all lazy-loaded from `app-routing.module.ts`):
- `/auth/login` — `AuthModule` → `LoginComponent`; protected by `NonAuthGuard` (redirects logged-in users)
- `/auth/register` — `AuthModule` → `RegisterComponent`; protected by `NonAuthGuard`
- `/auth/verify-email` — top-level route (not inside `AuthRoutingModule`), renders `VerifyEmailComponent` with root layout (not auth layout)
- `/backdoor-login` — `AdminActionsModule` (lazy); handles admin impersonation payload
- `/connection-request` and `/request/authenticate` — `ConnectionRequestActionEmailModule` (lazy); email-link action flow

Key components: `LoginComponent`, `SignInComponent`, `SignInTwoStepVerificationComponent`, `RegisterComponent`, `VerifyEmailComponent`, `ImportProfileModalComponent` (gated by `external_sign_in_enabled`), `LoginModalComponent`, `RegisterModalComponent`.

Services: `auth.service.ts`, `sign-up.service.ts`.

NgRx: `core/state/auth/` (session bootstrap) and `core/state/sign-up/` (multi-step registration state).

## Backend modules
- `sc-saas-backend/src/modules/auth/module.spec.md` — OTP login, registration variants, email verification, logout, JWT issuance
- `sc-saas-backend/src/modules/auth-external/module.spec.md` — cross-tenant import/export flow
- `sc-saas-backend/src/modules/global/module.spec.md` — `AdminActionsController` owns `GET backdoor-login/:userId/:adminMd5`

## Data flow

### OTP login
1. User enters mobile number / email on `SignInComponent`.
2. `auth.service.ts` → `POST api/v1/public/auth/mobile/login` — initiates OTP; backend sends SMS.
3. User enters 6-digit OTP on `SignInTwoStepVerificationComponent`.
4. Frontend hashes OTP with `md5()` and calls `POST api/v1/public/auth/mobile/login/verify` with `{ code: md5(otp), ... }`.
5. Backend verifies the stored md5 hash, issues JWT, sets `accessToken` cookie (`httpOnly`, `secure`, `sameSite: none`), and returns `{ accessToken, ...user }` in the response body.
6. NgRx `VerifyOtpSuccess` stores the `Auth` object in state and localStorage; HTTP interceptor attaches Bearer on all subsequent calls.

### Registration
1. User selects account type on `RegisterComponent`; tabs (`startups`, `job_seekers`) controlled by flags from NgRx global store.
2. Multi-step form managed by `core/state/sign-up/` slice.
3. `sign-up.service.ts` → `POST api/v1/public/otp_verifications/send` (SMS) or `POST .../send/whatsapp` (WhatsApp OTP) to verify mobile/email.
4. OTP verify: `POST api/v1/public/otp_verifications/verify` with md5-hashed code.
5. Uniqueness checks: `GET api/v1/public/auth/verify/mobile/:mobileNumber` and `GET .../verify/email/:email`.
6. Final submit: `POST api/v1/public/auth/register/startup` | `.../register/job-seeker` | `.../register/other` | `.../register` — backend gates `startup` and `job-seeker` routes with `Feature.STARTUP` and `Feature.JOB_SEEKERS` respectively.
7. On success, same JWT-issuance flow as OTP login; user lands on onboarding.

### Email verification
1. User receives email with a token link.
2. Frontend reads `?token=` query param in `VerifyEmailComponent` and calls `POST api/v1/public/auth/verify/email` with `{ emailAddress, verificationId }`.
3. Backend marks the email verified; frontend redirects to login.

### Backdoor login (admin impersonation)
1. Admin panel (PHP) navigates to `/backdoor-login` with a signed payload.
2. `AdminActionsModule` calls `GET api/v1/admin-actions/backdoor-login/:userId/:adminMd5`.
3. Backend validates `adminMd5` against `AdminUsersEntity.authToken`, then calls `AuthService.createAccessTokenByUserId()` and sets `accessToken` cookie — identical cookie shape to normal login.
4. Frontend stores the token in localStorage/NgRx state; user is now logged in as the impersonated account.

### Cross-tenant import (`auth-external`)
1. `ImportProfileModalComponent` appears when `external_sign_in_enabled` is true.
2. User enters email and account type; `auth.service.ts` → `POST api/v1/public/auth-external/login`.
3. Backend (destination tenant) proxies to `EXTERNAL_SIGN_IN_API_BASE_URL/v1/public/auth-external/send-otp` on the source tenant.
4. User enters OTP; frontend md5-hashes it and calls `POST api/v1/public/auth-external/login/verify/import`.
5. Backend proxies OTP to the source tenant's `verify/export`, receives the full stakeholder profile payload, runs `ImportService.import*()` for the resolved user type, then issues an `accessToken` cookie.
6. Frontend treats the response as a normal login success.

### Logout
1. NgRx `LogOut` action dispatched (from nav or `logout_on_rejection` side-effect).
2. If `single_session_login_enabled` is true, effect calls `GET api/v1/users/logout` to invalidate the server-side session row. Even if that call fails, logout proceeds locally.
3. localStorage and NgRx state are cleared; user redirected to `/auth/login`.

## Feature flags
- `startups` — backend: gates `POST register/startup`; frontend: controls visibility of the startup registration tab.
- `job_seekers` — backend: gates `POST register/job-seeker`; frontend: controls visibility of the job-seeker registration tab.
- `single_session_login_enabled` — backend: governs `users-login-session` entity writes and JWT strategy validation; frontend: controls whether `GET users/logout` is called on `LogOut`.
- `external_sign_in_enabled` — backend: `FeatureGuard` on `POST auth-external/login` and `POST auth-external/login/verify/import`; frontend: gates `ImportProfileModalComponent`.
- `external_sign_in_server_enabled` — backend only; gates the source-tenant export endpoints (`POST auth-external/send-otp`, `POST auth-external/login/verify/export`).

Both `startups` and `job_seekers` are read from `IBrandDetails.features` in the NgRx global store on the frontend and from the `saasFeatures` map on the backend — they must match the cockpit `tenant_users` column names exactly.

## API contract

### `POST api/v1/public/auth/mobile/login`
Request: `LoginDto` — `{ countryCode: string, email?: string, mobileNumber?: string }`
Response: `{ message, data: null }` (OTP sent; no token yet)

### `POST api/v1/public/auth/mobile/login/verify`
Request: `VerifyUserDto` — `{ email?, mobileNumber?, countryCode?, code: string (md5) }`
Response: `{ message, data: { accessToken: string, userId, name, accountType, ... } }`
Frontend `Auth` model maps these fields; the `accessToken` field name is a workspace invariant.

### `POST api/v1/public/auth/register/startup`
Request: `RegisterStartupUserDto` (class-validator, snake_case)
Response: `{ message, data: { accessToken, ...user } }`

### `POST api/v1/public/auth-external/login`
Request: `ExternalLoginDto` — `{ email: string, accountType: UserTypes }`
Response: `{ message, data: null }` (OTP proxied to source tenant)

### `POST api/v1/public/auth-external/login/verify/import`
Request: `ExternalVerifyUserDto` — `{ email, code (md5), accountType }`
Response: `{ message, data: { accessToken, ...user } }` — same shape as main login verify

Registration sub-paths are constructed by string concatenation on the frontend (`ENDPOINT.REGISTER + userType`). A backend path rename will not produce a TypeScript compile error; the only detection mechanism is running `/audit-contract` after any route change.

## Auth & security

**Frontend guards:**
- `NonAuthGuard` — prevents authenticated users from re-entering `/auth/**`.
- `AuthGuard` — used by all protected feature routes (not auth routes).
- No guard on `/backdoor-login` beyond what the backend validates; the frontend blindly accepts any JWT issued by the backdoor endpoint.

**Backend guards:**
- `RateLimiterGuard + @RateLimit` — applied to all login/register routes to limit brute-force attempts.
- `FeatureGuard + @Features(...)` — gates `register/startup`, `register/job-seeker`, `auth-external/*` routes.
- `backdoor-login` endpoint: **no `JwtAuthGuard`** — the only protection is `:adminMd5` path token validated against `AdminUsersEntity.authToken`. This endpoint issues a real JWT cookie and is very high blast-radius. An exposed or rotated `adminMd5` invalidates all admin operations platform-wide.
- `auth-external` endpoints: **no `JwtAuthGuard`** on any of the four routes — all are public, gated only by feature flags. The `login/verify/export` route returns full stakeholder profile data to any caller with the right flag enabled on the source tenant.

**Gaps:**
- `GET api/v1/admin-actions/forgot-password/:adminEmail` has no `adminMd5` token — it is fully open with no auth whatsoever.
- The `external_sign_in_server_enabled` flag + flag split is the only barrier preventing the export endpoint from leaking profile data to arbitrary callers.

## Known issues / Watch out for

- **OTP md5 hash mismatch (critical bug).** The frontend hashes the OTP with `md5()` before sending it in every OTP verify call (`mobile/login/verify`, `otp_verifications/verify`, `otp_verifications/verify/whatsapp`, `auth-external/login/verify/import`). The backend `verifications` module stores the OTP as an md5 hash in the DB — however, if any code path in the backend compares the incoming `code` field against the stored value using a plain equality check (`===`) rather than comparing two hashed values, this will always fail. Audit `VerificationsService` to confirm both the stored value and the incoming value are hashed before comparison.
- **Registration route string concatenation.** `sign-up.service.ts` builds paths as `ENDPOINT.REGISTER + userType`. A backend rename (e.g. `register/startup` → `register/startups`) will compile cleanly on the frontend and silently produce 404s at runtime. Always run `/audit-contract` after touching `auth` controller paths.
- **`VerifyEmailComponent` route mismatch.** The component is declared in `AuthModule` but its route is at the top level in `app-routing.module.ts`, so it renders with the root layout (navbar/sidebar) rather than the auth layout. Changing `AuthRoutingModule` will not affect this component's route.
- **`auth-external` `userId` may be `undefined`.** In `verifyAndImportUser`, if `userInfo.userType` hits the `default` branch of the switch (unsupported account type), `userId` remains `undefined` and `createAccessTokenByUserId(undefined)` is called — this will throw or produce an invalid token. No guard exists before that call.
- **Cross-tenant HTTP error leakage.** `auth-external/login()` and `verifyAndImportUser()` re-throw `error.response.data.message` from the source tenant directly to the caller, potentially exposing the source tenant's internal error messages.
- **`LogOut` with `{ ignoreRedirect: true }`.** Several dashboard services (investor, corporate, mentor, partner) call `authService.logout({ ignoreRedirect: true })` from a `setTimeout(1000)` inside `logout_on_rejection` side-effects. This delay and redirect suppression avoids double-navigation but means logout can be slightly deferred after rejection detection.
- **`saasFeatures` race at startup.** Feature flags are `{}` until `GlobalService.getSAASSettings()` completes at bootstrap. Any guard evaluating a flag before bootstrap completes will see all flags as falsy — registration routes for `startups`/`job_seekers` may appear unavailable momentarily.
