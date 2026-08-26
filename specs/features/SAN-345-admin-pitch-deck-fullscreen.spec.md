---
id: SAN-345
title: "Add Expand/Fullscreen CTA to Admin Panel Pitch Deck Viewer"
type: feature
status: approved
linear: https://linear.app/sanchiconnect/project/san-345-add-expandfullscreen-cta-to-admin-panel-pitch-deck-viewer-4c6e600cc152
owner: aman.k@sanchiconnect.com
repos: [admin]
contracts:
  api: []
  flags: []
  events: []
tenant_scoped: false
depends_on: []
created: 2026-08-26
---

# Add Expand/Fullscreen CTA to Admin Panel Pitch Deck Viewer

## Problem

Admins reviewing a startup's pitch deck (Admin Panel → Startups → startup-detail → Information tab
→ Pitch Deck panel, `themes/default/html/startup-detail/startup-detail.php`) can only view it in a
small embedded Bootstrap carousel (~360px card body) or by clicking **Download Deck**, which opens
the original PDF/PPT-converted images in a new tab. There is no way to view a slide at a larger,
readable size without leaving the page. This forces repeated downloads just to review decks across
many startups.

This spec adds an **Expand** CTA beside the existing **Download Deck** button that opens the
currently active slide in a fullscreen overlay — closable via Close (X), a click on the backdrop, or
Esc — reusing the same already-loaded slide images, no new network fetch.

Note: this is a redo. A prior attempt at this spec/implementation existed under this same Linear
project (SAN-345/SAN-346) but its branch was discarded before merging and the spec file was lost;
SAN-345 had been incorrectly marked Done in Linear despite no code landing. Both are corrected as of
this spec (SAN-345 → In Progress, SAN-346 assignee → Aman kabra).

## Acceptance criteria

- [ ] **FR-1**: An "Expand" CTA (icon + label) is added immediately beside the existing "Download
      Deck" button in the Pitch Deck panel header (`startup-detail.php` ~line 1020-1024), same
      height/alignment (`btn` group), only rendered when Download Deck is also rendered (i.e. inside
      the existing `if (isset(...['pitch_document_images']) && count(...) > 0)` block).
- [ ] **FR-2**: Clicking Expand opens a fullscreen Bootstrap modal overlay (dimmed backdrop) showing
      the currently active carousel slide, scaled to fit the viewport while preserving aspect ratio.
- [ ] **FR-3**: The overlay has prev/next controls, a numbered slide badge (parity with the embedded
      carousel's `<ol class="carousel-indicators">`), and a page-position indicator (e.g. "3 / 8").
- [ ] **FR-4**: Overlay closes via: (a) a visible Close (X) control, (b) click on the dimmed backdrop
      outside the image, (c) Esc key — all native Bootstrap 4 modal behavior (`data-backdrop` /
      `data-keyboard` default to `true`; no custom Esc listener needed). All three return the panel to
      its original embedded size instantly — no page reload, no scroll-position jump.
- [ ] **FR-4b**: Left/Right arrow keys navigate slides while the overlay is open (does not close it —
      only Esc closes).
- [ ] **FR-5**: The overlay opens on whichever slide is active in the embedded carousel; closing it
      leaves the embedded carousel synced to whichever slide was last shown in the overlay. One shared
      slide-index variable drives both.
- [ ] **FR-6**: Expand triggers no new file download and no new network fetch — the overlay reuses the
      same `<img>` `src` values already rendered for the embedded carousel (browser cache, not a
      re-fetch).
- [ ] **FR-7**: If a startup has no pitch deck uploaded (`pitch_document_images` empty/unset), no
      Expand CTA is rendered — same condition that already gates Download Deck today.
- [ ] **FR-8**: Expand CTA is visible to any admin role that already reaches the Information tab /
      Pitch Deck panel — no new permission check beyond what already gates that panel
      (`$this->canExportData` gates Download Deck only, not the panel itself — Expand is gated the
      same way as the panel/carousel, not tied to `canExportData`).
- [ ] **FR-9**: **Deferred** — event logging (Expand-open / Close) is out of scope for this spec (see
      Open questions). No analytics/logging code is added in this pass.

## Per-repo plan

### admin

- `themes/default/html/startup-detail/startup-detail.php`:
  - Header (~line 1020-1024): add an "Expand" `<a>`/`<button>` next to the Download Deck link, e.g.
    `id="expandPitchDeck"` with `<i class="fa fa-expand"></i>&nbsp; Expand`, inside the existing
    `canExportData`-independent part of the card header (Expand is not a data-export action, so it
    should render regardless of `$this->canExportData` — only gated by the same
    `pitch_document_images` count check that already wraps the whole card).
  - Reuse the Bootstrap 4 `.modal.fade` pattern already established elsewhere in this repo (e.g.
    `themes/default/html/milestones/details.php` ~line 322: `modal-dialog modal-dialog-centered`,
    `data-dismiss="modal"` close button) rather than SweetAlert2 (used for Delete/Backdoor confirm
    dialogs, but not suited to paginated image content) or the bundled-but-unused-here `venobox`
    lightbox library (loaded globally via `elements/footer.php` but has no established gallery markup
    in this codebase to extend safely). Add a new `modal fade` block, `id="pitchDeckExpandModal"`,
    `modal-dialog modal-dialog-centered modal-xl` (or a custom fullscreen class — see CSS below), with
    an image element, prev/next buttons, slide badge + "x / y" counter, and a Close (X) button with
    `data-dismiss="modal"`.
  - Add scoped CSS (near the existing `.carousel-item` / `.pageNumber` styles at the top of this file,
    ~line 14-54) for the fullscreen modal: image scaled via `max-height`/`max-width` with
    `object-fit: contain` inside a flex-centered `.modal-body`, dark backdrop already provided by
    Bootstrap's `.modal-backdrop`.
  - JS (bottom of file, alongside the existing `$(".carousel").carousel({...})` init ~line 2447 and
    the `#loginToBackdoor` / `#deleteAccount` handlers ~line 2697/3191): track one shared
    `currentPitchSlide` index.
    - Sync `currentPitchSlide` from the embedded carousel's native `slide.bs.carousel` event.
    - `#expandPitchDeck` click → set the modal's visible image/index to `currentPitchSlide`, call
      `$('#pitchDeckExpandModal').modal('show')`.
    - Modal prev/next buttons and Left/Right keydown (bound only while the modal is `shown.bs.modal`,
      unbound on `hidden.bs.modal` to avoid leaking a global listener) update `currentPitchSlide` and
      the modal's displayed image + counter.
    - `hidden.bs.modal` handler on `#pitchDeckExpandModal` → call
      `$('#carouselExampleIndicators').carousel(currentPitchSlide)` to sync the embedded carousel to
      wherever the overlay left off (FR-5).
    - Image source array reused directly from the PHP-rendered `pitch_document_images` values already
      emitted into the embedded carousel's `<img>` tags (read via a small JS array built once from
      those same `<img src>` attributes, not re-fetched from PHP/AJAX) — satisfies FR-6.
