---
id: SAN-728
title: "form-field.component crashes with NG0901 iterating control.value when it's not an array"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-728
sentry:
  - SC-SAAS-FRONTEND-D8
repos: [frontend]
commit: sc-saas-frontend@f463f3ef (branch ai_native_setup_vishali, pushed)
created: 2026-09-09
updated: 2026-09-09
---

# SAN-728 — form-field.component NG0901 on control.value

## Root cause
`form-field.component.html:820`:
```html
<tr *ngFor="let controlFile of control.value">
```
No fallback/guard on `control.value`. Angular's `NgForOf` differ throws `NG0901` (`NO_SUPPORTING_DIFFER_FACTORY`) when the bound value is truthy but not iterable/array-like — so `control.value` held some non-array truthy value at the moment of the crash (e.g. a legacy single-file object instead of a files array).

This component's own TypeScript already anticipates `control.value` can be non-array — `form-field.component.ts:391`:
```ts
if (Array.isArray(this.control.value)) {
  this.uploadedFilesUrl.push(...this.control.value)
  this.control.patchValue(this.uploadedFilesUrl);
} else {
  this.control.patchValue(this.uploadedFilesUrl);
}
```
The upload-handling logic guards against this; the template's file-list loop at line 820 was missed. The neighboring loop two lines below (`*ngFor="let file of (selectedFiles || [])"`, line 862) already uses the `|| []` fallback — but `selectedFiles` is always initialized as an array in this component (`selectedFiles = []`, only ever reassigned to `[]` or mutated via push/pop/splice), so that second loop was never actually at risk. Only `control.value` was.

## Fix
Added a getter reusing the same `Array.isArray` check the component already trusts elsewhere, and bound the template to it:
```ts
get controlValueList() {
  return Array.isArray(this.control.value) ? this.control.value : [];
}
```
```html
<tr *ngFor="let controlFile of controlValueList">
```
No API/DTO/flag/tenant-scoping impact — frontend-only template + one getter.

## Blast radius
`sc-saas-frontend`'s `form-field.component` only (shared dynamic-forms field component — used across multiple form types, but only the file-upload table row is affected).

## Verification
`npx tsc --noEmit -p tsconfig.app.json` — clean, no errors. `git diff --stat` confirms the change is scoped to exactly the two intended files. No existing `.spec.ts` covers this component (workspace-wide test blocker per CLAUDE.md), so no automated regression test was added — manual repro (patch a non-array value onto a file-upload `FormControl`, confirm the table now renders empty instead of throwing) is the substitute verification, still to be done by hand.

Vishali verified locally, then committed and pushed as `sc-saas-frontend@f463f3ef` on `ai_native_setup_vishali`. Linear moved to Done. Sentry SC-SAAS-FRONTEND-D8 marked resolved with a comment referencing the commit. Note this branch is still behind `main` (workspace-wide frontend deploy lag, tracked in SAN-589) — the fix won't reach production until the next deploy.
