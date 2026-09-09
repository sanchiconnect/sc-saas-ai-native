---
id: SAN-559
title: Cannot read 'maintenance_on_title' of null — maintenance-mode check
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-559
sentry:
  - SC-SAAS-FRONTEND-C7
repos: [frontend]
commit: 7d41a82b (branch ai_native_setup_vishali) — pre-existing, verified only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-559 — maintenance_on_title null read

## Root cause
`app.component.html` previously had `{{brandDetails.maintenance_mode.maintenance_on_title | titlecase}}` with no guard on `brandDetails`/`maintenance_mode`. This was the crash site matching the Sentry culprit `W(main)`.

## Finding — already fixed
Commit `7d41a82b` ("feat: branded maintenance page component", confirmed an ancestor of current HEAD, later polished by `c0d97aff`/`a1870497`) replaced the whole inline card with `<app-maintenance-page>` — a fully static component with no binding to `brandDetails`/`maintenance_mode` at all. Grepped the entire `src` tree: `maintenance_on_title`/`maintenance_on`/`maintenanceMode` now appear nowhere except the field's type declaration in `brand.model.ts`. The vulnerable read no longer exists.

No new change made in this session — verified only.

## Blast radius
None — no new change.

## Verification
Grep confirmed no remaining read site for the removed field.
