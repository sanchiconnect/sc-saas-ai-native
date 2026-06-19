---
id: FE-004
title: Challenge Lifecycle
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - POST api/v1/challenges
    - GET  api/v1/challenges/corporate
    - GET  api/v1/challenges/:challengeUUID/info
    - GET  api/v1/challenges/:challengeUUID/participants/list
    - PATCH api/v1/challenges/:challengeUUID
    - PATCH api/v1/challenges/:challengeUUID/status
    - DELETE api/v1/challenges/:challengeUUID
    - GET  api/v1/challenges/search
    - GET  api/v1/challenges/:challengeUUID/necessary-info
    - POST api/v1/participants/:challengeUUID/apply
    - GET  api/v1/participants/applied-challenges/list
    - PATCH api/v1/participants/applied-challenges/:participantChallengeUUID
    - GET  api/v1/public/search/challenges
    - GET  api/v1/public/challenges/:challengeUUID
    - POST api/v1/public/challenges
    - GET  api/v1/challenges/collections
    - GET  api/v1/challenges/collections/:id
    - GET  api/v1/challenges/collections/byUUID/:uuid
    - GET  api/v1/corporates/corporateBackdoorAccess/:cfaId
    - PATCH api/v1/jobs/hiring-profile
  flags:
    - business_challenges
    - business_challenge_collections_enabled
    - corporates
    - startups
  events: []
tenant_scoped: true
depends_on:
  - FE-001
updated: 2026-06-17
---

# FE-004 — Challenge Lifecycle

## Summary
Business Challenges are corporate-created innovation challenges that startups discover and apply to. The lifecycle covers corporate creation and management of challenges, public discovery and browsing via challenge collections, participant application via the in-app modal, and the CFA (Call for Applications) backdoor access path for corporates who reach a challenge via an external link. The entire surface is gated by the `business_challenges` flag; collections require an additional `business_challenge_collections_enabled` flag.

## Frontend entry points
Angular modules:
- `sc-saas-frontend/src/app/modules/challenges/` — `ChallengesModule` (corporate create/manage)
- `sc-saas-frontend/src/app/modules/challenge-details/` — `ChallengeDetailsModule` (recruiter detail + participants)
- `sc-saas-frontend/src/app/modules/challenge-search/` — `ChallengeSearchModule` (public search)
- `sc-saas-frontend/src/app/modules/challenge-public-details/` — `ChallengePublicDetailsModule` (public detail + apply)
- `sc-saas-frontend/src/app/modules/challenge-public-view/` — `ChallengePublicViewModule` (browse wrapper + `ChallengeCollectionComponent`)

Routes:

| Route | Module | Flag gate | Notes |
|---|---|---|---|
| `/challenges` | `ChallengesModule` | `business_challenges` | Corporate challenge list |
| `/challenges/create` | `ChallengesModule` | `business_challenges` | Challenge creation form |
| `/challenges/:id/edit` | `ChallengesModule` | `business_challenges` | Challenge edit form |
| `/challenges/:id/details` | `ChallengeDetailsModule` | `business_challenges` | Corporate detail + participants |
| `/search/challenges` | `ChallengeSearchModule` | `business_challenges` | Public search (see duplicate route bug) |
| `/search/challenges/:id` | `ChallengePublicDetailsModule` | `business_challenges` | Public detail + apply |
| `/search_challenges` | `ChallengePublicViewModule` | `business_challenges` | Browse wrapper |
| `/search_challenges/collection/:id/:slug` | `ChallengePublicViewModule` | `business_challenge_collections_enabled` | Collection detail |

`ChallengeCollectionComponent` is declared in `ChallengePublicViewModule`, not in a standalone module. The `challenge-collection/` directory exists but has no `module.ts`.

Service: `challenge.service.ts`.
NgRx: `core/state/challenges/` — `challengesList`, `challengesLoading`, `challengesError`.

## Backend modules
- `sc-saas-backend/src/modules/challenges/module.spec.md` — challenge CRUD, participant flows, public routes, collections
- `sc-saas-backend/src/modules/application-management/module.spec.md` — CFA/program application programs (used by challenge form via `corporateBackdoorAccess`)

## Data flow

### Challenge creation (corporate)
1. Corporate user navigates to `/challenges/create`; component redirects to `/errors/404` if `brandDetails.features.business_challenges` is falsy.
2. `ChallengeFormComponent` collects challenge details; optional company logo uploaded via `POST api/v1/public/challenges` (multipart, 25 MB, `companyLogo` file field) — this is the CFA/public create path, no auth.
3. For authenticated corporate creates: `challenge.service.ts` → `POST api/v1/challenges` with `CreateChallengeDto`.
4. Backend `ChallengesController`: `@UseGuards(FeatureGuard)` + `@Features(Feature.BUSINESS_CHALLENGES, Feature.CORPORATES)` + `JwtAuthGuard` + `RolesGuard(CORPORATE)`.
5. On success, NgRx `GetChallengesList` is dispatched to refresh the corporate list.
6. Challenge form also calls `PATCH api/v1/jobs/hiring-profile` to check hiring profile completeness — this is a shared no-op endpoint from the jobs module (see Known issues).

