---
id: SAN-377
title: form-field sanitizeInput crash on non-string values (duplicate of SAN-364)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-377
sentry:
  - SC-SAAS-FRONTEND-8C
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-377 — form-field sanitizeInput TypeError

Same root cause and fix as [SAN-364](SAN-364-sanitize-input-non-string.md) — `form-field.component.ts`'s `sanitizeInput` now guards on `typeof value === 'string'`. See that spec for full root cause/fix/verification detail.
