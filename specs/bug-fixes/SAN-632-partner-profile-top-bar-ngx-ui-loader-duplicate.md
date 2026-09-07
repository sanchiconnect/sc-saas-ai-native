---
id: SAN-632
title: "[ngx-ui-loader] loaderId \"master\" duplicated — partner-profile-top-bar"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-632
sentry:
  - SC-SAAS-FRONTEND-B1
repos: [frontend]
commit: sc-saas-frontend@84044731 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-632 — partner-profile-top-bar's ngx-ui-loader collision

## Root cause
`partner-profile-top-bar.component.html` has its own bare `<ngx-ui-loader>`, colliding with another "master" loader mounted elsewhere in the partners-edit tree. The exact colliding sibling wasn't pinned with certainty (the two most obvious candidates already had their loaders commented out from a past fix referencing SAN-548/SC-SAAS-FRONTEND-5K).

## Fix
Gave this loader a unique `loaderId` (`"partner-profile-top-bar-loader"`) — safe regardless of which sibling is actually colliding.

## Blast radius
None — same reasoning as SAN-628/630.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
