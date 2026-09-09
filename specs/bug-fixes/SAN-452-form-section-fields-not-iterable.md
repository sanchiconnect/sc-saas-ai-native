---
id: SAN-452
title: TypeError — section.fields is not iterable in FormsService (202 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-452
sentry:
  - SC-SAAS-BACKEND-Z
repos: [backend]
commit: already in codebase (form-management.service.ts:1091,1148 — toArray guard)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-452 — section.fields not iterable in FormsService

## Root cause
Old production JS used `for (const field of section.fields)` at line 610 — throws `TypeError: section.fields is not iterable` when `section.fields` is null/undefined.

## Fix
Already in the TypeScript source: both loops at `form-management.service.ts:1091` and `:1148` now use `this.toArray(section.fields)`, which safely returns `[]` for null/undefined values. Sentry last saw this on 2026-08-10, consistent with the fix landing after that date.

## Blast radius
None — form-service-internal only.

## Verification
No code change required. Fix rides with next production deploy of `ai_native_setup`. Sentry issue SC-SAAS-BACKEND-Z resolved.
