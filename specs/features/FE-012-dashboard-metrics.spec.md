---
id: FE-012
title: Dashboard & Growth Metrics
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET api/v1/dashboards/user
    - GET api/v1/dashboards/content
    - GET api/v1/metrics/all
    - GET api/v1/metrics/types/all
    - POST api/v1/metrics
    - PATCH api/v1/metrics
    - PATCH api/v1/metrics/request-update
    - GET api/v2/metrics/charts
    - GET api/v2/metrics/reviewers
    - PUT api/v2/metrics/reviewers
    - POST api/v2/metrics/reviewers/invite
    - GET api/v2/metrics/reviewer/metrics-list
    - GET api/v2/metrics/reviewer/metrics/:startupUUID/details
    - GET api/v2/metrics/reviewer/metrics/:startupUUID/charts
  flags:
    - growth_metrics
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-012 — Dashboard & Growth Metrics

## Summary

Role-aware home dashboard aggregating notification counts, upcoming meetings, events, news, and report downloads. Growth metrics entry, editing, chart visualisation (ApexCharts), and a reviewer access model that lets a startup share its time-series metric data with nominated external users. A print-layout companion (`GrowthMatricsPrintModule`) shares chart components for PDF export. `MarketInsightsModule` provides a separate nested intelligence surface (deals, investors, sectors, news) under `/market-insights`. The `growth-matrics` folder-name typo is load-bearing — do not rename without a full router sweep.

## Frontend entry points

Module spec:
- `sc-saas-frontend/src/app/modules/dashboard-v2/module.spec.md`

Routes (lazy-loaded):
- `/dashboard` — `DashboardV2Component` (embedded by role-specific modules; no router config in `dashboard-v2.module.ts` itself)
- `/growth-matrics` — `GrowthMatricsComponent` (title "Reports"; `ProtectedLayoutWrapperComponent`)
- `/growth-matrics-print` — `GrowthMatricsPrintComponent` (no nav chrome — print-only layout)
- `/market-insights/...` — 20+ sub-routes under `MarketInsightsModule` (`ProtectedLayoutWrapperComponent`; no per-route `AuthGuard` or feature-flag check — gating must happen in parent route or inside components)

`DashboardV2Module` exports `DashboardV2Component` but declares no lazy route — it is imported directly by role-specific routing modules which embed it.

Services:
- `DashboardV2Service` (`core/service/dashboard-v2.service.ts`): `getDashboardUserData()` and `getDashboardContent()`.
- `MetricsService` (`core/service/metrics.service.ts`): all metrics and reviewer API calls. Uses `ENDPOINT.MATRICS` constant (typo, matches folder). `getEndpoint(..., true)` selects the v2 context.

State: role-specific NgRx slices (`startup-dashboard`, `investor-dashboard`, `corporate-dashboard`, etc.). `MetricsService` dispatches to `startup-dashboard` and `startup` slices after saves. `GrowthMatricsModule` and `MarketInsightsModule` do not own their own NgRx slices.

Libraries: `ng-apexcharts` / `apexcharts` — time-series and bar charts in `MatricsChartsComponent`. `GrowthMatricsSharedModule` (declared in `modules/growth-matrics/growth-matrics-shared.module.ts`) is shared between `GrowthMatricsModule` and `GrowthMatricsPrintModule`.

## Backend modules

Module specs:
- `sc-saas-backend/src/modules/dashboard/module.spec.md`
- `sc-saas-backend/src/modules/metrics/module.spec.md`

`DashboardController` (path `dashboards`, v1): two read-only aggregation endpoints (`GET user`, `GET content`). Both require `JwtAuthGuard`. No feature flags. Pure fan-out — no owned entities.

`MetricsController` (path `metrics`, v1, class `@UseGuards(FeatureGuard)`): CRUD for metric values. `POST`, `PATCH`, `DELETE`, and `PATCH request-update` are `STARTUP`-role-only. Read routes (`GET`, `GET all`, `GET types/*`) allow `STARTUP|INVESTOR|CORPORATE|MENTOR|PARTNER` roles. All gated by `@Features(Feature.GROWTH_METRICS)` + `JwtAuthGuard`.

`MetricsV2Controller` (path `metrics`, v2, class `@UseGuards(FeatureGuard)`): chart aggregation + reviewer management. Startup-only routes: `GET reviewers`, `PUT reviewers`, `DELETE reviewers/:uuid`, `POST reviewers/invite`. Reviewer read routes (`GET reviewer/metrics-list`, `GET reviewer/metrics/:startupUUID/details`, `GET reviewer/metrics/:startupUUID/charts`) have `JwtAuthGuard` but **no `RolesGuard`** — any authenticated user can call them.

## Data flow

1. **Dashboard home** — on entry, `DashboardV2Service.getDashboardUserData()` calls `GET dashboards/user` for notification counts, upcoming meetings, and upcoming events. `getDashboardContent()` calls `GET dashboards/content` for report downloads, news, and webinars.
   - Note: the `videos` field in the content response comes from `GlobalService.getAllWebinars()` — a naming mismatch; frontend `IDashboardContent` must use `videos`, not `webinars`, as the property key.