### Challenge editing and status management
1. `PATCH api/v1/challenges/:challengeUUID` — update challenge details (same role/flag gates as create).
2. `PATCH api/v1/challenges/:challengeUUID/status` — change status (open, closed, etc.).
3. `DELETE api/v1/challenges/:challengeUUID` — permanently delete a challenge.
4. After each mutation, component re-dispatches `GetChallengesList`.

### Public discovery and search
1. User navigates to `/search/challenges` (both authenticated and unauthenticated).
2. `challenge.service.ts` → `GET api/v1/public/search/challenges` with filter params.
3. Backend `SearchController`: **no `@Features` gate** on `searchChallenges` — this endpoint fires regardless of tenant configuration (unlike all other search endpoints).
4. Response: paginated challenge list; `ChallengeSearchComponent` renders avatar cards.
5. User clicks challenge → `/search/challenges/:id` → `ChallengePublicDetailsComponent` → `GET api/v1/public/challenges/:challengeUUID`.
6. Backend `PublicChallengesController`: **no auth, no `FeatureGuard`** — the public detail always returns regardless of the `business_challenges` flag.

### Challenge collections
1. User navigates to `/search_challenges/collection/:id/:slug`; components redirect to 404 if `business_challenge_collections_enabled` is falsy.
2. `challenge.service.ts` → `GET api/v1/challenges/collections/byUUID/:id` for a single collection.
3. `GET api/v1/challenges/collections` for all collections listing.
4. Collections routes: `GET api/v1/challenges/collections`, `GET api/v1/challenges/collections/:id`, `GET api/v1/challenges/collections/byUUID/:uuid` — no JWT or role required; gated only by `@Features(Feature.BUSINESS_CHALLENGES)` via the class-level `FeatureGuard`.
5. `ChallengeCollectionComponent` (declared in `ChallengePublicViewModule`) renders the collection detail with member challenges listed.

### Participant application flow (startup)
1. Startup user on the public detail page clicks Apply; `ChallengeApplicationModalComponent` (from `shared/common-components/`) renders a dynamic form.
2. `challenge.service.ts` → `POST api/v1/participants/:challengeUUID/apply` with `ApplyChallengeDto`.
3. Backend `ChallengeParticipantsController`: `JwtAuthGuard` + `RolesGuard(STARTUP)` + rate-limit (3 req/60 s). **No `FeatureGuard` at the controller level** and **no `@Features` on any handler** — startup apply bypasses the `business_challenges` flag entirely on the server; the frontend flag check is the only enforcement.
4. Application row created with `challenge-participants.entity.ts`.
5. Startup can track applications via `GET api/v1/participants/applied-challenges/list` and update submissions via `PATCH api/v1/participants/applied-challenges/:participantChallengeUUID`.

### CFA backdoor access
1. A corporate user arrives at a challenge from an external Call-for-Applications link carrying a `cfaId`.
2. `challenge.service.ts` → `GET api/v1/corporates/corporateBackdoorAccess/:cfaId`.
3. This crosses into the `corporates` backend module — not the `challenges` module. The call establishes the CFA context; subsequent challenge form submission uses the CFA data.
4. This cross-module call is not reflected in the challenges backend spec.

## Feature flags
- `business_challenges` — backend: gating via `@Features(Feature.BUSINESS_CHALLENGES)` on the `ChallengesController` class and individual handlers; **not** applied to `ChallengeParticipantsController` (unintentional gap); frontend: all challenge components redirect to 404 if this flag is falsy.
- `business_challenge_collections_enabled` — frontend: gates collection routes; **not explicitly gated on the backend** collection endpoints beyond the class-level `@Features(Feature.BUSINESS_CHALLENGES)`.
- `corporates` — backend: co-gates all `ChallengesController` corporate-side routes alongside `business_challenges` (`@Features(Feature.BUSINESS_CHALLENGES, Feature.CORPORATES)`).
- `startups` — backend: co-gates startup-side routes in `ChallengesController` (`@Features(Feature.BUSINESS_CHALLENGES, Feature.STARTUPS)`).

All four flags map to the corresponding keys in `IBrandDetails.features` in the frontend NgRx global store.

## API contract

### `POST api/v1/challenges`
Request: `CreateChallengeDto` — title, description, reward, deadline, sector interests, tags, etc.
Response: `{ message, data: ChallengeEntity }`.

### `GET api/v1/public/search/challenges`
Query: `ChallengeSearchDto` — keyword, filters, `pageNumber`, `limit`.
Response: paginated challenge summary list. **No feature gate** — always returns regardless of tenant config.

