---
id: FE-006
title: Community Feed
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET    api/v1/community-wall/posts
    - GET    api/v1/community-wall/posts/me/comments
    - GET    api/v1/community-wall/posts/me/reactions
    - GET    api/v1/community-wall/posts/me/stats
    - GET    api/v1/community-wall/posts/me/polls
    - GET    api/v1/community-wall/posts/user/:userUUID
    - GET    api/v1/public/community-wall/posts/:postUUID
    - POST   api/v1/community-wall/posts
    - PATCH  api/v1/community-wall/posts/:postUUID
    - DELETE api/v1/community-wall/posts/:postUUID
    - GET    api/v1/community-wall/posts/:postUUID/comments
    - POST   api/v1/community-wall/posts/:postUUID/comments
    - POST   api/v1/community-wall/posts/:postUUID/comments/:commentUUID/reply
    - DELETE api/v1/community-wall/posts/:postUUID/comments/:commentUUID
    - GET    api/v1/community-wall/posts/:postUUID/reactions
    - POST   api/v1/community-wall/posts/:postUUID/react/:reactionType
    - POST   api/v1/community-wall/posts/:postUUID/comment/:commentUUID/react/:reactionType
    - GET    api/v1/community-wall/posts/:postUUID/react/count
    - POST   api/v1/community-wall/posts/upload-file
    - POST   api/v1/community-wall/posts/poll/vote
    - GET    api/v1/notifications
    - GET    api/v1/notifications/count
    - PATCH  api/v1/notifications/mark-all-read
    - POST   api/v1/notifications/platform
    - POST   api/v1/notifications/cron/memberships/build
    - POST   api/v1/notifications/cron/memberships/send
    - POST   api/v1/notifications/cron/memberships/expired
    - POST   api/v1/notifications/cron/memberships/set-limit
    - POST   api/v1/notifications/cron/program/reapply
    - POST   api/v1/notifications/cron/community-wall/weekly-posts
  flags:
    - community_feed
  events: []
tenant_scoped: true
depends_on:
  - FE-001
updated: 2026-06-17
---

# FE-006 — Community Feed

## Summary
Member-facing social feed with real-time notification push. Users can post text, images, and polls; react to and comment on posts; view their own activity by type (comments, reactions, polls); and receive notifications in real time via Socket.IO. Ad slots are injected inline in the feed via `AdViewerModule`. The notification badge aggregates counts across multiple domain areas (connections, mentorship hours, meetings, messages, documents, program submissions). All community-wall routes are gated by the `community_feed` flag on the backend; the frontend has no Angular `FeatureGuard` in its routing configuration.

## Frontend entry points
Angular modules:
- `sc-saas-frontend/src/app/modules/community-feed/` — `CommunityFeedModule` (feed + post views)
- `sc-saas-frontend/src/app/modules/notifications/` — `NotificationsModule` (notification inbox)
- `sc-saas-frontend/src/app/modules/ad-viewer/` — `AdViewerModule` (shared, no route; injected into feed templates)

Routes (all lazy-loaded, all children of `ProtectedLayoutWrapperComponent`):

| Path | Component | Notes |
|---|---|---|
| `/community` | `CommunityFeedComponent` | Main feed list |
| `/community/posts/post/:id` | `CommunityFeedPostComponent` | Single post via public endpoint; accessible if shared without login but routed through protected layout |
| `/community/posts/user/:userId` | `CommunityFeedComponent` | Feed filtered to a specific user |
| `/community/posts/me/:type` | `CommunityFeedComponent` | `type ∈ comments\|reactions\|polls`; dispatches `getPostsByType()` |
| `/notifications` | `NotificationsComponent` | Notification inbox |

Services: `community-feed.service.ts`, `notifications.service.ts`, `socket.service.ts` (singleton Socket.IO wrapper).

NgRx:
- `core/state/feed/` — `feedStats: { totalComment, totalPost, totalPostReaction, totalPoll }`.
- `core/state/notifications/` — `count: { pendingConnectionCount, sentConnectionCount, unreadNotificationCount, unreadMessageCount, pendingAcceptanceMentorHoursCount, pendingDocumentsUploadCount, pendingProgramFormSubmissionCount, pendingAcceptanceMeetingCount }`.

