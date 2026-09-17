---
id: SAN-639
title: "NG02100: TitleCasePipe fed raw poll option object instead of text field"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-639
sentry:
  - SC-SAAS-FRONTEND-A7
repos: [frontend]
commit: sc-saas-frontend@cbff07d3 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-639 — poll-post.component pipes raw option object through titlecase

## Root cause
Both the voting and voted-state templates in `poll-post.component.html` did `{{ option.optionText || (option | titlecase) }}`, piping the entire `option` object through `titlecase` whenever `optionText` was falsy. The `options` domain model (`community-feed.ts`) only declares `optionText` as its text field — there was never a legitimate second field to fall back to, so this fallback branch was an unreachable-in-correct-use bug that threw NG02100 whenever it did trigger.

## Fix
Changed both occurrences to `option.optionText || ''`.

## Blast radius
None — the fallback branch was never producing a meaningful value (there's no second text field on the model); an empty string is the correct degenerate case.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
