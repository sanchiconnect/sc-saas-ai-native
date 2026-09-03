---
id: SAN-580
title: loginFault crashes reading 'isRejected' of null — error handler itself failing
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-580
sentry:
  - SC-SAAS-FRONTEND-B5
repos: [frontend]
commit: sc-saas-frontend@044e2ade (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-580 — loginFault crashing on isRejected

## Root cause — not confidently confirmed
Ticket describes the login fault-logger itself crashing while inspecting an `isRejected` field on a null value. Exhaustively checked all 14 `loginFault` call sites across 12 service files, every `.isRejected` occurrence in the repo (all already null-safe via `?.` or a preceding `&&` guard), `auth.effect.ts`, `auth.reducer.ts`/`auth.action.ts`, the HTTP interceptor, `login.component.ts`, all auth-module templates, `profile.service.ts`, and relevant git history — **no unguarded `.isRejected` read adjacent to a `loginFault` log was found.** The exact crash mechanism as described could not be located; it may already be fixed, may be in a code path not yet checked, or may need a live repro.

## Fix (defensive hardening only — best-effort)
Applied the narrowest defensible hardening consistent with the ticket's intent: guarded `fault` itself (not just `fault.error`) in the two actual `loginFault` call sites reachable from the login page, `auth.service.ts`'s `login()` and `verifyOtp()` (lines 63, 99) — `fault.error?.message || fault.message || fault.status` → `fault?.error?.message || fault?.message || fault?.status`. No change to normal-case log output.

**Confidence: best-effort, not confirmed** — this makes the logger marginally safer regardless, but does not certainly address the exact `isRejected` symptom reported in Sentry. Flag for extra scrutiny; may need a live repro to actually confirm/close.

## Blast radius
None — additive null-safety only.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
