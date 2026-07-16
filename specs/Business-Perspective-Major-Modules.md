# SanchiSaaS — Business Perspective: Major Modules

**Document Type:** Business/Product Rationale (companion to the technical knowledge base)
**Status:** DRAFT — every claim below is Claude's inference from reading the module's actual functionality, not confirmed business fact
**Date:** 2026-07-16
**Companion documents:** workspace `knowledge.md`/`CLAUDE.md` (technical), each module's own `module.spec.md` (technical contract)

---

## Purpose and how to use this document

`knowledge.md`, `design.md`, `database.md`, and `api.md` answer "what does the code actually do." This document
tries to answer a different question that **can't be derived from source code**: why does this feature exist
commercially, what business goal does it serve, and what KPI would tell you it's working. Business goals and
target metrics live in the founders'/PMs' heads, not in the codebase — so **every entry below is a draft
inference from the module's functionality**, written so you have a starting point to correct rather than a
blank page. Nothing here should be treated as confirmed strategy until a business owner validates or edits it.

**How to keep this alive going forward:** when a new feature spec (`specs/features/*.spec.md`) is approved, or
an existing module gets a significant enhancement, add or update its entry here with the *actual* business
rationale from whoever made the call — replacing the `[INFERRED]` tag with a real citation (a person, a
meeting, a Linear issue). Over time this should read as "why we built this," not "what a code-reading agent
guessed we probably meant."

**Tagging convention:** `[INFERRED]` = Claude's draft guess from functionality, needs validation. `[CONFIRMED — <source>]` = validated by an actual business owner, replace as this happens.

---

## Summary table

| Module | Repo | One-line business purpose (inferred) | Primary KPI candidate (inferred) |
|---|---|---|---|
| Application Management (Call for Applications) | `sc-saas-backend` | Core acquisition funnel for an incubator's cohort intake — the reason a startup first touches the platform | Applications received per cycle; funnel conversion (view → apply → submit) |
| Program Management | `sc-saas-backend` | Structures a cohort/program into trackable rounds so incubators can run a repeatable selection process | Programs run per tenant per year; round-to-round advancement rate |
| Facility Management | `sc-saas-backend` | Monetizes physical coworking/incubator space — bookings, add-ons, payment integration built in | Facility booking revenue per tenant; utilization rate (bookings / available slots) |
| Events | `sc-saas-backend` | Community/networking engagement driver — keeps startups active on the platform between application cycles | Event attendance rate; RSVP-to-attendance conversion |
| Meetings | `sc-saas-backend` | Enables the mentor/investor/startup connections the platform's matching promises are worth — retention driver | Meetings scheduled per active user per month; acceptance rate |
| Job Board | `sc-saas-backend` | Adds a talent-marketplace layer — value-add for portfolio startups hiring, and for job-seekers joining via the platform | Job postings per tenant; applications per posting |
| Mentorship (hour logging) | `sc-saas-backend` | Makes mentor engagement measurable/reportable — the metric incubators use to prove program value to their own funders/boards | Logged + approved mentor hours per cohort |
| Payment Management | `sc-saas-backend` | Revenue infrastructure — the plumbing every other monetized module (facilities, memberships, courses) depends on | Payment success rate; gross transaction volume processed |
| Memberships | `sc-saas-backend` | Recurring-revenue subscription layer, independent of one-off program fees | Active memberships; upgrade-request conversion rate |
| Certificates | `sc-saas-backend` | Low-cost credibility/completion incentive that increases course/program completion — indirectly supports LMS and program stickiness | Certificates issued; verification-page views (signals external credibility use) |
| Ecosystem Directory | `sc-saas-backend` + `tenants` | Cross-tenant network effect — the more tenants opted in, the more valuable every tenant's directory becomes (classic multi-tenant flywheel) | % of tenants opted into ecosystem sharing; cross-tenant profile views |
| ID Cards | `sc-saas-backend` | Low-effort "feels like a real institution" perk — cheap to build, plausible retention/branding value, gated behind its own flag | Cards generated per active cohort member |
| IP Management (TTO proxy) | `sc-saas-backend` + `tenants` | Niche, high-value differentiator for government-linked/university incubators with a Technology Transfer Office mandate | Connect requests initiated; patent-browse engagement |
| Learning Management (LMS) | `sc-saas-backend` + `sc-saas-admin` | New paid-content revenue stream (course sales) and/or a retention/differentiation feature bundled into higher pricing tiers | Course enrollment revenue; completion rate; see the cost-burden analysis earlier in this session before pricing |
| AI Startup Scoring | `ai-startups-analyzer` | Flagship AI differentiator — automates the single most time-consuming manual task incubator staff do (reading every application) | Applications auto-scored per cycle; staff hours saved (self-reported or estimated) |
| AI Credits (wallet/billing) | `sanchiconnect-saas-tenants` | The monetization layer *for* AI Startup Scoring and any future AI feature — converts LLM API cost into a billable, capped unit | AI credits consumed per tenant per month; credit-purchase revenue |

