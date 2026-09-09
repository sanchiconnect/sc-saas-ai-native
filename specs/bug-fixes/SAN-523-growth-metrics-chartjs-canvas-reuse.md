---
id: SAN-523
title: Chart.js "canvas already in use" race condition on growth metrics charts
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-523
sentry:
  - SC-SAAS-FRONTEND-AD
repos: [frontend]
commit: sc-saas-frontend@4625e932 (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-523 — Chart.js canvas-already-in-use race condition

## Root cause
`MatricsChartsComponent.renderChart()` is `async` with an artificial 200ms `sleep` between checking `this.chartRef` and creating the new `Chart` on the canvas. It's called from both `ngAfterViewInit()` (once, on init) and `ngOnChanges()` (whenever the `cumulativeValue` input changes). If invoked twice in quick succession — e.g. the `cumulativeValue` input changing again while an in-flight call is still inside its `sleep`, or `ngOnChanges` firing right after `ngAfterViewInit` — both calls can pass the `if (this.chartRef) destroy()` check before either has (re)assigned `this.chartRef`, and both then call `new Chart(ctx, ...)` on the same canvas element. Chart.js tracks one chart per canvas internally and throws exactly this error on the second registration.

## Fix
Right before creating the new chart, added a check against Chart.js's own canvas registry via the static `Chart.getChart(ctx)` (available since Chart.js v3; this repo is on v4.4.3) and destroy whatever is actually attached to that canvas — not just whatever `this.chartRef` happens to reference at that moment.

## Blast radius
None in the non-overlapping case — `Chart.getChart(ctx)` returns `undefined` when nothing is attached, so the normal single-call render path is unaffected. It only kicks in to prevent double-registration when calls overlap.

## Verification
`tsc --noEmit` clean — confirms `Chart.getChart` is a valid static method on the installed chart.js v4.4.3 typings. No test suite configured for this repo; type-check + code-review was the strongest verification available.
