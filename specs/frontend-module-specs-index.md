---
type: index
repo: frontend
updated: 2026-06-17
---

# Frontend Module Specs — Index

All 26 `sc-saas-frontend` modules have a `module.spec.md`. This index maps each module to its spec, summarises its role, and flags security/quality notes surfaced during spec authoring.

> **How to use:** When working on a module, read its spec first — it records owned routes, Angular modules covered, consumed feature flags, backend modules called, and known footguns. When adding a route or flag gate, update the spec's `flags` / `backend_modules` frontmatter and `updated` date.

---

## Infrastructure

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `core` | [spec](../sc-saas-frontend/src/app/core/module.spec.md) | `CoreModule`, `HttpInterceptorModule`, `ServiceModule`, `StateModule` (38 NgRx effects) | *(none — infrastructure)* | `global` (cockpit verify_tenant + reference data, events, news, wishlist) |
| `shared` | [spec](../sc-saas-frontend/src/app/shared/module.spec.md) | `SharedModule`, `PipesModule` | `connections`, `community_feed`, `jobs`, `business_challenges`, `chat`, `online_meetings`, `certificates`, `startup_id_cards` | *(none — presentation/utility layer)* |

---

## Auth

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `auth` | [spec](../sc-saas-frontend/src/app/modules/auth/module.spec.md) | `AuthModule`, `AdminActionsModule`, `ConnectionRequestActionEmailModule` | `job_seekers`, `startups`, `single_session_login_enabled`, `external_sign_in_enabled` | `auth`, `auth-external`, `global` (admin-actions backdoor-login) |

---

## Stakeholder Profiles

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `startup` | [spec](../sc-saas-frontend/src/app/modules/startups/module.spec.md) | `StartupsModule`, `StartupFormsModule`, `PitchDeckRecorderModule`, `PitchDeckManagementComponent` | `startups`, `startup_financial_form`, `startup_supporting_documents`, `logout_on_rejection` | `startup` |
| `investor` | [spec](../sc-saas-frontend/src/app/modules/investors/module.spec.md) | `InvestorsModule` | `investors` | `investor` |
| `corporate` | [spec](../sc-saas-frontend/src/app/modules/corporate/module.spec.md) | `CorporateModule` | `corporates`, `logout_on_rejection` | `corporate` |
| `mentor` | [spec](../sc-saas-frontend/src/app/modules/mentors/module.spec.md) | `MentorsModule`, `TrackerModule` | `mentors`, `mentor_hours`, `logout_on_rejection` | `mentors`, `mentorship` |
| `partner` | [spec](../sc-saas-frontend/src/app/modules/partners/module.spec.md) | `PartnersModule` | `partners`, `logout_on_rejection` | `partner` |
| `service-provider` | [spec](../sc-saas-frontend/src/app/modules/service-provider/module.spec.md) | `ServiceProviderModule` | `service_providers`, `logout_on_rejection` | `service-providers` |
| `individual` | [spec](../sc-saas-frontend/src/app/modules/individuals/module.spec.md) | `IndividualProfileModule`, `TeamModule` | `individuals`, `logout_on_rejection`, `multiple_profiles`, `can_delete_profile`, `can_deactivate_profile`, `profiles_locked`, `limited_access` | `individual`, `user` |

---

## Jobs & Challenges

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `jobs` | [spec](../sc-saas-frontend/src/app/modules/hire/module.spec.md) | `HireModule`, `JobSearchModule`, `JobDetailsModule`, `JobPublicDetailsModule`, `JobInterviewModule`, `AppliedJobsModule` | `jobs`, `job_seekers` | `job` |
| `challenges` | [spec](../sc-saas-frontend/src/app/modules/challenges/module.spec.md) | `ChallengesModule`, `ChallengeDetailsModule`, `ChallengeSearchModule`, `ChallengePublicDetailsModule`, `ChallengeCollectionModule`, `ChallengePublicViewModule` | `business_challenges`, `business_challenge_collections_enabled` | `challenges` |

---

## Programs & Events

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `programs` | [spec](../sc-saas-frontend/src/app/modules/programs/module.spec.md) | `ProgramsModule`, `VsProgramsModule`, `CallForApplicationsModule`, `ProgramOfficeModule`, `ProgramOfficeTeamModule` | `startups`, `webinar_videos`, `programs_public_view` | `program-management`, `application-management`, `vs-programs-management`, `form-management`, `meetings` |
| `event-agenda` | [spec](../sc-saas-frontend/src/app/modules/event-agenda/module.spec.md) | `EventAgendaModule`, `PublicEventsModule`, `WebinarsModule` | `events`, `webinar_videos` | `global` (events + webinars via GlobalService) |

