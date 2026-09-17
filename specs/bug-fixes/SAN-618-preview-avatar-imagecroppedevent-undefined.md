---
id: SAN-618
title: "TypeError: Cannot destructure 'width' of imageCroppedEvent as it is undefined"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-618
sentry:
  - SC-SAAS-FRONTEND-C2
repos: [frontend]
commit: sc-saas-frontend@a66b15af (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-618 — preview-avatar.component.ts saveAvatarImage undefined crop event

## Root cause
`PreviewAvatarComponent.saveAvatarImage()` destructured `this.imageCroppedEvent` unconditionally. If "Save" is clicked before any crop event has fired (`imageCropped()` never called), `imageCroppedEvent` is still undefined, and the destructure throws.

## Fix
Added an early-return guard at the top of `saveAvatarImage()`: `if (!this.imageCroppedEvent) { return; }`. Normal crop-then-save flow is unchanged; Save now no-ops instead of throwing when clicked prematurely.

## Blast radius
None — guard only short-circuits an already-broken call path.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. Proposed a regression test (call `saveAvatarImage()` with `imageCroppedEvent` unset, assert no throw and `activeModal.close` not called) pending go-ahead; not yet written.