## Backend modules
- `sc-saas-backend/src/modules/community-wall/module.spec.md` — post CRUD, comments, reactions, polls, file uploads
- `sc-saas-backend/src/modules/notifications/module.spec.md` — notification inbox, badge-count aggregation, Socket.IO push, cron triggers

## Data flow

### Feed load and pagination
1. User navigates to `/community`; `ProtectedLayoutWrapperComponent` ensures authentication.
2. `CommunityFeedComponent` calls `community-feed.service.ts` → `GET api/v1/community-wall/posts` with pagination params.
3. Backend: `@Features(Feature.COMMUNITY_FEED) + JwtAuthGuard`; queries `community-wall-posts` table filtered by `req.user`.
4. Response: paginated post list; each post includes author info, content, reaction counts, comment count.
5. `AdViewerComponent` slots are rendered between post cards via `AdViewerModule`.
6. Infinite scroll (`InfiniteScrollModule`) loads additional pages.

### Post creation
1. User clicks "Create Post"; `CommunityFeedFormModalComponent` opens.
2. Emoji picker (`@ctrl/ngx-emoji-mart`) available — requires the emoji dataset to be imported separately.
3. Optional image/file upload: `POST api/v1/community-wall/posts/upload-file` (multipart, 25 MB max). **No `@Features` gate on this endpoint** — only `JwtAuthGuard`. Upload succeeds regardless of `community_feed` flag state.
4. On submit: `community-feed.service.ts` → `POST api/v1/community-wall/posts` with `CreateCommunityWallPostDto`.
5. Backend: `@Features(Feature.COMMUNITY_FEED) + JwtAuthGuard`.
6. On success, service triggers `GetStats` action via `tap()` to refresh `feedStats` in NgRx.

### Post edit and delete
1. Author edits post: `PATCH api/v1/community-wall/posts/:postUUID` with `UpdateCommunityWallPostDto`.
2. Author deletes post: `DELETE api/v1/community-wall/posts/:postUUID`.
3. Both gated by `@Features(Feature.COMMUNITY_FEED) + JwtAuthGuard`.
4. Both trigger `GetStats` on success.

### Comments and threaded replies
1. User adds a comment: `POST api/v1/community-wall/posts/:postUUID/comments` with `AddCommunityPostCommentDto`.
2. User replies to a comment: `POST api/v1/community-wall/posts/:postUUID/comments/:commentUUID/reply`.
3. Reply delete uses the same `DELETE api/v1/community-wall/posts/:postUUID/comments/:commentUUID` endpoint as comment delete — there is no separate reply-delete endpoint; the `commentUUID` (or `replyId`) is used directly.
4. Comments: `GET api/v1/community-wall/posts/:postUUID/comments` (paginated).

### Reactions
1. User reacts to a post: `POST api/v1/community-wall/posts/:postUUID/react/:reactionType`.
2. `reactionType` is a path param validated by `ParseEnumPipe(ReactionType)` on the backend.
3. User reacts to a comment: `POST api/v1/community-wall/posts/:postUUID/comment/:commentUUID/react/:reactionType`.
4. Reaction count: `GET api/v1/community-wall/posts/:postUUID/react/count`.
5. All reaction endpoints gated by `@Features(Feature.COMMUNITY_FEED) + JwtAuthGuard`.
6. Service dispatches `GetStats` after each mutation.

### Poll voting
1. User votes on an attached poll: `POST api/v1/community-wall/posts/poll/vote` with `SubmitPollVoteDto`.
2. **No `@Features` gate on `poll/vote`** — only `JwtAuthGuard`. Poll votes can be submitted regardless of `community_feed` flag state.

### Public post sharing
1. User shares a post link; recipient opens `/community/posts/post/:id`.
2. `CommunityFeedService.getSinglePost(postId)` → `GET api/v1/public/community-wall/posts/:postUUID`.
3. **Fully unauthenticated** on the backend — no JWT, no flag gate. Post content is returned to any caller.
4. The route still renders through `ProtectedLayoutWrapperComponent`, so logged-in users see the full shell; unauthenticated users see the protected layout's auth redirect rather than a public page.

### Real-time notifications (Socket.IO)
1. After login, `SocketService.setUrl(apiUrl)` is called (must happen before any `listenToRoom` subscription).
2. `SocketService.listenToRoom(userId)` subscribes to `fetch-count` and all `SocketNotificationType` events for the authenticated user's room.
3. Server emits to the user's room on new notifications (connection requests, suggestions, etc.); frontend dispatches `SetNotificationsCount` to update the NgRx badge counter.
4. Socket.IO connection URL is set dynamically from the tenant `apiUrl` at bootstrap.

