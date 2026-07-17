# SanchiSaaS — Product Vision & Business Objectives (Draft)

**Document Type:** Business/Product Rationale (companion to the technical knowledge base and to `Business-Perspective-Major-Modules.md`)
**Status:** DRAFT — every claim below is Claude's inference from reading the platform's actual functionality and investment pattern, not confirmed business fact
**Date:** 2026-07-17
**Origin:** Closes external gaps-register item **P-1** ("No stated product vision or objectives") — confirmed real: neither `specs/FRS-SanchiSaaS-Client.md` §2.1, `specs/SRS-SanchiSaaS-Client.md`, `specs/DDD-SanchiSaaS-Client.md`, nor the root `README.md` states a vision, mission, or business objective anywhere; all describe platform *capability* without stated *intent*.

---

## Purpose and how to use this document

This document tries to answer a question that **cannot be derived from source code with certainty**: why is SanchiSaaS being built the way it is, and what is it trying to achieve commercially over the current horizon. Vision and business objectives live in the founders'/product owner's heads, not in the codebase — every statement below is a **draft inference reverse-engineered from where real engineering effort has visibly gone** (which modules exist, which get the deepest investment, what's actively being built right now), written so there's a concrete starting point to correct rather than a blank page.

**Nothing here should be treated as confirmed strategy until the product owner validates, edits, or replaces it.** Tagging convention matches `Business-Perspective-Major-Modules.md`: `[INFERRED]` = Claude's draft guess from evidence, needs validation. `[CONFIRMED — <source>]` = validated by an actual business owner, replace as this happens.

---

## Product Vision (Draft) `[INFERRED]`

> To be the single operating system a startup incubator or accelerator runs its entire program on — replacing the patchwork of spreadsheets, generic CRMs, and disconnected point tools most programs stitch together today — while using AI to remove the single most time-consuming manual bottleneck in accelerator operations: reading and scoring every application by hand.

**Evidence this is inferred from, not invented:**
- The platform's module count and breadth (~15+ distinct business domains beyond bare application-tracking — facility management, IP/patent management, learning management, events, jobs, certificates, business challenges, community/networking, task management) reads as a deliberate "consolidate many point solutions into one" strategy, not an accidental feature-creep pattern.
- A dedicated microservice (`ai-startups-analyzer`) plus an entire cross-repo wallet/billing/ledger/reserve-settle-refund system (`ai_credit_*` tables spanning 3 repos, per `FT-005-ai-credits-system.spec.md`) exists purely to meter and monetize AI-assisted application scoring — this is substantial, deliberate engineering investment in one specific capability, not a minor add-on.

---

## Top Business Objectives for the Current Horizon (Draft) `[INFERRED]`

1. **Win and retain incubator/accelerator customers by being the consolidated platform**, so a program never needs a second tool for facilities, IP tracking, learning content, events, or community — the classic "land with core application-tracking, expand into every adjacent workflow" SaaS motion. *Evidence: breadth of built modules far exceeds what a bare CFA/application-tracking tool would need.*

2. **Establish AI-assisted application scoring as the flagship differentiator and a new monetized revenue line**, not just a cost-saving feature. *Evidence: the AI-Credits wallet/purchase/reserve/settle/refund system is a genuinely separate revenue mechanism (Easebuzz-backed credit packages) layered on top of the scoring feature itself — monetizing the AI capability directly, not just building it as a value-add.*

3. **Grow recurring, subscription-shaped revenue per tenant beyond the base program fee**, across multiple independent surfaces rather than one. *Evidence: a dedicated `subscriptions` entity (plan name/users/description, start/end/suspend dates) alongside a separate Memberships module and Learning Management's course-sales revenue stream — three distinct monetization surfaces already built, not one.*

4. **Reduce the operational cost of adding and running each new tenant**, so growth in tenant count doesn't scale operational headcount 1:1. *Evidence: the in-progress Tenant Onboarding feature (`sanchiconnect-saas-tenants-admin`, currently being built) exists specifically to cut a ~307-column/218-feature-flag manual setup process down via clone-from-existing-tenant + sectioned flag UI — a direct investment in operator efficiency, not an end-user-facing feature.*

5. **Extend the addressable market beyond day-to-day accelerator operations into adjacent founder-readiness tooling.** *Evidence: the cross-workspace integration with SanchiPowerpitch (`power-pitch-sanchiconnect-api`'s `/v1/externals/*` contract, called from `sc-saas-backend`'s `PowerPitchExternalService` for session/video/transcript handling) suggests ambition beyond "manage my cohort" into "help my founders become investment-ready" — a genuinely separate product surface, not a feature of the core accelerator-ops platform.*

---

## KPI Framework (Draft) `[INFERRED — metrics only, no targets]`

Closes external gaps-register item **P-2** ("No success metrics or KPIs"). For each objective above, this defines a **measurable metric/formula** and states whether the underlying data already exists to compute it today. It deliberately does **not** invent a target number (an SLA percentage, a revenue figure, an adoption rate) — a fabricated number reads as a real commitment, which this document cannot responsibly make. Every `Target` row is `[TBD — product owner]`.

### Objective 1 — Consolidated platform / land-and-expand
- **Metric:** Feature-flag adoption breadth per tenant — the % of the ~218 boolean feature flags on `tenant_users` actually enabled for a given tenant, tracked over time.
- **Formula:** `count(enabled flags for tenant) / 218`, sampled per tenant per month.
- **Data available:** Yes — `tenant_users` table, `sanchiconnect-saas-tenants`. No dashboard currently reads this in aggregate; the query itself is trivial.
- **Target:** [TBD — product owner]

### Objective 2 — AI scoring as flagship differentiator + monetization
- **Metric A (evaluation SLA):** Time from application-analysis upload to finalized score, per run.
- **Formula:** `finalize_time - analyses.created_at`, per `run_id`, aggregated (median/p95) per tenant per cycle.
- **Data available:** Yes — `ai-startups-analyzer`'s `analyses`/`batches` tables have `created_at`/`updated_at`; `sc-saas-backend`'s `application_program_analysis.cost_computed_at` marks finalize time. No SLA dashboard exists today, but the timestamps needed are already persisted.
- **Metric B (credit-revenue):** AI-credit purchase revenue per tenant per month.
- **Formula:** `sum(ai_credit_orders.amount)` where `status = 'paid'`, grouped by domain/month.
- **Data available:** Yes — `ai_credit_orders`/`ai_credit_transactions`/`ai_credit_ledger` (`sanchiconnect-saas-tenants`), populated on every real Easebuzz-confirmed purchase.
- **Target:** [TBD — product owner] (both SLA and revenue)

### Objective 3 — Recurring revenue growth beyond base program fee
- **Metric:** Combined monthly recurring value across all three independent monetization surfaces.
- **Formula:** `sum(active subscriptions.plan_users-implied value) + sum(active memberships value) + sum(LMS course-sales revenue)`, per tenant per month.
- **Data available:** Partial — `subscriptions` table exists (`sanchiconnect-saas-tenants`) but has no price/value column of its own (only `plan_name`/`plan_users`/dates), so revenue must be reconstructed from the actual Easebuzz/payment records, not read directly off the subscription row. Memberships and LMS course-sale revenue are more directly queryable from their own payment records.
- **Target:** [TBD — product owner]

### Objective 4 — Reduce per-tenant operational cost (onboarding efficiency)
- **Metric:** Time (operator-hours or wall-clock) to provision a new tenant, start to first-login-ready.
- **Formula:** No formula can be given yet — **no measurement infrastructure exists today.** The Tenant Onboarding feature itself (clone-from-existing-tenant + sectioned flag UI) is still at the planning stage in `sanchiconnect-saas-tenants-admin`, not shipped, so there is no timestamp anywhere marking "onboarding started" vs. "onboarding complete." This metric cannot be measured until that feature (or an equivalent instrumentation) ships.
- **Data available:** No.
- **Target:** [TBD — product owner, and contingent on the Tenant Onboarding feature actually shipping]

### Objective 5 — Adjacent market expansion (SanchiPowerpitch)
- **Metric:** Cross-product adoption — number/% of tenants whose users create at least one SanchiPowerpitch session via `PowerPitchExternalService` per month.
- **Formula:** Count of `POST /v1/externals/create-session` calls (or resulting sessions), grouped by tenant, per month.
- **Data available:** Unconfirmed — `sc-saas-backend` calls this endpoint, but whether call outcomes are logged/persisted anywhere queryable (vs. just proxied through) was not verified in this pass; would need a direct read of `PowerPitchExternalService` and the PowerPitch-side session store to confirm.
- **Target:** [TBD — product owner]

**What this framework does not attempt:** application-throughput (raw submission volume) is deliberately not listed as its own objective-level KPI here — it's more naturally a sub-metric of Objective 1's adoption tracking (via `Form Submission`/`Application Program Submission Progress` counts, both real, queryable entities per the DDD) than a standalone business objective. If the product owner wants raw throughput tracked as a headline number in its own right, it should be added explicitly rather than assumed.

---

## Open Questions for the Product Owner

These cannot be resolved by reading code — they require an actual answer from whoever owns product strategy:

1. Is the vision statement above directionally correct, or does it miss/misstate the actual strategic intent?
2. Are these the right top 3-5 objectives for **the current horizon** specifically (this quarter/half/year) — as opposed to the long-run direction the evidence above can plausibly support?
3. Is there a target market-segment focus (e.g., university/government-linked incubators specifically, given the IP/Technology-Transfer-Office-shaped module, vs. corporate accelerators, vs. both) that should be stated explicitly?
4. Is the SanchiPowerpitch integration a strategic bet on an adjacent product line, or an opportunistic/one-off integration with no larger strategic weight? This materially changes how much future engineering investment that integration should receive.
5. Are there business objectives entirely absent from this inference because no corresponding engineering investment exists yet (e.g., a stated growth/market-expansion target, a profitability target, a specific customer-acquisition-cost or retention goal)? Code-reading can only surface intent that's already been built toward — it cannot surface a goal nobody has started building for yet.
6. For each KPI Framework metric above: is the proposed metric/formula the right one to track, and what is the actual target number? None were invented — every `Target` field is intentionally blank.
7. Objective 4's KPI cannot be measured at all until the Tenant Onboarding feature ships (or equivalent instrumentation is added) — should measurement infrastructure (an "onboarding started"/"onboarding complete" timestamp pair) be added as an explicit acceptance criterion when that feature is implemented, so this KPI isn't permanently unmeasurable?

---

## Change Log

- 2026-07-17 | Initial draft, closing external gaps-register item P-1. Grounded entirely in observable engineering investment patterns across all 7 repos plus the SanchiPowerpitch cross-workspace contract — no vision/objective content invented without a cited piece of evidence. Every statement flagged `[INFERRED]` pending product-owner review.
- 2026-07-17 | Added the KPI Framework section, closing external gaps-register item P-2. Defined a measurable metric/formula per objective and stated data availability for each (confirmed available for Objectives 1-3, confirmed unavailable today for Objective 4 pending the Tenant Onboarding feature shipping, unconfirmed for Objective 5 pending a direct read of PowerPitch's session store). Deliberately left every target number `[TBD — product owner]` rather than inventing one — a fabricated number would read as a real commitment.