### `POST api/v1/participants/:challengeUUID/apply`
Request: `ApplyChallengeDto` — application form data.
Response: `{ message, data: ChallengeParticipantsEntity }`.
Rate-limited: 3 requests per 60 s per key prefix `CHALLENGE_APPLY`.

### `POST api/v1/public/challenges`
Request: `CreatePublicChallengeDto` (multipart/form-data, `companyLogo` file ≤ 25 MB).
Response: `{ message, data: ChallengeEntity }`.
**No auth, no FeatureGuard** — publicly reachable.

### `GET api/v1/challenges/collections/byUUID/:uuid`
Response: `{ message, data: ChallengeCollectionsEntity }` — includes the challenges array within the collection.

**NgRx type mismatch:** `GetChallengesListSuccess` in the frontend NgRx slice is typed as `PartnersInformation` (a copy-paste from the partners state slice). The actual runtime payload is challenge data. TypeScript will not catch shape mismatches between the challenges API response and partner-typed state — do not add compile-time assertions to this slice without fixing the type first.

## Auth & security

**Frontend:**
- All challenge routes are under `ProtectedLayout` — they require a logged-in user.
- Flag checks are component-level (`*ngIf` and redirect to `/errors/404`); no Angular `FeatureGuard` in the route config.
- CFA public create (`POST api/v1/public/challenges`) is intentionally unauthenticated; the frontend routes corporate users through the auth flow before reaching this point.

**Backend:**
- Corporate management routes: `@Features(Feature.BUSINESS_CHALLENGES, Feature.CORPORATES) + JwtAuthGuard + RolesGuard(CORPORATE)`.
- Startup discovery/application routes in `ChallengesController`: `@Features(Feature.BUSINESS_CHALLENGES, Feature.STARTUPS) + JwtAuthGuard + RolesGuard(STARTUP)`.
- `ChallengeParticipantsController`: `JwtAuthGuard + RolesGuard(STARTUP)` only — **no `FeatureGuard`, no `@Features`**.
- `PublicChallengesController`: **no auth, no `FeatureGuard`** — public create and read are always accessible.
- `reject/:challengeId/:adminMd5`: `@UseGuards(JwtAuthGuard)` is commented out — security rests entirely on `adminMd5` token validation.

**Gaps:**
- `GET api/v1/public/search/challenges` (in `SearchController`) has no `@Features` gate.
- `ChallengeParticipantsController` apply/list/update routes have no `business_challenges` flag gate — a startup can apply to a challenge on a tenant that has disabled the `business_challenges` flag.
- `POST api/v1/public/challenges` accepts uploads without any flag or auth check.

## Known issues / Watch out for

- **Duplicate lazy-load path (routing bug, critical).** Both `ChallengeSearchModule` and `ChallengePublicDetailsModule` are registered at the path `/search/challenges` in `app-routing.module.ts`. Angular matches the first registration and silently ignores the second. Depending on ordering, either the search list or the detail page may be unreachable. Verify which module is registered first and deduplicate the path.
- **Wrong NgRx payload type.** `GetChallengesListSuccess` is typed as `PartnersInformation` (a partners state model copied in error). Runtime data is challenge data. TypeScript will not surface shape mismatches through this action. Fix the type to `IChallenges[]` before adding any typed selectors that derive from this action.
- **`PATCH jobs/hiring-profile` cross-domain call.** `challenge.service.ts` calls a jobs endpoint from the challenges service. This is a cross-module frontend dependency: renaming `COMPLETE_HIRING_PROFILE` in `ApiEndpointService` or the backend `jobs/hiring-profile` path breaks the challenge form too. The backend endpoint is also a no-op (body commented out).
- **`ChallengeParticipantsController` is not flag-gated.** Participant apply/list/update routes bypass `business_challenges` on the server. A tenant that disables challenges cannot prevent startups from applying to existing challenge rows via the API.
- **`PublicChallengesController` and `PublicChallengeParticipantController` guard state.** The public challenge create has no flag gate or auth. The `PublicChallengeParticipantController` is declared but its only route is commented out — treat as dead surface.
- **`corporateBackdoorAccess` crosses module boundaries.** The challenges service calls `GET api/v1/corporates/corporateBackdoorAccess/:cfaId`, which is owned by the `corporate` module. This cross-module call is undocumented in the challenges module spec and means a change to the corporate backdoor-access endpoint silently breaks the challenge CFA flow.
- **Route ordering in `ChallengesController`.** Literal paths (`/search`, `/collections`, `/reject/:id/:adminMd5`) must be declared before the `/:challengeUUID` wildcard to avoid being captured. Preserve this ordering when adding challenge routes.
- **`ChallengeCollectionComponent` declaration scope.** `ChallengeCollectionComponent` is declared inside `ChallengePublicViewModule`. Any module that needs to reference it must import the entire view module; it cannot be used standalone.
