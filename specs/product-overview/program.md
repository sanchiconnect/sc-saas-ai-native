# program.md — SanchiConnect Product Charter

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 1 of 6
**Consolidates:** FRS v1.0 (§1–2), the three module specs (overviews, actors), UI/UX v6 (§1–2), the Sanchi Credits Sprint Plan (commercial model), and the team's 26 feature specs (product surface, roles-as-flags).
**Positioning:** the top of the specification set — what the product is, who it serves, what it is made of, how it is deployed and monetised, and which product-level decisions are open. The other five documents (`design`, `knowledge`, `database`, `api`, `ui-ux`) inherit their scope from here.
**Product:** SanchiConnect (referred to in platform documents as *SanchiSaaS*) — a multi-tenant incubator/accelerator management platform.

> Gaps are marked inline as **GAP · P-N** and collected in **§99**. The register lists only open items requiring resolution. `P-` = program-charter gaps; the other documents use `D-`, `K-`, `DB-`, `A-`, `U-`.

---

## 1. Purpose & How to Use This Document

This is the charter: the single place that states what SanchiConnect is, who uses it, what it comprises, and what remains undecided at the product level. Read it first, then read the domain document relevant to your task. It consolidates product-level truth that the source material spreads across a functional spec, three module specs, a design document, a sprint plan, and the team's feature specs — and it names the holes.

## 2. Product Overview

SanchiConnect is a **multi-tenant SaaS platform** on which an incubator, accelerator, or venture-studio organisation runs its programs end to end: it publishes calls for applications, collects and evaluates applications through configurable multi-round pipelines with jury scoring, manages an ecosystem of stakeholders, runs communications and events, issues certificates and digital ID cards, handles memberships and payments, and offers AI-assisted evaluation of applicants metered by a credit system.

The platform presents through **three layers**:

- **Member Web Application** — used by startups and every other stakeholder type, and by job seekers and public visitors.
- **Administration Panel** — used by program operators (super-administrators, program managers, jury, finance, ecosystem partners) to configure and run their programs.
- **Operator / Control-Plane layer** — used by the platform operator (SanchiConnect itself) to provision tenants, manage feature entitlements, and administer the AI-credit catalogue (packages, rates, grants, orders) through an operator UI over the shared control plane. This layer has no member-facing UI and is documented in `design.md` and `api.md`.

## 3. Business Context & Objectives

The commercial direction evidenced in the material is two-fold: membership/payment plans (tenant revenue) and a prepaid AI-credit system (operator revenue) — both detailed in §9. Beyond that, the platform's business intent is not written down.

> **GAP · P-1 — No stated product vision or objectives.** Neither the formal documentation nor the team's specs contains a vision, mission, or set of business objectives; both describe capability without intent. *Sanchi to provide:* a short product vision and the top three-to-five business objectives for the current horizon (from the product owner).

## 4. Goals & Success Metrics (KPIs)

The SRS supplies **non-functional targets** that act as system-level thresholds (content load 2–3 s, search 1–2 s, a 50,000-recipient broadcast dispatched within an agreed window, horizontal scale). These are carried into `design.md`. They are not, however, product KPIs.

> **GAP · P-2 — No success metrics or KPIs.** There is no measurable definition of success for the platform, any module, or the AI-credit product. Spec-driven acceptance anchors to measurable outcomes, so the product-level "done" cannot yet be stated. *Sanchi to provide:* KPI targets per objective (evaluation SLA, application throughput, credit-revenue, adoption).

## 5. Scope

### 5.1 In scope
The full member application layer, the full administration panel, the cross-cutting platform capabilities (multi-tenancy, branding, feature configuration, notifications), and the operator-side AI-credit administration.

### 5.2 Product surface
The platform's functional surface is covered by the team's feature specs, organised as **FA** (administration, 8 specs), **FAI** (AI, 2), **FE** (member/frontend, 12), and **FT** (tenant/control-plane, 4). The member side is therefore specced at feature level; the administration and control-plane sides likewise. This charter names the surface; the feature specs define its behaviour, and `knowledge.md` consolidates its rules.

**Member Web Application** covers registration & authentication, profiles, the eight stakeholder types, programs & calls for applications, business challenges, jobs & hiring, community & connections, messaging, learning, events & meetings, content library, facilities booking, payments & memberships, certificates & ID cards, support tickets, growth metrics, and search. **Administration Panel** covers authentication & access control, stakeholder management, program & application management, business challenges, jury & evaluation, learning admin, events admin, community moderation, finance & memberships, outreach & communications, content, certificates & ID cards, growth-metric oversight, support tickets, reporting & analytics, facilities admin, partner & recruitment admin, the custom form builder, third-party integrations, and system configuration.

