---
id: SAN-458
title: TypeError — Buffer.from(undefined) in createIcsAttachment (9 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-458
sentry:
  - SC-SAAS-BACKEND-1A
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-458 — Buffer.from(undefined) in createIcsAttachment

## Root cause
`createIcsAttachment()` in `src/core/utils/app.utils.ts` called `Buffer.from(icsEvent.value)` without guarding against `icsEvent.value` being `undefined`. The `ics` library's `createEvent()` returns `{ error, value }` — when generation fails, `value` is `undefined`.

## Fix
Added early-return null guard:
```ts
const icsEvent = createEvent(eventDetail);
if (!icsEvent.value) return null;
```
Callers in `meetings.service.ts` pass `null` to the email service, which sends the meeting email without the calendar attachment — correct graceful degradation.

## Blast radius
None — callers already handle `null` from this function.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