---

## Detail per module

### Application Management (Call for Applications)
**Business goal [INFERRED]:** This is very likely the platform's primary top-of-funnel acquisition mechanism — it's how a startup first becomes a record in the system, before any other module (mentorship, facilities, LMS) becomes relevant to them. A tenant incubator's entire cohort pipeline runs through this.
**Target KPIs [INFERRED]:** applications received per open call; view→apply→submit conversion; time-to-decision (how fast staff move applicants through rounds) — likely the single most-watched dashboard number for any tenant.
**Monetization angle [INFERRED]:** probably not directly monetized per-use — more likely the core value proposition that justifies the tenant's base subscription. Its health indirectly drives every downstream module's usage.
**Notes:** confirmed functionality includes document submissions, reminders/notifications, and public funnel-lead capture (`sc-saas-backend/src/modules/application-management/module.spec.md`) — meaning there's already funnel-stage tracking data available to build a real KPI dashboard from, if one doesn't already exist.

### Program Management
**Business goal [INFERRED]:** structures the *output* side of Application Management — turning accepted applicants into a program with defined rounds, so the incubator can run (and report on) a repeatable, defensible selection process rather than an ad-hoc one.
**Target KPIs [INFERRED]:** programs run per year; startups advanced per round; program-to-outcome tracking (if graduation/exit data exists elsewhere).
**Monetization angle [INFERRED]:** likely bundled into the base platform rather than separately priced — it's closer to "core operations" than an add-on.

### Facility Management
**Business goal [INFERRED]:** this is one of the few modules with **built-in payment integration** at the booking level (`facility_management/module.spec.md`) — strongly suggests it's meant to be a direct revenue line for tenants (charging members for coworking desks/meeting rooms/equipment), not just a scheduling convenience.
**Target KPIs [INFERRED]:** facility revenue per tenant per month; utilization rate; no-show rate on bookings.
**Monetization angle [INFERRED]:** likely revenue-share or a pricing-tier gate, given the payment integration is already wired in rather than being a "nice to have" calendar feature.
**Notes:** also supports QR-code/kiosk check-in flows without a logged-in session — suggests real physical-space operational use, not just a demo feature.

### Events
**Business goal [INFERRED]:** engagement/retention between application cycles — most incubator programs run only 1-4 cohorts a year; Events is one of the few things that gives startups/mentors a reason to open the platform in the gaps between them.
**Target KPIs [INFERRED]:** event attendance rate; RSVP-to-attendance conversion; recurring vs. one-off event mix.
**Monetization angle [INFERRED]:** probably not directly priced — more likely an engagement/retention lever that protects the base subscription by keeping the platform "sticky."

### Meetings
**Business goal [INFERRED]:** this is where the platform's core promise (connecting startups to mentors/investors) actually gets *used*, not just browsed. Matching/discovery features elsewhere are only valuable if they convert into scheduled meetings.
**Target KPIs [INFERRED]:** meetings scheduled per active user/month; acceptance rate; the existence of a `meeting_moderation_enabled` flag (routing to admin approval instead of direct invite) suggests some tenants explicitly want to control/curate this rather than let it run fully self-serve — worth understanding why before assuming "more meetings = better" is universally the right KPI framing.

