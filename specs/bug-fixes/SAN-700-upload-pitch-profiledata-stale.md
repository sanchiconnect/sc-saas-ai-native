---
id: SAN-700
title: "UploadPitchComponent crashes on undefined profileData when opening PowerPitch connect modal"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-700
sentry:
  - SC-SAAS-FRONTEND-C3
repos: [frontend]
commit: none — already fixed, see Investigation
created: 2026-09-08
updated: 2026-09-08
---

# SAN-700 — UploadPitchComponent null crash, already fixed as SAN-590 (duplicate)

## Investigation
`upload-pitch.component.ts:76-77` already uses `this.profileData?.name` / `this.profileData?.email` (optional chaining). `git log` shows commit `d5c72753` ("SAN-590: Cannot read properties of null (reading 'startupId') — UploadPitchComponent.handlePowerPitchConnect race, SC-SAAS-FRONTEND-CB") added exactly this guard — same component, same method, same underlying race (`profileData` not loaded before the connect-modal click handler reads it).

Sentry's captured frame (`name: this.profileData.name,` — no `?.`) matches the pre-SAN-590 code, not current source. This is the same defect already fixed and tracked as SC-SAAS-FRONTEND-CB / SAN-590.

No code change made.

## Blast radius
None.

## Verification
`git log --follow` + `git show` diff on `upload-pitch.component.ts`; confirmed `d5c72753` added the exact guard.

## Related
Duplicate of SC-SAAS-FRONTEND-CB (SAN-590, already shipped).

## Confidence note
High confidence.
