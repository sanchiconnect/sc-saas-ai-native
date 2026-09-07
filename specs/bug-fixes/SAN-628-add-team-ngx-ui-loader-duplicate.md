---
id: SAN-628
title: "[ngx-ui-loader] loaderId \"master\" duplicated — add-team nested inside team-list"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-628
sentry:
  - SC-SAAS-FRONTEND-4R
repos: [frontend]
commit: sc-saas-frontend@bce75ef8 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-628 — add-team's ngx-ui-loader collides with team-list's

## Root cause
`team-list.component.html` has its own bare `<ngx-ui-loader>` (default id "master") and always embeds `<app-add-team>` inline (not routed/modal-lazy), whose own template also declares a bare `<ngx-ui-loader>`. Both mount simultaneously, causing a duplicate "master" loaderId registration on every mount.

## Fix
Gave `add-team.component.html`'s loader a unique `loaderId` (`"add-team-loader"`).

## Blast radius
None — `ngx-ui-loader` instances with distinct ids operate independently; no shared loading-state logic depended on both sharing "master".

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
Part of a systemic `ngx-ui-loader` cluster (see SAN-630/632, and this repo's prior piecemeal fixes SAN-548, SAN-139/157/372/383) — a full audit of all bare `<ngx-ui-loader>` instances is recommended as a follow-up rather than continuing to patch one collision at a time.
