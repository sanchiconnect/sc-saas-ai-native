---
id: FA-007
title: Venture Studio
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api:
    - POST api/v1/applications/approve — approve a VS application (same endpoint as standard application management)
    - POST api/v1/applications/reject — reject a VS application
    - POST api/v1/applications/shortlist — shortlist a VS application
  flags: []
admin_modules:
  - sc-saas-admin/modules/venture-studio/module.spec.md
  - sc-saas-admin/modules/application_management/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/application-management/module.spec.md
updated: 2026-06-18
---

# FA-007: Venture Studio

## Summary

The venture studio (VS) is a distinct program type within the admin panel with its own application management flow, evaluation criteria, and round types. It shares backend API endpoints with standard application management (the backend does not distinguish VS from standard applications at the contract level) but uses a completely separate set of PHP files and a dedicated 62 KB functions include (`venture_studio_application_management_funcs.php`). VS programs can be linked to incubation programs to create a pipeline pathway from VS cohort to incubation. The VS module is not gated by a feature flag — it is a program type variant whose visibility depends on whether the tenant has created any VS programs.

## Admin entry points

The admin user arrives at the venture studio flow through the **Venture Studio** sidebar section (when VS programs exist for the tenant).

- **VS program list**: Admin views all venture studio programs for the tenant. Programs are typed separately in the DB from standard programs.
- **VS program creation/edit**: Admin creates or edits a VS program definition, including its link to a downstream incubation program (pipeline pathway).
- **VS application management** (`venture-studio-application-management.php`): Admin views, filters, and acts on VS applications. The list is backed by `venture_studio_application_management_funcs.php`.
- **VS application detail**: Admin views a single VS application, including evaluation scores, related entity data, and round history.
- **VS application status actions**: Admin shortlists, approves, or rejects a VS application. These actions trigger cURL calls to the backend API.

## DB flow

**VS program list and creation:**

1. **Client DB read** — VS program rows queried (filtered to the tenant's VS program type).
2. **Client DB write** (on create/edit) — VS program row inserted or updated. If a pipeline link is set, the downstream incubation program ID is stored on the VS program record.

**VS application list:**

1. **Client DB read** — VS application rows fetched via `venture_studio_application_management_funcs.php`. Filtering by round, status, and search term applied at query time.
2. **`getRelatedData()` called** — fetches related entity data (startup profile, founder details, etc.) for each application. This function contains the bitwise `&` bug (see Known Issues).
3. Results rendered to admin as a paginated list.

**VS application detail:**

1. **Client DB read** — single VS application row.
2. **Client DB read** — evaluation scores for the application.
3. **`getRelatedData()` called** — loads related entities. Subject to the same bitwise `&` bug.
4. **Client DB read** — round history for the application.

**VS application status change (shortlist / approve / reject):**

1. **Client DB write** — application status updated in the client DB.
2. **Backend API cURL call** — same approval/rejection endpoint as standard application management (see Backend API calls section below).
3. On success, admin is redirected back to the application list with a flash message.

## Backend API calls

VS application status changes call the same backend API endpoints used by standard application management. The backend does not have VS-specific endpoints — it treats VS applications identically to standard applications at the API contract level.

**Shortlist a VS application:**
- `POST api/v1/applications/shortlist`
- Payload: `{ applicationId, programId, status }`
- Admin uses the response status to confirm the DB state is now in sync. On backend error the cURL call is best-effort; the client DB write has already committed.

**Approve a VS application:**
- `POST api/v1/applications/approve`
- Payload: `{ applicationId, programId }`
- Backend triggers any downstream approval side effects (ecosystem sync, notifications). Admin does not interpret the response body beyond success/failure.

**Reject a VS application:**
- `POST api/v1/applications/reject`
- Payload: `{ applicationId, programId, reason }`
- Same best-effort pattern as approve.

All three cURL calls are wrapped in try/catch. A backend 500 does not roll back the client DB write — the client DB is always written first, backend sync is best-effort.

## Feature flags

None. The venture studio module is not gated by a feature flag PHP constant in `config.php`. VS program management is available to any tenant that has VS programs in its client DB. There is no `venture_studio_enabled` or equivalent constant to check. Access is controlled by role level and the presence of VS programs, not a flag.

## Auth & access

- VS program creation and editing requires a super-admin or program-admin role.
- VS application management (list + detail + status changes) requires at minimum a program-admin role scoped to the VS program.
- Evaluator-role users can view application detail and submit scores but cannot change application status.
- There is no secondary CSRF check on VS application status change actions beyond the standard session check — consistent with the broader application management module.

## Cross-repo impact

Because VS application status changes share the standard application management API contract:

- Any change to the `POST api/v1/applications/approve` or `reject` or `shortlist` endpoint shape (payload keys, response structure) in `sc-saas-backend` will break both the standard application management flow AND the VS flow simultaneously. The VS PHP functions file is a separate consumer of the same contract.
- The backend's application-management module (`sc-saas-backend/src/modules/application-management/`) does not distinguish VS from standard applications. If VS-specific approval logic is ever needed at the backend level (e.g. different notification template, different ecosystem push), the backend contract will need to be extended and both PHP callers updated.
- The frontend (`sc-saas-frontend`) does not currently surface VS applications to end users. If a VS approval is expected to trigger a frontend-visible state change (e.g. a member's VS application status widget), the backend approval side effects must be updated first.

## Known issues

1. **Bitwise `&` instead of logical `&&` in `getRelatedData()`.** `venture_studio_application_management_funcs.php` contains a single `&` (bitwise AND) where `&&` (logical AND) is intended in the `getRelatedData()` helper function. This is a copy-paste bug carried over from `application_program_management_funcs.php`. When both operands of the condition happen to have mismatched bit patterns that produce 0, the condition evaluates to false and the related entity block is silently skipped — the application detail or list row is returned with missing related data (empty startup name, missing founder details, etc.) and no error is raised. The symptom is intermittent blank fields on VS application cards.

2. **`create-venture-studio-program copy.php` (space in filename) is present in `modules/` and can be matched by the router.** The file is a dev artifact (a renamed copy of the program creation file). Under certain URL patterns or web-server rewrite rules, a request for `create-venture-studio-program` may resolve to this file rather than the canonical `create-venture-studio-program.php`, serving stale or duplicate content. The file should be removed from `modules/` entirely; its presence is a latent routing ambiguity.

3. **`ini_set('memory_limit', '6600000000000')` effectively removes the PHP memory limit for the VS funcs include.** The VS functions file sets a memory limit of approximately 6 TB at include time, matching the bug in the main application funcs. A runaway query or a very large VS cohort can consume all available server memory before PHP kills the process. There is no per-request cap on how many application rows or related entities are loaded into memory at once.
