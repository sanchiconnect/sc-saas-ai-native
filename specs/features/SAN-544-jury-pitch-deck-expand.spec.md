---
id: SAN-544
title: Add Expand/Fullscreen CTA to Pitch Deck on Jury Rating/Feedback screens
type: feature
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-544/sc-saas-admin-add-expandfullscreen-cta-to-pitch-deck-on-jury
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

# Add Expand/Fullscreen CTA to Pitch Deck on Jury Rating/Feedback screens

## Problem

SAN-345/SAN-346 added an Expand/Fullscreen CTA to the pitch deck viewer on the Startup
Detail "Information" tab (`themes/default/html/startup-detail/startup-detail.php`). The
same pitch deck carousel is also shown on the two Jury rating/feedback screens, directly
above the rating + free-text feedback form, but neither had the CTA — jury members could
only view the deck at small carousel size, with no way to inspect a slide up close before
scoring. The "ecosystem" admin view (Ecosystem → Startups) was checked and is not a
separate gap — it routes through the same `startup-detail.php` template, so SAN-345/346
already cover it.

## Acceptance criteria

- [x] `themes/default/html/jury/round-startups.php` pitch deck panel has an Expand button
      that opens the same fullscreen modal pattern as `startup-detail.php`.
- [x] `themes/default/html/jury/round-applications.php` pitch deck panel has the same.
- [x] Modal supports prev/next buttons, Left/Right arrow-key navigation, and an "x / y"
      slide counter.
- [x] Modal closes via X button, backdrop click, and Esc (native Bootstrap 4 modal
      behavior), and the embedded carousel below stays synced to the slide the modal was
      closed on.
- [x] No changes to the rating/feedback form (score inputs, `data[comments]` textarea)
      that sits below the pitch deck panel on either screen.
- [x] Manual click-through as a logged-in jury user on both screens — verified locally
      (XAMPP, `admin.localhost`) 2026-09-01.

## Per-repo plan

### admin
- `themes/default/html/jury/round-startups.php` — added the `#pitchDeckExpandModal` CSS
  block (own `<style>` tag, inserted after the file's existing second `<style>` block),
  the `#expandPitchDeck` button in the pitch deck card header (beside the existing,
  already-commented-out Download Deck link), the modal markup (image source:
  `$this->record["startup_pitch_deck"]['pitch_document_images']`), and the JS block
  (state sync / keyboard nav / open-close handlers) inside the file's existing
  `$(document).ready(...)` block, placed after footer.php is rendered so jQuery is
  already loaded.
- `themes/default/html/jury/round-applications.php` — identical treatment; image source
  is `$this->pitchDeck['pitch_document_images']` instead.
- `modules/jury/module.spec.md` and `modules/stakeholder-detail-pages.spec.md` — updated
  to cross-reference this change.

## Contracts & invariants

No flags, no API/DTO changes, no new DB access, no new fetch — the overlay reuses the
`<img src>` values already rendered into the DOM for the existing embedded carousel on
each page, exactly as SAN-345 did. Not tenant-scoped (pure client-side UI). None of the 6
workspace invariants are touched.

## Test plan

- admin: `php -l` on both touched files (clean). No test framework exists in this repo
  (per repo CLAUDE.md) — noting the gap rather than bootstrapping one for a UI-only
  change.
- cross-repo: none — single-repo, admin-only change.
- manual: pending — user to log in as jury locally (XAMPP, `http://admin.localhost/`)
  and click through both rating screens.

## Rollout

Single-repo (`sc-saas-admin`), no migrations, no flag gating needed — ships live to
whichever jury screen the admin build already serves. No deploy sequencing concerns.

## Out of scope

- `startup-detail.php` itself was not touched (already shipped, working — SAN-345/346).
- De-duplicating the now-3x-copied CSS/HTML/JS into a shared partial — considered and
  deferred (see comment on SAN-544); flagged for a future pass if a 4th call site shows
  up.
- Admin event logging (open/close) — the reference implementation (SAN-345) doesn't have
  it either; parity, not a gap introduced here.

## Open questions

(none — this is a direct replication of an already-approved, already-shipped pattern)
