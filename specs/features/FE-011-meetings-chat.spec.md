---
id: FE-011
title: Meetings & Chat
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET api/v1/meetings
    - GET api/v1/meetings/pending-acceptance
    - GET api/v1/meetings/public/:meetingUUID
    - POST api/v1/meetings
    - POST api/v2/meetings
    - PATCH api/v1/meetings/:meetingUUID/accept
    - PATCH api/v1/meetings/:meetingUUID/reject
    - DELETE api/v1/meetings/:meetingUUID
    - POST api/v1/meetings/:meetingUUID/propose
    - POST api/v1/meetings/:meetingUUID/propose/action
    - GET api/v1/meetings/notes/:meetingUUID
    - POST api/v1/meetings/notes/:meetingUUID
    - POST api/v1/meetings/notes/:meetingUUID/share
    - GET api/v1/meetings/users/calendar-availability
    - GET api/v1/meetings/users/calendar-availability/:userUUID
    - GET api/v1/meetings/users/calendar-availability/:userUUID/:date
    - PATCH api/v1/meetings/users/calendar-availability
    - GET api/v1/chat/conversation
    - POST api/v1/chat/conversation
    - GET api/v1/chat/conversation/:uuid/messages
    - POST api/v1/chat/conversation/:uuid/messages
    - POST api/v1/chat/conversation/:uuid/messages-file
    - PATCH api/v1/chat/conversation/:uuid/messages/:msgUUID/mark-read
    - DELETE api/v1/chat/conversation/:uuid/messages/:msgUUID
    - POST api/v1/conversations/send_chat_email/:groupChatUUID
    - POST api/v1/conversations/send_chat_notification/:groupChatUUID
  flags:
    - online_meetings
    - meeting_moderation_enabled
    - chat
    - cc_desk_communication
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-011 — Meetings & Chat

## Summary

Meeting scheduling (VideoSDK in-browser video calls), calendar availability, meeting notes, and dual-mode chat (CometChat SDK or in-house Socket.IO). The meeting join page is intentionally outside the auth guard to support email-linked invitations and interview candidates. Chat mode (CometChat vs in-house) is selected at runtime from `globalSettings.chat_type`. `SocketService` is a singleton shared between the notifications system and the chat module.

## Frontend entry points

Module specs:
- `sc-saas-frontend/src/app/modules/meetings/module.spec.md`
- `sc-saas-frontend/src/app/modules/chat/module.spec.md`

Routes (lazy-loaded):

### `MeetingsModule` (path `meeting`)
| Path | Component | Auth |
|---|---|---|
| `/meeting/:meetingId` | `MeetingComponent` | **No AuthGuard** — public join page |
| `/meeting/:meetingId/feedback` | `FeedbackComponent` | No AuthGuard (child of MeetingComponent) |

### `CalenderModule` (path `calender` — intentional typo, keep as-is)
All routes nested under `ProtectedLayoutWrapperComponent`:
- `` → `FullCalenderComponent`
- `notes` → `CalenderNotesComponent`
- `events` → `EventsCalenderComponent`

### `ChatModule` (path `chat`)
Both routes under `ProtectedLayoutWrapperComponent`:
- `conversations` → `ChatsWrapperComponent` (selects CometChat or in-house)
- `conversations/:userId` → `ChatsWrapperComponent` (pre-selects conversation with userId)

Services: `MeetingService` (`providedIn: 'root'`), `ConversationService`, `ChatService`, `SocketService` (`providedIn: 'root'`).

`SetAvailabilityModalComponent` is exported from `CalenderModule` for embedding in other modules (e.g. profile pages).

Libraries: `@videosdk.live/rtc-js-prebuilt` (VideoSDK in-browser call), `angular-calendar` with `date-fns` adapter, `@cometchat-pro/chat` SDK (CometChat mode), CometChat Angular UI Kit (vendored local package at `src/cometchat-pro-angular-ui-kit/`), `ngx-socket-io` (in-house mode).

## Backend modules

Module specs:
- `sc-saas-backend/src/modules/meetings/module.spec.md`
- `sc-saas-backend/src/modules/chat/module.spec.md`
- `sc-saas-backend/src/modules/conversations/module.spec.md`

`MeetingsController` (path `meetings`, v1, class `@UseGuards(FeatureGuard)`): most routes require `@Features(Feature.ONLINE_MEETINGS)` + `JwtAuthGuard`. Several routes intentionally lack JWT:
- `GET meetings/public/:meetingUUID` — meeting detail for the join page (VideoSDKGuard commented out)
- `GET meetings/:meetingUUID/job-interview` — for pre-authenticated interview links
- `POST meetings/:meetingCode/complete` — VideoSDK webhook callback (no auth)
- `GET meetings/feedback-reminder/trigger` — `JwtAuthGuard` commented out (unauthenticated debug route)

