---
id: SAN-467
title: .webp image format rejected by imageFileFilter (2 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-467
sentry:
  - SC-SAAS-BACKEND-1P
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-467 — .webp image format rejected by imageFileFilter

## Root cause
`imageFileFilter` in `src/core/utils/image-filter.ts` only accepted `.png`, `.jpg`, `.jpeg`. Modern browsers (Chrome, Edge) increasingly produce `.webp` for screenshots and uploads. Both Sentry events were from `environment: local`.

## Fix
Added `.webp` to the accepted extension list at line 9:
```ts
// Before
if (ext !== '.png' && ext !== '.jpg' && ext !== '.jpeg')
// After
if (ext !== '.png' && ext !== '.jpg' && ext !== '.jpeg' && ext !== '.webp')
```
Error message updated to include `webp`.

## Blast radius
Additive only — `.webp` uploads now proceed instead of being rejected. No existing accepted format affected. This filter is applied globally to all logo/image upload endpoints in the backend.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