---

## Communication

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `meetings` | [spec](../sc-saas-frontend/src/app/modules/meetings/module.spec.md) | `MeetingsModule`, `CalenderModule` | `online_meetings`, `meeting_moderation_enabled`, `chat` | `meetings` |
| `chat` | [spec](../sc-saas-frontend/src/app/modules/chat/module.spec.md) | `ChatModule` | `chat` | `chat` |
| `community-feed` | [spec](../sc-saas-frontend/src/app/modules/community-feed/module.spec.md) | `CommunityFeedModule`, `NotificationsModule`, `AdViewerModule` | `community_feed` | `community-wall`, `notifications` |
| `notifications` | [spec](../sc-saas-frontend/src/app/modules/notifications/module.spec.md) | `NotificationsModule` | none | `notifications` (REST + WebSocket) |
| `connection-v4` | [spec](../sc-saas-frontend/src/app/modules/connection-v4/module.spec.md) | `ConnectionV4Module`, `ConnectionsV3Module`, `ConnectionApproveRejectPageModule` | `connections`, `connections_wishlist` | `connections`, `connections-wishlist` |

---

## Content & Discovery

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `learning-management` | [spec](../sc-saas-frontend/src/app/modules/learning-management/module.spec.md) | `LearningManagementModule` | `learning_management` | `learning-management`, `payment-management` (course payment verify) |
| `resources` | [spec](../sc-saas-frontend/src/app/modules/resources/module.spec.md) | `ResourcesModule`, `GlossaryModule`, `ProductUpdatesModule`, `DeeptechNewsModule`, `StartupKitModule` | `resources_downloads`, `glossary`, `news`, `startup_kit`, `service_kit_application_connection` | `resources`, `glossary`, `news`, `startup-kit` |
| `search` | [spec](../sc-saas-frontend/src/app/modules/search/module.spec.md) | `SearchModule`, `GlobalSearchPageModule`, `IpSearchModule`, `IpRequestModule` | `elastic_search`, `ip_management`, `startups`, `investors`, `corporates`, `mentors`, `service_providers`, `partners`, `individuals`, `program_offices` | `search`, `elastic-search`, `ip-management` |
| `dashboard` | [spec](../sc-saas-frontend/src/app/modules/dashboard-v2/module.spec.md) | `DashboardV2Module`, `GrowthMatricsModule`, `GrowthMatricsPrintModule`, `MarketInsightsModule` | `growth_metrics` | `dashboard`, `metrics` |
| `milestones-tickets` | [spec](../sc-saas-frontend/src/app/modules/milestones/module.spec.md) | `MilestonesModule`, `TicketsModule` | `milestone_management`, `ticket_management` | `milestones`, `tickets` |
| `tracker` (Mentor Hours) | [spec](../sc-saas-frontend/src/app/modules/tracker/module.spec.md) | `TrackerModule` | `mentor_hours` | `mentorship` |
| `partners-dashboard` | [spec](../sc-saas-frontend/src/app/modules/partners-dashboard/module.spec.md) | `PartnersDashboardModule`, `PartnersDetailsModule` | none | `partner` |

---

## Finance

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `payments` | [spec](../sc-saas-frontend/src/app/modules/payment/module.spec.md) | `PaymentModule`, `PaymentGatewaysModule`, `MembershipModule`, `AccountModule`, `OrdersModule`, `CheckoutModule` | `payment_gateways` | `payment-management`, `memberships` |
| `facilities` | [spec](../sc-saas-frontend/src/app/modules/facilities-management/module.spec.md) | `FacilitiesManagementModule`, `ExternalFacilitiesManagementModule` | `facility_management` | `facility_management` |

---

## Infrastructure / Utilities

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `utilities` | [spec](../sc-saas-frontend/src/app/modules/utilities/module.spec.md) | `DynamicFormsModule`, `StaticFormFieldModule`, `ScCertificateRendererModule`, `ScIdCardRendererModule`, `CerificatesModule`, `PublicModule`, `PublicSharedModule`, `ShareLinksModule`, `BoothDisplayModule`, `InlineStylesCspModule`, `SliderModule`, `PageNotFoundModule` | `certificates`, `startup_id_cards`, `call_for_applications_submitted_email_enabled` | `form-management`, `certificates`, `id-cards` |

---

## Pitch Deck