### Notification badge count
1. `notifications.service.ts` → `GET api/v1/notifications/count` (JWT required).
2. Backend fans out 5–7 concurrent `Promise.all` calls (connections, mentorship, meetings, chat, documents) then a sequential `getMeetingCount` for users with team members.
3. Response: `NotificationCountType` with all badge fields; dispatched to `core/state/notifications/`.
4. `PATCH api/v1/notifications/mark-all-read` bulk-marks all notification rows as read; returns updated `NotificationsCount`. Frontend must re-dispatch to NgRx — do not assume the count drops to zero from the action payload alone.

### Notification inbox
1. User navigates to `/notifications`; `NotificationsComponent` loads.
2. `notifications.service.ts` → `GET api/v1/notifications?pageNumber=&limit=` (paginated).
3. Backend enriches `CONNECTION_REQUEST`, `CONNECTION_ACTION`, `INVESTOR_SUGGESTION`, `STARTUP_SUGGESTION` types with inline secondary DB lookups (N+1 pattern per notification type).
4. `sendTo = ALL` (`PLATFORM_MESSAGE`) notifications are visible to every user on the tenant.

## Feature flags
- `community_feed` — backend: `@Features(Feature.COMMUNITY_FEED)` on all authed `CommunityWallController` routes except `weekly-post`, `upload-file`, and `poll/vote` (see Known issues); frontend: all community routes depend on this flag, but no Angular `FeatureGuard` is in the route config. The backend flag gate is the primary enforcement.

No additional flags gate the notifications surface — notification routes have no `FeatureGuard` and no `@Features` decorators.

## API contract

### `POST api/v1/community-wall/posts`
Request: `CreateCommunityWallPostDto` — text content, optional media keys, optional poll definition.
Response: `{ message, data: CommunityWallPostEntity }`.

### `POST api/v1/community-wall/posts/:postUUID/react/:reactionType`
`:reactionType` must be a valid `ReactionType` enum member. Backend enforces via `ParseEnumPipe`; invalid values return 400.
Response: `{ message, data }` — toggling behavior (react adds, re-react removes).

### `POST api/v1/community-wall/posts/poll/vote`
Request: `SubmitPollVoteDto` — `pollId`, `optionId`, `postUUID`.
No `@Features` gate — callable regardless of `community_feed` flag.

### `GET api/v1/notifications/count`
Response: `NotificationCountType` — `{ pendingConnectionCount, sentConnectionCount, unreadNotificationCount, unreadMessageCount, pendingAcceptanceMentorHoursCount, pendingDocumentsUploadCount, pendingProgramFormSubmissionCount, pendingAcceptanceMeetingCount }`.

### `GET api/v1/notifications`
Query: `pageNumber` (default 1), `limit` (default 10).
Response: paginated `NotificationsEntity` list with enriched `object` fields for suggestion types.
Potential query bug: see Known issues for the `andWhere/orWhere` precedence issue.

### `PATCH api/v1/notifications/mark-all-read`
Response: updated `NotificationsCount` object — always re-dispatch to NgRx; do not assume all counts are zero after this call.

## Auth & security

**Frontend:**
- All community routes: `ProtectedLayoutWrapperComponent` (JWT guard at layout level).
- No Angular `FeatureGuard` on community-feed routes. The backend flag gate is the sole enforcement; the Angular bundle for the module loads before any network check.
- `SocketService` singleton must have `setUrl()` called before any `listenToRoom` subscription; calling `setUrl` after subscriptions attach to the old socket instance.

**Backend:**
- Authed community-wall routes: `@Features(Feature.COMMUNITY_FEED) + JwtAuthGuard`.
- Three routes bypass the `community_feed` flag:
  - `GET weekly-post`: **no `@Features`, no `JwtAuthGuard`** — completely public and ungated.
  - `POST upload-file`: `JwtAuthGuard` only — authenticated but not flag-gated.
  - `POST poll/vote`: `JwtAuthGuard` only — authenticated but not flag-gated.
- `GET api/v1/public/community-wall/posts/:postUUID`: fully unauthenticated, no flag gate.
- Notification routes: `JwtAuthGuard` only, no `FeatureGuard`.
- Six `POST api/v1/notifications/cron/*` endpoints: **no guard at all** — completely open.

