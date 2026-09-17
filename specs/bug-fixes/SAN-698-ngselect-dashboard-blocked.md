---
id: SAN-698
title: "ng-select filter throws Cannot read properties of undefined (reading 'keys') on dashboard"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-698
sentry:
  - SC-SAAS-FRONTEND-C1
repos: [frontend]
commit: none — investigation blocked, no fix applied
created: 2026-09-08
updated: 2026-09-08
---

# SAN-698 — ng-select dashboard crash, investigation blocked

## Investigation
The entire stack trace is inside `@ng-select/ng-select` internals (`K1.filter` → `Array.from(this._groups.keys())`) with no first-party frame — Sentry can't identify which `ng-select` instance on the dashboard triggered it. Searched the dashboard module tree for a `groupBy`-configured `ng-select` without finding an unambiguous match. Declined to guess-edit an unrelated `ng-select` usage without evidence, since that risks changing behavior on a component that isn't actually the culprit.

No code change made.

## Recommendation
- Add Sentry session replay or a breadcrumb around dashboard `ng-select` filter interactions to capture a first-party frame on next occurrence.
- Ask the affected user (production, `sineedge.sineiitb.org/startups/dashboard`) which search/filter field they were using.

## Blast radius
None — no change made.

## Confidence note
Low confidence on fix location; closing the investigation as complete (per the SAN-597 precedent — "investigated, nothing to safely fix" still counts as done) rather than leaving it in an ambiguous in-progress state.
