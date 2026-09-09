---
id: SAN-733
title: Commit bce6f8332 "Bug fix" silently reverted 3 Sentry fixes — restore the grid-prefill and financials String() guards
type: bug-fix
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-733
sentry:
  - SC-SAAS-FRONTEND-6T
  - SC-SAAS-FRONTEND-3P
  - SC-SAAS-FRONTEND-7J
repos: [frontend]
commit: none — working tree only, branch ai_native_setup_sandeep (commit withheld per explicit instruction)
created: 2026-09-09
updated: 2026-09-09
---

# SAN-733 — restoring three guards lost to an accidental revert

## Root cause

This is not a new defect. Commit **`bce6f8332`** (Sandy82290, 2026-08-21 10:03:46 +0530), message just *"Bug fix"*, reverted three previously-landed Sentry fixes across three files — net **5 insertions, 38 deletions**. It landed **18 minutes after** the commit it undid (`a6d131bb6`, 09:45:32 the same morning), which points at an accidental revert — a bad merge resolution or a stale-checkout overwrite — rather than a deliberate rollback. `bce6f8332` is in `origin/ai_native_setup`; it never reached `origin/main`.

What it removed:

1. **`form-field.component.ts`** — the whole `asGridSelection()` helper plus both call sites (SAN-441 / `SC-SAAS-FRONTEND-6T`). `textBoxGridSelection` is declared `Record<string, Record<string, string>>` but assigned straight from `participationDetailsOfField`, which is `any`. A submission stored before the field became a `text_input_grid` hands back a plain **string**, so the field holds a string; then `this.textBoxGridSelection?.[row]` evaluates to `undefined` (a string has no such index), the guard passes, and `this.textBoxGridSelection[row] = {}` assigns a property onto a string primitive — a `TypeError` in strict mode. Confirmed from the Sentry frame at `form-field.component.ts:526`, tenant `isgbb-bharatcares.sanchiapp.com`, real value `'ToC Component\nDescription (Quantitative & Qualitative)\nActivities\n…'`.
2. **`financials-details.component.ts`** — the `String()` wrapper and an `isNaN` early-return (SAN-560 / `SC-SAAS-FRONTEND-3P`).
3. **`attend-information.component.ts`** — the `file?.data?.[0]?.name` optional chain (SAN-445 Part B / `SC-SAAS-FRONTEND-4J`).

The cost of this revert went well beyond the three files. SAN-445 had been filed for 3P + 4J, both were fixed, `bce6f8332` undid both, and SAN-445 was then **Canceled** on 2026-08-27 — plausibly because someone found the fixes in git history and assumed they were still applied. `SC-SAAS-FRONTEND-4J` was subsequently re-diagnosed and re-fixed from scratch under SAN-532 on 2026-09-09, unaware a documented fix had existed. The same bug was paid for twice.

**A reverted fix is invisible to `git log --grep` and to `git log -S` on the new code.** The only reliable check is grepping the working tree for the guard itself.

## Fix

Three files, **+38 / −8**. Deliberately *not* a `git revert bce6f8332`: that would also undo the `attend-information` line which `e79b28a28` (SAN-532) has since rewritten differently, producing a conflict.

1. **`form-field.component.ts`** — restored `asGridSelection()` verbatim from `a6d131bb6`, including its full explanatory comment, and both call sites (lines 285, 295; helper at 554). The guard belongs at the **assignment**, not at the throw site: guarding at the throw would leave the string in place and `handleTextboxGrpChange`'s `Object.keys('ToC Component')` would then patch character indices into the form control — corrupting the submitted answer instead of crashing, which is strictly worse. That reasoning is `a6d131bb6`'s and is preserved in the restored comment.

2. **`financials-details.component.ts`** — restored only `const raw = String(val).replaceAll(',', '')`, threading `raw` through the existing `try/catch`.

   **Scope correction against the Linear description.** The ticket said "restore the `String()` + `isNaN` guard verbatim". That would have been wrong. `8b53d449b` (SAN-524, vishalikashyap, 2026-08-26) landed *after* the revert and wrapped `decimalPipe.transform` in a `try/catch` across 8 components. That supersedes the `isNaN` early-return and is arguably better — it still refuses to fabricate a `0`, but keeps the comma-stripping instead of bailing out entirely. So **the NG02100 half of 3P was already fixed in code**, merely undeployed. What the revert genuinely still cost was the `String()` wrapper: `val.replaceAll(',', '')` throws `TypeError: val.replaceAll is not a function` whenever `val` arrives as a number (a numeric patch from `patchFinancialValues` or the API) — a *different* error signature from NG02100, which would surface as its own Sentry group.

