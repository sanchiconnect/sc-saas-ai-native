---
id: SAN-383
title: duplicate ngx-ui-loader "master" registration in founders-list (duplicate of SAN-372)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-383
sentry:
  - SC-SAAS-FRONTEND-66
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-383 — founders-list duplicate ngx-ui-loader

Same root cause and fix as [SAN-372](SAN-372-ngx-ui-loader-duplicate-master.md) — `founders-list.component.html` had two bare `<ngx-ui-loader>` elements in the same template; the second was removed. See that spec for full root cause/fix/verification detail.