### Job Board
**Business goal [INFERRED]:** a talent-marketplace layer that adds value on two sides at once — portfolio startups get a hiring channel, and job-seekers get a reason to join the platform who wouldn't otherwise (a acquisition channel distinct from the startup-application funnel).
**Target KPIs [INFERRED]:** job postings per tenant; applications per posting; hire-through rate if trackable.
**Monetization angle [INFERRED]:** could plausibly be a separately-gated feature (job boards are a common paid add-on in adjacent SaaS categories) — worth confirming whether it's currently bundled or intended as a future upsell.

### Mentorship (hour logging)
**Business goal [INFERRED]:** this looks less like an engagement feature and more like a **reporting/compliance** one — incubators (especially publicly-funded or university-affiliated ones) frequently need to prove mentor engagement hours to their own funders or boards. This module's approval workflow (startup confirms hours, not just the mentor self-reporting) suggests it's built for defensible reporting, not just tracking.
**Target KPIs [INFERRED]:** logged + approved mentor hours per cohort; probably the number a tenant's own leadership reports upward, not one that faces end-users.

### Payment Management
**Business goal [INFERRED]:** infrastructure, not a feature in its own right — every monetized module (Facility Management, Memberships, and potentially Learning Management) is downstream of this. Its health (gateway uptime, success rate) is a platform-wide risk, not a single-module concern.
**Target KPIs [INFERRED]:** payment success rate; gross transaction volume across all modules that use it; gateway failure rate by provider (5 gateways supported — worth knowing if failure rates differ meaningfully by provider/region).
**Monetization angle:** N/A — this *is* the monetization plumbing, not something priced itself.

### Memberships
**Business goal [INFERRED]:** a recurring-revenue layer independent of one-off program/application fees — likely aimed at a different buyer motion (an ongoing subscriber relationship vs. a per-cohort application fee).
**Target KPIs [INFERRED]:** active memberships; upgrade-request conversion rate; churn/lapse rate if trackable.
**Monetization angle [INFERRED]:** directly monetized by definition — worth understanding whether this is tenant-priced-to-their-members or a SanchiSaaS-priced tier itself.

### Certificates
**Business goal [INFERRED]:** a low-cost, high-perceived-value completion incentive. The public certificate-verification-by-number feature suggests this is meant to carry real external credibility (a learner/member showing a certificate to an employer), not just an internal badge.
**Target KPIs [INFERRED]:** certificates issued; public verification-page views (a proxy for how often certificates are actually being shown to third parties, which is the actual value signal).
**Monetization angle [INFERRED]:** indirect — supports completion rates for Learning Management and Memberships rather than being priced on its own.

### Ecosystem Directory
**Business goal [INFERRED]:** this is the one module whose value is structurally different from the rest — it's a **network effect** feature. A single tenant's ecosystem directory is only as valuable as how many *other* tenants also participate. This is worth flagging distinctly in any pricing conversation: it may make sense to never gate this behind a per-tenant paywall, since restricting adoption directly reduces the value for every other participating tenant.
**Target KPIs [INFERRED]:** % of tenants opted in; cross-tenant profile views/searches; this is a platform-health metric more than a per-tenant one.

### ID Cards
**Business goal [INFERRED]:** looks like a low-engineering-cost, "feels like a real institution" perk — plausible retention/branding value (a startup founder with a digital ID card feels officially part of something) at minimal build cost. Already gated behind its own flag (`startup_id_cards`), suggesting it's already treated as an optional add-on rather than core.
**Target KPIs [INFERRED]:** cards generated per active cohort — likely a soft/vanity metric rather than a revenue one.

### IP Management (Technology Transfer Office proxy)
**Business goal [INFERRED]:** a niche but potentially high-value differentiator for a specific tenant segment — university-affiliated or government-linked incubators with a formal Technology Transfer Office mandate (patent licensing, tech-transfer connect requests). Not every tenant would need this; likely most valuable as a premium/vertical-specific feature rather than a broad one.
**Target KPIs [INFERRED]:** connect requests initiated; patent-browse engagement — probably only meaningful for the subset of tenants this actually applies to, so a blended average across all tenants would understate its value where it matters.

