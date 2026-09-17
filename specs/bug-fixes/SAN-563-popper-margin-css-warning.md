---
id: SAN-563
title: Popper "margin" CSS warning on startup-information edit page
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-563
sentry:
  - SC-SAAS-FRONTEND-60
repos: [frontend]
commit: n/a — no confident low-risk fix identified
created: 2026-09-03
updated: 2026-09-03
---

# SAN-563 — Popper margin CSS warning

## Finding
`startup-information.component.html` and its sub-components use `ngbTooltip` (ng-bootstrap) in several places — no app-owned custom Popper `popperOptions`/margin config was found. The warning most likely comes from ng-bootstrap's/Popper's own default styling rather than something this codebase explicitly wrote, which means a fix would mean overriding shared tooltip config (`NgbTooltipConfig` or a global Popper options override) — a sitewide change with real risk of shifting every tooltip's positioning across the app for a cosmetic console warning.

This Sentry group is also already assigned to **Mahima Sharma** in Sentry itself, suggesting it may already be owned/in progress outside Linear.

## Re-investigated 2026-09-03
Checked whether a scoped (non-global) fix was possible via `NgbTooltipConfig` at the component level instead of app-wide. Read the installed package directly: `node_modules/@ng-bootstrap/ng-bootstrap/tooltip/tooltip-config.d.ts` — in the installed version (`@ng-bootstrap/ng-bootstrap@^12.1.2`, per `package.json`), `NgbTooltipConfig` exposes only `placement` and `container`. **No Popper-modifier option exists at all in this version** — there is no supported API surface to pass an `offset`/`preventOverflow`-`padding` modifier, scoped or global. Also confirmed (again) no app-owned `.tooltip`/`.popover`/`bs-tooltip` CSS override exists in any `.scss` file — the warning is purely a library default.

The only real fix is upgrading `@ng-bootstrap/ng-bootstrap` past this version. Presented to the user as a decision (package upgrade = real regression risk across every tooltip/popover in the app, vs. leaving a cosmetic warning). **User decision: leave it, do not upgrade.**

## Action required
None, per user decision 2026-09-03. If revisited later: the fix requires upgrading `@ng-bootstrap/ng-bootstrap` (check changelog for breaking changes across tooltip/popover/modal APIs first), not a scoped code change — none is possible at the current version.

## Blast radius
None — no change made.

## Verification
N/A — no code change made.
