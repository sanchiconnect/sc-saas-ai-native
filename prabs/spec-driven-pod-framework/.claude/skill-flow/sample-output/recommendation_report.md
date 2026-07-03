# Skill Recommendation Report
**Project:** Mobile-First Checkout Experience (PRG-MFCE-001)
**Generated:** 2026-06-08
**Engine Version:** 1.0.0
**Status:** BLOCKED — knowledge-review governance gate uncleared

---

## Executive Summary

45 catalog skills evaluated. 20 Required, 10 Recommended, 7 Optional, 8 Not Recommended, 4 Skill Enhancements proposed. Execution is blocked until `knowledge-review` clears the ⏸ PENDING REVIEW gate in `knowledge.md`. Apple Pay certification must be initiated by end of June 2026 to meet the October beta target.

---

## Project Understanding

| Attribute | Value |
|---|---|
| Stack | Python FastAPI 0.111 · Pydantic v2 · PostgreSQL 16 · Next.js 14 PWA · React Native 0.74 |
| Compliance | PCI-DSS Level 1 / SAQ-A · GDPR (EU residency) · WCAG 2.1 AA |
| Infra | AWS ECS Fargate · RDS Multi-AZ · ElastiCache Redis 7 · CloudFront |
| NFRs | LCP <1.5s · 99.95% uptime · 15K concurrent sessions · 5-min RTO |
| Rollout | LaunchDarkly 5% → 25% → 100% phased |
| Timeline | Q2–Q4 2026 build · Dec 2026 full launch |
| AI-native | No — AI-native skill cluster excluded |

---

## Phase 01 Coverage Assessment

| Artifact | Core Content | Blockers |
|---|---|---|
| program.md | Complete | None |
| knowledge.md | Domain model complete (BR-001–BR-041, 3 state machines) | ⏸ PENDING REVIEW — governance gate uncleared; Program Context / Customer Expectations / As-Is all PLACEHOLDER |
| design.md | Stack, infra, security, observability complete | [TO-BE] System Architecture PLACEHOLDER — design-setup not run |
| database.md | 6 tables, PCI-DSS scope, GDPR erasure complete | [AS-IS] and [TO-BE] Design Session Output PLACEHOLDER |
| api.md | All endpoints, schemas, rate limiting, error contract complete | [AS-IS] and [TO-BE] Design Session Output PLACEHOLDER |
| ui-ux.md | Design tokens, component library, WCAG gates complete | [AS-IS] and [TO-BE] Design Session Output PLACEHOLDER |
| features.md | — | EMPTY — 0 requirements captured |

---

## Required Skills (20)

These skills are mandatory. Omitting any creates a compliance, security, or delivery-critical gap.

