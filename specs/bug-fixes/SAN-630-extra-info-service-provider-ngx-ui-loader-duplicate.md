---
id: SAN-630
title: "[ngx-ui-loader] loaderId \"master\" duplicated — extra-info-service-provider has two loaders in one template"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-630
sentry:
  - SC-SAAS-FRONTEND-AZ
  - SC-SAAS-FRONTEND-6P
repos: [frontend]
commit: sc-saas-frontend@8b910f0c (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-630 — extra-info-service-provider self-contained duplicate loader

## Root cause
`extra-info-service-provider.component.html` declared a bare `<ngx-ui-loader>` at both the component root and nested inside the toolbar div — a self-contained duplicate within one template, guaranteed to collide on every mount. SC-SAAS-FRONTEND-6P is the same file/root cause, confirming it also fires in production.

## Fix
Removed the nested loader, keeping only the root one (matches the pattern used in most other templates in this repo).

## Blast radius
None — the removed loader was a pure duplicate; the remaining root-level one already covers the same visual area.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
