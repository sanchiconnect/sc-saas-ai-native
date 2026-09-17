---
id: SAN-546
title: TypeError reading 'avatar' of undefined in InvestorsSearchCardComponent
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-546
sentry:
  - SC-SAAS-FRONTEND-B3
repos: [frontend]
commit: not committed (uncommitted local change on ai_native_setup_vishali working tree — verified by user)
created: 2026-09-02
updated: 2026-09-02
---

# SAN-546 — TypeError reading 'avatar' of undefined (search/investors)

## Root cause
`investors-search-card.component.ts:80`, inside the `getGlobalSettings` store subscription in `ngOnInit`:

```ts
if (this.investor.user.avatar) {
  this.avtarUrl = res.imgKitUrl + this.investor.user.avatar + '?tr=w-300,h-300,cm-pad_resize';
}
```

`this.investor` (the `@Input() investor: IInvestorSearchResponse`) is present, but its `user` sub-object is `undefined` for at least some investor search results, so `.avatar` throws `TypeError: Cannot read properties of undefined (reading 'avatar')`.

Classification: **CODE_ERROR** — missing null guard on a nested property not always populated by the API response.

## Fix
Optional-chained the access: `this.investor?.user?.avatar` in the `if` check. No behavior change for the populated case; the undefined-`user` case now falls through silently instead of throwing (same as any investor card with no avatar).

## Blast radius
Single-repo, single-component: `sc-saas-frontend` — `src/app/modules/search/pages/investors/components/investors-search-card/investors-search-card.component.ts`. No API contract, flag, or tenant-scoping impact.

## Verification
`tsc --noEmit` clean for the touched file (workspace-wide run surfaces pre-existing, unrelated `*.spec.ts` Jasmine-typings errors when run outside Angular's Karma config — not caused by this change). No test framework change requested. User has verified the fix locally. Not yet committed or pushed to git.
