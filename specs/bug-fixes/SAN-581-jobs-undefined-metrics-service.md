---
id: SAN-581
title: "Jobs(undefined) — real diagnostics bug per SAN-471, mislabeled module"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-581
sentry:
  - SC-SAAS-FRONTEND-81
repos: [frontend]
commit: sc-saas-frontend@f09f2d8c (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-581 — Jobs(undefined) diagnostics gap

## Root cause
`metrics.service.ts`'s `getMetrics()` (line 47) logged `console.warn(\`Jobs( ${fault.error.message} )\`)` — the stale "Jobs" label is a known copy-paste leftover (SAN-448; this actually routes through `TrackerModule`, not a jobs module — `getMetrics()` is called from `PublicLayoutSidebarComponent.fetchMatrics()`, rendered by `ProtectedLayoutWrapperComponent` on nearly every protected route). SAN-471 (Done) explicitly named this exact `(undefined)` shape as *"a real diagnostics bug and must keep reporting"* — deliberately left un-filtered because an `undefined` message means the error-logging code itself isn't capturing the real error, unlike the `(Invalid access token)` cases SAN-471 did filter.

## Fix
Wired in the existing `httpFaultMessage()` helper (`src/app/shared/utils/http-fault.util.ts` — its own docstring already names this exact ticket as one of the bugs it was built to fix, but it had only been wired into NgRx effects files, never into `core/service/*.ts`): `` fault.error.message `` → `` httpFaultMessage(fault) ``. Toast/redirect logic untouched — only the diagnostic string changed.

Left the other structurally-identical `console.warn(\`Jobs(...)\`)` sites in `metrics.service.ts`/`challenge.service.ts` untouched to keep the change scoped to this ticket (SAN-448 covers the stale label itself separately).

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-471 (identified this as a real bug), SAN-448 (the stale "Jobs" label), SAN-582/SAN-583 (same fix pattern, same helper, different services).
