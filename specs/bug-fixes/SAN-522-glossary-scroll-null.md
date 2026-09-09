---
id: SAN-522
title: GlossarySectionComponent getBoundingClientRect crash on empty letter click
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-522
sentry:
  - SC-SAAS-FRONTEND-AE
repos: [frontend]
commit: sc-saas-frontend@ae465a34 (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-522 — null getBoundingClientRect crash clicking empty glossary letter

## Root cause
Same shape as SAN-518: `GlossarySectionComponent.onClickAlphabet()` calls `document.getElementById(alphabet + 'Sections').getBoundingClientRect()` with no null check. The `{alphabet}Sections` id lives on `app-glossary-card`'s root element, but that card is only rendered for letters whose index made it into `firstColIndex`/`secondColIndex`/`thirdColIndex` — `setColumnIndexes()` deliberately skips any letter with an empty glossary bucket. Meanwhile the clickable A–Z letter bar renders a button for every letter regardless of whether it has entries. Clicking a letter with zero glossary entries finds no matching card in the DOM, so `getElementById` returns `null` and the scroll throws.

## Fix
Added `if (!element) { return; }` before the `getBoundingClientRect()` call, identical to the SAN-518 fix pattern.

## Blast radius
None — no behavior change for letters that do have terms (they still scroll exactly as before); clicking an empty letter becomes a silent no-op instead of a crash (there's nothing to scroll to anyway).

## Verification
`tsc --noEmit` clean; diff is 3 lines. No test suite configured for this repo; type-check + code-path review was the strongest verification available.
