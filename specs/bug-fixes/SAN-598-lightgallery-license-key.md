---
id: SAN-598
title: "lightGallery invalid production license key — 88 users, 130 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-598
sentry:
  - SC-SAAS-FRONTEND-17
repos: [frontend]
commit: sc-saas-frontend@96ea39cb (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-598 — lightGallery invalid production license key

## Root cause
`CommunityFeedSinglePostComponent`'s `settings: Partial<LightGalleryAllSettings>` object never set `licenseKey`, so lightGallery fell back to its own library default `0000-0000-000-0000` — a placeholder the library itself flags via `console.warn` as "not valid for production use" on every gallery open. That `console.warn` is picked up by Sentry's `captureConsoleIntegration({ levels: ['warn'] })` in `main.ts`, which is why this was the highest-volume unresolved issue in the 14-day window (88 users, 130 events) despite not being a functional crash.

## Fix
Added `licenseKey: 'GPLv3'` to the `settings` object in `community-feed-single-post.component.ts:63` — lightGallery's own documented free/open-source license key value, which silences the invalid-key warning without requiring a purchased commercial key.

## Blast radius
None. Purely additive field on an existing settings object; no other gallery behavior changed.

## Verification
`npx tsc --noEmit` clean on the changed file (baseline error count unchanged). Added a unit test asserting `settings.licenseKey` is truthy and not the invalid placeholder.