`MeetingsV2Controller` (path `meetings`, v2): single route `POST api/v2/meetings` — respects `meeting_moderation_enabled` flag.

`CalendarAvailabilityController` (path `meetings`, v1, sub-directory): all routes `JwtAuthGuard` + `@Features(Feature.ONLINE_MEETINGS)`.

`PublicMeetingsController` (path `public/meetings`, v1): **entirely unauthenticated, no FeatureGuard, no JwtAuthGuard**. All feedback routes, public meeting detail, and feedback-reminder trigger live here.

`ChatController` (path `chat/conversation`, v1, class `@UseGuards(FeatureGuard, JwtAuthGuard)`): all routes require `chat` feature and JWT, except `upload-logo` and the message file-upload routes (missing `@Features(Feature.CHAT)` metadata — see Watch out for).

`ConversationsController` (path `conversations`, v1): backs CometChat conversation envelope tracking. Several mutating routes may omit `@UseGuards(JwtAuthGuard)` — verify.

## Data flow

### Meeting scheduling
1. **Create** — `POST api/v1/meetings` (v1, always sends direct invite) or `POST api/v2/meetings` (v2, respects `meeting_moderation_enabled` flag; if on, routes to admin moderation instead of direct invite — different success response shape).
2. **Accept / reject** — `PATCH meetings/:uuid/accept` / `PATCH meetings/:uuid/reject`. Both dispatch `NotificationsActions.SetNotificationsCount` on success.
3. **Propose alternate time** — `POST meetings/:uuid/propose` (recipient only, once). `POST meetings/:uuid/propose/action` (host accepts/rejects the proposal).
4. **Join video call** — `MeetingComponent` calls `GET meetings/public/:meetingUUID` (no JWT) to load meeting detail, then initialises VideoSDK prebuilt with `meetingCode`. `meetingCode` is the VideoSDK room ID — not the UUID. Guard against null `meetingCode` (in-person or external-tool meetings have no VideoSDK room).
5. **Complete meeting** — `POST meetings/:meetingCode/complete` is called by the VideoSDK platform (no auth). Identified by `meetingCode`, not UUID.
6. **Meeting notes** — `GET/POST meetings/notes/:uuid`, `POST meetings/notes/:uuid/share` (emails notes to participants, empty body — backend resolves recipients).

### Calendar availability
- `GET meetings/users/calendar-availability` — own availability.
- `PATCH meetings/users/calendar-availability` — save own weekly schedule.
- **`getCalenderAvilablity()` in `MeetingService` returns a hardcoded static `of({...})` observable** — it does NOT call the backend. Do not confuse it with `getUsersAvailability()` which calls `GET meetings/users/calendar-availability`. The hardcoded method is dead/placeholder code.

### Chat (CometChat mode)
1. `ChatsWrapperComponent` reads `brandDetails.globalSettings.chat_type` to select the sub-implementation.
2. `ConversationsComponent` calls `CometChat.init(appId, appSettings)` then `CometChat.login(UID, AUTH_KEY)`.
3. All message transport is via the CometChat SDK; backend REST is not used for messaging.
4. `ChatService.sendChatEmail(grpId)` and `sendPlatformChatEmail(grpId)` call `POST conversations/send_chat_email/:grpId` and `POST conversations/send_chat_notification/:grpId` to fan out email/push alerts.

### Chat (in-house mode)
1. `ScConversationsComponent` fetches conversation list via `GET chat/conversation` (paginated).
2. `SocketService.setUrl(url)` is called when the tenant `apiUrl` resolves. After `setUrl`, callers MUST re-call `listenToRoom` and event subscriptions — the old `Socket` instance is discarded and subscriptions are not re-attached automatically.
3. Messages: `POST chat/conversation/:uuid/messages`. Real-time delivery via `SocketService.messages` Subject (not `BehaviorSubject` — messages emitted before subscription are lost).
4. File uploads: `POST chat/conversation/:uuid/messages-file` (no MIME filter on backend). Frontend should add client-side MIME validation.

## Feature flags

- `online_meetings` — gates all authenticated meeting routes. If off, all `api/v1/meetings/*` calls return 403.
- `meeting_moderation_enabled` — read at runtime in `createNewMeetingV2`. If the flag is not in the in-memory `saasFeatures` map (bootstrap hasn't populated it or it doesn't exist in the cockpit), the moderation branch is silently skipped — meetings are sent as direct invites instead of going to admin moderation.
- `chat` — gates all `api/v1/chat/*` routes. Also read in `meetingScheduledChatMessage` to decide whether to post a chat message after a meeting is accepted. If `chat` is undefined in `saasFeatures`, the chat message is silently skipped.
- `cc_desk_communication` — read at runtime to CC desk-admin email on meeting schedule/cancel. Involves two `AdminRolesEntity.find` + `AdminUsersEntity.find` queries per accepted-meeting email send (no caching).

