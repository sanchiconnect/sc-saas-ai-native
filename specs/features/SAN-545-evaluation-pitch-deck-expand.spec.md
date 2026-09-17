---
id: SAN-545
title: Add Expand/Fullscreen CTA to Pitch Deck on Application Evaluation screens
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-545/sc-saas-admin-add-expandfullscreen-cta-to-pitch-deck-on-application
owner: aman.k@sanchiconnect.com
repos: [admin]
contracts:
  api: []
  flags: []
  events: []
tenant_scoped: false
depends_on: []
created: 2026-09-01
---

# Add Expand/Fullscreen CTA to Pitch Deck on Application Evaluation screens

## Problem

Follow-up to SAN-544. While confirming the Jury rating screens were the only gap, two more
admin-side ("Evaluation") pitch deck locations were found still missing the SAN-345
Expand/Fullscreen CTA, and the user separately reproduced one of them live:

1. The CFA/individual-application "Round Progress" Kanban board
   (`themes/default/html/application_management/submission-application-management.php`) opens
   an applicant in an iframe at `application-submission-detail/{id}?printable=1&fromApplication=1`.
   That template (`themes/default/html/application-submission-detail.php`) has its own pitch
   deck panel, sourced from `forms_submissions.pitch_document_images` (not `startup_pitch_deck`),
   with no Expand CTA.
2. The accelerator-program Kanban board
   (`themes/default/html/startup-application-management.php`, `.openStartupDetail`) opens a
   startup in an iframe at `startup-detail/{id}?printable=1&fromApplication=1` — user reproduced
   this directly at `http://admin.localhost/startup-application-management/4/testing-dumnmy`.
   `modules/startup-detail.php` treats `printable=1` as a signal to render an entirely different
   template, `themes/default/html/startup-detail/startup-detail-printable.php`, instead of the
   already-fixed `startup-detail.php` — so SAN-345 never reached this path.

## Acceptance criteria

- [x] `application-submission-detail.php` pitch deck panel has the Expand CTA.
- [x] `startup-detail-printable.php`'s `fromApplication` pitch deck branch has the Expand CTA;
      the plain `else` (print/PDF, stacked-images, no-carousel) branch is intentionally untouched.
- [x] Both reuse the identical CSS/HTML/JS shape as SAN-345/SAN-544 (button, modal, prev/next,
      arrow keys, close via X/backdrop/Esc, carousel re-sync on close).
- [ ] Manual click-through by the user — pending for `application-submission-detail.php`;
      the `startup-detail-printable.php` fix was built in direct response to the user's live
      repro and awaits re-test.

## Per-repo plan

### admin
- `themes/default/html/application-submission-detail.php` — added CSS/button/modal (image
  source `$this->pitchDeck['pitch_document_images']`) and JS inside the existing
  `$(document).ready(...)` after `footer.php` renders.
- `themes/default/html/startup-detail/startup-detail-printable.php` — same treatment, scoped to
  the `<?php if ($this->fromApplication) { ?>` carousel branch only (image source
  `$this->record["startup_pitch_deck"]['pitch_document_images']`); the print/PDF `else` branch
  was left alone.
- `modules/stakeholder-detail-pages.spec.md` — updated to document both, and to note this is now
  the 5th copy of the same CSS/HTML/JS in the repo (alongside `startup-detail.php`,
  `round-startups.php`, `round-applications.php`) — flagged as worth extracting into a shared
  partial on the next touch.

## Contracts & invariants

No flags, no API/DTO changes, no new DB access, no new fetch in either file — both overlays reuse
`<img src>` values already rendered into the DOM. Not tenant-scoped. None of the 6 workspace
invariants touched.

## Test plan

- admin: `php -l` on both files (clean). No test framework in this repo — noted, not bootstrapped.
- cross-repo: none — single-repo, admin-only.
- manual: `startup-detail-printable.php` fix built directly from the user's repro
  (`startup-application-management/4/testing-dumnmy`); `application-submission-detail.php`
  still needs a click-through.

## Rollout

Single-repo, no migrations, no flag gating.

## Out of scope

- The print/PDF branch of `startup-detail-printable.php` (no carousel, not a candidate for a
  fullscreen overlay).
- Extracting the now-5x-duplicated CSS/HTML/JS into a shared partial — deferred again, flagged
  more strongly this time.

## Open questions

(none)
