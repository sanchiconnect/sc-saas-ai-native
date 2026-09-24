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

## Follow-up: the template itself also needed a fix

A live test on the real tenant (screenshot-confirmed) showed the "Open Link" button still rendering
for a 1:1 Online event even with `event_location_type`/`event_link` left empty by the backend fix
above. Root cause: the email template (`event-speaker-registration`) never checked `event_link` at
all — its location cell was `{{#if event_location}} {{event_location}} {{else}} <Open Link button
href="{{event_link}}"> {{/if}}`, so whenever `event_location` was falsy it unconditionally rendered the
Open Link button, regardless of whether `event_link` actually had a value. The backend leaving
`event_link` empty was necessary but not sufficient — the template's own logic was the other half of
the bug.

Found the template's actual source: `sc-saas-backend/src/modules/global/admin/spa_email_templates.repository.ts`'s
`installDefaultEmailTemplates()` seed data (not, as initially assumed, entirely absent from the repo —
an earlier investigation in this session missed this 568KB file). First attempt wrapped the entire
`<tr>` in `{{#if event_location}}...{{else}}{{#if event_link}}...{{/if}}{{/if}}` so the whole row would
disappear for a 1:1 Online event. **Revised per explicit request:** keep the `{{#if}}` entirely inside
the existing value `<td>` instead of wrapping the `<tr>`/label cell — raw Handlebars text sitting
directly between `</tr>` and `<tr>` (outside any `<td>`) isn't valid table content and risks the
WYSIWYG email-template editor mangling it on save. Final shape, nested inside the one `<td>` that
already held the original `{{#if event_location}}...{{else}}<Open Link>{{/if}}`:

```
{{#if event_location}} {{event_location}} {{else}} {{#if event_link}} <Open Link> {{/if}} {{/if}}
```

Now: Venue shows when set (offline, any event type, unaffected); Open Link shows only when `event_link`
is actually set (non-1:1 online — webinar-style events, unaffected); for a 1:1 Online event (neither
set), the cell renders empty — no dead link — though the row itself (with an empty label cell too,
since `event_location_type` is also left empty by the backend fix) still takes up its row in the table,
rather than disappearing. Accepted trade-off for not touching the table's row structure.

**Important caveat, explained to the user:** `installDefaultEmailTemplates()` only *inserts* a row for
a `templateCode` that doesn't already exist in a tenant's `spa_email_templates` table — it never
updates `templateContent` on an existing row (it only backfills the separate `defaultTemplateContent`
column when that happens to be null, and nothing in this codebase reads that column back to re-apply
it). So this seed-file fix only reaches **brand-new tenants** provisioned after this change lands.
Every already-provisioned tenant (including the one used for live testing) keeps its stale template
content until someone manually re-applies the corrected HTML via Developer → Email Management in the
admin panel — which the user was walked through directly, with the exact HTML to paste, since this
sandbox has no way to reach that tenant's DB directly.

## Verified

- `npx tsc --noEmit` clean on the changed repository file.
- `npx eslint` — 2 pre-existing prettier errors elsewhere in this 568KB file (lines 391, 3712), confirmed via `git diff --stat` (1 line changed) to be unrelated to this edit, not introduced by it.
- The pasted-back HTML given to the user for manual application was built directly from the exact raw
  HTML they copied from the live Admin UI's source-code view, not reconstructed from a guess — same
  attributes, styling, and `data-offset-key`s preserved verbatim in both branches.

## Not verified — genuinely outstanding

No live send test yet confirming the corrected template (once manually applied to the test tenant)
actually renders all three cases (Venue / Open Link / hidden) correctly in a received email.

## Rollout

Not committed. Awaiting review and a real test from the user. The admin-panel template edit is a
separate, immediate action the user needs to apply directly (not a code deploy) for their current test
tenant to see the fix.

## Open questions

None blocking.