## 6. Stakeholders, Actors & Roles

### 6.1 Member Web Application roles
| Role | Description |
|------|-------------|
| Startup | Primary applicant/member; company profile, applies to programs, tracks growth metrics/milestones, posts jobs |
| Investor | Investor profile (org or individual); discovers and connects with startups |
| Mentor | Provides mentorship; logs sessions for approval |
| Corporate | Posts business challenges; engages startups on innovation |
| Partner | Institutional partner managing its own sub-ecosystem of startups, contacts, and a program team |
| Service Provider | Offers services; maintains a directory profile |
| Program Office | Institutional program-running partner with its own profile, team, dashboard |
| Individual | Non-organisational member profile |
| Job Seeker | Searches and applies to job postings |
| Public Visitor | Unauthenticated visitor browsing public directories, listings, marketing content |

### 6.2 Administration Panel roles
| Role | Description |
|------|-------------|
| Super-Administrator | Full access to all administrative functions for the tenant |
| Program Manager | Manages assigned programs/challenges; reviews and progresses applications |
| Corporate Program Manager | Manages challenges/applications for a specific corporate account |
| Jury Member | Reviews and scores assigned applications/startups/candidates |
| Recruitment Partner | Manages job postings and applicants for assigned jobs |
| Partner Administrator | Manages a scoped slice of the ecosystem (own stakeholders, programs, contacts) |
| Finance/Operations Staff | Manages membership plans, payment configuration, invoicing, taxation |
| Developer/Technical Administrator | Configures platform-level settings, integrations, reporting infrastructure |

Authorisation is **role plus scope of assignment**, enforced on the backend for every request; the granular per-administrator **Allowed Features** flags refine this further. Detail in `design.md` §13.

### 6.3 Operator / platform actor
The platform operator administers tenants and the AI-credit catalogue through an operator UI over the control plane. This actor is real and building against it is under way, yet it appears in no formal role model.

> **GAP · P-4 — Operator persona undocumented.** The operator role that manages tenants, entitlements, and the credit catalogue has no persona or permission-scope definition. *Sanchi to provide:* the operator persona and its scope.

## 7. Product Structure & Module Inventory

A defining structural rule, confirmed at entity and feature-spec level: the platform runs a **two-track program model** — a profile-linked **Program** ("Startup Programs" navigation) and a general-application **Application Program** ("Custom Programs" navigation) — as genuinely separate entity families that share a common round/jury/rating pattern, not one entity with a type flag. This is elaborated in `knowledge.md` §4.3.

The administrative structure groups as: Dashboard; Startup Programs (application pipeline, round configuration, AI Analysis, program timeline); Custom Programs; Facility Management; Ecosystem Management (the eight stakeholder directories plus connections); Engagement (meetings, introductions, events); Settings (team management, profile forms, email templates, settings panel, connections matrix, Zoho management, certificate/ID-card builders); Broadcast Messaging; and AI Credits.

## 8. Tenancy, Deployment & Entitlement Model

The platform is **polyglot across six repositories** (member frontend, administration panel, business API, control plane, AI evaluation service, and a third-party integration gateway) — the full topology and stacks are in `design.md` §3.

Tenancy has **two isolation layers**: business data is **database-per-tenant** (each tenant its own database), while the **control plane is a single shared database with one row per tenant** (keyed by `domain`) holding identity, connection details, branding, and the feature flags. Both front ends and the backend bootstrap from the control plane's tenant-verification endpoint.

Platform capabilities are gated by a **feature-flag set of 218 boolean columns** on the control-plane tenant entity, loaded at bootstrap and enforced by route guards. Entire modules are switched on or off per tenant this way; packaging and entitlement are expressed purely as configuration. Branding is per-tenant. Mechanism detail is in `design.md` §5–6.

## 9. Monetisation & Commercial Model

Two mechanisms are evidenced:

**(a) Membership & payments.** Members purchase membership plans; programs may require payment as part of application submission; finance staff configure plans, invoicing, and taxation. Payments run through a **multi-gateway hub** (PayPal, Razorpay, Stripe, Easebuzz, PayU), tenant-selectable, with funds flowing to the tenant (incubator).

**(b) AI Credits — Sanchi Credits.** A **prepaid credit system** in which the platform operator sells credit packs, each tenant holds a per-tenant wallet, and AI evaluation actions debit the wallet at DB-driven task rates. Credit purchases run through a **distinct platform-level Easebuzz gateway** with funds flowing to the SanchiConnect operator — separate from the tenant payment flow above. Full domain rules are in `knowledge.md` §4.6.

