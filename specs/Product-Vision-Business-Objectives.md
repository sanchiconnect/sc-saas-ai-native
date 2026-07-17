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

## Open Questions for the Product Owner

These cannot be resolved by reading code — they require an actual answer from whoever owns product strategy:

1. Is the vision statement above directionally correct, or does it miss/misstate the actual strategic intent?
2. Are these the right top 3-5 objectives for **the current horizon** specifically (this quarter/half/year) — as opposed to the long-run direction the evidence above can plausibly support?
3. Is there a target market-segment focus (e.g., university/government-linked incubators specifically, given the IP/Technology-Transfer-Office-shaped module, vs. corporate accelerators, vs. both) that should be stated explicitly?
4. Is the SanchiPowerpitch integration a strategic bet on an adjacent product line, or an opportunistic/one-off integration with no larger strategic weight? This materially changes how much future engineering investment that integration should receive.
5. Are there business objectives entirely absent from this inference because no corresponding engineering investment exists yet (e.g., a stated growth/market-expansion target, a profitability target, a specific customer-acquisition-cost or retention goal)? Code-reading can only surface intent that's already been built toward — it cannot surface a goal nobody has started building for yet.

---

## Change Log

- 2026-07-17 | Initial draft, closing external gaps-register item P-1. Grounded entirely in observable engineering investment patterns across all 7 repos plus the SanchiPowerpitch cross-workspace contract — no vision/objective content invented without a cited piece of evidence. Every statement flagged `[INFERRED]` pending product-owner review.
