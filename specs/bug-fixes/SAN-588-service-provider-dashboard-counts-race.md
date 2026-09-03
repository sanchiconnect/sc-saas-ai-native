---
id: SAN-588
title: Cannot access 'pendingConnectionCount', counts is undefined — service-provider-dashboard race condition
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-588
sentry:
  - SC-SAAS-FRONTEND-C8
repos: [frontend]
commit: sc-saas-frontend@fa4471fd (branch ai_native_setup_vishali, pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-588 — service-provider-dashboard counts race condition

## Root cause
Sentry's culprit label (`dashboard-v2.component`, from the webpack lazy-chunk name) was misleading — the actual crash site is not in `dashboard-v2` at all. Verified by grepping the whole repo for unguarded `counts.pendingConnectionCount` dot-access:

- `dashboard-v2.component.html` is already fully guarded (`counts?.[count.countKey]`).
- `connection-count.component.html` has the same unguarded pattern, but that component (`app-connection-count`) is dead code — its selector is never referenced in any template.
- The real, reachable site is `service-provider-dashboard.component.ts`:
  - Line 61: `counts: NotificationsCount | undefined;` — no default value.
  - Lines 92-96: `getNotificationsCount` selector subscription sets `this.counts = res`, guarded by `if (res)`.
  - Lines 98-129: a **separate, unrelated** `getBrandDetails` selector subscription builds `this.countBoxes`, reading `this.counts.pendingConnectionCount` / `this.counts.unreadMessageCount` with no guard at all.

These are two independent async NgRx selector subscriptions with no ordering guarantee. `getBrandDetails` (tenant-level bootstrap data) plausibly resolves before `getNotificationsCount` (a per-user API call), so `this.counts` is still `undefined` when `countBoxes` is built. The dashboard-v2 chunk attribution is a webpack bundling artifact, not evidence the bug lives there.

## Fix
Added `?.` on both reads: `this.counts?.pendingConnectionCount`, `this.counts?.unreadMessageCount` — matching the optional-chaining convention already used for this exact data shape elsewhere in the codebase (`dashboard-v2.component.html`, `protected-layout-header.component.html`).

## Blast radius
None — values simply render as `undefined` (falsy) until `counts` loads, then update normally once `getNotificationsCount` fires. No change to success-path behavior.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file — only pre-existing `.spec.ts` test-typings noise elsewhere (same baseline as the rest of this project). No automated test suite exists for this repo (workspace-wide `guardian`-skill blocker), so this is the strongest available verification.

## Related
Same general "counts race" bug class as SAN-483 (dashboard-v2 family) and SAN-512 (connection-v4) — this specific file/site was not covered by either of those earlier fixes, despite being the same anti-pattern.
