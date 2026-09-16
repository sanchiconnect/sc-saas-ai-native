---
id: SAN-768                     # Linear parent (Enhancement project, "One-on-One Booking Enhancement" milestone).
                                 # Full issue set: SAN-769/773-776/770/771/784 (backend), SAN-777/781/782/778/779 (admin),
                                 # SAN-780/772 (frontend), SAN-783 (QA).
title: Events Module — One-on-One Slot Booking, Approval Modes & Notifications
type: feature
status: in-review               # code written and self-verified (tsc clean both TS repos); not yet exercised against
                                 # a live DB/browser — see Test plan. Two Open questions remain, so not yet `approved`
                                 # in the strict sense even though implementation already exists (spec authored
                                 # retroactively from the BRD, after the code, per explicit user request).
linear: https://linear.app/sanchiconnect/issue/SAN-768/enhancement-one-on-one-events-slot-integrity-approval-modes-caps-and
owner: vishali.k@sanchiconnect.com
repos: [backend, admin, frontend]
                                 # DEPENDENCY ORDER, and load-bearing: admin's new form fields write directly to
                                 # `events` columns that only exist once sc-saas-backend has booted at least once
                                 # (TypeORM `synchronize: true`, no separate migration file) — see Rollout.
contracts:
  api:
    - "PATCH v2/events/reject_request/:eventAttendeeUUID/:adminMd5 (sc-saas-backend, CHANGED — behavior fix only, same signature: now actually sends the rejection email via sesEmailService.sendMeetingRequestRejectedEmail; previously updated status and returned silently)"
    - "PATCH v2/events/approve_request/:eventAttendeeUUID/:adminMd5 (sc-saas-backend, CHANGED — added optional ?skipAutoReject=true query param; also now auto-rejects Manual-mode siblings on the same slot unless that flag is set)"
    - "PATCH v2/events/cancel_attendee_meeting/:eventAttendeeUUID/:adminMd5 (sc-saas-backend, CHANGED — fixed a pre-existing @Param('eventUUID') vs. route :eventAttendeeUUID mismatch that made this endpoint always 400; repurposed as the FR-1.5 reversal endpoint for an Approved attendee, and the FR-1.2-mapped ordinary-reject path for a Pending one)"
    - "PATCH v2/events/attend/:eventUUID/:eventAttendeeUUID/withdraw (sc-saas-backend, NEW — FR-1.4 self-withdrawal, JWT-protected, hard-deletes the attendee row)"
  flags: []                     # no TenantUsersEntity flag touched — Approval Mode is a per-event field, not a
                                 # platform-wide tenant flag; the pre-existing `events_one_to_one_feature` brand
                                 # setting (gates one_to_one events existing at all) is untouched by this spec.
  events: []
tenant_scoped: true             # Event/EventAttendee rows are ordinary tenant data, scoped the same way every other
                                 # events-module query already is (one-deployment-per-tenant backend config) — no new
                                 # cross-tenant surface introduced.
depends_on: []
created: 2026-09-15
---

# Events Module — One-on-One Slot Booking, Approval Modes & Notifications

## Problem

