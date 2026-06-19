---
id: FA-001
title: Application Evaluation
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api:
    - POST api/v1/programs/application/approve — triggers backend to create program membership and push to ecosystem directory
  flags:
    - application_management
admin_modules:
  - sc-saas-admin/modules/application_management/module.spec.md
  - sc-saas-admin/modules/jury/module.spec.md
  - sc-saas-admin/modules/program-management/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/application-management/module.spec.md
updated: 2026-06-18
---

# FA-001: Application Evaluation

## Summary

The application evaluation flow is the primary lifecycle management path for startup (and mentor) applications within a program. Admin staff create programs and evaluation rounds, receive applications submitted by startups through the frontend PWA, manage their progression through shortlisting and rejection, assign jury members to evaluate submissions, aggregate jury scores, and finally approve or reject applicants. Approval triggers a backend API call that creates a program membership record and best-effort pushes the new member to the ecosystem/tenants directory. The mentor application sub-flow mirrors this path but uses a separate set of admin pages and a distinct application number sequence.

## Admin entry points

The flow begins in `modules/application_management/programs/` where the admin user creates a program with a type (incubation, acceleration, fellowship, etc.), defines intake limits, and links the program to a cohort or batch label. Once a program exists, evaluation rounds are created in `modules/application_management/rounds/` — each round carries open and close dates and the scoring criteria (weighted rubric or simple score) that jury members will use.

Applications submitted by startups through the frontend appear in `startup-application-management.php`. The admin user sees a filterable table of applications with their current status (submitted, shortlisted, rejected, approved). From this list the admin can move individual applications to shortlisted or rejected, or open a detail view to review the submitted form data and attached documents.

Mentor program applications are managed at `modules/mentor_application_management.php` — a separate entry point with an independent application number sequence but the same status progression.

## DB flow

1. **Tenants DB (read):** The admin panel resolves the current tenant's `admin_domain` from config and selects the per-tenant client DB connection. No direct program or application data lives in the tenants DB.
2. **Client DB (read) — program list:** Reads `programs` and `program_rounds` tables to populate the program/round selectors in the application list view.
3. **Client DB (read) — application list:** Reads `startup_applications` (or `mentor_applications`) joined to `startups` and `users` for the list view. Filters by program, round, and status.
4. **Client DB (read) — application detail:** Reads the application row plus any linked file attachment paths. Reads `jury_assignments` to show which jury members are assigned.
5. **Client DB (read/write) — status transitions:** Updates the `status` column on the application row (submitted → shortlisted or rejected). Writes an entry to `application_status_history` if that log table is present.
6. **Client DB (read/write) — jury assignment:** `modules/jury/` reads `admin_users` and `users` (jury-role members) to build the assignable list, then writes to `jury_assignments`.
7. **Client DB (read) — score aggregation:** Reads `jury_scores` grouped by `application_id` to produce per-application aggregate scores visible to the admin.
8. **Backend API call — approval:** On approval, admin calls `POST api/v1/programs/application/approve` (see Backend API calls). After a successful response the application row's `status` is set to `approved` in the client DB.

## Backend API calls

**POST api/v1/programs/application/approve**

- Called from the approve action in `startup-application-management.php` via cURL (credentials sourced from `config/config.php` `api_server_url` + `accessToken`).
- Payload: `{ applicationId, startupId, programId, roundId }` (exact field names resolved from the admin's form POST).
- What the backend does: creates a `program_members` record, dispatches a notification to the startup user, and wraps a best-effort push to the tenants/ecosystem directory in try/catch so a directory 500 does not roll back the already-committed approval.
- Admin action on response: on HTTP 200/201 the admin writes `status = approved` to the client DB and redirects with a success flash. On non-200 the admin shows an error message and does NOT update the DB row — the application stays in its prior status.

No other backend API calls are made during the evaluation flow itself (program creation, round management, jury assignment, and scoring all operate directly on the client DB).

## Feature flags

- **`application_management`** — PHP constant defined in `config/config.php`. Must be truthy for the program management, rounds, and application list views to render. The approval cURL call is also gated behind this constant check at the top of `startup-application-management.php`. If the constant is absent or falsy the entire flow is inaccessible regardless of admin role.

## Auth & access

- Admin must have an active PHP session (`$_SESSION['admin_id']` set and verified against the client DB `admin_users` table).
- Program creation and round management require role level 1 (super-admin) or a role with explicit program-management permission.
- Application list, shortlisting, and rejection are accessible to role level 2 (program manager) and above.
- Jury assignment requires role level 1 or program-manager role.
- The final approve/reject action requires role level 1 (super-admin) — a program manager cannot approve.
- Mentor application management follows the same role gates on its own pages.

## Cross-repo impact

- **sc-saas-backend:** The `POST api/v1/programs/application/approve` endpoint owns the membership creation and ecosystem push. If this endpoint changes its expected payload shape or its response structure, the admin cURL caller breaks silently (cURL does not throw on 4xx; the admin must check `$response['status']`).
- **sc-saas-frontend:** Startups see their application status through the frontend PWA. The status values written directly to the client DB by the admin (shortlisted, rejected, approved) are the same values the backend serves to the frontend via its own application-status endpoint. An admin direct-DB write that uses a status string not recognized by the backend enum will cause the frontend to show an unknown state.
- **Ecosystem/tenants directory:** The best-effort push from the backend on approval writes to the tenants directory. If the tenants directory schema for ecosystem entries changes, the push silently fails; the application is still approved but the startup does not appear in the global ecosystem index.

## Known issues

1. **Unbounded PHP resource limits in `application_program_management_funcs.php`:** `ini_set('memory_limit', '6600000000000')` and `ini_set('max_execution_time', '6600000000000')` are set at the top of this file. Every request that includes application management functions inherits these values, making it impossible to enforce per-request resource budgets and allowing a runaway query to hold a PHP-FPM worker indefinitely.

2. **Bitwise `&` instead of logical `&&` in `getRelatedData()` helpers:** The condition used to guard related-entity data loading uses the bitwise AND operator (`&`) on two boolean expressions. The result is always a valid boolean-ish integer but evaluates differently from `&&` when the left operand is falsy and the right operand has side effects. In practice this silently drops related entity data (attached documents, linked mentor profiles) for certain application states, making the detail view appear incomplete without any error.

3. **Mentor application number race condition:** `generateMentorApplicationNo()` uses `SELECT MAX(application_no) + 1` (or equivalent `COUNT + 1`) without a DB-level uniqueness constraint on the `mentor_applications.application_no` column. Two concurrent mentor applications submitted at the same moment can receive the same application number. There is no retry or conflict detection.

4. **Hardcoded `reply_to` in outreach emails:** Notification emails sent during application status transitions (shortlist/reject confirmations) set `reply_to` to `programs@yopmail.com` — a throwaway address used during development. Replies from applicants are silently discarded. This is a dev artifact that was never corrected before production deploy.
