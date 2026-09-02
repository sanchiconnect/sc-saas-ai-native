---
id: SAN-547
title: TypeError reading 'year' of null in AddMeetingModalComponent.calculateSlots on form reset
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-547
sentry:
  - SC-SAAS-FRONTEND-C5
repos: [frontend]
commit: not committed (uncommitted local change on ai_native_setup_vishali working tree — verified by user)
created: 2026-09-02
updated: 2026-09-02
---

# SAN-547 — TypeError reading 'year' of null in calculateSlots (add-meeting-modal)

## Root cause
A native `<form (reset)>` event resets `this.meetingForm`, setting the `date` control to `null` and emitting it through `valueChanges`. The subscription at `add-meeting-modal.component.ts:389-392` calls `recalculateSlots(date)` with `date = null`; when the calendar availability mode matches, that calls `this.calculateSlots(null, duration)`. `calculateSlots` reads `date.month` / `date.year` / `date.day` unconditionally, with no guard for `date` being null, so accessing a property on `null` throws.

Classification: **CODE_ERROR** — same class of defect as `SAN-485` (`.split` on a null `duration` in this same component), fixed there with an early-return guard.

## Fix
Added an early-return guard at the top of `calculateSlots`, matching the existing `SAN-485` pattern in this file:

```ts
if (!date) {
  // no date selected yet (e.g. the form was just reset) — nothing to recalculate
  return;
}
```

No behavior change for the normal case — a date is always required before this method does anything useful; only the null-date case (form just reset) stops throwing.

## Blast radius
Single-repo, single-component: `sc-saas-frontend` — `src/app/shared/common-components/add-meeting-button/add-meeting-modal/add-meeting-modal.component.ts`. `calculateSlots` has exactly one caller (`recalculateSlots`), so no other call site is affected. No API contract, flag, or tenant-scoping impact.

## Verification
`tsc --noEmit` clean for the touched file (workspace-wide run surfaces pre-existing, unrelated `*.spec.ts` Jasmine-typings errors when run outside Angular's Karma config — not caused by this change). User has verified the fix locally. Not yet committed or pushed to git.