| ID | Skill | Phase | Confidence | Rationale |
|---|---|---|---|---|
| REC-001 | knowledge-review | 02-KC | 95 | Governance gate uncleared; blocks design-setup and all downstream work |
| REC-002 | design-setup | 02-KC | 93 | 4 spec files have PLACEHOLDER TO-BE sections; depends on REC-001 |
| REC-003 | spec-generation | 02-KC | 90 | features.md empty (0 requirements); no spec.md or tasks.md; depends on REC-002 |
| REC-004 | DecisionLedger | 03-Planning | 88 | PCI-DSS/GDPR audit trail; Apple/Google Pay certification decisions |
| REC-005 | PolicyCatalog | 03-Planning | 95 | PCI-DSS + GDPR compliance rails required before build; feeds SpecFlow |
| REC-006 | SpecFlow | 03-Planning | 92 | Multi-pod parallel build plan; depends on spec-generation, PolicyCatalog, ContextFabric |
| REC-007 | TraceGraph | 03-Planning | 90 | BR traceability is a stated coding standard (design.md); HITL chain-of-custody required |
| REC-008 | KnowledgeMesh | 04-Build | 92 | 41 business rules + 3 state machines require accurate context for all build agents |
| REC-009 | SecretShield | 04-Build | 97 | Stripe API keys, JWT RSA private key, Google Maps API key, AWS credentials all present |
| REC-010 | TrustFabric | 04-Build | 95 | PCI-DSS gateway tokens + GDPR PII AES-256 + BR-020 enforcement at code generation |
| REC-011 | DevCopilot | 04-Build | 95 | Exact stack match: React/TypeScript + Python FastAPI + PostgreSQL (catalog Project Types) |
| REC-012 | ReviewPilot | 04-Build | 92 | Python/FastAPI + TypeScript/React match; 100% payment-module coverage required |
| REC-013 | ExperienceStudio | 04-Build | 88 | WCAG 2.1 AA mandatory NFR; 7 checkout components require Gate 2 accessibility validation |
| REC-014 | NexusDeploy | 04-Build | 90 | Docker/ECS Fargate; generates deploy-manifest.yaml required by SimLab and RolloutAdvisor |
| REC-015 | Guardian | 05-Validate | 93 | E2E tests for all 4 checkout workflows; BR-020/021/024 are safety-critical |
| REC-016 | PolicyEnforcer | 05-Validate | 95 | PCI-DSS + GDPR hard compliance gates; zero critical/high violations required |
| REC-017 | SimLab | 05-Validate | 92 | 15K concurrent sessions NFR; LCP <1.5s; BR-023 30s gateway timeout; BR-031 geocoding fallback |
| REC-018 | ParityChecker | 06-Release | 90 | Stripe test vs. live mode parity; multi-region AWS deployment |
| REC-019 | ReleaseIntel | 06-Release | 88 | Phased 5% → 25% → 100% rollout; live payment blast-radius assessment |
| REC-020 | RolloutAdvisor | 06-Release | 90 | LaunchDarkly explicitly in design.md; 5-min RTO; 99.95% availability SLA |

---

## Recommended Skills (10)

High value for this project; omit only if capacity is constrained.

| ID | Skill | Phase | Confidence | Rationale |
|---|---|---|---|---|
| REC-021 | AssumptionTracker | 03-Planning | 78 | Apple/Google Pay cert risks rated Medium/High in risk register |
| REC-022 | Conductor | 03-Planning | 75 | 4-pod parallel execution requires coordination layer |
| REC-023 | ContextFabric | 03-Planning | 78 | 5-domain capability gap detection before SpecFlow clusters are assigned |
| REC-024 | PortfolioPrioritizer | 03-Planning | 72 | Q3 2026 certification deadlines + multi-feature capacity allocation |
| REC-025 | ScenarioPlanner | 03-Planning | 70 | $2.8M ROI sensitivity; cert delay impact quantification |
| REC-026 | SpecImpactAnalyzer | 03-Planning | 75 | Cert delay may force mid-sprint spec changes across all 4 pods |
| REC-027 | ValueModeler | 03-Planning | 78 | $2.8M + 2.1% → 3.5% conversion + 4.2 → 1.8 min checkout time anchors |
| REC-028 | PerformanceOptimizer | 04-Build | 72 | Multi-pod generation workload; payment module is highest complexity cluster |
| REC-029 | RunbookSynth | 07-Operations | 75 | 3-region AWS + complex payment gateway + zero-tolerance ERROR policy on payment module |
| REC-030 | ValueTracker | 07-Operations | 73 | Google Analytics KPIs defined; closes ValueModeler ROI loop |

---

## Optional Skills (7)

Conditional value. Activate only when the stated condition is met.

| ID | Skill | Phase | Confidence | Condition |
|---|---|---|---|---|
| REC-031 | doc-extraction | 02-KC | 62 | Customer-provided documents exist |
| REC-032 | meeting-extraction | 02-KC | 65 | Call transcripts available |
| REC-033 | requirements-elicitation-charter | 02-KC | 60 | Additional discovery meetings are planned |
| REC-034 | ResearchCopilot | 03-Planning | 58 | No discovery evidence files provided; activate if competitive research needed |
| REC-035 | ExperimentOps | 07-Operations | 63 | A/B testing in scope but skill status is "Proposed"; LaunchDarkly covers traffic split |
| REC-036 | IncidentLens | 07-Operations | 60 | Useful after 4–6 production sprints; low value pre-launch |
| REC-037 | RuntimeIQ | 07-Operations | 65 | Datadog APM already configured; incremental value only |

