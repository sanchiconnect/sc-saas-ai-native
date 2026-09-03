---
id: SAN-584
title: NG02100 DecimalPipe crash on oversized numeric paste
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-584
sentry:
  - SC-SAAS-FRONTEND-BJ
repos: [frontend]
commit: sc-saas-frontend@084ee361 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-584 — DecimalPipe crash on oversized paste

## Root cause
`milestone-details.component.ts`'s `checkValue(event)` (~line 309), used by the "Add Value" milestone-quantitative-update input (`(input)="checkValue($event)"`, bound via `[(ngModel)]="item.valueToUpdate"`), called `this.decimalPipe.transform(val, '1.0-0')` directly, **twice**, with no try/catch — unlike every site the SAN-524 fix patched. Its only guard was `isNaN(val)`, which doesn't catch every crash-inducing input Angular's internal `strToNumber` chokes on (e.g. clearing the field to `''`, or a value parsing to `Infinity`).

## Fix
Wrapped the transform call in the same try/catch pattern as SAN-524 (fallback to raw `val` on failure), and reused a single computed `formatted` value for both the `console.log` and the assignment (previously called `transform` twice, so the first call already threw before the assignment could run).

## Confidence note
**Best-effort.** Audited all 13 files that inject `DecimalPipe` — this was the only live user-input handler still missing a try/catch, a strong mechanistic match. Could not reproduce the exact literal `999999999999XX` failing on this specific line before the fix (it was already blocked by the pre-existing `isNaN` check); the gap closed here covers adjacent inputs (empty string, scientific-notation overflow) that hit the same uncaught-throw code path. Flag for extra scrutiny if this doesn't fully resolve the Sentry group.

## Blast radius
None — additive guard; valid numeric input behaves identically.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-524 (reference fix pattern), SAN-560 (sibling ticket, same class, already fixed by SAN-524 directly).
