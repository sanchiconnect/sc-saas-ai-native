---
id: SAN-574
title: loginFault Bad Request Exception hides real validation reason — investor org-details edit
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-574
sentry:
  - SC-SAAS-FRONTEND-2G
repos: [frontend]
commit: sc-saas-frontend@2ec27740 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-574 — loginFault Bad Request hides validation reason

## Root cause
`investors.service.ts`'s `patchInvestorOrganizationInfo()` (called by `OrganizationDetailsComponent.onSubmit()`) logged `console.warn(\`loginFault( ${fault.error?.message || fault.message || fault.status} )\`)`, showing the generic "Bad Request Exception" string instead of the backend's real per-field validation message.

## Fix
Traced the SAN-475 reference fix (`sendOTPFault`, commit `5bb0aff4`) and `http-fault.util.ts`'s doc comment: the backend returns validation errors as `{ message: "Bad Request Exception", error: ["<real message>", ...] }`. Changed the warn to `` fault.error?.error?.[0] || fault.error?.message || fault.message || fault.status ``, matching SAN-475's exact precedence. The toast on the same line already used `GlobalService.getErrorMessage()`, which already had equivalent array-first logic — only the diagnostic log needed the fix.

## Blast radius
None — diagnostic string only; toast/UX behavior unchanged.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-475 (`sendOTPFault`, same backend response shape, different call site).
