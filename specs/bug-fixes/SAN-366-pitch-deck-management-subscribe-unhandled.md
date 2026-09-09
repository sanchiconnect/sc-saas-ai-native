---
id: SAN-366
title: pitch-deck-management subscribe re-throws already-toasted 400 to Sentry; underlying PowerPitchDeck contract gap left open
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-366
sentry:
  - SC-SAAS-FRONTEND-2J
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-366 — pitch-deck-management setDefaultPitchType unhandled error

## Root cause
Actual error: `HttpErrorResponse` — `PATCH .../startups/pitch-deck/default/pitch-type → 400 Bad Request`. `setPowerPitchUrl`/`setDefaultPitchType` call `.subscribe()` with no error callback; `tap`'s error branch only stops the loader, so RxJS re-throws the already-toasted error to Angular's global ErrorHandler/Sentry.

**Real underlying cause of the 400 (not fixed here — see Decision):** the frontend's `PitchType` enum has 3 values (`power_pitch`, `power_pitch_deck`, `upload_pitch` — `cometchat-pro-angular-ui-kit/.../enums.ts:294-297`); the backend's `PitchType` enum only has 2 (`power_pitch`, `upload_pitch` — `core/constants/enum.ts:360-363`), and `pitch_type` is a strict MySQL ENUM column. Clicking "Set as Default" on the Power Pitch Deck (Loom) tab sends `pitchType: 'power_pitch_deck'`, which the backend DTO's `@IsEnum` validation rejects with 400 before any service logic runs — matches all 369 affected users exactly. This entity has no `powerPitchDeckUrl` column at all (Loom URLs live on separate per-document-type fields), and the module's own spec notes PowerPitchDeck has no working "record/set a new Loom video" UI yet.

## Fix
Added `{ next: () => {}, error: () => {} }` to both `.subscribe()` calls in `pitch-deck-management.component.ts`. Confirmed both underlying service methods already show a toast via their own `catchError` before re-throwing, so this only stops the duplicate unhandled-error report — no change to user-facing behavior.

## Decision
The actual contract gap (PowerPitchDeck has no backend support) is a real, separate bug requiring a product decision — hide the "Set as Default" button on that tab (frontend-only, safe) vs. build full backend support (enum + DB migration + service logic, needs a decision on URL storage model). Left open per product decision, 2026-08-19.

## Blast radius
None on the applied fix — purely additive error handling.

## Verification
`tsc --noEmit` clean.
