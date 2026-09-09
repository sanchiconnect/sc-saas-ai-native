---
id: SAN-464
title: TypeError — null.map on allowedShortCodes in WhatsappService (3 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-464
sentry:
  - SC-SAAS-BACKEND-17
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-464 — null.map on allowedShortCodes in WhatsappService

## Root cause
`sendMessages()` in `whatsapp.service.ts:50` cast `template.allowedShortCodes` directly to `string[]` without guarding against `null`. When a WhatsApp template in the DB has no short codes configured, the field is `null`, and the subsequent `.map()` call crashes.

## Fix
Added `?? []` null-coalescing:
```ts
// Before
const allowedShortCodes = template.allowedShortCodes as string[];
// After
const allowedShortCodes = (template.allowedShortCodes ?? []) as string[];
```

## Blast radius
None — templates with no `allowedShortCodes` now process cleanly (empty array = no short code filtering).

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