- No other admin files touched. No `config/config.php` flag constants — this spec introduces no flag.

## Contracts & invariants

- **Flags:** none — no new flag, no existing flag consumed.
- **API:** none — no new endpoint, no DTO change, no cURL call added. `/audit-contract` is not
  applicable to this spec.
- **Events:** none shipped in this pass (FR-9 deferred).
- **Invariants at risk:** none of the 6 workspace invariants are touched — no flag name, no API
  contract, no tenant-verification shape, no auth change. Tenant scoping (#5): no new query is added;
  the overlay only re-renders `<img>` `src` values already produced by the existing, already-scoped
  PHP query (`startup-detail.php` ~line 1181-1198, itself confined to the tenant DB connection
  resolved at bootstrap per `sc-saas-admin`'s per-tenant-DB model). `/check-isolation` is not
  applicable — no new data access.

## Test plan

- admin: no test suite / no CI in this repo (per repo CLAUDE.md). Verification substitutes:
  - `php -l` on the edited template file.
  - Manual browser walkthrough on a tenant with a multi-slide pitch deck: Expand renders only when a
    deck exists; opens on the active slide; prev/next + arrow keys navigate and update the "x / y"
    counter; Close (X), backdrop click, and Esc all close the overlay; embedded carousel reflects the
    overlay's last slide after close; Network tab shows no new request for the slide images when
    Expand is clicked or navigated; repeat with `canExportData` false to confirm Expand still renders
    without Download Deck.
- cross-repo: not applicable — admin-only change, no other repo consumes anything this spec touches.

## Rollout

- Single-repo, additive UI change to one template file. No migration, no flag, no coordinated deploy
  with any other repo — ship whenever `sc-saas-admin`'s normal deploy runs.

## Out of scope

- FR-9 event logging (Expand-open/Close) — no existing lightweight analytics/logging mechanism was
  found in `sc-saas-admin` to write to (see Open questions). Left for a future, separately-scoped
  follow-up if product still wants it.
- Extending this pattern to the "Documents" tab — tracked separately as **SAN-525** (Backlog,
  deliberately not started until this spec ships).
- Editing/annotating the deck in fullscreen.
- Startup-facing or public deck viewers (`sc-saas-frontend` is not in `repos`).
- Dedicated mobile/tablet layout beyond standard responsive reflow.
- Non-image deck formats.
- Multi-deck comparison view.

## Open questions

All resolved 2026-08-26 (product/dev-lead decisions via Aman kabra in conversation):

- **Page-position indicator — RESOLVED: yes.** Show "x / y" inside the overlay in addition to the
  numbered slide badge (FR-3).
- **Arrow-key navigation — RESOLVED: yes.** Left/Right arrow keys navigate slides while the overlay
  is open, in addition to Esc closing it (FR-4b).
- **FR-9 event logging — RESOLVED: defer.** No existing lightweight analytics/logging mechanism
  exists in `sc-saas-admin` to log to (`profile_audit_logs` is backend-written and admin-read-only
  per its module spec; no GA/Mixpanel/equivalent is loaded). Building a new persistence path for this
  is out of scope for this UI-only spec. FR-9 is marked deferred, not dropped — revisit if product
  wants real instrumentation.
- **Documents tab extension — RESOLVED: separate follow-up.** Tracked as **SAN-525**, explicitly not
  started until SAN-345/SAN-346 are done; announce its start separately at that time.
