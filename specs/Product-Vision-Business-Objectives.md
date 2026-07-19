# SanchiSaaS — Product Vision & Business Objectives

**Document Type:** Business/Product Rationale (companion to the technical knowledge base and to `Business-Perspective-Major-Modules.md`)
**Status:** Vision + core KPIs CONFIRMED by Sanchi (2026-07-17); the 5 supporting objectives and all KPI targets below that remain `[INFERRED]`/`[TBD]`
**Date:** 2026-07-17
**Origin:** Closes external gaps-register item **P-1** ("No stated product vision or objectives") — confirmed real: neither `specs/FRS-SanchiSaaS-Client.md` §2.1, `specs/SRS-SanchiSaaS-Client.md`, `specs/DDD-SanchiSaaS-Client.md`, nor the root `README.md` states a vision, mission, or business objective anywhere; all describe platform *capability* without stated *intent*.

---

## Purpose and how to use this document

This document tries to answer a question that **cannot be derived from source code with certainty**: why is SanchiSaaS being built the way it is, and what is it trying to achieve commercially over the current horizon. Vision and business objectives live in the founders'/product owner's heads, not in the codebase — every statement below is a **draft inference reverse-engineered from where real engineering effort has visibly gone** (which modules exist, which get the deepest investment, what's actively being built right now), written so there's a concrete starting point to correct rather than a blank page.

**Nothing here should be treated as confirmed strategy until the product owner validates, edits, or replaces it.** Tagging convention matches `Business-Perspective-Major-Modules.md`: `[INFERRED]` = Claude's draft guess from evidence, needs validation. `[CONFIRMED — <source>]` = validated by an actual business owner, replace as this happens.

---

## Product Vision `[CONFIRMED — Sanchi, 2026-07-17]`

> Sell the AI feature and increase company ARR.

This is the stated, authoritative vision — short and commercially direct, not an elaboration Claude added. Everything below this point should be read as "in service of selling the AI feature and growing ARR," and any objective/KPI that doesn't trace back to that should be treated as a candidate for de-scoping, not as a peer priority.

### Prior draft inference (superseded, kept for evidence trail only)

Before this was confirmed, the vision below was reverse-engineered from engineering investment patterns. It's kept here because the confirmed vision above validates most of its reasoning (AI monetization is now explicitly the point, not an inferred one) — but it should no longer be cited as the vision statement itself:

> To be the single operating system a startup incubator or accelerator runs its entire program on — replacing the patchwork of spreadsheets, generic CRMs, and disconnected point tools most programs stitch together today — while using AI to remove the single most time-consuming manual bottleneck in accelerator operations: reading and scoring every application by hand.

**Evidence this was inferred from:**
- The platform's module count and breadth (~15+ distinct business domains beyond bare application-tracking — facility management, IP/patent management, learning management, events, jobs, certificates, business challenges, community/networking, task management) reads as a deliberate "consolidate many point solutions into one" strategy, not an accidental feature-creep pattern.
- A dedicated microservice (`ai-startups-analyzer`) plus an entire cross-repo wallet/billing/ledger/reserve-settle-refund system (`ai_credit_*` tables spanning 3 repos, per `FT-005-ai-credits-system.spec.md`) exists purely to meter and monetize AI-assisted application scoring — this is substantial, deliberate engineering investment in one specific capability, not a minor add-on.

---

## Top Business Objectives for the Current Horizon

Objective 2 is now the **confirmed primary objective** — it's a direct restatement of the vision above, not an inference. Objectives 1/3/4/5 remain `[INFERRED]`: plausible supporting motions given what's been built, but not yet validated against the confirmed vision, and not necessarily equal in priority to Objective 2.

1. **Win and retain incubator/accelerator customers by being the consolidated platform**, so a program never needs a second tool for facilities, IP tracking, learning content, events, or community — the classic "land with core application-tracking, expand into every adjacent workflow" SaaS motion. *Evidence: breadth of built modules far exceeds what a bare CFA/application-tracking tool would need.* `[INFERRED]`

2. **Sell the AI feature and grow ARR from it** — establish AI-assisted application scoring as the flagship, directly monetized capability. `[CONFIRMED — Sanchi, 2026-07-17]`. *Evidence: the AI-Credits wallet/purchase/reserve/settle/refund system is a genuinely separate revenue mechanism (Easebuzz-backed credit packages) layered on top of the scoring feature itself — monetizing the AI capability directly, not just building it as a value-add.*

3. **Grow recurring, subscription-shaped revenue per tenant beyond the base program fee**, across multiple independent surfaces rather than one. *Evidence: a dedicated `subscriptions` entity (plan name/users/description, start/end/suspend dates) alongside a separate Memberships module and Learning Management's course-sales revenue stream — three distinct monetization surfaces already built, not one.* `[INFERRED]`

4. **Reduce the operational cost of adding and running each new tenant**, so growth in tenant count doesn't scale operational headcount 1:1. *Evidence: the in-progress Tenant Onboarding feature (`sanchiconnect-saas-tenants-admin`, currently being built) exists specifically to cut a ~307-column/218-feature-flag manual setup process down via clone-from-existing-tenant + sectioned flag UI — a direct investment in operator efficiency, not an end-user-facing feature.* `[INFERRED]`

5. **Extend the addressable market beyond day-to-day accelerator operations into adjacent founder-readiness tooling.** *Evidence: the cross-workspace integration with SanchiPowerpitch (`power-pitch-sanchiconnect-api`'s `/v1/externals/*` contract, called from `sc-saas-backend`'s `PowerPitchExternalService` for session/video/transcript handling) suggests ambition beyond "manage my cohort" into "help my founders become investment-ready" — a genuinely separate product surface, not a feature of the core accelerator-ops platform.* `[INFERRED]`

---

## KPI Framework

Closes external gaps-register item **P-2** ("No success metrics or KPIs"). For each objective above, this defines a **measurable metric/formula** and states whether the underlying data already exists to compute it today. It deliberately does **not** invent a target number (an SLA percentage, a revenue figure, an adoption rate) — a fabricated number reads as a real commitment, which this document cannot responsibly make. Every `Target` row is `[TBD — product owner]`, confirmed or not.

### Core KPIs `[CONFIRMED — Sanchi, 2026-07-17]`

Sanchi named three KPIs directly, mapped here to Objective 2 (the confirmed primary objective) with formulas/data-availability grounded in actual schema — the KPI *names* are confirmed; the formulas below are Claude's proposed operationalization of them and should be checked against whatever the team already tracks informally, since a name like "adoption rate" can be computed more than one defensible way.

- **AI-credit revenue / ARR growth**
  - **Formula:** `sum(ai_credit_orders.amount)` where `status = 'paid'`, grouped by domain/month; ARR growth = period-over-period % change of that sum (annualized).
  - **Data available:** Yes — `ai_credit_orders`/`ai_credit_transactions`/`ai_credit_ledger` (`sanchiconnect-saas-tenants`), populated on every real Easebuzz-confirmed purchase.
  - **Target:** [TBD — product owner]

- **AI feature adoption rate**
  - **Formula — proposed, not yet confirmed which reading Sanchi means:** either (a) `count(tenants with ai_credits_enabled = true) / count(all tenants)` — a coarse "who's turned it on" measure, or (b) `count(applications run through AI analysis) / count(total applications submitted)`, per tenant per cycle — a finer "how much of the real workload actually uses it" measure. These can diverge a lot (a tenant can have the flag on but rarely trigger analysis) — worth explicitly picking one, or tracking both.
  - **Data available:** Yes for (a) — `tenant_users.ai_credits_enabled`. Yes for (b) — `ai-startups-analyzer`'s `analyses` table joined against `sc-saas-backend`'s total application-submission count. Neither is aggregated in a dashboard today.
  - **Target:** [TBD — product owner]

- **Evaluation throughput / SLA**
  - **Formula — SLA (latency):** `finalize_time - analyses.created_at`, per `run_id`, aggregated (median/p95) per tenant per cycle. **Throughput (volume):** `count(analyses.id)` completed per period (day/week/tenant).
  - **Data available:** Yes — `ai-startups-analyzer`'s `analyses`/`batches` tables have `created_at`/`updated_at`; `sc-saas-backend`'s `application_program_analysis.cost_computed_at` marks finalize time. No SLA/throughput dashboard exists today, but the timestamps and row counts needed are already persisted.
  - **Target:** [TBD — product owner]

### Supporting KPIs for the other (still-inferred) objectives `[INFERRED — metrics only, no targets]`

### Objective 1 — Consolidated platform / land-and-expand
- **Metric:** Feature-flag adoption breadth per tenant — the % of the ~218 boolean feature flags on `tenant_users` actually enabled for a given tenant, tracked over time.
- **Formula:** `count(enabled flags for tenant) / 218`, sampled per tenant per month.
- **Data available:** Yes — `tenant_users` table, `sanchiconnect-saas-tenants`. No dashboard currently reads this in aggregate; the query itself is trivial.
- **Target:** [TBD — product owner]

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

## Resolved (product decision, 2026-07-17)

1. **Vision** — confirmed by Sanchi: "sell the AI feature and increase company ARR." Not the broader "single OS for accelerators" framing this document originally inferred; that framing is demoted to background evidence, not the stated goal.
2. **Core KPIs** — confirmed by Sanchi: AI-credit revenue / ARR growth, AI feature adoption rate, evaluation throughput / SLA. See "Core KPIs" above.

## Open Questions for the Product Owner

Still open — these cannot be resolved by reading code and haven't been answered yet:

1. Are the 5 supporting objectives (1, 3, 4, 5 — Objective 2 is now confirmed) the right ones for **the current horizon** specifically (this quarter/half/year) given the now-confirmed vision, or are some of them lower-priority distractions from "sell the AI feature and grow ARR"?
2. Is there a target market-segment focus (e.g., university/government-linked incubators specifically, given the IP/Technology-Transfer-Office-shaped module, vs. corporate accelerators, vs. both) that should be stated explicitly?
3. Is the SanchiPowerpitch integration a strategic bet on an adjacent product line, or an opportunistic/one-off integration with no larger strategic weight? This materially changes how much future engineering investment that integration should receive.
4. Are there business objectives entirely absent from this inference because no corresponding engineering investment exists yet (e.g., a stated growth/market-expansion target, a profitability target, a specific customer-acquisition-cost or retention goal)? Code-reading can only surface intent that's already been built toward — it cannot surface a goal nobody has started building for yet.
5. For the two "AI feature adoption rate" formula readings proposed above (flag-enabled vs. actual-usage), which one (or both) should be the tracked definition? And what are the actual target numbers for all three confirmed KPIs, plus the still-`[TBD]` targets on the supporting-objective KPIs?
6. Objective 4's KPI cannot be measured at all until the Tenant Onboarding feature ships (or equivalent instrumentation is added) — should measurement infrastructure (an "onboarding started"/"onboarding complete" timestamp pair) be added as an explicit acceptance criterion when that feature is implemented, so this KPI isn't permanently unmeasurable?

---

## Change Log

- 2026-07-17 | Initial draft, closing external gaps-register item P-1. Grounded entirely in observable engineering investment patterns across all 7 repos plus the SanchiPowerpitch cross-workspace contract — no vision/objective content invented without a cited piece of evidence. Every statement flagged `[INFERRED]` pending product-owner review.
- 2026-07-17 | Added the KPI Framework section, closing external gaps-register item P-2. Defined a measurable metric/formula per objective and stated data availability for each (confirmed available for Objectives 1-3, confirmed unavailable today for Objective 4 pending the Tenant Onboarding feature shipping, unconfirmed for Objective 5 pending a direct read of PowerPitch's session store). Deliberately left every target number `[TBD — product owner]` rather than inventing one — a fabricated number would read as a real commitment.
- 2026-07-17 | **Confirmed by Sanchi**: Vision ("sell the AI feature and increase company ARR") and 3 core KPIs (AI-credit revenue/ARR growth, AI feature adoption rate, evaluation throughput/SLA). Replaced the inferred vision as the authoritative statement (kept old inference as evidence trail, not deleted); re-tagged Objective 2 as `[CONFIRMED]` and objectives 1/3/4/5 explicitly as `[INFERRED]`; added a "Core KPIs" section mapping the 3 confirmed KPI names to grounded formulas/data-availability (flagging that "AI feature adoption rate" has two plausible readings — flag-enabled vs. actual-usage — not yet disambiguated); resolved Open Question #1 from the prior pass. Target numbers for all KPIs remain `[TBD — product owner]`.
