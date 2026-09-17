---
id: SAN-701
title: "DecimalPipe crash on ongoing-commitments-list amount input (NG02100)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-701
sentry:
  - SC-SAAS-FRONTEND-BY
repos: [frontend]
commit: none — already fixed, see Investigation
created: 2026-09-08
updated: 2026-09-08
---

# SAN-701 — DecimalPipe NG02100 crash, already fixed (stale production event)

## Investigation
`ongoing-commitments-list.component.ts:99-112` already wraps `decimalPipe.transform()` in a `try/catch` that falls back to the raw value on `NG02100`. Confirmed via `git show 51eb6706:.../ongoing-commitments-list.component.ts` (the exact release tagged on this Sentry event) — it shows the OLD unguarded code, matching Sentry's captured "Most Relevant Frame" line-for-line. Commit `8b53d449` ("SAN-524: DecimalPipe NG02100 crash on non-numeric paste into number fields", merged 2026-08-26, after this event's release `51eb6706`) added the guard present in current source.

This is a stale, pre-fix production event whose release predates the SAN-524 fix.

No code change made.

## Blast radius
None.

## Verification
`git show <release-hash>:<path>` diff against current source; confirmed guard added by `8b53d449` postdates the event's release.

## Related
[[SAN-696]] (same root cause, sibling component `financials-details`, same fix commit).

## Confidence note
High confidence — direct byte-for-byte comparison of the deployed release's source against current source.
