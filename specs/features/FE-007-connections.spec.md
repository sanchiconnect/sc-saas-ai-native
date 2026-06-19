---
id: FE-007
title: Connections & Wishlist
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - POST api/v1/connections/send/request
    - POST api/v1/connections/investor
    - PATCH api/v1/connections/accept/:connectionUUID
    - PATCH api/v1/connections/reject/:connectionUUID
    - DELETE api/v1/connections/:connectionUUID
    - GET api/v1/connections
    - GET api/v1/connections/requests/:type
    - GET api/v1/connections/types/counts
    - GET api/v1/connections/list/basic/all
    - POST api/v1/connections/check/request/:toUserUUID
    - POST api/v1/connections/upload/connection-document
    - POST api/v1/public/connections/action
    - POST api/v1/wishlist/create/:toUserUUID
    - GET api/v1/wishlist/:userId
    - DELETE api/v1/wishlist/:toUserUUID
  flags:
    - connections
    - connections_wishlist
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-007 — Connections & Wishlist

## Summary

Peer-to-peer connection requests between platform members: send, accept, reject, remove connections; manage a "saved for later" wishlist of profiles; and handle email-link accept/reject flows without requiring the recipient to be logged in. `ConnectionV4Module` is the active version; the legacy `connections-v3` module lives on as a synchronously loaded child providing filtered list views. The email-link flow is served by a separate `ConnectionApproveRejectPageModule` under a public layout.

## Frontend entry points

Module specs:
- `sc-saas-frontend/src/app/modules/connection-v4/module.spec.md`

Routes (lazy-loaded from `modules/connection-v4/`):
- `/connections` — `ConnectionV4Component` (overview)
- `/connections/:connectionsType` — `ConnectionsV3Component` (received / sent / rejected tabs; synchronously imported, not a separate lazy route)
- `/connections/saved-for-later` — `WishlistComponent`
- `/connections/active-requests` — hard redirect to `/connections`
- `/connection-action/:actionType` — `ConnectionApproveRejectPageComponent` (public layout, no `AuthGuard`)

Service: `ConnectionsService` (`providedIn: 'root'`). Subscribes to the NgRx `global` store `getBasicConnectionList` selector at construction to cache the `isConnected()` result. Notification badge counts (`pendingConnectionCount`, `sentConnectionCount`) are driven from `core/state/notifications/`.

`WishlistComponent` calls `GlobalService.getAllWhishlist()` — it does NOT have a dedicated service; the wishlist reads go through `GlobalService`. Save and delete operations also appear to route through `GlobalService` (confirm before assuming `WishlistComponent` is read-only).

## Backend modules

Module specs:
- `sc-saas-backend/src/modules/connections/module.spec.md`
- `sc-saas-backend/src/modules/connections-wishlist/module.spec.md`

`ConnectionsController` (path `connections`, v1): all routes `JwtAuthGuard` + `@Features(Feature.CONNECTIONS)` except the reminder callback (`POST :connectionUUID/reminder/:adminMd5`) which is open and authenticated only by the `adminMd5` path token. `create-group-chat/:connectionUUID` also lacks guards — see Watch out for.

`PublicConnectionController` (path `public/connections`, v1): `POST action` — token-less but still `@Features(Feature.CONNECTIONS)`.

`ConnectionsWishlistController` (path `wishlist`, v1): all routes `JwtAuthGuard` + `@Features(Feature.CONNECTIONS_WISHLIST)`.

## Data flow

1. **List & badge counts** — on module entry, `ConnectionsService` dispatches `GetBasicConnectionsList()` to populate the NgRx `global` store; `getConnectionsTypesCount()` populates tab badge counts.
2. **Send request** — `POST connections/send/request` (generic) or `POST connections/investor` (investor fast-path). Both return the same response shape; do not consolidate without checking backend business logic.
3. **Accept / reject** — `PATCH connections/accept/:uuid` / `PATCH connections/reject/:uuid`. Both dispatch `NotificationsActions.SetNotificationsCount` on success.
4. **Email-link flow** — recipient receives a link containing an action token. `ConnectionApproveRejectPageComponent` (no `AuthGuard`) calls `POST api/v1/public/connections/action` with `{ actionType: 'accept' | 'reject', token }`. The backend `PublicConnectionController` resolves and acts on the connection record without a JWT.
5. **Wishlist** — `WishlistComponent` fetches via `GlobalService.getAllWhishlist()` (`GET wishlist/:userId`). Save/delete go to `POST wishlist/create/:toUserUUID` and `DELETE wishlist/:toUserUUID`. The `toUserUUID` is a UUID string; the backend resolves it to a numeric `otherUserId` in the service.
6. **Document upload** — `POST connections/upload/connection-document` (`FileInterceptor`, 25 MB cap). Frontend must enforce a client-side size check; the backend returns a hard 413 beyond the limit.
7. **Online status** — `GET connections/check_user_online_status` (marked `@ApiExcludeEndpoint`; receives `userIds` as a comma-separated query string).

