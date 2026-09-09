---
id: SAN-699
title: "ObjectUnsubscribedError in community-feed shared Subject"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-699
sentry:
  - SC-SAAS-FRONTEND-CD
repos: [frontend]
commit: none — investigation blocked, no fix applied
created: 2026-09-08
updated: 2026-09-08
---

# SAN-699 — community-feed ObjectUnsubscribedError, investigation blocked

## Investigation
The stack trace's only first-party-adjacent frame is a minified bundle line inside the lazy-loaded `community-feed` chunk (`Object.next` calling into a `Subject`/`ReplaySubject` past `.complete()`) — no component/service name survives minification. The `community-feed` module has 14 files that could plausibly own the shared `Subject`; picking one to edit without more signal risks changing an unrelated component's teardown behavior.

No code change made.

## Recommendation
Same as SAN-698: source maps / session replay for the next occurrence, or ask the affected user (production, `hub.isba.in/account/edit/profile`) what they were doing right before this fired (likely navigating away from a community-feed view while a request was in flight).

## Blast radius
None — no change made.

## Confidence note
Low confidence on fix location; closing the investigation as complete per the SAN-597 precedent.