2. **Metrics list** — `MetricsService.getMetrics()` → `GET metrics/all`. Response bucketing depends on `saasSettings[SaaSSettingKey.GROWTH_METRICS_DURATION]`: `'quarterly'` → quarter string; otherwise → `YYYY-M` month. A scaffold of all periods since startup approval is pre-populated with empty arrays.
3. **Submit metrics** — `MetricsService.saveMetrics(payload)` → `POST metrics` (body: `{ metrics: [{ metricTypeId, date, value }] }`). Backend bulk-inserts and upserts a `MetricsDefaultersEntity` row marking `dataUploaded = true`.
4. **Update metrics** — `PATCH metrics` (body: `{ metrics: [{ metricUUID, metricValue }] }`). `canEdit` flag must be `true` — set to `false` after each edit. Only an out-of-band admin action can re-enable it. `requestUpdate` (`PATCH metrics/request-update`) triggers a review request with a `requestMessage`.
5. **Charts** — `GET api/v2/metrics/charts`. Bucketing caveat: `getSubmittedMetrics` (v1) buckets by `createdAt` month; `getAllSubmittedMetrics` (v1) and reviewer charts bucket by `metric.date`. Two v1 endpoints show different groupings for the same data — do not mix them in the same chart.
6. **Reviewer management** — `PUT api/v2/metrics/reviewers` replaces the full reviewer list. Newly added reviewers receive SES email + optional WhatsApp notification via `sendReviewerMetricAllotmentEmail`. `POST reviewers/invite` checks `authService.checkUserAlreadyExist` and sends a registration deep-link with a `uuidv4` invitation code. **That code is never persisted** — it cannot be redeemed server-side.
7. **Reviewer reads** — `GET reviewer/metrics-list` (reviewer's assigned startups), `GET reviewer/metrics/:startupUUID/details`, `GET reviewer/metrics/:startupUUID/charts`. Any authenticated user can call these endpoints (no `RolesGuard`); access scoping relies on the repository-level check that the caller is in the startup's reviewer list.
8. **Print layout** — `/growth-matrics-print` renders `GrowthMatricsPrintComponent` which shares `GrowthMatricsSharedModule` for chart components. No nav chrome.

## Feature flags

- `growth_metrics` — gates all `MetricsController` (v1) and `MetricsV2Controller` (v2) routes. If off, `MetricsService` calls will return 403. `GrowthMatricsModule` must check `features.growth_metrics` before rendering the metrics UI.
- Must exist in the cockpit. Run `/trace-flag growth_metrics` before any rename.
- No feature flag gates dashboard routes (`GET dashboards/user`, `GET dashboards/content`) — the dashboard always renders even when sub-features (news, events) are flagged off elsewhere. Sub-services decide what they return.

## API contract

- Metric v1 `GET metrics` and `GET metrics/all` both exist but bucket by different date fields (`createdAt` vs `metric.date`). Do not use `GET metrics` and `GET metrics/all` interchangeably.
- `GET api/v2/metrics/charts` and `GET api/v1/metrics/all` are separate endpoints for different contexts (reviewer charts vs startup's own submissions). The frontend `MetricsService.getCharts()` uses the v2 endpoint; `getMetrics()` uses v1.
- Invite code generated by `POST reviewers/invite` is a `uuidv4` that is never persisted. The email recipient cannot redeem this code server-side — the invite flow is incomplete. Do not surface this as a working invite until the code is persisted.
- `console.log('quarters', ...)` remains in `getAllSubmittedMetrics` — leaks startup metric data to stdout in production. Remove before enabling on high-privacy tenants.

## Auth & security

- **Reviewer read routes (`GET reviewer/metrics-list`, `GET reviewer/metrics/:startupUUID/details`, `GET reviewer/metrics/:startupUUID/charts`) have no `RolesGuard`** — any authenticated user can call them. Access control relies entirely on repository-level scoping (checking the caller is in `MetricsReviewersEntity.reviewerIds`). If the repository check is ever bypassed or incorrectly implemented, any authenticated user can read any startup's growth metrics.
- Dashboard aggregation in `DashboardService` reaches directly into many sibling repositories (not just services). A signature change to any `getXById` or `getMeetings` repo method breaks the dashboard build — this is a blast-radius concern.
- `GET api/v2/metrics/reviewer/metrics/:startupUUID/details` and `/charts`: the `startupUUID` param is not further validated beyond being a UUID. Confirm the repository-level reviewer check validates both that the startup exists and that the caller is specifically in that startup's reviewer list.

## Known issues / Watch out for

- **Folder name typo is load-bearing**: `modules/growth-matrics/` (not `growth-metrics`), service constant `ENDPOINT.MATRICS`, and the lazy-load path in `app-routing` all use the `matrics` spelling. Do NOT rename the folder without also updating `app-routing.module.ts`, the `ENDPOINT.MATRICS` constant, and all lazy-load path references.
- **`MarketInsightsModule` has no per-route `AuthGuard` or feature flag check** on any of its 20+ child routes. Role and flag gating must happen via the parent route guard in `app-routing.module.ts` or inside the components themselves. If the parent guard is removed, all market insights pages become open to any authenticated user.
- **`DashboardV2Module` declares no router config** of its own — it is embedded by role-specific modules. Changes to the exported `DashboardV2Component` selector affect every role dashboard simultaneously.
- **`getDashboardContent` response `videos` field** comes from `GlobalService.getAllWebinars()` — a naming mismatch. Frontend `IDashboardContent` domain model must use `videos` not `webinars` as the property key.
- **`MetricsCustomChartsEntity` is registered in `TypeOrmModule.forFeature`** but no repository or service method references it — dead registration consuming a DB table slot.
- **Large commented-out `updateMetrics` loop** at lines 386–396 in `MetricsService` — leftover dead code; not load-bearing but should be removed.
- **`GrowthMatricsPrintModule` deliberately omits `ProtectedLayoutWrapperComponent`** — print pages render without nav. Ensure route-level auth is still enforced by the parent route guard before allowing access to print routes.