---

## Not Recommended (8)

Excluded due to project type mismatch or inapplicable prerequisites.

| ID | Skill | Reason |
|---|---|---|
| REC-038 | code-extraction | Greenfield build — no existing codebase to extract |
| REC-039 | EvalHarness | AI-native projects only; no AI outputs in checkout |
| REC-040 | InsightOps | Requires EvalHarness + RedTeamX outputs; both excluded |
| REC-041 | PromptBench | No AI feature prompts to benchmark |
| REC-042 | RedTeamX | No AI-facing components in checkout flow |
| REC-043 | ControlPlane | AI-native projects only; no AI agent cost tracking applicable |
| REC-044 | DriftGuard | AI-native projects only; no AI model outputs to monitor |
| REC-045 | TransformIQ | No AI opportunity backlog; opportunity-catalogue.yaml not applicable |

---

## Skill Enhancements (4)

Targeted additions to existing skill behavior. Submit to skill maintainers before Phase 02 execution.

**REC-046 — knowledge-review: Certification Timeline Validation**
Add a certification initiation date check to the Design Readiness Assessment. Apple Pay requires 6–8 weeks lead time; Google Pay requires 4–6 weeks. Check must validate initiation date vs. Oct 2026 beta target and block sign-off if lead time is insufficient.
Placement: Knowledge Completeness Checklist → Compliance & Constraints section.
Confidence: 82

**REC-047 — spec-generation: Empty features.md Preflight Check**
Add a Phase 0 preflight that halts if features.md contains zero FR-n entries. Present three options: run meeting-extraction, run doc-extraction, or start inline elicitation. Do not proceed to spec generation with an empty feature set.
Placement: New Step 0 before Pre-generation source summary.
Confidence: 88

**REC-048 — TrustFabric: PAYMENT_TOKEN PII Classification Level**
Add a dedicated PAYMENT_TOKEN classification level (above FINANCIAL) with four hard rules: never returned in API responses, AES-256 at rest mandatory, never written to logs, BR-022 single-use wallet token check enforced. Map to `payments.gateway_token` and `payment_method_tokens.gateway_token`.
Placement: PII Taxonomy section + generated code validation step.
Confidence: 90

**REC-049 — PolicyCatalog: PCI-DSS SAQ-A Compliance Guards**
Add a PCI_DSS_SAQ_A category to policy-library.md with four specific guards: (1) no custom card input fields — Stripe Elements only, (2) no `payment_method_id` or `gateway_token` in any log output, (3) Apple/Google Pay must use `@stripe/react-stripe-js PaymentRequestButton`, (4) no raw PAN/CVV/expiry in any endpoint. Inject into all payment-module and gateway_token-touching SpecFlow clusters.
Placement: policy-library.md new category + compliance signal scanner update.
Confidence: 88

---

## Execution Plan

### Phase 02 — Knowledge Completion (BLOCKED)

| Step | Action | Owner | Blocker |
|---|---|---|---|
| 02.1 | Clear knowledge-review governance gate with Pod Lead + Program Lead | Pod Lead | ⏸ PENDING — do not proceed until signed off |
| 02.2 | Populate Program Context, Customer Expectations, As-Is System in knowledge.md | Pod Lead | Requires 02.1 |
| 02.3 | Run doc-extraction (if documents exist) and/or meeting-extraction (if transcripts exist) | — | Optional; run before 02.4 |
| 02.4 | Run design-setup to populate TO-BE Design Session Output sections across design.md, database.md, api.md, ui-ux.md | — | Requires 02.1 |
| 02.5 | Run spec-generation to populate features.md and generate spec.md + tasks.md | — | Requires 02.4; will trigger REC-047 preflight |

### Phase 03 — Planning

