---
id: SAN-526
title: ObjectUnsubscribedError in community-feed-stats-count — stale duplicate of SAN-513
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-526
sentry:
  - SC-SAAS-FRONTEND-A9
repos: [frontend]
commit: "n/a — already fixed under SAN-513 (sc-saas-frontend@2fe7ae95, merged to origin/ai_native_setup)"
created: 2026-08-26
updated: 2026-08-26
---

# SAN-526 — ObjectUnsubscribedError in community-feed-stats-count (duplicate)

## Root cause
Not a new bug — this is the exact same defect already fixed under SAN-513 / SC-SAAS-FRONTEND-3S: `CommunityFeedStatsCountComponent.ngOnDestroy()` used to call both `this.destroyed$.complete()` and `this.destroyed$.unsubscribe()`. `.unsubscribe()` on the Subject itself permanently closes it, so the nested `getFeedStats` subscription set up inside the outer `profileData$` callback (`community-feed-stats-count.component.ts:83-86`) threw `ObjectUnsubscribedError` instead of completing harmlessly whenever it fired after teardown.

Checked the current source: `ngOnDestroy()` already contains only `this.destroyed$.complete();`, with an explanatory comment citing SC-SAAS-FRONTEND-3S/SAN-513 — no `.unsubscribe()` remains. Checked git: the fix landed in commit `2fe7ae95` on 2026-08-25 13:46 IST and is already on `origin/ai_native_setup` (the shared branch, not just a personal one). This Sentry event's `First Seen` (2026-08-25 05:52:38, release `b30d7d9a`) is ~8 hours *before* the fix commit and on an older release than events triaged the same day (`aa6d869e`) — a historical occurrence captured before the fix shipped, not reproducible on current code.

## Fix
None needed — already fixed and merged to the shared branch under SAN-513.

## Blast radius
None — no code touched for this ticket.

## Verification
Confirmed by reading current source + git history (commit `2fe7ae95`, present on `origin/ai_native_setup`) rather than a new code change or test run. Sentry issue marked resolved directly (rather than left open pending a fix) since the underlying defect is already shipped.
