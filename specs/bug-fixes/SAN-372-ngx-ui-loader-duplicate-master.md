---
id: SAN-372
title: duplicate ngx-ui-loader "master" registration (startup-all-required-details-form / founders-list)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-372
sentry:
  - SC-SAAS-FRONTEND-2X
  - SC-SAAS-FRONTEND-66
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-372 — duplicate ngx-ui-loader "master" registration

## Root cause
Two independent instances of the same pattern already fixed twice before in this repo (SC-SAAS-FRONTEND-1F, SC-SAAS-FRONTEND-10):
- `startup-all-required-details-form.component.html` declared a bare `<ngx-ui-loader>`, but this component is always rendered as a child of `programs-details-page.component.html`, which already renders its own `<ngx-ui-loader>` — both register the default `"master"` id simultaneously.
- `founders-list.component.html` had **two** bare `<ngx-ui-loader>` elements in the same template (lines 11 and 53), independent of any parent — crashes on every render regardless of host page.

## Fix
Removed the duplicate `<ngx-ui-loader>` element in each file (in `founders-list`, removed the second of the two; the parent's/first instance remains).

## Blast radius
None — 316 `.start()/.stop()` calls repo-wide all target the single shared `"master"` instance; removing only the duplicate template elements doesn't affect any of them. `founders-list.component.ts` itself has zero `ngxLoaderService` calls (uses a local `loader` boolean), so its `<ngx-ui-loader>` markup was dead either way.

## Verification
Template-only change; no type-check applicable. Confirmed via `git diff` that only the intended `<ngx-ui-loader>` lines were touched.
