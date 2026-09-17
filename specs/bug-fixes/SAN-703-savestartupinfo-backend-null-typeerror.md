---
id: SAN-703
title: "saveStartUpInfo fails with raw backend TypeError Cannot read properties of null (reading 'isApproved')"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-703
sentry:
  - SC-SAAS-FRONTEND-CS
repos: [backend]
commit: none — root cause is in sc-saas-backend, out of this session's scope
created: 2026-09-08
updated: 2026-09-08
---

# SAN-703 — backend null-dereference leaking a raw TypeError to the client (filed as Repo: Backend)

## Investigation
Captured in the `sc-saas-frontend` Sentry project, but the root cause is backend. `startup.service.ts`'s `saveStartUpInfo()` only does `console.warn(\`saveStartUpInfo( ${fault?.error?.message} )\`)` — it logs whatever `fault.error.message` the backend returned. The captured message is a raw, unhandled JS `TypeError` (`Cannot read properties of null (reading 'isApproved')`) — the shape of a NestJS default exception-filter response when a controller/service throws an uncaught error. This means the backend's `STARTUP_INFO` PATCH handler dereferences `.isApproved` on something `null` for this tenant/user, and leaks the raw JS error text to the client (an info-leak in addition to the 500).

No frontend code change applies — the frontend already toasts `getErrorMessage(fault, 'Error saving!')` correctly. Per the cross-repo scoping rule, this was labeled `Repo: Backend` in Linear rather than worked here; the actual fix (null guard + proper `BadRequestException`/`NotFoundException` in the `sc-saas-backend` startup-info PATCH controller/service) needs a separate session scoped to that repo.

## Blast radius
None in `sc-saas-frontend`. Backend fix location: `sc-saas-backend` startup-info PATCH controller/service, wherever `.isApproved` is read on a value that isn't guaranteed non-null.

## Confidence note
High confidence on the diagnosis (backend uncaught exception), not yet fixed since it requires work in a different repo.
