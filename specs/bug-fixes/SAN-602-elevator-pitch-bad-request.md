---
id: SAN-602
title: "update ElevatorPitch Info(Bad Request Exception) — 17 users, 22 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-602
sentry:
  - SC-SAAS-FRONTEND-6G
repos: [frontend, backend]
commit: sc-saas-backend@ac4b663f (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-602 — update ElevatorPitch Info(Bad Request Exception)

## Root cause
Frontend investigation first traced this to `pitch-deck.service.ts:35`, which logs `fault.error.message` — that value was always the literal generic string `"Bad Request Exception"`, useless for diagnosing which field failed. Backend investigation found why: NestJS's default `ValidationPipe` exceptionFactory throws `BadRequestException(errors)` where `errors` is an **array** of flattened class-validator constraint messages. `HttpException.initMessage()` only copies `response.message` onto `exception.message` when it's a string — for an array it falls back to the generic `"<ClassName> Exception"` text. `GlobalExceptionFilter` built its `message` response field from that generic `exception.message`, discarding the real per-field detail that was already present in `exception.response.message` (and surfaced separately in the filter's `error` field, which the frontend's user-facing toast correctly reads — only the diagnostic `console.warn` used the useless `.message`).

The `PitchDeckDto` validators themselves were checked and found correct (the XSS-stripping transform runs before `IsNotHTML` as intended) — this was purely an error-serialization gap, not a validation-rule bug.

## Fix
`global-exception.filter.ts`: when `exception.response.message` is an array, `message` in the response body now surfaces the joined array instead of the generic fallback text. `error` is left exactly as before — nothing is exposed that wasn't already present in `error`, and no existing field name/shape is renamed or removed.

## Blast radius
Enriches an existing error-response field's content for validation failures only; does not change any successful-response shape or any field frontend/admin currently parse by name. Grepped `sc-saas-frontend`/`sc-saas-admin` for hardcoded matches on the old generic `"Bad Request Exception"` text — none found (the only match, in `sc-saas-admin/modules/partners/auth/login.php`, is that file building its own unrelated PHP response, not a consumer of this endpoint).

## Verification
Ran the actual backend test suite (not just typecheck): `global-exception.filter.spec.ts` — 4/4 new tests pass, alongside the file's existing coverage.
