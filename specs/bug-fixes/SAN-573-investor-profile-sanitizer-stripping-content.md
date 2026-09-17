---
id: SAN-573
title: Angular sanitizer stripping content from investor public profile — possible data loss
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-573
sentry:
  - SC-SAAS-FRONTEND-46
repos: [frontend]
commit: n/a — needs live-content inspection before any fix
created: 2026-09-03
updated: 2026-09-03
---

# SAN-573 — sanitizer stripping content on investor profile

## Finding
`investor-public-profile-v2.component.html` binds `profileData?.aboutUs`/`keyInvestments` directly via `[innerHTML]` with no pipe — Angular's built-in `DomSanitizer` runs automatically on any `[innerHTML]` binding and is what's emitting this warning.

**Important — a plausible-looking fix was checked and rejected:** the sibling v1 profile page (`investor-public-profile.component.html`) and `investor-compare-card.component.html` both bind the *same* `aboutUs` field via `[innerHTML]="profileData?.aboutUs | decodeHtmlString"`. Read `pipe.decodeHtmlString.ts`'s implementation before assuming this is the fix to replicate: `decodeHtmlString` sets `tempElement.innerHTML = value` then returns `tempElement.innerText` — i.e. it strips **all** HTML formatting down to plain text. Applying it to v2 would not fix "some content stripped," it would silently flatten all rich-text formatting on every profile, every time — a larger, more silent form of content loss than what Angular's targeted sanitizer warning describes. **Do not apply this pipe as a fix for this ticket.**

The real fix requires inspecting what `aboutUs`/`keyInvestments` actually contains for the specific reported profile (`tech.thub.sanchidev.in/investors/profile/.../aladdinn`) to determine whether Angular is correctly stripping malicious/malformed markup (close as working-as-intended) or incorrectly stripping legitimate formatting the user's rich-text editor produced (needs a `bypassSecurityTrustHtml`-based fix scoped to trusted, already-sanitized-on-save content only).

## Re-investigated 2026-09-03
Re-confirmed no safe code fix is possible without seeing the actual live HTML content for the reported profile — deciding between "close as working-as-intended" and "scope a `bypassSecurityTrustHtml` fix" requires that data, which isn't available from static code. Conclusion stands.

## Action required
Inspect the live `aboutUs`/`keyInvestments` HTML for the specific reported profile before deciding: close as working-as-intended, or scope a `bypassSecurityTrustHtml` fix.

## Blast radius
None — no change made.

## Verification
N/A — no code change made.
