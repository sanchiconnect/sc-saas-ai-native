---
id: SAN-475
title: sendOTPFault( Bad Request Exception ) — real validation reason hidden
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-475
sentry:
  - SC-SAAS-FRONTEND-6Q
repos: [frontend]
commit: uncommitted (working tree only, awaiting review)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-475 — sendOTPFault( Bad Request Exception ) — real validation reason hidden

## Root cause
"Bad Request Exception" is a generic, NestJS-auto-derived message, not a real backend error string. When `SendOtpDTO`'s `class-validator` rules reject the OTP-send payload (e.g. invalid email format), NestJS's `HttpException` base class derives `.message` from the exception's *class name* (`BadRequestException` → "Bad Request Exception") whenever the thrown object has no string `.message` of its own — which is exactly the case for a `ValidationPipe` failure (its argument is an array of validation messages).

The real validation reason survives, but in the wrong field: `sc-saas-backend/src/core/exceptions/global-exception.filter.ts:46-49` builds the JSON response as `{ message: exception.message, error: exception.response.message }` — the generic derived text lands in `message`, the actual validation array lands in `error`. `SignUpService.sendOTP()` (frontend) only read `fault.error.message`, i.e. the useless field, so the real reason was dropped from both the Sentry log and the user-facing toast.

Independently confirmed as the same backend behavior in **SAN-448** Part A (`update ElevatorPitch Info( Bad Request Exception )`, a different call site).

## Fix
- `sign-up.service.ts` — `sendOTP()` catchError: `fault?.error?.message` → `fault?.error?.error?.[0] || fault?.error?.message`.
- `program-public-apply-modal.component.ts` — `sendOtpRequest()` error handler: same precedence added ahead of the existing fallback string.

Matches the pattern `sign-up.effect.ts`'s `RegisterFault` action already used for the same backend response shape (`err.error?.error?.[0] || err.error.message`).

## Decision — backend root cause deliberately NOT fixed here
The structural bug is `sc-saas-backend`'s `global-exception.filter.ts` swapping `message`/`error` semantics, affecting every `ValidationPipe` 400 across all 58 backend modules, consumed by frontend + admin (workspace invariant #2). Fixing it there requires `/audit-contract` across all consumers first (some, like `RegisterFault`, already work around today's shape by reading `.error` first — changing the filter without checking every consumer risks breaking that workaround). Out of scope for a single-site frontend ticket; recommend a dedicated backend follow-up if the `X( Bad Request Exception )` pattern keeps recurring (it already has, twice: here and SAN-448).

## Blast radius
Frontend-only change, scoped to the OTP-send call chain already touched by SAN-470. No backend/contract change made.

## Verification
`npx tsc -p tsconfig.app.json --noEmit` clean. No automated test exists for this flow (workspace-wide guardrail).

## Related
See `sc-saas-frontend/src/app/modules/programs/module.spec.md` and `sc-saas-frontend/src/app/modules/auth/module.spec.md` ("Watch out for") for the documented fix. Builds on SAN-470 (same call chain). Same backend symptom as SAN-448 Part A.
