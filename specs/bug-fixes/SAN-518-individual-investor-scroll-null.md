---
id: SAN-518
title: individual-investor-edit-form getBoundingClientRect crash on null scroll target
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-518
sentry:
  - SC-SAAS-FRONTEND-AN
repos: [frontend]
commit: sc-saas-frontend@c540d4b6 (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-518 — individual investor org-info save: null scroll target

## Root cause
`individual-investor-edit-form.component.ts` `onSubmit()` does `document.getElementById('investment-details-section').getBoundingClientRect()` after a successful save. That element id only exists in `investments-details.component.html` — the **organization**-investor flow's own step page — and is never rendered inside this **individual**-investor form's own template, so `getElementById` always returns `null` here. Copy-paste leftover from the org flow; the org flow's own `onSubmit()` doesn't scroll at all, it navigates to the next wizard step instead. The individual flow uses tab-based nav, so there was never a working version of this scroll on this page.

## Fix
Wrapped the scroll block in `if (element) { ... }`, matching how every other investor edit-form's `onSubmit` already behaves (toast only, no scroll).

## Blast radius
None — the scroll block was already non-functional on this page (the target element never exists here); the guard just removes the crash. No behavior removed that users could rely on.

## Verification
`tsc --noEmit` clean. No test suite configured for this repo; type-check + code-path review (confirmed via routing that the target element is never rendered on this page) was the strongest verification available.