| Step | Action | Dependencies |
|---|---|---|
| 03.1 | Run PolicyCatalog → generate policy-library.md (apply REC-049 SAQ-A guards) | 02.5 complete |
| 03.2 | Run ContextFabric → 5-domain capability gap map | 02.5 complete |
| 03.3 | Run AssumptionTracker, ValueModeler, PortfolioPrioritizer, ScenarioPlanner | 03.1–03.2 |
| 03.4 | Run SpecFlow → multi-pod parallel build plan | 03.1, 03.2, 02.5 |
| 03.5 | Run TraceGraph, DecisionLedger, SpecImpactAnalyzer, Conductor | 03.4 |

### Phase 04 — Build

| Step | Action | Dependencies |
|---|---|---|
| 04.1 | Run KnowledgeMesh → knowledge context for all build agents | 03.5 |
| 04.2 | Run SecretShield → credentials vault gate (mandatory before any code generation) | 04.1 |
| 04.3 | Run TrustFabric → PII/payment-token enforcement (apply REC-048) | 04.1 |
| 04.4 | Run DevCopilot → code generation across all pods | 04.1–04.3 |
| 04.5 | Run ReviewPilot → 100% payment-module coverage | 04.4 |
| 04.6 | Run ExperienceStudio → WCAG 2.1 AA gate on 7 checkout components | 04.4 |
| 04.7 | Run NexusDeploy → deploy-manifest.yaml | 04.4 |
| 04.8 | Run PerformanceOptimizer (recommended) | 04.4 |

### Phase 05 — Validate

| Step | Action | Dependencies |
|---|---|---|
| 05.1 | Run Guardian → E2E tests for all 4 checkout workflows | 04.5–04.7 |
| 05.2 | Run PolicyEnforcer → PCI-DSS + GDPR hard gates (zero critical/high) | 04.5–04.7 |
| 05.3 | Run SimLab → 15K concurrent load + LCP + timeout + geocoding fallback | 04.7 |

### Phase 06 — Release

| Step | Action | Dependencies |
|---|---|---|
| 06.1 | Run ParityChecker → Stripe test/live parity + multi-region | 05.1–05.3 |
| 06.2 | Run ReleaseIntel → phased rollout blast-radius assessment | 05.1–05.3 |
| 06.3 | Run RolloutAdvisor → LaunchDarkly gate configuration | 06.1–06.2 |

### Phase 07 — Operations

| Step | Action | Condition |
|---|---|---|
| 07.1 | Run RunbookSynth → 3-region runbooks (recommended) | Post-launch |
| 07.2 | Run ValueTracker → KPI closure loop | Post-launch |
| 07.3 | Activate ExperimentOps, IncidentLens, RuntimeIQ | If conditions met (see Optional) |

---

## Key Risks and Gaps

| Risk | Severity | Action Required |
|---|---|---|
| knowledge-review ⏸ PENDING REVIEW — blocks entire Phase 02+ plan | Critical | Schedule Pod Lead + Program Lead review immediately; no other Phase 02 work can start |
| features.md EMPTY — 0 requirements captured | Critical | Run doc-extraction / meeting-extraction before spec-generation; REC-047 preflight will enforce |
| Apple Pay certification lead time — 6–8 weeks; Oct 2026 beta target requires initiation by end of June 2026 | High | Initiate Apple Pay certification application this week; REC-046 adds formal check to knowledge-review |
| Google Pay certification — 4–6 weeks lead time | High | Initiate alongside Apple Pay; certifications are independent processes |
| APAC data residency legal review unresolved | High | ap-southeast-1 region launch should not proceed until legal review is complete |
| 29 catalog skills missing Project Types field | Medium | Catalog maintainer action; does not block execution but increases false-positive risk in Phase 4 matching |
| design-setup not run — 4 spec files have PLACEHOLDER TO-BE sections | Medium | Blocked on knowledge-review clearance; resolved by REC-002 |
| AI-native skill cluster excluded (EvalHarness, RedTeamX, InsightOps, PromptBench, ControlPlane, DriftGuard) | Info | Not applicable to this project type; no action required |