### Learning Management (LMS)
**Business goal [INFERRED]:** the newest and most build-intensive module here — most likely intended either as (a) a new paid-content revenue stream (tenants sell courses to their members) or (b) a retention/differentiation feature bundled into a higher pricing tier. The presence of `CoursePriceEntity` and `EnrollCourseDto` with `priceCode`/`orderNumber` fields (`sc-saas-backend/src/modules/learning-management/module.spec.md`) confirms real paid-enrollment plumbing exists — this is built to be sold, not just a free perk.
**Target KPIs [INFERRED]:** course-sale revenue per tenant; completion rate; enrolled-learner count.
**Monetization angle:** see this session's cost-burden analysis before finalizing a price — CloudFront egress bandwidth is the dominant, usage-scaling cost driver, and two confirmed storage leaks (orphaned assets on video replace/delete) mean the cost side needs fixing before a confident per-tenant price can be set.
**Status flag:** currently soft-launched — sidebar menu entries are commented out in `sc-saas-admin` (`learning_management/module.spec.md`), so this may not yet be a broadly available feature.

### AI Startup Scoring
**Business goal [INFERRED]:** the platform's clearest AI-native differentiator — it automates the single most time-consuming manual task an incubator's staff does (reading every application against a rubric). This is likely the single strongest "why choose SanchiSaaS over a generic accelerator CRM" argument available today.
**Target KPIs [INFERRED]:** applications auto-scored per cycle; adoption rate among tenants with the flag available; staff-hours-saved (even if only self-reported/estimated, this is probably the number that sells the feature in a sales conversation).
**Monetization angle [INFERRED]:** almost certainly consumption-metered rather than flat-fee, given it's billed through AI Credits rather than bundled — see below.

### AI Credits (wallet/billing)
**Business goal [INFERRED]:** this module *is* the monetization mechanism for AI Startup Scoring (and presumably any future LLM-backed feature) — it converts a variable, provider-dependent LLM API cost into a fixed, billable, capped unit the tenant purchases in advance. This is the piece that makes "AI scoring" a sustainable revenue line rather than an unbounded cost center for SanchiSaaS itself.
**Target KPIs [INFERRED]:** AI credits consumed per tenant per month; credit-package purchase revenue; margin between LLM provider cost and credit price (this is the number that determines whether the AI-scoring feature is actually profitable, not just popular).
**Notes:** per earlier work this session (see memory `project_ai_credits_debit_gap`), there's a known gap where the analyzer doesn't yet auto-debit the wallet on every scoring run — worth resolving before this becomes a heavily-marketed revenue line, since unmetered usage under a "credits" branding is a direct margin leak.

---

## Open questions for a business owner to resolve

These are the gaps I can't fill by reading code — flagging them explicitly rather than guessing further:

- What is the actual pricing/packaging model today? (per-tenant flat tiers, per-feature add-ons, usage-metered, or some mix?)
- Which of these modules are currently *live* in production for paying tenants vs. soft-launched/pilot-only? (Learning Management is confirmed soft-launched; unclear for others.)
- Are there existing KPI dashboards/reporting for any of these, or would the "Primary KPI candidate" column above need net-new instrumentation?
- Is there a documented ICP (ideal customer profile) per module — e.g., is IP Management genuinely only relevant to a specific tenant segment, and if so, is it priced/positioned that way already?

---

## Change Log

- 2026-07-16 | Initial draft. 16 major modules covered across `sc-saas-backend`, `sc-saas-admin`,
  `ai-startups-analyzer`, and `sanchiconnect-saas-tenants`, drafted entirely from functionality
  (`module.spec.md` files + this session's own findings) — no business input yet incorporated. Excluded
  `task-management` from the major-modules list since it's a scaffolded stub with no implemented
  controller/service (`sc-saas-backend/src/modules/task-management/module.spec.md`), not a live feature.
