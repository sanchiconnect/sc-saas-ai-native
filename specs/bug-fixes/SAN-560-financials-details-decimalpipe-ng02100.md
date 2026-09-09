---
id: SAN-560
title: NG02100 DecimalPipe crash on financials-details step
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-560
sentry:
  - SC-SAAS-FRONTEND-3P
repos: [frontend]
commit: 8b53d449 (branch ai_native_setup_vishali) — pre-existing (SAN-524), verified only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-560 — DecimalPipe NG02100 in financials-details.component

## Root cause
Same class as SAN-524: `DecimalPipe.transform(val, '1.0-0')` throwing `NG02100` on non-numeric/oversized pasted input inside a numeric `FormControl`'s `valueChanges` handler.

## Finding — already fixed
Commit `8b53d449` (the SAN-524 fix) touched 8 files in one pass, including `financials-details.component.ts` — lines 218-231 already wrap the `decimalPipe.transform` call in a `try { ... } catch { formatted = val }` guard, falling back to the raw string instead of throwing. Its template has no separate `| number`/`| currency` pipe usage. Confirmed `8b53d449` is an ancestor of current HEAD via `git merge-base --is-ancestor`, and no later commit touched this file.

No new change made in this session — verified only.

## Blast radius
None — no new change.

## Verification
`git log`/`git merge-base` confirmed the guard is present and unmodified since.