| Module | Spec | Angular Modules Covered | Key Flags | Backend Modules Called |
|---|---|---|---|---|
| `pitch-deck-management` | [spec](../sc-saas-frontend/src/app/modules/pitch-deck-management/module.spec.md) | `PitchDeckManagementComponent`, `ConnectPowerPitchModalComponent`, `PowerPitchEditPageWrapperComponent` | `video_pitch_mandatory`, `video_types` | `power-pitch-module` (pp-api via PowerPitchExternalService) |
| `pitch-deck-recorder` | [spec](../sc-saas-frontend/src/app/modules/pitch-deck-recorder/module.spec.md) | `PitchDeckRecorderModule`, `DeckWebcamRecorderComponent` | `video_pitch_mandatory` | *(legacy — current flow routes through ConnectPowerPitchModal)* |

---

## Security findings summary (surfaced by spec authoring)

These findings were captured in module `Watch out for` sections. They are **not fixed here** — they are documented for awareness and prioritisation.

| Severity | Module | Finding |
|---|---|---|
| 🔴 Critical | `learning-management` | `GET videos/:id/hls-url` has no `@Features` or `JwtAuthGuard` on the backend — any caller who knows a `videoAssetId` retrieves a signed CloudFront HLS URL without auth. Frontend nav guard is the only access control. |
| 🔴 Critical | `payments` | Nearly all backend payment routes have `JwtAuthGuard` commented out — no server-side identity check on order creation, coupon verification, or transaction recording. |
| 🔴 Critical | `payments` | `PaymentGatewaysComponent` hardcodes `localhost:3000` for Stripe/PayPal/Razorpay create-order calls and embeds a test Stripe publishable key — must not be deployed in production. |
| 🟠 High | `auth` | OTP verify sends `code` as an md5 hash (`login/verify`, `auth-external/login/verify/import`, `otp_verifications/verify`, `otp_verifications/verify/whatsapp`) — must match the backend's storage format exactly (backend stores md5 but compares against plaintext: a known `verifications` module bug means verification always fails unless client sends md5). |
| 🟠 High | `meetings` | `/meeting/:meetingId` has no `AuthGuard` — intentionally accessible via emailed link. `fetchMeetingData` calls the public backend route which has no `JwtAuthGuard` — full meeting entity exposed to any caller with the UUID. |
| 🟠 High | `facilities` | `/external-facilities` route has `AuthGuard` commented out — unauthenticated users can reach the ecosystem facility listing. `EcosystemFacilityManagementController` on the backend has no `JwtAuthGuard`. |
| 🟠 High | `jobs` | `public/resumes/submit` and `public/resumes/upload` are fully unauthenticated on the backend — rate-limited only. Frontend sends no auth header. |
| 🟠 High | `payments` | Membership routes (`history`, `last`, `types`) are unauthenticated on the backend — any caller who knows `profileType` + `profileId` can read membership history. |
| 🟠 High | `payments` | `getProformaInvoiceHtml` returns raw HTML; injecting via `[innerHTML]` requires `DomSanitizer.bypassSecurityTrustHtml` — only safe if backend sanitises content. |
| 🟡 Medium | `core` | `GlobalService` calls multiple unauthenticated backend reference-data and news endpoints that carry no tenant-scoping check client-side — the correct tenant is resolved via the cockpit bootstrap, but a stale `apiUrl` in localStorage could point to a wrong tenant. |
| 🟡 Medium | `startup` | `logout_on_rejection` side-effect runs inside a 1-second `setTimeout` on every completeness poll. High polling frequency causes a visible toast-before-logout race. |
| 🟡 Medium | `jobs` | `/job-interview/:id` has no layout shell wrapper — no navbar or sidebar; global layout styles do not apply. Guard is also absent. |
| 🟡 Medium | `jobs` | `PATCH jobs/hiring-profile` is a no-op on the backend (service body commented out) — the frontend call returns 200 but nothing persists. |
| 🟡 Medium | `community-feed` | No Angular `FeatureGuard` on community routes — backend enforces `community_feed` flag, but the nav item is not hidden before the network call if the flag is off. |
| 🟡 Medium | `meetings` | `getCalenderAvilablity()` returns hardcoded static data, not a live API call. Confusing with `getUsersAvailability()` which calls the real endpoint. |
| 🟡 Medium | `meetings` | `EditMeetingComponent`, `DeleteMeetingComponent`, and `MeetingDetailsModalComponent` are commented out of `CalenderModule` declarations and exports — these components exist on disk but are not registered and cannot be used until uncommented. |
| 🟡 Medium | `utilities` | `updatePublicFile()` in `FormManagementService` has a `console.log(payload)` in the production code path — remove before prod. |
| 🟡 Medium | `search` | `/global-search` relies on `elastic_search` flag but there is no Angular `FeatureGuard` on the route — flagging the route off requires a guard addition. |