**Gaps:**
- `POST api/v1/notifications/cron/*` — 6 endpoints are unauthenticated and publicly reachable. Any external caller can trigger membership-expiry emails, community-wall weekly digests, or program reapply reminders. This is an intentional dev convenience but a security gap in production.
- `GET weekly-post` is unauthenticated and has no feature gate — returns weekly post data regardless of tenant config.
- `POST upload-file` and `POST poll/vote` are callable on a tenant with `community_feed` disabled.

## Known issues / Watch out for

- **6 cron-trigger POST endpoints are completely open (security gap).** `POST api/v1/notifications/cron/memberships/build`, `.../send`, `.../expired`, `.../set-limit`, `.../program/reapply`, `.../community-wall/weekly-posts` — all six have no `JwtAuthGuard`, no `FeatureGuard`, no `RolesGuard`. Any unauthenticated HTTP client can trigger membership expiry emails or community digest sends in production. If these must remain as escape hatches, they should at minimum require an `adminMd5` token or an internal-network IP allowlist.
- **`getNotifications` query precedence bug.** The `NotificationsRepository` QueryBuilder uses `.andWhere('toUserId = :userId').orWhere('sendTo = :sendTo')` without wrapping in a bracket group. TypeORM may generate `(X AND toUserId = userId) OR (sendTo = ALL)`, producing `(prior conditions AND toUserId check) OR sendTo=ALL`. This means `PLATFORM_MESSAGE` (sendTo=ALL) notifications may be returned to all users regardless of any preceding `andWhere` filter, potentially surfacing all broadcast notifications for every paginated call. Validate the generated SQL and wrap in `Brackets()`.
- **`community_feed` flag has 3 bypass routes.** `upload-file`, `poll/vote`, and `weekly-post` are not gated by `Feature.COMMUNITY_FEED`. If the feature is meant to be fully tenant-controlled, these three routes are gaps. The class-level `@UseGuards(FeatureGuard)` only enforces a gate where a method-level `@Features` is present — it does not enforce the class-level flag on methods that lack a method-level `@Features` decorator.
- **Socket.IO `setUrl` must precede `listenToRoom`.** If `SocketService.setUrl(apiUrl)` is called after `listenToRoom(userId)` has already subscribed (e.g. if the tenant `apiUrl` is resolved asynchronously after component init), the `fromEvent` subscriptions attach to the original empty socket instance and will never fire. Ensure `setUrl` is called in the app bootstrap flow before any community-feed component subscribes.
- **Emoji dataset must be imported explicitly.** `CommunityFeedFormModalComponent` uses `@ctrl/ngx-emoji-mart` — the emoji picker is blank if the emoji data asset is not imported. Confirm `@emoji-mart/data` is referenced in the app's assets or the module's import.
- **Reply-delete reuses comment-delete URL.** `deleteCommentReply` in `CommunityFeedService` calls `DELETE community-wall/posts/:postId/comments/:replyId` — the same URL shape as `deleteComment`. There is no separate backend route for deleting replies vs top-level comments; the backend uses the UUID to distinguish. Confirm the backend repository method handles both cases via UUID lookup.
- **`GET notifications/messages` always routes to CometChat.** `NotificationsController.getMessages` delegates to `CometChatSDKervice.getMessagesWithCount` regardless of the tenant's `CHAT_TYPE` setting. Tenants configured for in-house chat will receive CometChat errors from this endpoint.
- **`sendTo = ALL` notifications are unguarded write.** `POST api/v1/notifications/platform` (which inserts a `PLATFORM_MESSAGE` with `sendTo = ALL`) is guarded by `JwtAuthGuard` but has no role guard — any authenticated user can broadcast a platform-wide message to all users on the tenant.
- **N+1 enrichment in `getNotifications`.** The notification list enriches `INVESTOR_SUGGESTION` and `STARTUP_SUGGESTION` types with per-notification DB lookups inside a loop. For a default page size of 10, this can generate up to 10 additional queries per suggestion type. Consider batch-fetching suggestions outside the loop.
- **`AdViewerModule` re-export requirement.** `AdViewerComponent` and `PipesModule` must be re-exported via `AdViewerModule` for sibling modules (`CommunityFeedModule`, etc.) to use them without redeclaring. Do not import `AdViewerComponent` directly from its file path.
