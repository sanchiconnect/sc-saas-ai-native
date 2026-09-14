---
id: SAN-705
title: "Technology domain required — auto-save bypasses the existing client-side validation guard"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-705
sentry:
  - SC-SAAS-FRONTEND-CN
  - SC-SAAS-FRONTEND-CP
  - SC-SAAS-FRONTEND-D9
  - SC-SAAS-FRONTEND-D4
  - SC-SAAS-FRONTEND-DN
repos: [frontend]
commit: sc-saas-frontend@608d3773 (ai_native_setup_vishali)
created: 2026-09-08
updated: 2026-09-14
---

# SAN-705 — auto-save bypasses the industry/technology validity guard

## Investigation (original, 2026-09-08)
`industry-technology.component.ts` already has `isTechSelected`/`isIndustrySelected` getters feeding a `saveButtonDisabled` getter, and the "Next" step button is `[disabled]="saveButtonDisabled"` — the form cannot be submitted with zero technology domains selected **through that button**. Marked Done/not-a-bug on this basis.

## Reopened 2026-09-14 — the guard doesn't cover the actual trigger

Re-read the component on 2026-09-14 after 3 new Sentry recurrences of the identical message arrived
(`SC-SAAS-FRONTEND-D9`, `-D4`, `-DN`). The original investigation checked the explicit "Next Step" button, but
missed that **SAN-508 removed the visible Save button and replaced it with a 20s dirty-gated auto-save**
(`autoSaveService.register({ isDirty, save: () => this.handleSave(true) })`). That auto-save callback checks
only `isDirty` — never `isFormDataValid` — so it submits incomplete data on every tick while the form is
dirty-but-incomplete, round-tripping to the backend for a 400 each time. The explicit Next-Step path was never
actually broken; the auto-save path always was.

Same unguarded `handleSave()` shape confirmed in the sibling `partner-industry-technology.component.ts`
(`partners-dashboard` module) — `SC-SAAS-FRONTEND-D9` is this component's variant.

## Fix

Guard the auto-save path only, in both components' `handleSave()`, right after the existing early-return:
```ts
if (silent && !this.isFormDataValid) {
  return;
}
```
The explicit Next-Step path (`handleSave(false)`) is untouched — it was already correctly gated by
`saveButtonDisabled`/`isCurrentStepValid` before this call could ever be reached with invalid data.

Files:
- `src/app/modules/startups/pages/edit/industry-technology/industry-technology.component.ts`
- `src/app/modules/partners-dashboard/pages/edit/partner-industry-technology/partner-industry-technology.component.ts`

## Blast radius
None functionally — auto-save silently no-ops for one tick when the step is incomplete (previously it
errored silently too, since `silent` already suppressed the error toast; the user-visible behavior is
identical, minus the wasted 400 round-trip). Explicit save/Next-Step behavior unchanged. No API/flag/tenant-isolation
contract touched.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on both files (only pre-existing, unrelated Jasmine/Karma `.spec.ts`
errors elsewhere in the run). No `.spec.ts` exists for either component. Tests-first blocked workspace-wide (no
`guardian` skill yet) — this is the substitute verification.

## Related
[[SAN-704]] (same class, elevator pitch form — confirmed *actually* fixed: `Validators.required` present on
the elevator-pitch `FormControl`, unaffected by the auto-save gap since that form has no auto-save-only path
issue reproduced).

## Rollout
Committed and pushed as `sc-saas-frontend@608d3773` ("SAN-705: auto-save bypasses industry/technology
validity guard") on `ai_native_setup_vishali`, after Vishali's review and explicit go-ahead. Still subject to
the workspace's known frontend deploy lag — this branch reaching production depends on the next deploy.

## Confidence note
High confidence — root cause and fix verified by direct code read, not inference from the Sentry payload alone.
