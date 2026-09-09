---
id: SAN-704
title: "Elevator pitch required — no client-side validation before submit (Sentry noise)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-704
sentry:
  - SC-SAAS-FRONTEND-CP
repos: [frontend]
commit: none — already fixed, see Investigation
created: 2026-09-08
updated: 2026-09-08
---

# SAN-704 — elevator pitch required, already client-side guarded

## Investigation
`elevator-pitch-form.component.ts`'s `pitchForm.elevatorPitch` control already has `Validators.required`, and the submit button in the template already has `[disabled]="!pitchForm.valid || loader"` (`elevator-pitch-form.component.html:59-62`). The form cannot be submitted empty through the UI today.

Sentry event carried `environment: local`, `release: sc-saas-frontend@unknown` — no release tag, consistent with a local/stale test session rather than a reproducible gap in current code.

No code change made.

## Blast radius
None.

## Verification
Read `elevator-pitch-form.component.ts` and its template; confirmed both the form validator and the disabled-button binding are present.

## Related
[[SAN-705]] (same class: backend validation message correctly surfaced but should be pre-empted client-side; that one is also already guarded).

## Confidence note
Medium-high confidence — the guard is present and correct, but an edge case (e.g. keyboard Enter bypassing the disabled button, or the "local"/"unknown" event coming from a genuinely different, older checkout) can't be fully ruled out without a live repro.