Run `/trace-flag online_meetings`, `/trace-flag meeting_moderation_enabled`, `/trace-flag chat`, `/trace-flag cc_desk_communication` before any rename.

## API contract

- `createMeeting` v1 (`POST api/v1/meetings`) and v2 (`POST api/v2/meetings`) share the same DTO but differ in routing behavior. The v2 response shape differs when `meeting_moderation_enabled` is active — the frontend must handle both shapes.
- `proposeTime` can only be called by the meeting **recipient** (not the host), and only once. The backend returns an error if the host calls it or if a proposal already exists. Frontend must disable the "propose new time" option for the meeting host.
- `shareMeetingNotes` sends an empty body `{}` — the backend resolves recipients from the meeting entity. There is no client-side control over who receives the notes.
- Chat conversation and message UUIDs are validated with `ParseUUIDPipe` on the backend (returns 400 for non-UUIDs).

## Auth & security

Cross-repo security gaps:

1. **`GET meetings/feedback-reminder/trigger` is unauthenticated**: `JwtAuthGuard` is commented out. Any caller knowing the URL can trigger bulk SES feedback-reminder emails. A `console.log('Triggered feedback reminder via Postman')` in the source confirms this is a debug route left open in production.
2. **`POST meetings/:meetingCode/complete` has no auth**: VideoSDK webhook pattern, but `meetingCode` is not validated as a UUID and there is no caller verification. Any entity knowing a meeting code can mark it complete.
3. **`GET public/meetings/feedback-submitted/:meetingId/:email`** takes a raw `email` string with no auth — exposes all feedback submitted for a meeting to any caller who knows the integer `meetingId` and any one email that submitted feedback.
4. **`POST api/v1/public/meetings/:meetingUUID/submit-feedback`** is entirely unauthenticated — no JWT, no feature flag (public controller has no `FeatureGuard`). Any caller can submit feedback for any meeting UUID.
5. **`GET meetings/public/:meetingUUID`** has no `JwtAuthGuard` (VideoSDKGuard commented out). The full meeting entity is exposed to any caller with the UUID. Do not surface sensitive meeting fields in the join view.
6. **`upload-logo` and message file-upload routes in `ChatController` are missing `@Features(Feature.CHAT)` metadata.** The class-level `FeatureGuard` is present but without `@Features` metadata it does not gate on `chat`. These upload routes are effectively always accessible to authenticated users even if the `chat` flag is off.
7. **CometChat `AUTH_KEY`** is stored as a module-level constant (`COMETCHAT_CONSTANTS.AUTH_KEY`). This key must not be committed to version control or rendered to the DOM. It should be loaded from `globalSettings` rather than a static constant.

## Known issues / Watch out for

- **`getCalenderAvilablity()` returns hardcoded static data** and is not connected to the backend availability API. Do not use it for real scheduling — use `getUsersAvailability()`.
- **`EditMeetingComponent`, `DeleteMeetingComponent`, and `MeetingDetailsModalComponent`** are commented out of both `declarations` and `exports` in `CalenderModule`. They exist in the `calender-component/` folder but are not registered. Must be uncommented and imported before use.
- **`SocketService.setUrl(url)` creates a new `Socket` instance** and discards the old one. Event subscriptions on the old instance are not automatically re-attached. After any `setUrl` call, callers must re-call `listenToRoom` and re-subscribe to events.
- **CometChat Angular UI Kit is vendored** at `src/cometchat-pro-angular-ui-kit/` (not an npm package). If the kit version or path changes, all CometChat imports will break. Keep a record of the vendored version.
- **`MeetingsController` and `CalendarAvailabilityController` both register under path `meetings`/version `1`.** Route uniqueness is maintained only by path-segment differences. A future path clash will cause silent shadowing.
- **`sendScheduledMeetingEmail` fires two DB queries** (`AdminRolesEntity.find` + `AdminUsersEntity.find`) on every accepted-meeting email path when `cc_desk_communication` is on — no caching. High-volume deployments will see a significant DB read penalty on meeting acceptance.
- **`ConversationDetailsComponent` subscribes to `SocketService.messages` as a plain Subject** — messages emitted before the component subscribes are lost. Join the room and set up the subscription before the component is ready to render, not lazily.