## Feature flags

- `connections` — gates all authenticated connection routes on the backend. Also gates `POST public/connections/action` — email-link flows will 403 if this flag is disabled for the tenant.
- `connections_wishlist` — gates all `api/v1/wishlist/*` routes. Frontend must hide `/connections/saved-for-later` or show a graceful empty state if this flag is off.

Both flags must exist in the cockpit (`sanchiconnect-saas-tenants` `TenantUsersEntity`) before use. Run `/trace-flag connections` and `/trace-flag connections_wishlist` before any rename or removal.

## API contract

Key shape notes for frontend consumers:

- `GET connections/types/counts` — returns per-status counts used to drive tab badges.
- `GET connections/requests/:type` — `type` must be a value from `ConnectionRequestType` enum (sent / received / rejected); backend throws `ConflictException` on unknown values.
- `GET connections/list/basic/all` — lightweight list; cached in `getBasicConnectionList` selector; must be dispatched at app bootstrap (not per-component) for `isConnected()` to be reliable.
- `POST connections/check/request/:toUserUUID` — check status with a specific user; also has a variant without the path param (`POST connections/check/request`).
- Wishlist `GET` route has two forms: `GET wishlist/:userId` and `GET wishlist/:userId/:userAccountType`. The two-segment form is declared first in the controller to avoid shadowing.

## Auth & security

- All authenticated connection endpoints require JWT; `ConnectionsService` attaches the token via the `JwtInterceptor`.
- `POST api/v1/public/connections/action` is intentionally token-less for email recipients who may not be logged in. It remains flag-gated — if `connections` is disabled the endpoint returns 403.
- `POST :connectionUUID/reminder/:adminMd5` is an admin-triggered route; the `adminMd5` token is the sole authenticator. This token must not appear in browser-visible URLs or logs.
- `GET connections/create-group-chat/:connectionUUID` has no guards (no `JwtAuthGuard`, no `@UseGuards`) — it relies only on knowing the UUID. Verify this is intentional before using it in any user-facing flow.

Cross-repo security gap: `POST connections/upload/connection-document` accepts any file type (only a 25 MB limit is enforced). The frontend should add a client-side MIME-type allowlist before upload.

## Known issues / Watch out for

- **Version history**: `ConnectionV4Module` imports `ConnectionsV3Module` synchronously. Do not register `connections-v3` as a separate lazy-loaded route in `app-routing` — it will conflict with the child routing in `connection-v4`.
- **Legacy `connections/` folder** contains only `connections.model.ts` (routing removed). If a routing module is ever added and registered in `app-routing` it will shadow `connection-v4` routes. Keep it model-only.
- **`WishlistComponent` calls `GlobalService`**, not a dedicated service. This is an architectural smell: global service responsibility is diffuse. Future work should introduce a `WishlistService` or wire the calls into `ConnectionsService`.
- **`isConnected()` reliability** depends on `getBasicConnectionList` being populated at bootstrap via `GetBasicConnectionsList()`. A component-level dispatch (rather than bootstrap-level) will cause multiple redundant fetches because `ConnectionsService` is `providedIn: 'root'`.
- **`checkOnlineStatus`** is `@ApiExcludeEndpoint` and excluded from Swagger, but is a real live endpoint. The `userIds` query param is a comma-separated string of UUIDs — document this in the service call signature.
- **Wishlist `userId` validation** uses `parseInt`; a value of `0` is rejected as falsy, and a non-integer string surfaces as a 500 (bare `throw new Error(...)`) rather than a 400. Frontend must pass a valid positive integer.
- **`SendConnectionRequest` vs `SendConnectionRequestFromInvestor`** — both POST to different backend endpoints with overlapping but distinct logic. Do not consolidate these calls without auditing the backend business rules for each path.
