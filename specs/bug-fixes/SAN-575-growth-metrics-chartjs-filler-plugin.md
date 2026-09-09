---
id: SAN-575
title: Chart.js 'fill' used without Filler plugin registered — growth-metrics charts
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-575
sentry:
  - SC-SAAS-FRONTEND-AC
repos: [frontend]
commit: sc-saas-frontend@27ce3595 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-575 — Chart.js Filler plugin not registered

## Root cause
`matrics-charts.component.ts` uses `fill: true` in a chart config without the `Filler` plugin registered in its `Chart.register(...)` call — the same registration call site touched by the SAN-523 canvas-reuse fix on this exact page.

## Fix
Added `Filler` to the `chart.js` import and to the existing `Chart.register(...)` call (same call site as SAN-523), rather than creating a second registration elsewhere. Verified `Filler` is exported by the installed `chart.js@4.4.3`.

## Blast radius
None — registering an additional plugin doesn't change existing chart behavior, only stops the console warning and lets `fill` render correctly if it wasn't already.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-523 (Chart.js canvas-reuse fix, same file/registration call).