> **GAP · P-5 — The AI-credit commercial model has no canonical requirements.** The credit system — pricing, rates, wallet, grants, gateway — exists only in the sprint plan, in screenshots, and in code; it is absent from the formal documentation *and* from the team's feature specs. It is a live commercial subsystem with no requirements pass. *Sanchi to provide:* a full requirements pass (is it billing, a soft cap, or a pilot?) and the confirmed catalogue and rates.

> **GAP · P-6 — Analysis credit rate undecided.** The live product shows 10 credits per applicant for analysis; the sprint plan sets 50 SC per applicant as the Phase-1 default. Because rates are operator-configurable, 50 is a default rather than a hard value, but the gap between what is live and what is planned is a real commercial decision. *Sanchi to decide:* the authoritative rate and whether the live system is migrating from 10 to 50.

## 10. Key Domains

The product's domain entities, business rules, and state machines — programs and rounds, applications and submissions, jury evaluation, the ecosystem stakeholder families, communications, and the AI-analysis and credit domains — are defined in **`knowledge.md`**, with their persistence in **`database.md`**. This charter only names them.

## 11. Open Product Decisions

Decisions the product owner must make before the affected areas can be locked:

1. AI credits: billing, soft cap, or pilot? Confirmed catalogue and rates. *(P-5, P-6)*
2. Bulk Email large-file delivery: inline-vs-link acceptable, threshold, link expiry, file-count ceiling, gating flag, and whether delivery routes through the backend or the admin. *(see `design.md` §12, `knowledge.md` §4.10)*
3. WhatsApp as a broadcast delivery channel: live, flag-gated, or dropped? *(WhatsApp is already wired for OTP and admin actions.)*
4. The operator persona and its permission scope. *(P-4)*

## 12. Assumptions & Constraints

- The formal FRS describes the platform "as currently implemented" — it is an as-built functional record. The team's feature specs likewise capture as-built behaviour and already surface quality/security findings; reconciling documentation against code is an ongoing transition activity.
- **Polyglot, multi-repo constraint:** the product spans six repositories with different stacks; the spec set and any change must account for cross-repo contracts (notably the frozen tenant-verification contract and the feature-flag column contract).
- **Two live subsystems are net-new** and not yet specced anywhere but the sprint plan and BRD: AI Credits and Bulk Email multi-file attachments. These are the natural first spec-driven pilots.

## 13. Glossary

| Term | Definition |
|------|------------|
| Tenant | A single incubator/accelerator organisation, with its own branding, data, and configuration |
| Stakeholder | Any registered profile type (startup, investor, mentor, corporate, partner, service provider, program office, individual) |
| CFA | Call for Applications — a structured, multi-round program application process |
| Program / Application Program | The two program tracks — profile-linked vs general application |
| Round | An evaluation stage within a program's pipeline |
| Jury | A panel of reviewers assigned to score and evaluate applications |
| Control plane | The shared service that identifies tenants and holds their configuration and feature flags |
| Feature flag | A per-tenant entitlement toggle (a boolean column on the control-plane tenant entity), enforced by backend guards |
| SC | Sanchi Credit — the unit of the prepaid AI-credit system |

> **GAP · P-7 — Glossary incomplete for new subsystems.** Terms introduced by the credit and attachment work (wallet, ledger, reserve/settle, task rate, grant, package, order; delivery mode) are undefined in any glossary. *Sanchi to confirm:* canonical definitions as those subsystems are specced.

## 14. Source Traceability

Consolidates **FRS v1.0** (§1 purpose/scope, §2 overview/roles, functional-area inventory), the **three module specs** (overviews, actors, structural rules), **UI/UX v6** (navigation map, structure), the **Sanchi Credits Sprint Plan** (commercial model, operator layer), and the **team's 26 feature specs** (the product surface and roles-as-flags). Their reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| P-1 | §3 | Product vision & business objectives | A charter needs stated intent | Product owner |
| P-2 | §4 | Success metrics / KPIs | Acceptance anchoring; product-level "done" | Product owner |
| P-4 | §6.3 | Operator persona & permission scope | Operator manages tenants/credits but is in no role model | Product owner |
| P-5 | §9 | Full AI-credit commercial requirements | Live subsystem with no canonical spec | Product owner + team |
| P-6 | §9 | Analysis credit-rate decision (10 vs 50) | Commercial decision blocking the credit spec | Product owner |
| P-7 | §13 | Glossary terms for new subsystems | Shared vocabulary for credits and attachments | Team |

*The next document is `knowledge.md` — the domain model, business rules, and state machines — reconciled against the team's feature specs.*
