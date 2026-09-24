---
id: SAN-970
title: Speaker email omits External Meeting Link section for 1:1 Online events
type: bug-fix
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-970
repos: [backend]
created: 2026-09-24
updated: 2026-09-24
---

# SAN-970 — don't show a dead External Meeting Link for a 1:1 Online event's speaker email

## Request

For an Event Type = "1:1 Meeting" + Delivery Mode = "Online" event, the SAN-906 speaker-registration
email showed an "External Meeting Link" section with an "Open Link" button pointing nowhere. In Person
(offline) events should keep showing Venue as before — not reported as broken.

## Investigation finding

Confirmed by code, not assumption: `events.event_registration_url` is genuinely `null` for every
one_to_one event, by design (SAN-788) — `themes/default/html/events/edit/info.php` hides the
`#eventRegistrationUrl` field entirely whenever `event_type == "one_to_one"`, and
`modules/events/edit/info.php` explicitly skips server-side validation of that field for the same event
type, because a 1:1 event has no single shared meeting URL — each attendee gets their own per-slot link
on `events_attendees.meetingToolType`/`meetingExternalUrl` instead.

## Root cause

`sendEventSpeakerRegistrationEmail()` (`admin-actions.service.ts`) branched purely on
`event.deliveryMode`, with no check on `event.eventType` and no null-check on `eventRegistrationUrl` —
so for a 1:1 + Online event it unconditionally set `event_location_type = 'External Meeting Link'` and
`event_link = event.eventRegistrationUrl` (always `null` for this event type), producing a dead "Open
Link" button in the sent email.

## Fix

Guarded the ONLINE branch with `event.eventType !== EventTypes.ONE_TO_ONE`. For a 1:1 Online event,
`event_location_type`/`event_location`/`event_link` all stay at their declared empty-string defaults —
the location section of the email gets nothing to render. The OFFLINE (Venue) branch is now reached via
`else if (event.deliveryMode != EventSpeakerDeliveryMode.ONLINE)`, unconditional on event type exactly
as before — Delivery Mode = In Person still shows Venue regardless of event type, unaffected by this
change.

## Design decisions taken (not asked, judgment calls)

- **Left the OFFLINE/Venue branch's condition unchanged in spirit** (still fires whenever delivery mode
  isn't online), just restructured as an `else if` rather than a bare `else`, so the new one_to_one
  exclusion on the ONLINE side doesn't accidentally fall through into the Venue branch for a 1:1 Online
  event — it should render neither section, not silently become "Venue" instead.
- **Did not touch the DB-stored email template itself.** The actual Handlebars markup
  (`EmailTemplateCode.EVENT_SPEAKER_REGISTRATION`) lives in a per-tenant DB row, not this repo, so its
  exact behavior for an empty `event_location_type` couldn't be inspected from code. Flagged as a
  genuinely open question in the Linear issue rather than assumed away.

## Verified

- `npx tsc --noEmit` clean, `npx eslint` clean (0 new errors — pre-existing unrelated unused-import
  warnings only) on the changed file.
- Confirmed `EventTypes.ONE_TO_ONE` and the `eventType` column name against `events.entity.ts` and
  `core/constants/enum.ts` directly rather than guessing the identifier.
- `git status --short` — only `admin-actions.service.ts` (fix) + `module.spec.md` (docs) touched.

## Not verified — genuinely outstanding

Two things, both requiring a real environment this sandbox doesn't have:

1. No live send test (no admin login) — needs a real Speaker Details submit on a 1:1 Online event to
   confirm the received email no longer shows a broken link section.
2. **Template behavior unconfirmed.** Whether the DB-stored email template already omits its location
   block cleanly when `event_location_type` is empty, or instead renders an empty/malformed row (e.g. a
   blank label with no value) — this can only be confirmed by actually looking at the template content
   in a real tenant DB or by sending a real test email and inspecting the result.

## Rollout

Not committed. Awaiting review and a real test from the user.

## Open questions

The template-behavior question above is not blocking this specific code change (which does the correct,
controllable thing on the data side), but the fix isn't fully "done" as a user-facing improvement until
someone confirms the template renders cleanly with an omitted location.
