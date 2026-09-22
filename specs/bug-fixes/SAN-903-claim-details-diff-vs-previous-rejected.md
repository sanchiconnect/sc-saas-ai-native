---
id: SAN-903
title: "Claim Details — show diff vs. previous rejected claim on resubmission"
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-903
sentry: []
repos: [admin]
commit: <not committed — user reviewing locally first> (branch to be confirmed)
created: 2026-09-22
updated: 2026-09-22
---

# SAN-903 — Claim Details diff on resubmission

## Requirement
When a startup's claim is rejected and they resubmit, the new claim's "Claim Details" modal should show what actually changed vs. the immediately-preceding rejected claim — Beneficiary Details field-by-field, and Documents — not just the new claim's data in isolation.

## Blocker found + resolved (see [SAN-904](https://linear.app/sanchiconnect/issue/SAN-904), `sc-saas-backend`, companion ticket)
Beneficiary Details was one row per startup, upserted in place — a rejected claim's original values were already gone by the time a resubmission existed to diff against. SAN-904 snapshots the 11 Beneficiary Details fields onto `operational_cost_claims` itself at submit time and has `getClaimDetails()` return the previous rejected claim (with its own snapshot + documents) as `previousRejectedClaim`. This ticket is the admin-side rendering of that data — it depends on SAN-904 having landed.

## Fix
`sc-saas-admin`'s proxy (`modules/operation_cost/claims.php`'s `details` route) needed **no change** — it's a pure pass-through of the backend's `data` object, so the new `previousRejectedClaim` field flows through automatically.

`themes/default/html/operation_cost/claims.php`:
1. New card "Changes Since Last Rejected Claim" in the Claim Details modal's Beneficiary Details column, `display:none` by default — only shown when `data.previousRejectedClaim` is present.
2. `renderClaimDiff(currentBankDetails, currentDocuments, previous)` (new JS function):
   - Shows the previous claim's rejection date + reason as context.
   - If `previous.bankDetails` is `null` (pre-SAN-904 claim, no snapshot), shows "prior data unavailable" instead of a false/empty diff.
   - Otherwise, walks the same 11 fields the Beneficiary Details card itself renders (same `{label, key}` list, same order — so the diff reads as a direct companion, not a re-derived list that could drift), shows `old → new` only for fields that actually differ, and "No Beneficiary Details changed" when none did.
   - Documents diff: compares `originalFileName` per `documentType` between the two claims (added/removed/changed) — filename is the only practical comparison signal available client-side, since no raw storage key is ever sent to the browser and the signed `url` is freshly re-signed on every load (can't be compared directly).
3. Wired into the existing `loadClaimDetails()`/`resetDetailsModal()` flow: reset hides/clears the new card; `renderClaimDiff()` runs after the current claim's own Beneficiary Details and Documents are already populated (it compares against them).

## Design notes / limitations (confirmed acceptable with the user before building, RE-CONFIRMED 2026-09-22 after seeing it live)
- Diff only works going forward from SAN-904 landing — existing already-rejected claims have no snapshot and show "prior data unavailable", not a real diff. Cannot be retroactively recovered (the original data was already overwritten before this fix existed). **User's exact words after reviewing the actual behavior**: "'prior data unavailable' is expected because no snapshot exists. Please keep the current behavior as it is." This is confirmed-correct, working-as-intended — do not "fix" it in a later session by trying to backfill or hide it.
- Documents diff is by filename, not byte-for-byte content — a re-upload of a file with the identical name would not show as "changed". Judged acceptable; over-engineering a content-hash comparison wasn't asked for and the backend doesn't currently store one.

## Blast radius
Only the Claim Details modal (one card + its JS) and the diff function itself. No change to the claims list/table, filters, counters (SAN-902), bulk actions, or the Reject/Sanction action bar.

## Verification
No PHP linter available locally — reviewed the diff by hand: HTML tags balance, JS braces/parens balance, reuses existing CSS classes (`ocr-detail-card`, `ocr-detail-documents`, `ocr-doc-label`) rather than introducing new ones. No test framework exists in this repo. Depends on SAN-904's backend response shape — verified against that ticket's actual `getClaimDetails()` return shape (`previousRejectedClaim.bankDetails`/`.documents`/`.rejectedAt`/`.rejectionReason`), not guessed. Not committed/pushed — user reviewing locally first.