For a One-on-One event, a time slot could receive more than one applicant, but approving one did not reject the
others — more than one startup could end up confirmed for what's meant to be a single meeting. Separately,
rejection was unreliable regardless of cause: `sc-saas-admin`'s reject action bypassed the backend's real reject
call entirely (a local archive+delete instead), and even when the backend endpoint *was* called correctly (e.g. via
this spec's own new auto-reject path), it never sent an email — it only flipped the status. On top of these two
defects, admins had no choice between hands-off first-come booking and reviewed booking, no way to cap how many
applications a popular slot draws, and no way to loop a colleague into an event's status emails. The event-type
dropdown also carried a few near-duplicate options that should collapse into one each.

Source: `specs/features/BRD-Events-Module-OneOnOne-Booking.pdf` (v2 — 34 gaps resolved across two review rounds,
including three decisions reversed mid-review; §13.2 leaves one item explicitly open, see Open questions below).

## Acceptance criteria

*(Numbered against the BRD's own FR/AC references.)*

- [ ] A One-on-One slot can never end up with more than one Approved applicant — approving one in Manual mode
  auto-rejects every other Applied applicant on that same slot — BRD FR-1.1 AC1-AC3.
- [ ] Every ordinary rejection (auto-reject via FR-1.1, or a direct admin rejection) sends the applicant the same
  rejection email, through a pathway that actually calls the backend and actually sends mail — BRD FR-1.2 AC1-AC3.
  A reversal (FR-1.5) does NOT use this template — see below.
- [ ] A closed slot — already Approved (Manual), already booked (Automatic), or already at its cap with no one
  approved yet — has its Apply action disabled entirely; no application record and no email are ever generated for
  a blocked attempt — BRD FR-1.3 AC1-AC4.
- [ ] A startup can withdraw its own pending (Applied) application; this is a clean void (no status shown anywhere,
  as if it never happened), frees the slot's live cap immediately, and does NOT spend the startup's per-event slot
  limit — BRD FR-1.4 AC1-AC5.
- [ ] An admin can reverse an Approved applicant (either mode) via the existing `remove_attendee`/"Delete Record"
  action — not a new button. The reversed applicant returns to **Applied** (not Rejected), receives a distinct
  "your confirmed meeting was cancelled" email (not FR-1.2's template), and every co-applicant auto-rejected by
  that same approval is restored to Applied too — BRD FR-1.5 AC1-AC6.
- [ ] Manually adding an attendee (admin's existing manual-add flow) does NOT trigger FR-1.1's auto-reject cascade,
  but DOES spend one of that startup's FR-3.2 slot-limit attempts — BRD FR-1.6 AC1-AC2.
- [ ] A One-on-One event has exactly one Approval Mode (Automatic/Manual), never left unset, locked once the event
  is live — BRD FR-2.1 AC1-AC2.
- [ ] Automatic mode books the first applicant with no review step and closes the slot atomically (concurrent
  applicants: arbitrary first-write-wins, the loser gets ordinary FR-1.3 treatment) — BRD FR-2.2 AC1-AC4.
- [ ] Manual mode has an admin-configured per-slot application cap counted **live** (Applied + Approved, not
  cumulative) — BRD FR-3.1 AC1-AC7.
- [ ] A separate per-event, per-startup slot limit is a **lifetime** count: a true Rejected application spends an
  attempt permanently; Withdrawn and Reversed do not — BRD FR-3.2 AC1-AC6.
- [ ] Both caps lock once the event is live, same as Approval Mode — BRD FR-3.3 AC1-AC2.
- [ ] Every event notification email can carry an admin-specified CC list — true CC (not BCC), unlimited addresses,
  no internal/external restriction, open to any admin with event access — BRD FR-4.1 AC1-AC5.
- [ ] A Manual-mode applicant gets an acknowledgment email on submission; admin gets notified on a new application,
  on a slot reaching its cap, and on a withdrawal; admin gets a reminder (never an auto-expiry) as a Manual-mode
  event's date nears with still-unreviewed slots — BRD FR-4.2-FR-4.5.
- [ ] The event-type dropdown offers "Demo Day / Product Launch" and "Tradeshow / Exhibition / Conference" as
  single merged choices for **newly created events only** — historical events keep their exact original label,
  untouched, forever (no migration) — BRD FR-5.1/FR-5.2.
- [ ] The existing approve pathway is unchanged in shape, and demonstrably still fires its confirmation email when
  triggered with no admin in the loop (Automatic-mode booking) — BRD §12 "gap #11."

## Per-repo plan

### backend

- **Entities** (`src/modules/events/entities/`, TypeORM `synchronize: true` — no separate migration file exists or
  is needed in this repo's convention):
  - `events.entity.ts`: added `approvalMode` (`EventApprovalMode` enum, default `'manual'` so already-live
    one_to_one events keep today's behavior unchanged), `applicationCap`/`maxSlotsPerStartup` (nullable ints —
    remain nullable at the entity/DB level for defensive compatibility, though `sc-saas-admin`'s form no longer
    ever submits null for a Manual-mode event, see admin plan), `ccEmails` (nullable JSON string array).
  - `event-attendees.entity.ts`: added `rejectionCause` (`EventAttendeeRejectionCause` enum, admin-visibility only,
    never varies the applicant-facing email), `reversedBy`/`reversedAt` (nullable audit trail for FR-1.5).
  - `src/core/constants/enum.ts`: added `EventApprovalMode`, `EventAttendeeRejectionCause`, and two new additive
    `EventTypes` values (`DEMO_DAY_PRODUCT_LAUNCH`, `TRADESHOW_EXHIBITION_CONFERENCE`) — the 5 old individual
    values are untouched, since historical events keep using them forever (FR-5.1/5.2, going-forward-only).
- **`events.service.ts`** — the bulk of the logic, refactored around three new/extracted private helpers so every
  path shares exactly one implementation:
  - `bookOneToOneMeetingAndSendConfirmation(eventAttendee, event, admin?)` — extracted from the old inline
    `approveEventAttendeeRequest` body; `admin` is optional throughout (unchanged downstream signatures already
    supported it), so calling it with `admin=undefined` from Automatic-mode booking answers BRD gap #11 by
    construction rather than by inspection.
  - `performOrdinaryReject(eventAttendee, event, cause, rejectedByAdminId)` — the ONE reject pathway (FR-1.2 AC3):
    sets status, sets `rejectionCause`, and sends `sesEmailService.sendMeetingRequestRejectedEmail`. Called by the
    public `rejectEventAttendeeRequest` (cause=MANUAL), `approveEventAttendeeRequest`'s new auto-reject-the-rest
    loop (cause=AUTO_REJECTED_ON_APPROVAL), and `cancelAttendeeMeeting`'s Pending-attendee branch (cause=MANUAL,
    per the BRD's own tentative §12 mapping).
  - `notifyEventOwner(event, subject, message)` — plain-text admin notification via the generic
    `sesEmailService.sendEmail()` primitive (FR-4.3/FR-4.4); a functional minimum, not polished copy, since the
    BRD explicitly leaves channel/wording to engineering (§15).
  - `approveEventAttendeeRequest(adminMd5, eventAttendeeUUID, skipAutoReject = false)` — new `skipAutoReject` param
    (FR-1.6), set via the controller's new `?skipAutoReject` query param, itself set by `sc-saas-admin`'s manual-add
    call (see admin plan).
  - `attendEvent(...)` — now takes the full `event` (not just `event.id`) into `addAttendeeWithSlotLock`; adds the
    FR-3.2 pre-flight limit check (`countLiveSlotLimitApplications`); branches Automatic (books + confirms
    immediately) vs. Manual (sets PENDING_MODERATION + FR-4.2 acknowledgment email + FR-4.3 admin notifications,
    including a cap-reached check).
  - `cancelAttendeeMeeting(adminMd5, eventAttendeeUUID)` — rewritten. Also fixes two pre-existing bugs this feature
    depended on: `getEventById(eventAttendee.id)` was fetching the wrong entity (attendee id, not `eventAttendeeId`),
    and the controller passed the wrong `@Param` key (see below) so this endpoint 400'd on every real call before
    this fix. Now branches on the attendee's real status: APPROVED → FR-1.5 reversal (cancel meeting, distinct
    email via `meetingsService.sendCancelledMeetingEmail`, status back to PENDING_MODERATION, restore
    `AUTO_REJECTED_ON_APPROVAL` siblings); PENDING_MODERATION → ordinary reject via `performOrdinaryReject`.
  - `withdrawEventAttendeeApplication(session, eventAttendeeUUID)` — new; hard-deletes the row (clean void, FR-1.4)
    after ownership/status checks, then fires the FR-4.4 admin notification.
- **`event-attendees.repository.ts`**: `addAttendeeWithSlotLock` now takes the full `event` object and is
  approvalMode/applicationCap-aware (closed = any live attendee in Automatic mode; closed = an Approved attendee OR
  cap reached in Manual mode) — a closed slot still returns `{conflict: true}` with **no row ever written**, which
  is what satisfies FR-1.3 AC4 without any new "blocked attempt" bookkeeping. New:
  `getPendingSiblingsForSlot`, `getAutoRejectedSiblingsForSlot`, `countLiveSlotLimitApplications` (excludes
  `reversedBy IS NOT NULL` rows, giving FR-3.2 AC5 for free), `deleteEventAttendeeById`.
- **`events.controller.ts`**: fixed `cancel_attendee_meeting`'s `@Param('eventUUID')` → `@Param('eventAttendeeUUID')`
  mismatch (documented as a known issue in this module's own `module.spec.md` before this fix); added
  `?skipAutoReject` query param to `approve_request`; added the new `withdraw` route (JWT-protected, same guard
  shape as `attend`/`updateAppliedEvent`).
- **CC threading** (`src/core/services/ses-email.service.ts`, `src/modules/meetings/meetings.service.ts`): added
  optional `ccEmails?`/`additionalCcEmails?` params to `sendMeetingRequestRejectedEmail`,
  `sendScheduledMeetingEmail`, `sendCancelledMeetingEmail` — additive, undefined for every existing non-events
  caller, merged alongside the pre-existing desk-based CC feature (`Feature.CC_DESK_COMMUNICATION`) rather than
  replacing it.
- **Not built in this pass:** FR-4.5 (event-date reminder for unreviewed Manual-mode slots) needs a new scheduled
  job, not inline request-handling logic — `src/modules/cron/invitation-reminder.service.ts` is the closest
  existing template. Left as a follow-up (see Open questions).
- **`events.service.ts` (working label "SAN-792" in code comments — a follow-up done in the same chat session as
  SAN-772/780 below, not a separately tracked Linear issue):** `getPlatformEvents()` and `getAllEvents()` — the two
  service methods behind the calendar's event list/modal — now also set `event['myApplications']` for One-on-One
  events: every one of the requesting startup's own attendee rows for that event (uuid/date/timeFrom/timeTo/
  approvalStatus), via a new private `getMyOneToOneApplications(eventAttendees, userId)` helper. Purely additive —
  `checkIfResponseExists` (a single first-match record, kept for every other event type and every existing
  consumer) is unchanged. This exists because `checkIfResponseExists` can only ever surface ONE of a startup's
  applications, which silently made a `maxSlotsPerStartup` > 1 unusable through the UI (see frontend plan below) —
  a startup with one pending application had no way to see or apply for a second allowed slot, and a stale
  Rejected row could mask a live Pending one on a different slot.

### admin

- `themes/default/html/events/edit/info.php`: added Approval Mode radio + Application Cap + Max Slots per Startup
  + CC Emails fields, following the file's existing show/hide-by-`event_type` pattern (`#timeSlotDifference`/
  `#dayTimeStartsFrom`). Help text moved to `(i)` tooltip icons per UI feedback (`data-toggle="tooltip"`, already
  initialized globally in this file). Both cap fields are **required** whenever enabled (`max_slots_per_startup`
  always for a one_to_one event; `application_cap` only in Manual mode, hidden and not required in Automatic) —
  `data-parsley-required` toggled dynamically alongside each field's show/hide so a hidden field can never block
  submission. Once `publish_status == 'published'`, all three lock to read-only client-side.
- `modules/events/edit/info.php` (the POST handler): mirrors the live-lock server-side — for a live event, ignores
  any submitted Approval-Mode/cap value and keeps what's already stored, so the lock holds even against a bypassed
  submit. Validates both caps as required whole numbers ≥1 (no "uncapped"/null option — reversed from an earlier
  pass per explicit follow-up feedback) and CC addresses via `filter_var(..., FILTER_VALIDATE_EMAIL)`.
- `modules/events/details.php`: fixed the reject branch (was building the reject URL but never calling it — a
  local `events_attendees_archived` insert + delete instead, silently bypassing the backend and its rejection
  email). Also fixed the `deleteAttendee` handler, which unconditionally hard-deleted the local row **before**
  calling the backend — meaning `cancel_attendee_meeting` always operated on an already-deleted row. Now looks up
  the record's real status first; Approved/Pending rows go through the backend endpoint (which owns the state
  transition), and a genuine local delete is reserved only for an already-Rejected record (no BRD-defined model for
  that case at all).
- `modules/events/add_attendee.php`: appends `?skipAutoReject=true` to its existing `approve_request` call, so a
  manual add doesn't cascade-reject other applicants on the slot (FR-1.6).
- `modules/events/list.php` + `themes/default/html/events/edit/info.php`: Event Type dropdown — the create/edit
  form only offers the two merged options for a new event, but still displays/preserves an existing event's
  original value if it's one of the 5 old ones; the list-page filter dropdown adds the two merged options
  alongside all 12 existing ones (none removed), since historical events still need to be filterable.

### frontend

- `src/app/core/service/global.service.ts`: added `withdrawEventSlot(eventId, attendeeId)` calling the new backend
  withdraw endpoint.
- `src/app/shared/utils/common-methods.ts`: new `formatEventTypeLabel()` wrapping the existing generic
  `formatEnumStringForUI()` with the pre-existing Webinar override plus the two new merged-type overrides;
  replaces the previously-duplicated inline ternary in `public-events.component.html` and
  `event-details-modal.component.html`.
- `src/app/shared/common-components/event-details-modal/` (the NON-one-to-one modal, `eventType !== 'one_to_one'`)
  and `public-events.component.html` (the public/pre-login preview page): a stray earlier pass had leaked the
  Approval Mode badge ("Instant Booking"/"Requires Approval") and per-slot cap/limit text onto these two
  generic-event surfaces, including hard-coded fake defaults (`applicationCap: 5`, `maxSlotsPerStartup: 2`) shown
  on every webinar/other event type regardless of its real configuration. Removed from `event-details-modal`
  entirely (that component only ever renders for non-one_to_one events); gated behind
  `event?.eventType === 'one_to_one'` in `public-events.component.html`, which is generic across event types.
- `src/app/shared/common-components/event-details-one-on-one-modal/` — the applicant-facing Apply/status UI,
  substantially reworked twice in the same session (working label "SAN-792" in code comments; not a separately
  tracked Linear issue — see the backend note above):
  - **First pass** (building on the existing SAN-772 single-application model): added the closed/full slot
    indicator (`closedSlotReasonLabel`/`closedSlotReasonTooltip`, driven by the event's own `approvalMode`), an
    inline error banner for a failed apply attempt (`applyErrorMessage`/`applyErrorSeverity`, severity read from
    the backend's HTTP status rather than its message text), a withdraw confirmation dialog (SweetAlert2, matching
    the app's existing confirm-before-destructive-action pattern), and hardened the event-questions fetch (no
    error handler previously existed, so a failed fetch left `eventQuestionsList` `undefined` and threw inside
    `handleBook()`).
  - **Second pass** (this is the FR-3.2 multi-slot fix, using the backend's new `myApplications`): replaced the
    single-application (`attendeeDetail`/`checkIfResponseExists`) model with a `myApplications: any[]` list, copied
    locally in `ngOnInit` and mutated in place on a fresh booking/withdrawal so the UI updates immediately without
    waiting on a refetch. Per-slot rendering is now driven by one state-machine method, `getSlotView(slot, date)`,
    in priority order: (1) the startup's own application for this EXACT slot — `mine-pending` (boxed, with the
    confirmation message and an inline Withdraw action right on the row), `mine-approved` (full green row),
    `mine-rejected` (full red row, and deliberately NOT re-offered as bookable through this row, even though the
    backend's own duplicate check technically allows re-applying to a slot after a rejection there — kept simple
    to match the agreed UI reference); (2) `limit-locked` — the startup's own `maxSlotsPerStartup` reached, which
    locks every remaining open slot (not just the one last clicked), each showing a lock icon and the "reached the
    maximum" message; (3) `full` — the slot's own `booked` flag (cap reached by other startups, or already booked
    in Automatic mode), showing a `cap/cap` fill count next to the badge (an approximation: the API has no live
    per-slot count, but a full slot always sits exactly at its cap since the backend closes it the instant that's
    reached, so `applicationCap/applicationCap` is accurate without a new field); (4) `open` — the plain Book
    action. Matching a `date`/`timeFrom` between a slot (plain "YYYY-MM-DD"/"HH:mm:ss" strings) and an application
    record (a TypeORM `date` column serialized as a full ISO timestamp, and whatever `timeFrom` precision was
    actually submitted) needed normalizing to just the first 10/5 characters (`toDateKey`/`toTimeKey`) — a direct
    `===` never matched even for the exact same slot.
  - A dev-only test toggle (`?mockOneToOne=1` on the page URL, gated on `!environment.production`) seeds fake
    `myApplications`/`applicationCap`/`maxSlotsPerStartup` data so the cap/limit/withdraw states can be exercised
    against a live event before the backend change above is actually deployed to a given environment (the frontend
    calls a remote dev API per `environment.ts`, not a local backend, so a local backend edit alone doesn't take
    effect there). Clearly commented for removal once that's no longer needed everywhere it's tested.
  - **Known theme gap found and fixed along the way:** `badge-light-info`/`badge-light-warning`/
    `badge-light-secondary`/`badge-light-danger` are not actually defined anywhere in this app's compiled CSS
    (`src/assets/css/build.css` only defines `badge-light-primary` and `badge-light-success`) — the base `.badge`
    rule defaults `color: #fff`, so any other `badge-light-*` variant silently rendered invisible white-on-white
    text instead of erroring. All new badges here use only the two defined `badge-light-*` variants, or the plain
    neutral `badge-light`; the pre-existing "Requires Approval" badge (both here and in
    `public-events.component.html`) had the same bug and was fixed the same way. This same gap likely affects any
    OTHER `badge-light-warning`/`-danger`/`-secondary` usage elsewhere in the frontend — not audited/fixed outside
    the files touched by this spec.

## Contracts & invariants

- **Flags:** none. Approval Mode/caps/CC are per-event fields, not a tenant-level flag.
- **API:** see `contracts.api` above — one new route, three behavior-changed routes on existing signatures.
  `sc-saas-admin` is the only consumer of all four (direct cURL calls, not through a shared client library);
  `sc-saas-frontend` consumes only the new withdraw route and the existing `attend`/`attend/:id` routes it already
  used. Run `/audit-contract` before this is considered fully verified — not run in this session.
  Additionally (working label "SAN-792"): `GET events/upcoming` and `GET events` (`getPlatformEvents()`/
  `getAllEvents()`) gained an additive `myApplications` array field on each One-on-One event object — no existing
  field's shape changed, and every other event type's response is untouched.
- **Events:** none — this platform has no formal domain-event bus for this module; "notifications" here are direct
  transactional email sends, not published events.
- **Invariants at risk:**
  - **API contract (#2, backend-owned):** the four routes above are the actual surface to check
    `sc-saas-admin`'s cURL callers and `sc-saas-frontend`'s `GlobalService` against.
  - **Tenant scoping (#5):** no new cross-tenant surface — every new/changed query still runs against the same
    one-deployment-per-tenant backend, scoped exactly like the pre-existing Events module queries it extends.
  - **Poly-repo deploy ordering (general guardrail, not one of the 6 named invariants, but load-bearing here):**
    `sc-saas-admin`'s new form fields write directly to `events.approval_mode`/`application_cap`/
    `max_slots_per_startup`/`cc_emails` columns that only exist once `sc-saas-backend` has booted at least once
    post-deploy (TypeORM `synchronize: true` creates them). Deploying admin ahead of backend will fail admin's
    event-save with an unknown-column DB error. See Rollout.
  - Flag names (#1), the tenant-verification contract (#3), auth (#4), and the cross-workspace PowerPitch
    contract (#6) are all unaffected.

## Test plan

- backend: `npx tsc --noEmit -p tsconfig.json` — passes clean. No jest tests added in this pass; no live DB
  available in this environment to exercise the actual transaction/slot-lock/email-send behavior.
- frontend: `npx tsc --noEmit -p tsconfig.app.json` — passes clean. Not run in a browser.
- frontend (SAN-792 follow-up, same session): `npx tsc --noEmit -p tsconfig.app.json` AND a full
  `npx ng build --configuration development` both re-run clean after each edit in this pass — the AOT build step
  specifically catches Angular template-binding type errors that plain `tsc` misses (this is how the
  `eventQuestionList: []`-typed input mismatch and a couple of template binding issues were actually caught).
  Manually exercised in a live browser against a real event (cap/limit/withdraw/full states, and the
  `?mockOneToOne=1` dev toggle for states not yet reachable because this backend change wasn't deployed to the
  environment being tested against at the time) — not exercised as an automated test.
- admin: no PHP linter available in this environment; all edits reviewed by hand against the working patterns
  they extend (approve branch's status-code check, existing show/hide field toggles, existing Parsley
  required-toggling convention).
- cross-repo (not yet performed — this is what QA-1/SAN-783 exists to do): walk Manual mode end-to-end (multiple
  applicants → approve one → confirm the rest are auto-rejected with email → confirm cap/limit counting) and
  Automatic mode (first applicant auto-booked with confirmation email, no admin action, second applicant sees a
  disabled Apply action) against a real DB; verify the reversal flow (`remove_attendee` on an Approved attendee)
  restores co-applicants correctly; verify CC actually arrives visibly (not BCC) on a real send; verify zero
  historical events were relabeled after the event-type merge ships.

## Rollout

1. **Deploy `sc-saas-backend` first**, in this order within the repo if split further: the reject-email fix
   (urgent, no dependencies) can ship alone; everything else in this spec can follow as one deploy since it's all
   one coherent change to the same handful of methods. Let TypeORM `synchronize: true` create the new columns.
2. **Deploy `sc-saas-admin` only after step 1 has actually run** — its new form fields write directly to the
   columns step 1 creates; deploying out of order breaks event saves with a DB error, not a graceful failure.
3. **Deploy `sc-saas-frontend`** — depends on the backend's new withdraw route existing, AND (as of the SAN-792
   follow-up) on `events.service.ts`'s `myApplications` field being live on whatever API the frontend build points
   at (`environment.ts`'s `apiEndpoints.baseUrl`, a remote host — not automatically kept in sync with a local
   backend checkout). Without it, the applicant-facing UI degrades safely to the plain closed/full state instead of
   showing the startup's own Applied/Approved/Rejected status, rather than erroring. Independent of admin's deploy
   timing.
4. No flag gating exists for this feature. Approval Mode defaults to `manual` for already-published one_to_one
   events, so behavior for any event that existed before this ships is unchanged until an admin explicitly touches
   its settings (which they now can't, once it's live — so in practice, pre-existing live events keep exactly
   today's single-applicant-per-slot behavior forever, and only newly-created one_to_one events get to choose).

## Out of scope

Per BRD §6.2, confirmed by the Product Owner:
- Any change to how slots are generated/scheduled (time-slot length, day-start-time, date/time windows, breaks).
- ~~The applicant-facing UI for viewing/managing an application's status, beyond the minimal Rejected-state display
  and Withdraw control~~ — superseded: a follow-up in this same session (see the frontend plan's "second pass"
  above) DID build a broader per-slot status/history UI (Applied/Approved/Rejected/Full/limit-locked, multiple
  simultaneous applications up to `maxSlotsPerStartup`), because §FE-2's original narrower scope turned out to make
  a `maxSlotsPerStartup` > 1 event unusable through the UI. Still out of scope: any change to the underlying
  approval/reversal/notification mechanics this spec already covers, and anything beyond this One-on-One Apply
  flow (no other event type, no admin-side UI change).
- Any retroactive cleanup of slots that already have more than one Approved applicant today (forward-only fix).
- Video-meeting mechanics, meeting notes, feedback questionnaires (FR-MTG-01-03) — unaffected.
- Approval-mode/cap behavior for any event type other than One-on-One.
- Relabeling any existing/historical event under any type, merged or not (FR-5.1/5.2 apply going forward only).
- Any change to the approve pathway's existing shape — only verified it still fires correctly with no admin in the
  loop, not redesigned.
- Reschedule's interaction with any of this feature's new rules — explicitly deferred by the Product Owner to a
  separate, later decision; existing reschedule behavior is untouched.

## Open questions

- **BRD §13.2 (still open in the BRD itself):** does manually adding an attendee also trigger FR-1.3's slot
  closure for everyone else on that slot? Not addressed by FR-1.6 either in the BRD or in this implementation —
  `approveEventAttendeeRequest`'s `skipAutoReject` path does not additionally close the slot. Needs Product Owner
  input before finalizing that specific sub-behavior.
- **BRD §12 (tentative, not separately confirmed):** `remove_attendee` on a still-Pending (not yet Approved)
  attendee is implemented as an ordinary admin rejection, per the BRD's own proposal — flagged there as "Claude's
  proposal, not separately confirmed." Should be verified against actual admin expectations before relying on it.
- **FR-4.5 (event-date reminder) is not implemented** — needs a new cron job (see `notifyEventOwner`'s doc comment
  and the backend plan above). BE-8/SAN-784 is only partially done until this exists.
- Exact notification channel (email/in-panel/both) and FR-4.5's reminder timing are explicitly left to engineering
  by the BRD (§15) and have not been decided — FR-4.3/FR-4.4 were implemented as plain-text emails as a functional
  minimum, not a decided final design.

This spec is **not yet approvable** in the strict sense (non-empty Open questions) even though the code already
exists — the two BRD-sourced open items should be routed to the Product Owner, and FR-4.5 scoped as a follow-up,
before this is marked `done`.