3. **`step-financials-info.component.ts`** — same `String()` fix. **Not named in the ticket.** It is the culprit of `SC-SAAS-FRONTEND-7J` (`Error: NG02100`, 16 events / 4 users) and carries the identical defect on `tractionsForm`. Included because fixing one financials component and leaving its sibling broken made no sense.

## Blast radius

Contained to `sc-saas-frontend`. No feature flag, no controller/DTO, no data access — `/trace-flag`, `/audit-contract` and `/check-isolation` are all genuinely n/a rather than skipped.

- `asGridSelection` is re-applying already-shipped, already-reviewed code, so behaviour returns to a known-good state rather than a new one. It is `private` and used only by the two grid prefill sites; `radio_grid` (line 251) and `checkbox_grid` (line 272) take different code paths and are untouched.
- `String()` is a no-op in the normal case — `String('1,50,000') === '1,50,000'`. It only changes the case that previously threw.
- The `try/catch` semantics are unchanged: a non-numeric value still falls through to `formatted = raw`, so nothing renders a fabricated `0` or blank.
- Normal numeric entry (`1,50,000` → `150000` → formatted) is unchanged in all three files.

## Trade-off

`asGridSelection` silently discards a string-valued prefill and substitutes `{}`, so a legacy submission's stored answer is not shown back to the applicant — it appears blank rather than crashing the form. That is the right trade against a crash, but it is data loss from the user's point of view and it is **not** the real fix. `a6d131bb6` raised the underlying question and it has now gone unanswered for roughly three weeks: are these legacy rows from before the field type changed? If so a one-off data migration is the real fix and this guard is only the seatbelt. Recorded as an open decision on SAN-733 rather than invented.

Six further components carry the identical missing-`String()` defect, all latent, all from SAN-524's set: `growth-matrics-form:114`, `individual-investor-edit-form:287`, `investments-details:217`, `organization-details:328`, `create-milestone-form:98`, `ongoing-commitments-list:102`. Deliberately left out of this ticket rather than silently widening a two-file scope to eight; flagged for a separate issue.

## Verification

- `npx tsc -p tsconfig.app.json --noEmit` → exit 0.
- `npx ng build --configuration development` → exit 0, i.e. AOT with `strictTemplates: true` accepts the change; only pre-existing SCSS autoprefixer warnings.
- Guards confirmed present by grep, not by assumption: `asGridSelection` at 285/295/554; `String(val)` in both financials components.
- **No automated test coverage added.** All three components have only Angular CLI stub specs with no providers, which cannot pass as-is. A real regression test for `asGridSelection` needs a `TestBed` harness supplying 8 dependencies (`ToastAlertService`, `FormManagementService`, `DomSanitizer`, `ActivatedRoute` — whose `snapshot.data` is read in the constructor — `NgbModal`, `Store`, `NgxUiLoaderService`, `GlobalService`). Proposed and awaiting a decision; not built unilaterally.
- **Not reproduced in a browser.** Specifically unverified: a real submission whose stored grid value is a string.

## Line-ending hazard worth recording

`financials-details.component.ts` is a **CRLF** file (645 CRLF lines). A first edit made with a naive text-mode write normalised the entire file to LF and produced a **1296-line diff for a 6-line change**. It was reverted and re-applied preserving line endings; the final diff is 9/3 with CRLF intact. Anyone editing this file programmatically must preserve `\r\n` — read and write with newline handling disabled.

## Not deployed

None of this reaches users until `main` ships. `origin/main` tip is `15b195fe2` dated 2026-08-14 — 26 days stale, with `ai_native_setup` **187 commits** ahead. Tracked as SAN-589, still in Backlog. That deploy gap, not this fix, is the reason these Sentry groups keep firing.
