# Framework Skill Catalog

Generated: 2026-06-12
Catalog Version: 2
Skills Cataloged: 70
Catalog Scope: Full
Validation Status: PASS WITH FLAGS
Flags: 44 (Project Types not declared in skill source for 44 skills)

---

## AssumptionTracker

**Skill Name:** AssumptionTracker

**Purpose:** Ingests weak-evidence flags from ResearchCopilot and explicit assumptions in openspec.yaml, assigns a confidence score (0–1) to each assumption, flags low-confidence items as HITL gate blockers, tracks resolution throughout the sprint lifecycle, and escalates unresolved items to DecisionLedger for explicit risk acceptance.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Assumption inventory from openspec.yaml and evidence-map.md with deduplication
- Confidence scoring using evidence strength, prior sprint history, and dependency factors
- HITL blocker classification based on configurable threshold and risk posture
- Resolution tracking with VALIDATE / ACCEPT_RISK / DEFER / DESCOPE recommendations
- Escalation payload generation for DecisionLedger on risk-accepted assumptions

**Owned Responsibilities:**
- Sprint assumption confidence management
- HITL gate blocker identification and tracking
- Assumption resolution lifecycle

**Inputs:**
  Mandatory:
    - artifacts/evidence-map.md: Weak-evidence flags from ResearchCopilot
    - artifacts/openspec.yaml: Sprint requirements with assumption tags
    - specs/knowledge.md: Domain-level assumption context
  Optional:
    - references/assumption-history.yaml: Prior sprint assumption resolutions

**Outputs:**
- artifacts/assumption-log.md: Scored assumptions with HITL blocker classification and resolution status

**Dependencies:**
- ResearchCopilot: Provides evidence-map.md used as primary input
- DecisionLedger: Receives escalation payloads for ACCEPT_RISK resolutions

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Confidence thresholds are subjective until calibrated across 2–3 sprints
- First sprint scoring is approximation — all HITL_BLOCKERS require manual POD Lead review
- Identifies risks; does not resolve them — resolution requires human judgment
- Proposed status: threshold definition and escalation rules need stakeholder alignment before production use

**Summary:** Scores sprint assumptions from ResearchCopilot evidence and openspec.yaml, flags low-confidence items as HITL gate blockers, and escalates risk-accepted items to DecisionLedger.

---

## ArtifactsGeneration

**Skill Name:** ArtifactsGeneration

**Purpose:** A collection of five on-demand artifact generator utilities that auto-generate prerequisite files required by downstream skills. Each generator reads available Phase 01 specifications to infer content, writes the target artifact without requiring human input, and flags anything it cannot confidently infer in a post-generation summary. Generators are invoked individually when their target artifact is absent or needs regeneration — they are not tied to any execution phase.

**Phase:** On-demand (no phase assignment — invoked by downstream skills or directly by user when a prerequisite artifact is missing)

**Capabilities:**
- Sprint artifact bootstrapping: generates `artifacts/openspec.yaml` and `artifacts/sprint-capacity.yaml` from specs and targeted elicitation (CreateOpenspec)
- Policy library auto-generation: produces `references/policy-library.md` by inferring applicable compliance frameworks from project context (CreatePolicyLibrary)
- Coding convention generation: produces `.cursorrules` at the project root from tech stack and coding standards in specs (CreateCursorrules)
- AI builder guide generation: produces `AGENTS.md` at the project root from program identity, specs, and business rules (CreateAgents)
- Data contract generation: produces one `data-contracts/<entity>.yaml` per database entity from schema, API, and domain knowledge (CreateDataContracts)

**Owned Responsibilities:**
- On-demand prerequisite artifact creation for downstream skills
- Inference-first generation from existing Phase 01 specifications with gap flagging

**Inputs:**
  Mandatory (varies by generator):
    - specs/program.md: Program identity, goals, constraints
    - specs/design.md: Tech stack, coding standards, architecture, security design
    - specs/knowledge.md: Business rules, domain entities, roles, compliance considerations
    - specs/database.md: Tables, fields, data types, relationships, retention rules (CreateDataContracts)
  Optional:
    - specs/api.md: API contracts, field exposure rules (CreateDataContracts, CreateOpenspec)
    - specs/impl.md: Environment configuration, CI/CD, additional coding standards (CreateCursorrules)
    - specs/tasks.md: Task catalogue for sprint scope resolution (CreateOpenspec)

**Outputs:**
- artifacts/openspec.yaml: Sprint requirement spec (CreateOpenspec)
- artifacts/sprint-capacity.yaml: Sprint team capacity definition (CreateOpenspec)
- references/policy-library.md: Master compliance rail library (CreatePolicyLibrary)
- .cursorrules: Project-root coding convention rules for DevCopilot and ReviewPilot (CreateCursorrules)
- AGENTS.md: Project-root AI builder guide for DevCopilot and ReviewPilot (CreateAgents)
- data-contracts/<entity>.yaml: One contract per database entity for TrustFabric validation (CreateDataContracts)

**Dependencies:**
- No upstream skill dependencies — reads Phase 01 specifications directly
- Downstream consumers: Conductor, SpecFlow, PolicyCatalog, TraceGraph, Guardian, PerformanceOptimizer, TrustFabric, DevCopilot, ReviewPilot

**Project Types:**
- All project types using the SpecPod framework that require sprint execution, compliance rails, or data contract validation

**Constraints:**
- Generators run automatically from specs — interactive elicitation only occurs in CreateOpenspec when content cannot be inferred
- Each generator is invoked individually for its specific target artifact; there is no combined run mode
- Does not appear in any sequential prompt file — invoked on-demand only
- Gap flagging is post-generation only; generators do not block on missing input

**Summary:** Five on-demand artifact generators that auto-produce prerequisite files (openspec, policy library, cursorrules, AGENTS.md, data contracts) from existing Phase 01 specifications, enabling downstream skills to run without manual artifact preparation.

---

## AxiomTestGen

**Skill Name:** AxiomTestGen

**Purpose:** Deterministic software test-case generation for a single epic or task, invoked after DevCopilot finishes implementation. Derives oracles from the spec (never from the implementation), binds tests to the real code surface, applies formal test-design techniques, and produces four artifacts: runnable test files, a machine-readable test-plan manifest, a requirement-to-test traceability matrix, and a coverage-gap report with HITL flags.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Scope resolution from tasks.md and task-breakdown.yaml (epic/task ID + AC set + scope boundary)
- Framework/language auto-detection (pytest, jest/vitest, JUnit 5, go test, Rust built-in); asks only if ambiguous
- Acceptance-criteria decomposition into atomic Given/When/Then assertions traceable to AC IDs
- Binding to verified symbol table from DevCopilot provenance (ai-manifest.json) — blocks hallucinated APIs
- Formal test-design technique application: EP, BVA, decision tables, state-transition, pairwise reduction, property-based
- Oracle derivation from spec only (spec.md, api.md, database.md) — never from the implementation
- Mandatory edge-case injection: boundary, null/empty/missing, format/type violation, error paths, idempotency/retry, ordering/concurrency
- Coverage gap check against >90% line+branch target with HITL-flagged gap report
- Determinism enforcement: injected clocks, mocked I/O, seeded RNG, no order dependence
- Self-check: parse/lint every generated test; assertion-strength check; case-ID/AC-link verification

**Owned Responsibilities:**
- Spec-traceable test-case generation per epic/task
- Test-plan manifest production for Guardian/CI handoff
- Coverage gap identification and HITL escalation

**Inputs:**
  Mandatory:
    - specs/spec.md: Consolidated spec — authoritative oracle source for acceptance criteria
    - specs/tasks.md: Task catalogue — resolves epic/task scope
    - artifacts/task-breakdown.yaml: Decomposed task tree with AC IDs and scope boundary
    - artifacts/ai-manifest.json: Builder assignments and artifact provenance (task → source files)
    - src/…: Implemented source from DevCopilot — bound for surface/signatures only
  Optional:
    - specs/api.md: API contracts — oracle for contract-level tests
    - specs/design.md: Design constraints bounding legal behaviour
    - specs/database.md: Schema — oracle for persistence/integration tests
    - artifacts/policy-catalogue.yaml: Coverage targets and test-data policy (synthetic-only, PII rules)

**Outputs:**
- tests/<epic-id>/…: Runnable test files (unit/integration/contract/acceptance) in detected framework convention
- test-plan.<epic-id>.yaml: Machine-readable manifest — case ID, level, technique, AC link, oracle, fixtures
- test-traceability.md: Bidirectional acceptance-criterion → test-case matrix
- coverage-gap-report.md: Uncovered/ambiguous ACs with HITL flags (🔴 Blocking, 🟡 Caution, 🟢 Info)

**Dependencies:**
- DevCopilot: Produces src/ implementation and ai-manifest.json provenance — required upstream
- SpecFlow / SpecGenerator: Produces spec.md, tasks.md, task-breakdown.yaml — required upstream
- Guardian: Consumes test-plan.<epic-id>.yaml as execution gate evidence — primary downstream
- ReviewPilot: Consumes generated test files during PR review
- EvalHarness: Consumes test results where LLM-as-judge scoring applies
- CI / NexusDeploy: Consumes test-plan manifest for pipeline gating

**Project Types:**
- Any project type supported by detected test framework (Python/pytest, TypeScript/jest or vitest, Java/JUnit 5, Go/testing, Rust/built-in)

**Constraints:**
- Generates tests only — does not execute, measure live coverage, or gate (Guardian/CI scope)
- Adversarial and security negative cases belong to RedTeamX; AxiomTestGen covers input-validation negatives only
- Coverage % is a floor, not proof of correctness — mutation testing recommended for critical tasks
- Requires all five mandatory inputs; will not infer acceptance criteria from source code
- Model escalates to Opus for criticality tier: critical or NFR-safety epics

**Summary:** Generates a complete, spec-traceable test suite (unit/integration/contract/acceptance) after DevCopilot implementation, producing four artifacts — runnable tests, a test-plan manifest, a traceability matrix, and a coverage-gap report — with oracles derived exclusively from the spec and >90% coverage as the minimum target.

---

## code-extraction

**Skill Name:** code-extraction

**Purpose:** Parses legacy or existing source code to extract as-is system knowledge into the program knowledge base, covering source code behavior, API surface, data model, and architectural patterns.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Source code analysis (entry points, module structure, business logic, external dependencies, auth patterns)
- API definition parsing (OpenAPI, Swagger, WSDL, gRPC)
- Database schema extraction from SQL schemas and migration scripts
- Infrastructure and IaC analysis
- knowledge.md update with AS-IS system entries
- api.md update with AS-IS API surface
- database.md update with AS-IS data model and entity relationship summary
- design.md update with AS-IS architecture seed and technical debt register

**Owned Responsibilities:**
- As-is system knowledge extraction from code artifacts
- Legacy system behavior documentation
- Technical debt identification

**Inputs:**
  Mandatory:
    - Source code artifacts: At least one of — source files, repository, schema SQL, migration scripts, OpenAPI/Swagger/WSDL, config files, or IaC
  Optional:
    - knowledge.md: Existing knowledge for conflict detection
    - api.md: Existing API docs for conflict detection
    - database.md: Existing schema for conflict detection
    - design.md: Existing design for conflict detection

**Outputs:**
- Updates to knowledge.md (AS-IS SYSTEM section)
- Updates to api.md (AS-IS API surface)
- Updates to database.md (AS-IS data model)
- Updates to design.md (AS-IS ARCHITECTURE seed)
- Code Extraction Report

**Dependencies:**
- None

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Never infer business rules not evidenced in code; flag as [INFERRED — requires validation]
- Dead code goes to Technical Debt Register, not active behavior documentation
- Credentials or secrets found in code must not be reproduced — note presence as security finding only
- Large codebases: prioritize entry points → routing → domain models → schema → service logic

**Summary:** Analyzes legacy or existing source code to extract and document as-is system behavior, API surface, data model, and architecture into program knowledge files.

---

## Conductor

**Skill Name:** Conductor

**Purpose:** Central cross-phase sprint orchestrator that reads all planning artifacts, maps every task to the correct AI Builder and accelerator skill, sequences dispatch respecting inter-agent dependencies, holds dispatch until HITL gates are cleared, and maintains the live sprint board throughout the sprint.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Pre-flight validation of all required input files and gate status
- Task-to-builder mapping using capability matrix
- Dependency resolution and BLOCKED task flagging
- Sprint board generation with task status tracking
- Dispatch log with timestamped events
- Completion forecast calculation
- Escalation on task failure, HITL timeout, and mid-sprint spec change

**Owned Responsibilities:**
- Sprint task dispatch orchestration
- AI Builder coordination and load balancing
- HITL gate enforcement (never bypasses)
- Sprint board state management
- Escalation management

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Sprint requirements
    - artifacts/task-breakdown.yaml: Task cluster definitions (from SpecFlow)
    - artifacts/ai-manifest.json: Component registry (from SpecFlow)
    - artifacts/policy-catalogue.yaml: Compliance rails (from PolicyCatalog)
    - artifacts/traceability-report.md: Traceability verification (from TraceGraph)
    - artifacts/sprint-scope-ranked.md: Ranked scope list (from PortfolioPrioritizer)
    - artifacts/assumption-log.md: HITL blocker status (from AssumptionTracker)
    - artifacts/decision-ledger.md: Decision audit trail (from DecisionLedger)
    - specs/tasks.md: Task inventory from prior phase
    - specs/program.md: Program charter from prior phase
  Optional:
    - artifacts/context.yaml: Enterprise context (from ContextFabric)
    - artifacts/impact-analysis.md: Spec change impact (from SpecImpactAnalyzer)
    - artifacts/rework-scope-patch.yaml: Re-queue list (from SpecImpactAnalyzer)

**Outputs:**
- artifacts/sprint-board.md: Live task board with builder assignments and status
- artifacts/dispatch-log.md: Append-only timestamped dispatch event log

**Dependencies:**
- SpecFlow: Provides task-breakdown.yaml and ai-manifest.json
- PolicyCatalog: Provides policy-catalogue.yaml
- TraceGraph: Provides traceability-report.md
- PortfolioPrioritizer: Provides sprint-scope-ranked.md
- AssumptionTracker: Provides assumption-log.md
- DecisionLedger: Provides decision-ledger.md
- ContextFabric: Provides context.yaml (optional)
- SpecImpactAnalyzer: Provides impact-analysis.md and rework-scope-patch.yaml (if spec changed)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Never bypasses a HITL gate; queues and waits for POD Lead confirmation
- Requires Gate 1 (Plan Sign-off) clearance before any dispatch
- Open HITL blockers in assumption-log.md halt all dispatch
- Re-routing decisions on failed tasks are suggestions; POD Lead makes the final call

**Summary:** Orchestrates sprint task dispatch by mapping tasks to AI Builders, enforcing HITL gates, and maintaining the live sprint board throughout the sprint week.

---

## ContextFabric

**Skill Name:** ContextFabric

**Purpose:** Refreshes the enterprise context snapshot each sprint by mapping new requirements to existing system capabilities, detecting gaps requiring new build tasks, and publishing a versioned context.yaml that SpecFlow uses as the authoritative system capability reference.

**Phase:** 02-Data-Readiness (also active in 03-Platform-Enablement for live context retrieval)

**Capabilities:**
- Capability inventory from spec files (API endpoints, database entities, UI components, business logic, integration points)
- Change detection against prior context.yaml snapshot
- Requirement-to-capability mapping with EXISTS / EXISTS_MODIFIED / GAP / ASSUMED classification
- Gap complexity estimation (LOW / MEDIUM / HIGH)
- Versioned context.yaml generation

**Owned Responsibilities:**
- Enterprise context grounding per sprint
- Capability gap detection and build task recommendation
- System capability registry maintenance

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Sprint requirements to map
    - specs/knowledge.md: As-is system knowledge
    - specs/design.md: Technical architecture
    - specs/database.md: Schema definitions
    - specs/api.md: API contracts
  Optional:
    - artifacts/ai-manifest.json: Previously generated artifacts as confirmed capabilities
    - Enterprise API docs / schema files: Extended capability evidence
    - Change signals (incident logs, drift reports): Capability change annotations

**Outputs:**
- artifacts/context.yaml: Versioned capability inventory with requirement-to-capability mapping
- Capability Gap Report (section of context.yaml rendered for POD Lead)

**Dependencies:**
- spec-knowledge: Provides knowledge.md
- spec-design: Provides design.md
- spec-database: Provides database.md
- spec-api: Provides api.md
- SpecFlow: Provides ai-manifest.json (optional, prior sprint)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Context coverage bounded by machine-readable spec files; undocumented systems are blind spots
- Tribal knowledge requires manual POD Lead annotation
- Maps capabilities but does not validate against live running systems
- Proposed status: context refresh cadence and scope boundary rules need further definition

**Summary:** Refreshes a versioned enterprise context snapshot mapping requirements to existing capabilities, flags gaps requiring new build tasks, and publishes context.yaml for SpecFlow consumption.

---

## ControlPlane

**Skill Name:** ControlPlane

**Purpose:** Financial and security governor of the production AI system — enforces hard monthly cost ceilings per agent and per feature, right-sizes compute allocations based on observed usage patterns, and monitors access patterns for security anomalies.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Monthly cost ceiling enforcement per agent with configurable alert threshold (default 70%)
- Cost monitor script generation with billing API integration
- Consumption block generation (Kubernetes NetworkPolicy, API gateway throttling, or middleware)
- Security anomaly detection with configurable sensitivity
- Cost dashboard generation showing per-agent spend vs. ceiling
- Cost-config.yaml generation as authoritative scaling bounds for RuntimeIQ

**Owned Responsibilities:**
- Production AI system cost governance
- Monthly cost ceiling enforcement
- Security posture monitoring and anomaly alerting
- cost-config.yaml maintenance for RuntimeIQ

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Per-feature resource requirements and token budgets
    - artifacts/deploy-manifest.yaml: Deployed agents and services to govern
    - artifacts/roi-brief.md: Sprint budget context
    - specs/design.md: Architecture decisions affecting resource footprint
    - Monthly cost ceiling per agent: Elicited from POD Lead
    - Alert threshold percentage: Elicited (default 70%)
    - Billing data source: Elicited
    - Security monitoring sensitivity: Elicited
    - Alert notification channel: Elicited

**Outputs:**
- operate/control-plane/cost-config.yaml: Master cost governance config
- operate/control-plane/control-plane-monitor.py: Billing poller and alert sender
- operate/control-plane/cost-gate.py: Consumption enforcement middleware
- operate/control-plane/cost-limit-networkpolicy.yaml: Kubernetes cost enforcement (if K8s)
- operate/control-plane/security-monitor.py: Access pattern anomaly detector
- operate/control-plane/cost-dashboard.json: Per-agent spend vs. ceiling dashboard
- operate/control-plane/cost-event-log.md: Cost alert log
- operate/control-plane/security-event-log.md: Security anomaly log

**Dependencies:**
- RuntimeIQ: Consumes cost-config.yaml for scaling bounds
- IncidentLens: Consumes security-event-log.md for incident cross-reference

**Project Types:**
- AI-native production systems

**Constraints:**
- Security baseline requires 7-day observation-only period before alerting
- Consumption block activation requires POD Lead confirmation at first trigger
- Billing API unreachable falls back to conservative daily estimate with POD Lead alert
- Ceiling already exceeded at first run: CRITICAL alert issued; block not activated without POD Lead confirmation

**Summary:** Governs production AI system costs by enforcing configurable monthly ceilings per agent and monitoring access patterns for security anomalies, with automated alerting and consumption blocking.

---

## DecisionLedger

**Skill Name:** DecisionLedger

**Purpose:** Captures every scope, spec, and HITL gate decision made during the sprint in a structured, append-only log — timestamped, linked to requirement IDs, and attributed to a named approver — and produces official attestation records for all HITL gates.

**Phase:** 02-Data-Readiness (invoked on-demand throughout the sprint)

**Capabilities:**
- Append-only decision entry creation with auto-incrementing IDs
- Decision types: scope-change, spec-change, defer, descope, gate-clearance, risk-acceptance, assumption-resolution
- Query by requirement ID, date range, approver, or type
- Superseded entry marking (prior decisions marked but never deleted)
- Sprint summary report generation (business-lead-ready)
- HITL gate attestation record production

**Owned Responsibilities:**
- Immutable sprint decision audit trail
- HITL gate attestation records
- Decision traceability by requirement ID

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: For REQ-ID validation
  Optional:
    - artifacts/decision-ledger.md: Prior run file for append mode
    - artifacts/impact-analysis.md: For spec change entries
    - artifacts/sprint-scope-ranked.md: For defer entries

**Outputs:**
- artifacts/decision-ledger.md: Append-only timestamped decision log
- artifacts/decision-summary.md: Business-lead-ready sprint decision summary

**Dependencies:**
- SpecImpactAnalyzer: Provides impact-analysis.md for spec change entries
- PortfolioPrioritizer: Provides sprint-scope-ranked.md for defer entries

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Never modifies or deletes entries; corrections are new entries that supersede prior ones
- Verbal-only decisions that bypass the system leave no trace; POD Lead must log them manually
- Append-only integrity must be enforced by POD Lead outside of DecisionLedger invocations

**Summary:** Maintains an immutable append-only audit log of all sprint scope, spec, and gate decisions with timestamps and approver attribution, queryable by requirement ID or date.

---

## design-setup

**Skill Name:** design-setup

**Purpose:** Conducts a structured interactive design session with the Pod Lead and Program Lead to define all to-be technical architecture decisions and populate TO-BE content across design.md, uiux.md, api.md, database.md, and impl.md.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Pre-design context load from knowledge.md, features.md, and existing design files
- Structured questionnaire across 8 design domains: system architecture, technology stack, data architecture, API design, UI/UX direction, infrastructure and deployment, security and compliance, cross-cutting concerns
- Constraint and compatibility validation against knowledge.md
- Design Validation Report with confirmed decisions, constraint conflicts, migration risks, and pending decisions
- TO-BE content population for all five design files

**Owned Responsibilities:**
- TO-BE technical architecture definition
- Technology stack selection and documentation
- Design document population across design.md, uiux.md, api.md, database.md, impl.md

**Inputs:**
  Mandatory:
    - knowledge.md: Business objectives, constraints, as-is system, technology constraints
    - features.md: Feature requirements and priorities
  Optional:
    - design.md: Existing AS-IS architecture and any seeded TO-BE decisions
    - uiux.md: Existing AS-IS UI documentation

**Outputs:**
- design.md (TO-BE SYSTEM ARCHITECTURE section)
- uiux.md (TO-BE UI/UX DESIGN section)
- api.md (TO-BE API DESIGN section)
- database.md (TO-BE DATA MODEL section)
- impl.md (Implementation Guide — full document)

**Dependencies:**
- knowledge-review: Recommended prerequisite; warned if knowledge.md lacks REVIEWED status

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Never overwrites AS-IS sections in any file
- Endpoint inventory in api.md and full entity model in database.md deferred to Sprint 0 detailed design
- All design decisions must reference the constraint or expectation from knowledge.md that motivated them
- TBD or not-sure answers recorded as [DESIGN DECISION PENDING] with explicit owner

**Summary:** Leads a structured 8-domain design session to capture all TO-BE technical architecture decisions and populate design.md, uiux.md, api.md, database.md, and impl.md.

---

## DevCopilot

**Skill Name:** DevCopilot

**Version:** 2.2.0

**Purpose:** Primary implementation assistant for AI Builders during build days — generates spec-anchored code for a React/Python FastAPI/PostgreSQL stack with provenance headers, spec traceability IDs, and convention compliance, then gates delivery behind a closed-loop Spec Conformance Score (SCS ≥ 90%, zero critical failures) with up to three automated re-engineering passes before escalating to the POD Lead.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Task context assembly from task-breakdown.yaml, openspec.yaml, KnowledgeMesh, and TrustFabric
- Pre-generation checklist validation (requirement clarity, data contracts, duplication check, compliance rail)
- Stack-specific code generation: React/TypeScript (functional components, Tailwind, React Query, Zod), Python FastAPI (Pydantic v2, SQLAlchemy 2.0 async, Alembic), PostgreSQL (UUID PKs, Alembic migrations)
- Provenance header injection per generated file
- Closed-loop Spec Conformance Validation: six-dimension SCS scoring (D1 acceptance criteria 35%, D2 API contract 20%, D3 data model 15%, D4 convention 10%, D5 policy 10%, D6 TrustFabric PII 10%) using an adversarial verifier role separate from the generator
- Dual delivery gate: SCS ≥ 0.90 AND zero critical-severity failures — a single critical FAIL blocks delivery regardless of aggregate score
- Targeted re-engineering loop (max 3 iterations) with monotonic SCS improvement guard; escalates to POD Lead on plateau or exhaustion
- Convention compliance enforcement against .cursorrules (dimension D4)
- TrustFabric PII constraint enforcement (dimension D6, every iteration, any FAIL is critical)
- Ambiguity escalation to POD Lead with spec-ambiguity-escalation.log (takes precedence over the conformance loop)

**Owned Responsibilities:**
- Spec-anchored code generation for React/FastAPI/PostgreSQL stack
- Closed-loop spec-conformance validation and re-engineering before delivery
- Convention compliance enforcement
- Provenance header injection
- Per-task spec-conformance-report.json production
- Ambiguity escalation logging

**Inputs:**
  Mandatory:
    - artifacts/task-breakdown.yaml: Assigned task and requirement ID
    - artifacts/openspec.yaml: Acceptance criteria for the requirement (verifier ground truth)
    - specs/design.md: Architectural patterns and naming conventions
    - specs/api.md: API contracts and request/response schemas (verifier ground truth for D2)
    - specs/database.md: Schema definitions and ORM patterns (verifier ground truth for D3)
    - artifacts/policy-catalogue.yaml: Compliance rail prompt for this task (verifier ground truth for D5)
    - .cursorrules: Coding conventions (verifier ground truth for D4)
    - AGENTS.md: Builder operating instructions
    - KnowledgeMesh retrieval: Contextualised spec chunks per task
    - TrustFabric flags: PII and data contract constraints (verifier ground truth for D6)
  Optional:
    - artifacts/ai-manifest.json: Existing component registry for duplication check

**Outputs:**
- Implementation code files with provenance headers (delivered only after clearing the conformance gate)
- spec-conformance-report.json: Per-task final SCS, dimension scores, iteration audit trail, and DELIVERED or ESCALATED verdict
- spec-ambiguity-escalation.log: One entry per escalated ambiguity

**Dependencies:**
- KnowledgeMesh: Provides contextualised spec chunks (upstream)
- TrustFabric: Provides PII constraints and data contract rules (upstream, scored as D6 every iteration)
- SecretShield: All context payloads pass through SecretShield before injection (upstream gate)
- ReviewPilot: Receives only gate-cleared artifacts; spec-conformance-report.json accompanies the PR (downstream)
- NexusDeploy: Artifacts registered against requirement IDs (downstream)
- EvalHarness / TraceGraph: Boundary — DevCopilot's loop validates spec conformance of the artefact; behavioural test generation and BDD coverage remain owned downstream

**Project Types:**
- React/TypeScript frontend, Python FastAPI backend, PostgreSQL database stack

**Constraints:**
- Does not generate infrastructure-as-code (NexusDeploy scope)
- Does not write BDD feature files (TraceGraph scope)
- Ambiguous spec requirements must be escalated before generation; the conformance loop assumes an unambiguous, atomic requirement as its ground truth
- Works best with atomic, well-defined spec requirements — compound requirements should be split by the POD Lead before invocation
- The 90% gate is a delivery threshold, not a quality ceiling; it never licenses shipping a critical-severity failure
- The re-engineering loop is bounded at MAX_REENGINEER_ITERS (default 3); persistent sub-threshold results are escalated, never silently shipped
- Token budget: ~50K base + ~15K per re-engineering iteration, ~95K worst case (first-pass estimates — confirm empirically before registering in SpecPod_skill_execution_tracker.xlsx)

**Summary:** Generates spec-anchored, convention-compliant code for React/FastAPI/PostgreSQL tasks, then gates delivery behind a closed-loop SCS ≥ 90% / zero critical failures conformance check with up to three automated re-engineering passes, producing a per-task spec-conformance-report.json and escalating unresolved failures to the POD Lead.

---

## doc-extraction

**Skill Name:** doc-extraction

**Purpose:** Parses and extracts structured knowledge from customer-provided documents into the program knowledge base, routing each piece of content to the correct knowledge file and flagging conflicts with existing entries for human resolution.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Document intake and type classification (requirements spec, architecture doc, BRD, functional spec, data dictionary, compliance doc, UI/UX specification, etc.)
- Content classification into routing categories (context, expectations, as-is system, architecture, data, API, UI, constraints, open items, to-be requirements)
- Conflict detection (direct conflict, extension, duplication, new content)
- knowledge.md update with source attribution and category tagging
- design.md update for AS-IS architectural content
- uiux.md update for AS-IS UI content
- Extraction report with conflict summary and follow-up questions

**Owned Responsibilities:**
- Document-sourced knowledge extraction and routing
- Conflict detection and flagging for human resolution

**Inputs:**
  Mandatory:
    - Customer-provided document: Any of — requirements spec, architecture spec, BRD, functional spec, data dictionary, compliance doc, wireframe descriptions, PDF/Word file
  Optional:
    - knowledge.md: Existing knowledge for conflict detection
    - design.md: Existing design for conflict detection
    - uiux.md: Existing UI spec for conflict detection

**Outputs:**
- Updates to knowledge.md (context, expectations, as-is system, constraints, open items sections)
- Updates to design.md (AS-IS ARCHITECTURE section, if technical content found)
- Updates to uiux.md (AS-IS UI & UX section, if UI content found)
- Extraction Report with conflict summary and follow-up question recommendations

**Dependencies:**
- None

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Preserve original customer language in knowledge.md; do not paraphrase customer expectations
- Never write speculative content without [INFERRED] tag
- To-be requirements from documents go to knowledge.md [EXPECTATIONS] only; not to design files
- Documents over 50 pages: process section by section with user confirmation

**Summary:** Parses customer-provided documents and routes structured knowledge into knowledge.md, design.md, and uiux.md with source attribution and conflict flagging.

---

## DriftGuard

**Skill Name:** DriftGuard

**Purpose:** Continuously samples live AI model outputs from production traffic and evaluates them against the locked openspec.yaml behavioral specification and EvalHarness golden-set baselines, scoring semantic drift per feature and triggering revalidation workflows when cumulative drift exceeds the configured threshold.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Spec baseline parsing from openspec.yaml acceptance criteria and output format contracts
- EvalHarness golden output baseline management
- Configurable traffic sampling with observability stack integration
- Multi-dimension drift scoring: semantic quality, output format compliance, response length, accuracy, latency, tone/safety
- Drift direction classification (regression vs. improvement)
- Revalidation trigger generation when threshold breached
- Per-feature drift report and dashboard

**Owned Responsibilities:**
- Production model output drift detection
- Revalidation trigger when drift threshold exceeded
- Drift history and trend reporting

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Behavioral spec, acceptance criteria, output format contracts
    - artifacts/deploy-manifest.yaml: Deployed model versions and endpoints
    - artifacts/traceability-report.md: Requirement-to-feature mapping
    - specs/features.md: Feature acceptance criteria
    - EvalHarness baseline: Golden output set from sprint validation
    - Live production traffic: Via configured observability stack
  Optional:
    - Prior context.yaml: For change detection

**Outputs:**
- operate/drift-guard/drift-config.yaml: All drift configuration
- operate/drift-guard/drift-scorer.py: Sampling, scoring, and reporting agent
- operate/drift-guard/sampling-config.yaml: Observability stack sampler
- operate/drift-guard/drift-report.md: Per-feature drift score history
- operate/drift-guard/revalidation-trigger.yaml: Written when threshold exceeded
- operate/drift-guard/eval-baseline/baseline-manifest.yaml: Golden output manifest
- operate/drift-guard/drift-dashboard.json: Drift trend dashboard

**Dependencies:**
- EvalHarness: Provides golden output baseline
- TraceGraph: Provides traceability-report.md

**Project Types:**
- AI-native production systems with observable traffic

**Constraints:**
- Operates in spec-only mode if no EvalHarness baseline exists
- Claude API unavailable falls back to regex/rule-based scoring flagged as scored_by: fallback
- Does not validate capabilities against live running systems

**Summary:** Monitors production AI output quality by sampling live traffic and scoring against spec and EvalHarness baselines, triggering a revalidation workflow when drift exceeds the configured threshold.

---

## EvalHarness

**Skill Name:** EvalHarness

**Purpose:** Provides a shared, consistent LLM-as-Judge scoring rubric for evaluating the semantic quality of every AI-generated output across the sprint — consumed by Guardian, RedTeamX, and SimLab — ensuring that quality means the same thing regardless of which agent is evaluating.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Rubric construction from openspec.yaml semantic criteria (accuracy, tone, completeness, conciseness, safety, groundedness, custom dimensions)
- HITL golden reference elicitation (POD Lead defines expected outputs or pass/fail thresholds)
- LLM-as-Judge evaluation with structured scoring prompt
- Weighted aggregate score calculation per output
- Drift detection against prior sprint rubric (flags shifts > 0.5 points)
- eval-rubric.yaml generation as shared rubric for all Validate agents

**Owned Responsibilities:**
- Shared semantic evaluation framework
- LLM-as-Judge scoring methodology
- Sprint-level evaluation rubric management
- Evaluation drift detection across sprints

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Semantic evaluation criteria per feature
    - artifacts/golden-references/: Human-defined expected outputs per feature
    - AI model outputs: Actual outputs to evaluate (from Guardian, RedTeamX, SimLab, or direct)
  Optional:
    - artifacts/eval-rubric-prev.yaml: Prior sprint rubric for drift detection

**Outputs:**
- artifacts/eval-rubric.yaml: Compiled rubric consumed by Guardian, RedTeamX, and SimLab
- artifacts/eval-results.json: Per-output scores with rationale
- artifacts/eval-summary.md: Sprint-level quality summary for Release gate
- artifacts/eval-drift-alert.md: Written only if drift detected

**Dependencies:**
- None (EvalHarness provides shared rubric to other agents; it does not depend on them)

**Project Types:**
- AI-native projects with AI-generated outputs requiring semantic quality evaluation

**Constraints:**
- Cannot operate without golden references; POD Lead must define them before scoring
- LLM-as-judge evaluations carry systematic biases (length bias, position bias, self-familiarity bias)
- Drift detection requires at least one prior sprint's rubric
- Scores semantic quality only; functional correctness is Guardian's domain

**Summary:** Constructs a shared LLM-as-Judge evaluation rubric from openspec.yaml criteria and POD Lead-defined golden references, scoring AI outputs and detecting quality drift across sprints.

---

## ExperienceStudio

**Skill Name:** ExperienceStudio

**Purpose:** Validates that every UI/UX design decision made by the AI Builder is causally traceable to documented stakeholder intent in ui-ux.md and openspec.yaml, operating as the Gate 2 design sign-off mechanism that prevents UX misalignment discovered late in the sprint.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Intent hierarchy parsing from ui-ux.md with journey-to-requirement ID mapping
- Design analysis of UI artefacts (screenshots, Figma exports, component code)
- Per-journey conformance evaluation: ALIGNED / DEVIATED / UNCOVERED / EXTENDED
- Revision request generation with traceable spec obligation (not aesthetic preference)
- Gate 2 attestation when all journeys are ALIGNED

**Owned Responsibilities:**
- UX conformance validation against documented stakeholder intent
- Gate 2 design sign-off attestation

**Inputs:**
  Mandatory:
    - specs/ui-ux.md: Primary experience specification — intent hierarchy and user journeys
    - artifacts/openspec.yaml: Functional acceptance criteria
    - UI artefacts: Screenshots, code, or descriptions of design under review
  Optional:
    - specs/design.md: Technical design constraints affecting UI implementation
    - specs/features.md: Feature catalogue with user-facing scope

**Outputs:**
- experience-conformance-report.md: Coverage matrix, revision requests, Gate 2 attestation status

**Dependencies:**
- KnowledgeMesh: Upstream context retrieval for ui-ux.md chunks and prior sprint feedback

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Cannot enforce unstated aesthetic preferences; they must be documented in ui-ux.md first
- EXTENDED items (design additions beyond spec) require POD Lead decision before acceptance
- Does not validate WCAG accessibility compliance (that is policy-catalogue scope)

**Summary:** Validates UI/UX design artifacts against documented stakeholder intent from ui-ux.md and openspec.yaml, producing a conformance report and Gate 2 attestation when all user journeys are aligned.

---

## ExperimentOps

**Skill Name:** ExperimentOps

**Purpose:** Enables a small team to run statistically rigorous A/B and multi-armed experiments in production by generating complete experiment configuration — traffic routing, variant definitions, guardrail monitors, significance calculators, and auto-stop logic — from a structured hypothesis and parameters.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Experiment manifest generation from hypothesis, variants, traffic allocation, and metric definitions
- Traffic routing configuration (header-based, user ID hash, random, feature flag, API gateway)
- Guardrail monitor generation with configurable degradation thresholds and automatic experiment stop
- Statistical significance calculator (two-proportion z-test or t-test based on metric type)
- Auto-stop enforcement at maximum runtime
- Experiment results report with winner recommendation

**Owned Responsibilities:**
- Production A/B and multi-armed experiment configuration
- Guardrail safety enforcement with automatic traffic reversion on breach

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Feature definitions for experimentation candidates
    - artifacts/deploy-manifest.yaml: Deployed variants, service endpoints, routing layer
    - Experiment hypothesis, variants, traffic allocation, primary metric, guardrail metrics: Elicited from POD Lead
    - Statistical significance threshold, minimum and maximum runtime: Elicited
  Optional:
    - operate/runtime-iq/thresholds.yaml: Existing SLA thresholds as guardrail defaults
    - operate/value-tracker/value-tracker-config.yaml: Business metric mappings

**Outputs:**
- operate/experiment-ops/experiment-[id]-manifest.yaml: Complete experiment definition
- operate/experiment-ops/traffic-router.py (or routing config): Variant traffic routing
- operate/experiment-ops/guardrail-monitor.py: Continuous guardrail enforcement
- operate/experiment-ops/significance-calculator.py: Statistical significance evaluator
- operate/experiment-ops/auto-stop.sh: Maximum runtime enforcement
- operate/experiment-ops/experiment-dashboard.json: Real-time experiment dashboard
- operate/experiment-ops/experiment-results-report.md: Results with winner recommendation

**Dependencies:**
- RuntimeIQ: Provides thresholds.yaml for guardrail defaults
- ValueTracker: Provides value-tracker-config.yaml for metric mappings

**Project Types:**
- AI-native production systems with measurable business metrics and traffic routing capability

**Constraints:**
- Statistical significance requirements and guardrail thresholds must be agreed with stakeholders before production experiments run
- deploy-manifest.yaml required for routing configuration
- Guardrail breach triggers immediate automatic experiment stop with all traffic routed to control
- Proposed status: experiment design and guardrail thresholds require stakeholder alignment

**Summary:** Generates complete A/B experiment configuration with traffic routing, guardrail monitoring, and automatic stopping, enabling statistically rigorous production experiments without dedicated data science infrastructure.

---

## Guardian

**Skill Name:** Guardian

**Purpose:** Converts locked acceptance criteria into executable Gherkin test suites before the Build phase begins, then continuously executes those tests as code modules land, triaging every failure into exactly one of three categories — SPEC_ERROR, CODE_ERROR, or ENV_ERROR.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Acceptance criteria parsing from openspec.yaml with ambiguity elicitation
- Gherkin feature file generation (Generation Mode): happy path + negative path + boundary scenarios per criterion
- Test execution against available source code modules (Execution + Triage Mode)
- Failure triage: SPEC_ERROR (POD Lead amends spec), CODE_ERROR (AI Builder fixes code), ENV_ERROR (POD Lead resolves infra)
- Requirement coverage reporting with Release gate verdict

**Owned Responsibilities:**
- Test suite generation from acceptance criteria
- Test execution and failure triage
- Requirement coverage reporting

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Acceptance criteria source of truth
    - artifacts/ai-manifest.json: Component-to-builder mapping for test tagging
    - artifacts/traceability-report.md: Requirement IDs for test linkage
  Conditional:
    - Source code modules (src/**): Required for Execution + Triage Mode; not needed for Generation Mode
  Optional:
    - artifacts/eval-rubric.yaml: EvalHarness rubric for semantic test scoring

**Outputs:**
- tests/*.feature: One .feature file per requirement/component
- artifacts/test-results.json: Structured pass/fail with triage categories
- artifacts/coverage-report.md: Requirement coverage percentage and Release gate verdict

**Dependencies:**
- TraceGraph: Provides traceability-report.md
- EvalHarness: Provides eval-rubric.yaml for semantic scoring (optional)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Test coverage quality bounded by acceptance criteria completeness; vague criteria produce shallow tests
- Generates Gherkin scenarios but not step definition implementations (builders implement step defs)
- Does not execute tests requiring live external APIs without stubs
- Release gate requires ≥ 80% coverage and zero untriaged failures

**Summary:** Generates executable Gherkin test suites from acceptance criteria and executes them against built code modules, triaging every failure as SPEC_ERROR, CODE_ERROR, or ENV_ERROR.

---

## IncidentLens

**Skill Name:** IncidentLens

**Purpose:** Converts production incidents from a cost centre into a product improvement signal by classifying incidents as one-off, pattern, or systemic, tracing root causes to spec gaps or infrastructure limits, and producing actionable sprint backlog items for recurring systemic issues.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- New incident intake and structured logging (Mode A: log + classify)
- Pattern analysis across accumulated incident history (Mode B: pattern + backlog generation)
- SLA metric cross-reference at time of incident from RuntimeIQ sla-breach-log.md
- Root cause classification: spec_gap, missing_test, infrastructure_limit, dependency_failure, data_quality
- Sprint backlog item generation for systemic issues in Markdown or YAML format
- RunbookSynth enrichment with root causes and verified fixes

**Owned Responsibilities:**
- Production incident classification and pattern analysis
- Incident-derived sprint backlog items for systemic issues
- Failure intelligence accumulation across sprints

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Spec baseline for spec gap classification
    - artifacts/deploy-manifest.yaml: Deployment version at time of incident
    - operate/runtime-iq/sla-breach-log.md: SLA metrics for incident cross-reference
    - operate/runtime-iq/thresholds.yaml: NFR baselines for context
    - operate/control-plane/security-event-log.md: Security events for cross-reference
    - Incident details: Elicited for Mode A (timestamp, affected services, symptom, error type, resolution, root cause)

**Outputs:**
- operate/incident-lens/incident-log.md: Classified incident history
- operate/incident-lens/incident-pattern-report.md: Pattern analysis with root causes
- operate/incident-lens/backlog-items.md: Sprint backlog recommendations
- operate/incident-lens/backlog-items.yaml: Machine-readable backlog for Conductor
- operate/incident-lens/runbook-enrichments.yaml: Known issue and verified fix data for RunbookSynth

**Dependencies:**
- RuntimeIQ: Provides sla-breach-log.md and thresholds.yaml
- ControlPlane: Provides security-event-log.md

**Project Types:**
- AI-native production systems

**Constraints:**
- Only captures incidents that flow through defined channels; verbal-only incidents leave no trace
- Root cause unknown incidents flagged as pending_investigation
- Intelligence base builds meaningfully over 4–6 sprints of data
- Pattern/systemic backlog items require POD Lead HITL gate before writing to sprint board

**Summary:** Classifies production incidents as one-off, pattern, or systemic, traces root causes, and generates sprint backlog items for recurring systemic issues to close the incident-to-improvement loop.

---

## InsightOps

**Skill Name:** InsightOps

**Purpose:** Aggregates outputs from all five preceding validation agents — Guardian, EvalHarness, RedTeamX, SimLab, and PolicyEnforcer — identifies failure patterns that no individual agent can detect in isolation, and traces patterns back to spec gaps with specific amendment recommendations.

**Phase:** 03-Platform-Enablement (also active in 05-Simplified-AI-Operations for feedback loop contribution)

**Capabilities:**
- Cross-agent signal aggregation per requirement ID with aggregate signal (GREEN / AMBER / RED)
- Pattern detection across five types: cross-agent correlation, component blast radius, spec gap signal, environmental pattern, regression signal
- Spec amendment recommendations with affected requirement IDs and estimated amendment effort
- Priority action list generation ordered by severity and effort
- Consolidated validation report with release gate verdict

**Owned Responsibilities:**
- Validation results synthesis across all Validate-phase agents
- Spec gap identification and amendment recommendation
- Release gate evidence consolidation
- Feedback loop triggers for next sprint planning

**Inputs:**
  Mandatory:
    - artifacts/test-results.json: Guardian functional test results
    - artifacts/eval-results.json: EvalHarness semantic quality scores
    - artifacts/adversarial-test-suite.json: RedTeamX adversarial test results
    - artifacts/simlab-results.json: SimLab load and chaos test results
    - artifacts/policy-scan-results.json: PolicyEnforcer compliance scan results
    - artifacts/openspec.yaml: For spec amendment recommendations
    - artifacts/traceability-report.md: For root cause requirement tracing
  Optional:
    - artifacts/operate-metrics/: Prior Operate phase logs for trend analysis

**Outputs:**
- artifacts/validation-report.md: Consolidated sprint quality summary and release gate verdict
- artifacts/spec-amendments.md: Specific openspec.yaml amendment recommendations
- artifacts/action-list.md: POD Lead-ready ordered action list with owners and effort
- artifacts/feedback-loop-triggers.yaml: Operate-phase production signal file (when Operate logs available)

**Dependencies:**
- Guardian: Provides test-results.json
- EvalHarness: Provides eval-results.json
- RedTeamX: Provides adversarial-test-suite.json
- SimLab: Provides simlab-results.json
- PolicyEnforcer: Provides policy-scan-results.json
- TraceGraph: Provides traceability-report.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Cannot run until all five validation agents have produced outputs for the current sprint
- Pattern detection is probabilistic; POD Lead judgment required to validate root cause hypotheses
- Spec amendment recommendations are starting points, not final amendments

**Summary:** Synthesizes all five Validate-phase agent outputs to identify cross-agent failure patterns, trace root causes to spec gaps, and produce a priority action list with consolidated release gate verdict.

---

## KnowledgeMesh

**Skill Name:** KnowledgeMesh

**Purpose:** Centralised RAG context backbone for all build-phase agents — prevents context divergence by indexing all sprint spec files into a single versioned knowledge plane from which DevCopilot, ExperienceStudio, ReviewPilot, and TrustFabric retrieve context.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Index construction from all spec files with 300–500 token chunks tagged by source, section, requirement IDs, sprint ID, and version hash
- Relevance-scored query handling with top-N chunk retrieval
- Staleness detection and invalidation on source document changes
- Coverage assessment reporting retrieval confidence per spec area

**Owned Responsibilities:**
- Build-phase knowledge retrieval centralisation
- Context version management and staleness detection
- Single knowledge plane across all build agents

**Inputs:**
  Mandatory:
    - specs/knowledge.md: As-is system knowledge
    - specs/design.md: Technical architecture
    - specs/api.md: API contracts
    - specs/database.md: Schema definitions
    - specs/features.md: Feature catalogue
    - specs/impl.md: Implementation constraints
    - artifacts/openspec.yaml: Sprint requirements
    - artifacts/task-breakdown.yaml: Decomposed task tree
    - artifacts/decision-ledger.md: Architectural decisions
  Optional:
    - artifacts/ai-manifest.json: Previously generated artifacts

**Outputs:**
- knowledge-mesh-index.md: Chunk inventory and requirement coverage map (internal)
- Retrieval responses: Chunks with metadata delivered to requesting agent per query
- knowledge-coverage-report.md: Per-spec-area retrieval confidence (on audit request)
- knowledge-mesh-invalidation.log: Timestamped staleness events

**Dependencies:**
- ContextFabric: Receives invalidation signals when platform context changes

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Retrieval quality bounded by documentation coverage; undocumented behavior requires direct code analysis by AI Builder
- Does not perform semantic understanding of retrieved chunks; DevCopilot applies context to generation
- Does not persist state between conversations; index rebuilt each sprint session

**Summary:** Provides a centralised, versioned RAG knowledge index for build-phase agents, indexing all sprint spec files and serving relevance-scored context chunks with staleness detection.

---

## knowledge-review

**Skill Name:** knowledge-review

**Purpose:** Presents the accumulated knowledge base to the Pod Lead or Program Lead for structured section-by-section review, correction, and sign-off, then produces a validated knowledge.md with REVIEWED status and a design readiness assessment before the design phase begins.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Section-by-section review across seven knowledge domains and features.md
- Business completeness checklist gap analysis
- knowledge.md and features.md rewrite incorporating all corrections and additions
- Expectation priority annotation (FIRM / EXPLORATORY / NEEDS VALIDATION)
- Open item resolution with [RESOLVED: date] or [DESIGN BLOCKER] flagging
- Design Readiness Assessment with READY / RESOLVE BLOCKERS / ADDITIONAL DISCOVERY recommendation

**Owned Responsibilities:**
- Knowledge base validation gate before design phase
- Design readiness assessment

**Inputs:**
  Mandatory:
    - knowledge.md: Accumulated knowledge base to review
  Optional:
    - features.md: Feature requirements for review

**Outputs:**
- Validated knowledge.md with STATUS: REVIEWED ✓ stamp
- Updated features.md with corrected priority signals
- Design Readiness Assessment

**Dependencies:**
- doc-extraction: Prior extraction step (checked for completeness, not hard required)
- code-extraction: Prior extraction step (checked for completeness, not hard required)
- meeting-extraction: Prior extraction step (checked for completeness, not hard required)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Presents content in natural language, not raw markdown
- Never deletes existing entries — marks as [SUPERSEDED: date]
- Mandatory checkpoint before design-setup; design-setup warns if this skill has not been completed

**Summary:** Facilitates a structured section-by-section review of the knowledge base with the Pod Lead, producing a validated and signed-off knowledge.md with design readiness assessment.

---

## meeting-extraction

**Skill Name:** meeting-extraction

**Purpose:** Processes meeting transcripts or call notes from customer sessions to extract structured knowledge, routing business context and rules to knowledge.md, feature requirements to features.md, and technology decisions to design.md, while flagging contradictions with existing knowledge.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Transcript intake and type classification (verbatim, AI summary, hand-written notes)
- Content classification into 13 routing categories with explicit routing rules
- Meeting brief generation for Pod Lead and Program Lead consumption
- knowledge.md update (business context, rules, workflows, as-is, expectations, constraints, open items)
- features.md update with sequentially numbered FR-n entries and priority signals
- design.md update for TO-BE technology and architecture decisions
- Post-write conflict detection with Conflict Report

**Owned Responsibilities:**
- Customer meeting knowledge extraction
- Feature requirement capture from customer conversations
- Meeting brief generation

**Inputs:**
  Mandatory:
    - Meeting transcript, call notes, or meeting record: Verbatim, AI-generated, or hand-written
  Optional:
    - knowledge.md: Existing knowledge for conflict detection
    - features.md: Existing feature list for deduplication and FR number continuation
    - design.md: Existing design decisions for conflict detection

**Outputs:**
- Meeting brief with executive summary, business knowledge, pain points, features, decisions, open items, scope signals, risk signals, recommended actions
- Updates to knowledge.md
- Updates to features.md
- Updates to design.md

**Dependencies:**
- None

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Preserve customer voice; quote directly or paraphrase minimally
- Business rules must capture trigger, condition, and outcome precisely
- Features are capabilities, not implementation details
- Sensitive stakeholder observations go to meeting brief only, never to knowledge files

**Summary:** Processes customer meeting transcripts and routes extracted content to knowledge.md (business knowledge), features.md (feature requirements), and design.md (technology decisions) with conflict detection.

---

## NexusDeploy

**Skill Name:** NexusDeploy

**Purpose:** Sprint close-out gate that verifies every requirement has a corresponding reviewed, policy-clean artifact before issuing the deploy manifest; also executes deployment pipeline in the Release phase and registers production artifacts in the Operate phase.

**Phase:** 03-Platform-Enablement (also active in 04-AI-Solution-Deployment and 05-Simplified-AI-Operations)

**Capabilities:**
- Artifact registry construction from provenance headers in source files
- Per-requirement completeness validation: artifact present, review approved, no policy violations, NFR evidence pass
- Deploy manifest preparation with checksums, rollout strategy, and service definitions
- ai-manifest.json update merging new sprint artifacts with prior sprint catalogue
- Completeness report with specific blocker identification

**Owned Responsibilities:**
- Sprint completeness verification before deployment
- Deploy manifest generation
- Artifact registry maintenance across sprints

**Inputs:**
  Mandatory:
    - artifacts/task-breakdown.yaml: Expected artifact list per requirement
    - artifacts/openspec.yaml: Requirement IDs and acceptance criteria
    - artifacts/ai-manifest.json: Current artifact catalogue
    - artifacts/review-verdict.yaml: PR review pass/fail per requirement (from ReviewPilot)
    - data-contract-violations.yaml: Unresolved PII violations (from TrustFabric)
    - prompt-bench-nfr-evidence.yaml: NFR pass/fail for AI features (from PromptBench)
    - Source code modules with provenance headers: Generated artifacts
    - Infrastructure config (Dockerfile, docker-compose): Container build definitions

**Outputs:**
- Sprint Completeness Report with COMPLETE/ARTIFACT_MISSING/REVIEW_PENDING/REVIEW_BLOCKED/POLICY_VIOLATION/NFR_FAIL status per requirement
- deploy-manifest.yaml: Generated only when all requirements are COMPLETE
- Updated ai-manifest.json

**Dependencies:**
- ReviewPilot: Provides review-verdict.yaml
- TrustFabric: Provides data-contract-violations.yaml
- PromptBench: Provides prompt-bench-nfr-evidence.yaml

**Project Types:**
- Docker-first, cloud-agnostic deployment targets

**Constraints:**
- Requirements added informally outside the spec process are invisible to NexusDeploy
- Does not execute builds; only prepares the manifest for CI/CD pipeline consumption
- Does not manage secrets in manifest; environment variables referenced by name only

**Summary:** Verifies that every sprint requirement has a reviewed, policy-clean artifact before generating a containerized deploy manifest, blocking deployment until all completeness conditions are satisfied.

---

## ParityChecker

**Skill Name:** ParityChecker

**Purpose:** Verifies staging-to-production environment parity before Gate 3 sign-off by comparing configurations across eight environment dimensions and classifying drift as CRITICAL_DRIFT (deploy blocker), NOTABLE_DRIFT, or EXPECTED_DIFF.

**Phase:** 04-AI-Solution-Deployment

**Capabilities:**
- First-run elicitation across eight dimensions: runtime/infrastructure, application dependencies, database and data services, external services and API versions, feature flags, secrets and environment variables, monitoring and observability, network and security
- YAML config file generation for staging and production (persisted for future sprint reuse)
- Diff mode for subsequent sprints (compares stored YAML files directly)
- Classification of each difference with gate impact

**Owned Responsibilities:**
- Staging-to-production environment parity verification
- Gate 3 (QA Sign-off) parity prerequisite

**Inputs:**
  Optional (determines run mode):
    - artifacts/release/env-config-staging.yaml: If present with production file, runs diff mode
    - artifacts/release/env-config-production.yaml: Required alongside staging config for diff mode

**Outputs:**
- artifacts/release/parity-check-report.md: Full diff with classification and gate verdict
- artifacts/release/env-config-staging.yaml: Generated on first run
- artifacts/release/env-config-production.yaml: Generated on first run

**Dependencies:**
- None (ReleaseIntel and RolloutAdvisor depend on this skill's output)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Secrets are names never values; actual secret values must never be elicited, stored, or logged
- One CRITICAL_DRIFT item blocks Gate 3 with no partial credit
- EXPECTED_DIFF items must be declared with rationale; undeclared expected differences are treated as drift

**Summary:** Compares staging and production environment configurations across eight dimensions, classifying drift and blocking Gate 3 if any critical drift exists.

---

## PerformanceOptimizer

**Skill Name:** PerformanceOptimizer

**Purpose:** Enforces intelligent model routing and sprint token budget compliance — matching each generation task to the optimal model tier based on complexity, context size, and output type, while monitoring cumulative token spend to prevent budget overruns.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Task profiling on three dimensions: complexity (LOW/MEDIUM/HIGH), context size (SMALL/MEDIUM/LARGE), output type (CODE/STRUCTURED/ANALYSIS/EXTRACTION)
- Model routing decisions with explicit routing matrix for Anthropic and OpenAI model tiers
- Sprint token budget monitoring with projected overrun calculation
- Threshold-based alerting (80%: alert with recommendations; 95%: force route to Haiku; 100%: block)
- Cost reduction recommendations identifying highest-cost remaining tasks
- End-of-sprint token consumption report for budget calibration

**Owned Responsibilities:**
- Per-task model routing decisions
- Sprint token budget monitoring and enforcement

**Inputs:**
  Mandatory:
    - artifacts/task-breakdown.yaml: Task list with complexity and context size estimates
    - artifacts/openspec.yaml: NFR latency targets per feature
    - artifacts/sprint-capacity.yaml: Sprint token budget allocation
    - Live token consumption: Running totals per agent and builder
  Optional:
    - PromptBench results: Per-task-type quality/cost profiles for routing calibration

**Outputs:**
- Routing decision per task (YAML): recommended model, rationale, estimated tokens and cost
- Token Consumption Dashboard: Snapshot on demand or at 80% alert
- token-consumption-report.yaml: End-of-sprint per-agent, per-task, per-model consumption log

**Dependencies:**
- PromptBench: Provides benchmark results to calibrate routing heuristics

**Project Types:**
- AI-native projects using Claude (Haiku/Sonnet/Opus) and/or OpenAI (GPT-4o-mini/GPT-4o/o3) models

**Constraints:**
- Routing heuristics are task-type-based, not outcome-based; improve with PromptBench data after 2–3 sprints
- Does not control model selection inside third-party tools (e.g. Cursor internal calls)
- Budget tracking requires agents to report token usage; unreported usage produces inaccurate estimates

**Summary:** Routes each generation task to the optimal model tier and monitors sprint token budget, alerting at 80% consumption and blocking further LLM calls at 100%.

---

## PolicyCatalog

**Skill Name:** PolicyCatalog

**Purpose:** Maps every requirement in openspec.yaml to its applicable compliance policies before build starts, generating per-task compliance guard prompts injected into SpecFlow cluster definitions and Conductor task dispatches to ensure compliance is enforced at code generation time.

**Phase:** 02-Data-Readiness (also active in 03-Platform-Enablement for compliance rail injection)

**Capabilities:**
- Requirement compliance signal scanning (PII fields, auth flows, data persistence, external transmission, audit logging, consent flows, deletion/retention operations)
- Policy matching against policy library with POL-[FRAMEWORK]-[NNN] IDs
- Compliance guard prompt generation (3–5 sentences per policy, builder-ready)
- Gap analysis flagging requirements with unmatched compliance signals as POLICY_GAP

**Owned Responsibilities:**
- Per-requirement compliance policy assignment
- Compliance guard prompt generation for build phase injection

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Sprint requirements to scan
    - specs/database.md: Schema for PII field identification
    - specs/api.md: Endpoint definitions for compliance signal detection
    - specs/features.md: Feature context
    - references/policy-library.md: Master policy catalogue with guard prompts per framework

**Outputs:**
- artifacts/policy-catalogue.yaml: Per-requirement compliance status and guard prompts
- Per-task compliance rail prompts: Injected into artifacts/task-breakdown.yaml via SpecFlow

**Dependencies:**
- spec-database: Provides database.md
- spec-api: Provides api.md
- spec-generation: Provides features.md
- SpecFlow: Receives policy_rails arrays appended to cluster entries

**Project Types:**
- Projects with regulatory compliance requirements (GDPR, HIPAA, SOC2, PCI-DSS, etc.)

**Constraints:**
- Catalogue coverage bounded by policy-library.md; novel requirements must be manually added before enforcement
- Classifies compliance signals but does not perform legal interpretation
- Final compliance responsibility remains with the POD Lead

**Summary:** Maps all sprint requirements to applicable compliance policies from the policy library and generates per-task guard prompts injected into build phase cluster definitions.

---

## PolicyEnforcer

**Skill Name:** PolicyEnforcer

**Purpose:** Scans generated source code and runtime behavior against the project's compliance policy catalogue, enforcing a hard gate requiring zero critical violations and zero high violations before any artifact enters the Release phase.

**Phase:** 03-Platform-Enablement (also active in 05-Simplified-AI-Operations for runtime governance)

**Capabilities:**
- Policy catalogue loading and validation
- Static source code scan: PII in logs, hardcoded secrets, injection vulnerabilities, insecure dependencies, missing input validation, insecure cryptography
- Runtime behaviour scan: PII in API responses, sensitive data over unencrypted channels, auth bypass, rate limit gaps, error message leakage
- Violation classification by severity: critical, high, medium, informational
- Release gate compliance attestation generation

**Owned Responsibilities:**
- Source code compliance policy enforcement
- Runtime behaviour compliance scanning
- Release gate compliance attestation

**Inputs:**
  Mandatory:
    - artifacts/policy-catalogue.yaml: Defines all enforceable policies
    - Source code (src/**): All build-phase generated code
    - Configuration files (*.yaml, *.env, *.json): Scanned for secrets and hardcoded values
  Optional:
    - artifacts/deploy-manifest.yaml: Runtime endpoint list
    - Runtime request/response logs: Required for runtime scan mode
    - TrustFabric PII classification: Per-field sensitivity classification

**Outputs:**
- artifacts/policy-scan-report.md: Full violation list with severity and remediation guidance
- artifacts/policy-scan-results.json: Machine-readable results for InsightOps
- artifacts/compliance-attestation.md: Release gate attestation — critical/high violation count

**Dependencies:**
- PolicyCatalog: Provides policy-catalogue.yaml (must exist before scan can proceed)

**Project Types:**
- Projects with compliance requirements (GDPR, CCPA, OWASP, HIPAA, PCI-DSS, SOC2, AI safety)

**Constraints:**
- Only enforces policies present in policy-catalogue.yaml; unlisted regulatory requirements are invisible
- Pattern-based static scanning has false-positive risk
- Runtime scanning requires logs captured during Guardian test execution
- Does not perform penetration testing or infrastructure security assessment (RedTeamX scope for AI surfaces)

**Summary:** Scans source code statically and runtime behaviour against the compliance policy catalogue, blocking release on any critical or high severity violations.

---

## PortfolioPrioritizer

**Skill Name:** PortfolioPrioritizer

**Purpose:** Ranks all sprint backlog candidates using a composite score of business value, urgency, strategic alignment, dependency enablement, and risk reduction, then draws a capacity cut line to determine what ships this sprint versus deferred to the next.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Unified candidate inventory combining task-breakdown requirements and TransformIQ candidates
- Composite scoring with five dimensions and POD Lead-configurable strategic weights
- Must-ship override insertion at top of ranked list
- Dependency cluster locking (clusters score as their weakest item)
- Capacity cut line calculation with configurable buffer
- BORDERLINE item flagging for POD Lead judgment
- Defer rationale generation per deferred item

**Owned Responsibilities:**
- Sprint backlog ranking and prioritization
- Capacity allocation and cut line determination
- Defer decision documentation with rationale

**Inputs:**
  Mandatory:
    - artifacts/roi-brief.md: Value/effort ratio per requirement (from ValueModeler)
    - artifacts/task-breakdown.yaml: Candidate requirements with effort estimates (from SpecFlow)
    - artifacts/traceability-report.md: Dependency graph for cluster locking (from TraceGraph)
    - artifacts/opportunity-backlog-rescored.md: Candidate additions (from TransformIQ)
    - specs/features.md: Feature context and priority signals
    - specs/program.md: Programme objectives for strategic alignment scoring

**Outputs:**
- artifacts/sprint-scope-ranked.md: Ranked scope with PROCEED/DEFERRED/BORDERLINE classification and rationale

**Dependencies:**
- ValueModeler: Provides roi-brief.md
- SpecFlow: Provides task-breakdown.yaml
- TraceGraph: Provides traceability-report.md
- TransformIQ: Provides opportunity-backlog-rescored.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Scoring weights must be calibrated by humans; stale weights produce misleading rankings
- Political priorities and stakeholder relationships not in the spec cannot be inferred; apply manually via overrides
- Recommends only; POD Lead makes the final scope decision
- Proposed status: scoring model and weighting criteria require stakeholder alignment before production use

**Summary:** Ranks all sprint backlog candidates using weighted composite scoring and draws a capacity cut line, producing a PROCEED/DEFERRED/BORDERLINE ranked scope list with defer rationale.

---

## program-charter

**Skill Name:** program-charter

**Purpose:** Guides the user through a structured elicitation session to capture all dimensions of a software program, then generates a canonical specs/program.md and scaffolds the standard project folder layout. This is the mandatory entry point for all program work.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Structured elicitation across five groups: foundation, scope and users, architecture and systems, design and UX, delivery and risk
- specs/program.md generation from elicitation
- Spec stub creation for knowledge.md, design.md, ui-ux.md, database.md, api.md
- Project folder scaffolding (specs/, src/, tests/, CLAUDE.md, .claude/)
- CLAUDE.md generation with AI collaboration instructions
- Recommended spec initialization order guidance

**Owned Responsibilities:**
- Program charter creation (specs/program.md)
- Project folder structure initialization
- Spec stub creation for all downstream specs

**Inputs:**
  Mandatory:
    - User elicitation responses across five groups
  Optional:
    - Existing charter (for adaptation or re-generation)

**Outputs:**
- specs/program.md: Authoritative program charter
- specs/knowledge.md: Stub with pending notice
- specs/design.md: Stub with pending notice
- specs/ui-ux.md: Stub with pending notice
- specs/database.md: Stub with pending notice
- specs/api.md: Stub with pending notice
- CLAUDE.md: AI collaboration instructions
- src/, tests/, .claude/ directories

**Dependencies:**
- None

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- No feature decomposition section in program.md; features managed by feature-brief skill
- Must precede all other spec skills and feature briefs
- No sprint plans, architecture decisions, or sub-skills should precede program-charter

**Summary:** Generates specs/program.md via structured elicitation and scaffolds the complete project folder structure including spec stubs for all downstream specification skills.

---

## PromptBench

**Skill Name:** PromptBench

**Purpose:** Benchmarks AI feature prompt variants before they enter production by running each against a representative query sample across multiple models, measuring quality, latency, and cost, and delivering a ranked recommendation with NFR pass/fail evidence for the Release gate.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Benchmark matrix construction (prompt variant × model × query)
- Multi-provider execution: Claude (Haiku/Sonnet/Opus), OpenAI (GPT-4o-mini/GPT-4o/o3-mini), and configurable others
- Quality scoring via LLM-as-judge, exact match against ground truth, or human-defined rubric
- Metric aggregation: quality_avg, quality_p10, latency_p50/p95, cost_per_1k
- NFR pass/fail verdict per variant/model combination
- Three-dimensional ranking: best quality, best cost, best balanced

**Owned Responsibilities:**
- Prompt variant benchmarking before production deployment
- Model selection evidence and recommendation
- NFR pass/fail evidence for NexusDeploy release gate

**Inputs:**
  Mandatory:
    - Candidate prompt variants (2–5): From AI Builder
    - Query sample set (10–50 queries): Curated by POD Lead
    - artifacts/openspec.yaml: NFR targets (accuracy threshold, latency p95, cost per request)
    - Target model list: From POD Lead or default
    - Evaluation criteria: LLM-as-judge rubric, ground truth labels, or human rubric

**Outputs:**
- prompt-bench-report.md: Results matrix, winner recommendation, failure analysis, model routing recommendation
- prompt-bench-nfr-evidence.yaml: Structured NFR pass/fail per variant/model for NexusDeploy

**Dependencies:**
- NexusDeploy: Consumes prompt-bench-nfr-evidence.yaml as deploy gate input
- PerformanceOptimizer: Receives benchmark results for sprint routing calibration

**Project Types:**
- AI-native projects with AI feature prompts requiring quality and cost optimization

**Constraints:**
- Benchmark quality depends entirely on query sample representativeness; minimum 20 queries including edge cases recommended
- Does not run real API calls by default; POD Lead must explicitly confirm live execution
- LLM-as-judge scoring introduces evaluator bias; high-stakes features should supplement with human-reviewed ground truth

**Summary:** Benchmarks prompt variants across models on quality, latency, and cost to recommend the optimal variant for production and provide NFR pass/fail evidence for the release gate.

---

## RedTeamX

**Skill Name:** RedTeamX

**Purpose:** Subjects every AI-generated component to systematic adversarial attack before deployment, covering prompt injection, jailbreaks, PII extraction probes, role confusion, and boundary manipulation from the attacker's perspective.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Component risk profiling (CRITICAL / HIGH / MEDIUM / LOW based on data sensitivity and user exposure)
- Adversarial attack suite generation across six categories: prompt injection, jailbreak/role confusion, PII extraction, data exfiltration, boundary manipulation, semantic manipulation
- Attack count scaling by risk level (5 per CRITICAL, 3 per HIGH, 2 per MEDIUM, 1 per LOW)
- Response classification: ROBUST / DEGRADED / VULNERABLE
- Remediation recommendations with input sanitisation, output filtering, and architectural options

**Owned Responsibilities:**
- Adversarial and safety testing of AI components
- Vulnerability identification and remediation guidance

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Risk profile and safety-critical paths
    - artifacts/ai-manifest.json: AI component inventory
    - artifacts/eval-rubric.yaml: Safety dimension scoring (from EvalHarness)
    - Source prompts/handlers (src/): AI-facing code under test
    - references/adversarial-vector-library.yaml: Known attack patterns
  Optional:
    - artifacts/policy-catalogue.yaml: For policy-specific attack generation

**Outputs:**
- artifacts/adversarial-test-suite.json: All attack vectors with pass/fail per component
- artifacts/vulnerability-report.md: Human-readable findings with remediation guidance
- artifacts/redteam-summary.md: Sprint-level safety verdict for Release gate

**Dependencies:**
- EvalHarness: Provides eval-rubric.yaml for safety dimension scoring
- SpecFlow: Provides ai-manifest.json

**Project Types:**
- AI-native projects with AI-facing components processing user input

**Constraints:**
- Covers known vectors from adversarial-vector-library.yaml only; novel zero-day techniques require manual library additions
- Does not test infrastructure-level security (PolicyEnforcer scope)
- ROBUST classification means resistant to known vectors, not unconditionally safe
- VULNERABLE findings are immediate blockers; surface to POD Lead before proceeding to next component

**Summary:** Systematically attacks AI components using six adversarial categories, classifying each as ROBUST/DEGRADED/VULNERABLE and providing specific remediation guidance for any vulnerabilities found.

---

## ReleaseIntel

**Skill Name:** ReleaseIntel

**Purpose:** Synthesizes planning artifacts into a binary release verdict with a structured blast-radius table, replacing the POD Lead's manual cross-referencing of five separate reports during Friday QA review and targeting a 30–45 minute review time.

**Phase:** 04-AI-Solution-Deployment

**Capabilities:**
- Input audit and deployment scope extraction from sprint-board.md or deploy-manifest.yaml
- Readiness signal synthesis from traceability, scenario matrix, assumption log, and decision ledger
- Per-component blast-radius quantification across five dimensions: user segments, dependent features, integration points, data risk, rollback complexity
- Open issues classification: P0 (deploy blocker), P1 (high risk), P2 (medium risk), P3 (low risk)
- Binary release verdict: READY TO DEPLOY or NOT READY — BLOCKED

**Owned Responsibilities:**
- Release readiness synthesis
- Blast-radius assessment per deployed component
- Gate 3 evidence report

**Inputs:**
  Mandatory:
    - artifacts/sprint-board.md: Task completion status (fallback if no deploy-manifest)
    - artifacts/task-breakdown.yaml: Task tree with component detail
  Strongly recommended:
    - artifacts/traceability-report.md: Requirements coverage
    - artifacts/scenario-matrix.md: Risk scenario assessment
  Recommended:
    - artifacts/assumption-log.md: Unresolved HITL blockers
    - artifacts/decision-ledger.md: Pending ADRs
    - specs/spec.md: Master specification
  Optional:
    - artifacts/release/deploy-manifest.yaml: Explicit deployment scope (priority 1 if present)

**Outputs:**
- artifacts/release/release-intel-report.md: Binary verdict with blast-radius table and open issues list

**Dependencies:**
- TraceGraph: Provides traceability-report.md
- ScenarioPlanner: Provides scenario-matrix.md
- AssumptionTracker: Provides assumption-log.md
- DecisionLedger: Provides decision-ledger.md
- SpecFlow: Provides task-breakdown.yaml

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Verdict appears first in the report; evidence follows
- Every blast-radius rating must cite a specific source artifact
- Deployment scope inferred from sprint-board.md must be declared as inference
- Informs the POD Lead; the Go/No-Go decision belongs to a named human

**Summary:** Synthesizes sprint planning artifacts into a binary READY/NOT READY release verdict with blast-radius assessment per component and a prioritized P0–P3 open issues list.

---

## requirements-elicitation-charter

**Skill Name:** requirements-elicitation-charter

**Purpose:** Reads a program charter or equivalent initiating document and generates a disciplined, domain-organized question pack that a Program Lead or Pod Lead can use in early customer meetings to close knowledge gaps and validate assumptions.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Charter analysis producing confirmed facts, implicit assumptions, identified gaps, and conflict flags
- Question pack generation across eight domains: business context, existing system, functional requirements, technical/integration constraints, data and migration, UI/UX, organizational/delivery, open charter issues
- Gap reference labeling (GAP-n) and intent notes per question
- Charter ambiguity flagging and recommended meeting sequence

**Owned Responsibilities:**
- Pre-meeting discovery question generation
- Charter gap and conflict identification

**Inputs:**
  Mandatory:
    - Program charter, SOW, or equivalent initiating document

**Outputs:**
- questions-[YYYY-MM-DD].md: Domain-organized question pack with charter analysis summary and flagged ambiguities

**Dependencies:**
- program-charter: Charter or equivalent document must exist as input

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Every question must trace to a specific charter gap or assumption; no generic boilerplate
- Maximum 8–10 questions per domain; quality over volume
- Sensitive questions (budget, challenging prior decisions) flagged with [SENSITIVE] marker
- If charter is very thin (< 1 page), states this explicitly and asks whether to proceed with inference-heavy questions

**Summary:** Analyzes a program charter to identify knowledge gaps and assumptions, generating a structured question pack across eight domains for customer discovery meetings.

---

## ResearchCopilot

**Skill Name:** ResearchCopilot

**Purpose:** Validates each draft requirement against available discovery evidence — interviews, analytics, support tickets, and prior sprint reports — classifying evidence strength, surfacing contradictions, and flagging weak-evidence requirements as AssumptionTracker candidates.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Evidence source indexing (qualitative interviews, analytics exports, support tickets, prior sprint reports)
- Per-requirement cross-reference against evidence index
- Evidence strength classification: CONFIRMED / PARTIAL / WEAK / CONTRADICTED / NO-EVIDENCE
- Contradiction detection with MINOR / MAJOR / BLOCKING severity
- AssumptionTracker escalation for WEAK, CONTRADICTED, and NO-EVIDENCE requirements

**Owned Responsibilities:**
- Sprint requirement evidence validation
- Discovery evidence synthesis and classification

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Draft requirements to validate
    - specs/knowledge.md: Domain context and prior research signals
    - specs/features.md: Feature intent context
  Optional:
    - Interview transcripts or meeting notes
    - Analytics exports / usage telemetry
    - Prior sprint validation reports
    - Support ticket exports

**Outputs:**
- artifacts/evidence-map.md: Per-requirement evidence strength classification with citations and AssumptionTracker escalation list

**Dependencies:**
- AssumptionTracker: Receives escalation of WEAK/CONTRADICTED/NO-EVIDENCE requirements

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Only as good as the evidence inputs provided; tribal knowledge without transcript input is invisible
- Evidence older than 90 days is automatically downweighted to WEAK unless corroborated by a recent source
- Classification is heuristic; identifies signals, not legal proof of user need
- BLOCKING contradictions prevent requirement dispatch until resolved

**Summary:** Validates sprint requirements against discovery evidence, classifying evidence strength per requirement and escalating weak or contradicted requirements to AssumptionTracker.

---

## ReviewPilot

**Skill Name:** ReviewPilot

**Purpose:** Automated PR review layer that pre-reviews every pull request for spec compliance, acceptance criteria coverage, coding convention violations, and structural issues, classifying findings as BLOCKING, ADVISORY, or INFORMATIONAL before the POD Lead's human review.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- PR metadata extraction from provenance headers with requirement-to-acceptance-criteria mapping
- Spec conformance check per requirement: PASS / FAIL / PARTIAL / UNTESTABLE verdict per criterion
- Python convention checks: no print(), type annotations, no raw SQL, exception handling in routes, no PII in responses
- TypeScript/React convention checks: no console.log, no any type, API client usage, loading/error states, props interfaces
- Structural analysis: wrong directory placement, missing test files, circular imports, direct DB access from route layer
- Finding classification: BLOCKING / ADVISORY / INFORMATIONAL

**Owned Responsibilities:**
- Automated PR spec compliance verification
- Coding convention enforcement
- Finding classification before POD Lead review

**Inputs:**
  Mandatory:
    - PR diff (changed files and line diffs): Primary review target
    - artifacts/openspec.yaml: Acceptance criteria
  Recommended:
    - .cursorrules: Coding conventions
    - AGENTS.md: Project conventions
    - TrustFabric compliance flags: PII violations in changed code
    - artifacts/ai-manifest.json: Existing component registry
    - specs/design.md: Architecture constraints

**Outputs:**
- PR Review Report: Spec conformance table, blocking findings, advisory findings, informational findings, merge verdict
- review-verdict.yaml: Machine-readable verdict for NexusDeploy

**Dependencies:**
- TrustFabric: Provides PII compliance flags
- KnowledgeMesh: Retrieves acceptance criteria and convention context
- NexusDeploy: Receives review-verdict.yaml as deploy gate input

**Project Types:**
- Python/FastAPI backend and TypeScript/React frontend projects

**Constraints:**
- Per-PR scope only; cannot evaluate cross-PR architectural decisions spanning multiple PRs
- Does not execute code or run tests; spec conformance assessed by static analysis
- Cannot review infrastructure changes (Dockerfile, docker-compose, CI config)

**Summary:** Pre-reviews every PR for spec conformance, acceptance criteria coverage, and convention compliance, classifying findings as BLOCKING/ADVISORY/INFORMATIONAL before POD Lead review.

---

## RolloutAdvisor

**Skill Name:** RolloutAdvisor

**Purpose:** Recommends the safest rollout method, generates a specific rollback plan with RTO targets, and defines the Monday smoke test checklist based on the deployment's risk profile from ReleaseIntel and ParityChecker, enabling mechanical deployment execution.

**Phase:** 04-AI-Solution-Deployment

**Capabilities:**
- Composite risk tier determination from blast radius, P1 risks, parity drift, and scenario matrix
- Rollout method recommendation: feature-flag toggle, canary (with phase percentages and hold times), blue-green, or direct rolling deploy
- Trigger threshold definition for canary progression and rollback activation per risk tier
- Per-component rollback plan with step-by-step procedure, RTO target, and verification steps
- Cross-component rollback sequencing
- Monday smoke test checklist generation with specific expected outcomes per item

**Owned Responsibilities:**
- Rollout strategy recommendation
- Rollback plan with RTO targets
- Post-deployment smoke test checklist

**Inputs:**
  Mandatory:
    - artifacts/release/release-intel-report.md: Blast radius and P0/P1 issues (from ReleaseIntel)
    - artifacts/release/parity-check-report.md: Environment parity verdict (from ParityChecker)
    - artifacts/task-breakdown.yaml: Component detail and rollback notes
  Strongly recommended:
    - artifacts/scenario-matrix.md: Risk scenarios that could activate at deployment
  Mandatory fallback:
    - artifacts/sprint-board.md: Deployment scope if no deploy-manifest
  Optional:
    - artifacts/release/deploy-manifest.yaml: Explicit deployment scope

**Outputs:**
- artifacts/release/rollout-strategy.md: Recommended rollout method with phase thresholds and trigger conditions
- artifacts/release/rollback-plan.md: Per-component rollback procedures with RTO targets and smoke test checklist

**Dependencies:**
- ReleaseIntel: Provides release-intel-report.md
- ParityChecker: Provides parity-check-report.md
- ScenarioPlanner: Provides scenario-matrix.md
- SpecFlow: Provides task-breakdown.yaml

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Go/No-Go for deployment belongs to a named human; RolloutAdvisor recommends but does not decide
- If ReleaseIntel or ParityChecker show blockers, all outputs are DRAFT ONLY with unresolved blockers listed on every page
- Conservative thresholds by default; cost of unnecessary rollback is 30 minutes vs. cost of missed trigger is a production incident

**Summary:** Generates a pre-approved rollout strategy and rollback plan from deployment risk profile, enabling mechanical Monday deployment execution rather than improvised decision-making.

---

## RunbookSynth

**Skill Name:** RunbookSynth

**Purpose:** Generates and maintains complete, step-by-step operational runbooks per deployed feature by reading the deploy manifest, system architecture, and incident history — automatically updating on deployment events and enriching with IncidentLens verified fixes to prevent stale documentation.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Deploy manifest parsing to enumerate deployed features, versions, dependencies, configurations
- System context extraction from design.md and api.md for operational procedures
- Per-feature runbook generation across POD Lead-selected sections: system overview, deployment procedures, health checks, scaling, rollback, alert response, known issues, dependency management, security incident response, contact matrix
- Rollback runbook generation from RolloutAdvisor rollback plan in deploy manifest
- Runbook versioning with prior versions moved to history directory
- Update trigger script generation for configured trigger events

**Owned Responsibilities:**
- Operational runbook generation and maintenance
- Incident-enriched Known Issues and Verified Fixes documentation

**Inputs:**
  Mandatory:
    - artifacts/deploy-manifest.yaml: Deployed services, versions, configs, rollback plan
    - artifacts/openspec.yaml: Feature specs and integration contracts
    - specs/design.md: System architecture and dependency map
    - specs/api.md: API contracts and error response codes
    - artifacts/decision-ledger.md: Architectural decisions relevant to operations
  Optional:
    - operate/incident-lens/incident-log.md: Resolved incidents for Known Issues section
    - operate/drift-guard/drift-report.md: Known drift patterns for runbook enrichment

**Outputs:**
- operate/runbook-synth/runbook-[feature-id]-[version].md: Per-feature operational runbook
- operate/runbook-synth/runbook-rollback-[version].md: Rollback-specific runbook (if selected)
- operate/runbook-synth/runbook-index.md: Master index with version history
- operate/runbook-synth/runbook-update-trigger.sh: Watch script for trigger events
- operate/runbook-synth/runbook-config.yaml: RunbookSynth configuration
- operate/runbook-synth/history/: Prior runbook versions

**Dependencies:**
- IncidentLens: Provides incident-log.md and runbook-enrichments.yaml
- DriftGuard: Provides drift-report.md for drift pattern enrichment

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- deploy-manifest.yaml required; cannot generate runbooks without deployment context
- Features in openspec.yaml not in deploy manifest generate spec-only runbooks with a warning
- Runbook sections with no available source content are omitted silently and noted in runbook-config.yaml

**Summary:** Generates versioned operational runbooks per deployed feature from spec and deploy manifest, automatically updating on deployment events and enriching with IncidentLens incident data.

---

## RuntimeIQ

**Skill Name:** RuntimeIQ

**Purpose:** Continuous SLA sentinel for the production environment — ingests live telemetry, compares against NFR targets locked in openspec.yaml, alerts the POD Lead on breaches, enforces auto-scaling within ControlPlane cost ceilings, and contributes performance evidence to the next sprint planning session.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- NFR target parsing from openspec.yaml per feature (latency percentiles, error rate, availability, token consumption)
- Observability stack configuration generation (Prometheus, Datadog, OpenTelemetry, CloudWatch, Azure Monitor, ELK, or generic)
- Auto-scaling policy generation (Kubernetes HPA, cloud autoscaling, or generic) within ControlPlane cost bounds
- Alert routing configuration per selected channel
- SLA dashboard generation with NFR target overlays
- Monitoring agent script generation with feedback loop contribution per cycle

**Owned Responsibilities:**
- Production SLA monitoring and breach alerting
- Auto-scaling enforcement within cost ceilings
- SLA breach log maintenance
- Per-sprint performance evidence for planning sessions

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: NFR SLA targets per feature
    - artifacts/deploy-manifest.yaml: Deployed services and agent endpoints
    - specs/design.md: Architecture topology and expected traffic patterns
    - operate/control-plane/cost-config.yaml: Hard cost ceiling and approved scaling bounds
    - Observability stack type, metrics endpoint, alert channel, monitoring interval, scaling bounds: Elicited

**Outputs:**
- operate/runtime-iq/sla-dashboard.json: Live SLA dashboard
- operate/runtime-iq/ (observability config): Stack-specific monitoring rules (one file type based on stack)
- operate/runtime-iq/runtime-iq-monitor.py: Master monitoring agent
- operate/runtime-iq/thresholds.yaml: NFR threshold registry
- operate/runtime-iq/sla-breach-log.md: Running SLA breach log
- Auto-scaling policy file (deployment-target-specific)

**Dependencies:**
- ControlPlane: Provides cost-config.yaml for scaling bounds

**Project Types:**
- AI-native production systems with observability infrastructure

**Constraints:**
- openspec.yaml required; aborts with explicit message if absent
- deploy-manifest.yaml absence triggers manual elicitation for runtime details
- ControlPlane not configured triggers a warning (not a block)
- Does not scale beyond ControlPlane-approved cost ceiling

**Summary:** Monitors production SLA metrics against openspec.yaml NFR targets, alerts on breaches, enforces auto-scaling within cost ceilings, and contributes performance evidence to next sprint planning.

---

## ScenarioPlanner

**Skill Name:** ScenarioPlanner

**Purpose:** Stress-tests sprint scope choices by running a 3-scenario (best/expected/worst) ROI analysis per major scope configuration, identifying the assumptions that most heavily influence outcomes, calculating minimum viable scope, and flagging high-variance items.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Assumption sensitivity analysis ranking by value_at_risk × (1 - confidence_score)
- 3-scenario ROI matrix computation (best/expected/worst) per POD Lead-selected scope option
- Minimum viable scope calculation (must-ship items expanded until ROI threshold met in expected scenario)
- Variance ratio flagging: > 3× best/worst = HIGH_VARIANCE, 2–3× = MEDIUM_VARIANCE

**Owned Responsibilities:**
- Sprint scope ROI sensitivity analysis
- Minimum viable scope identification
- High-variance scope item flagging

**Inputs:**
  Mandatory:
    - artifacts/roi-brief.md: Base ROI estimates (from ValueModeler)
    - artifacts/sprint-scope-ranked.md: PROCEED/DEFERRED scope list (from PortfolioPrioritizer)
    - artifacts/assumption-log.md: Assumption confidence scores (from AssumptionTracker)
    - artifacts/task-breakdown.yaml: Effort estimates per cluster (from SpecFlow)
    - specs/program.md: Programme objectives

**Outputs:**
- artifacts/scenario-matrix.md: 3-scenario ROI matrix per scope option, top-3 assumption sensitivities, high-variance items, and scope recommendation

**Dependencies:**
- ValueModeler: Provides roi-brief.md
- PortfolioPrioritizer: Provides sprint-scope-ranked.md
- AssumptionTracker: Provides assumption-log.md
- SpecFlow: Provides task-breakdown.yaml

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Scenario quality entirely dependent on accuracy of ValueModeler inputs and realism of POD Lead best/worst estimates
- Probability estimates are illustrative, not statistical predictions
- Informs POD Lead judgment; does not make the scope decision
- Proposed status: scenario parameters and sensitivity ranges require business definition before meaningful outputs

**Summary:** Stress-tests sprint scope options by computing best/expected/worst ROI scenarios, identifying the highest-sensitivity assumptions, and calculating minimum viable scope.

---

## SecretShield

**Skill Name:** SecretShield

**Purpose:** Silent mandatory gate that scans every context payload destined for a generation accelerator and redacts credentials, API keys, tokens, and secrets before they enter an LLM context window, using dual-method detection — regex pattern matching plus entropy analysis.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- Regex pattern matching for 12 known credential format categories (Anthropic, OpenAI, AWS, JWT, PostgreSQL, generic secrets, private keys, GitHub, Slack, Google, Bearer tokens)
- Semantic/entropy analysis for high-entropy strings (> 3.5 bits/char, length ≥ 20) not matching known patterns
- Disposition decisions: silent redact, redact-and-alert, block payload, pass-through for whitelist matches
- Append-only redaction log (file path, pattern type, action — never the secret value itself)
- Whitelist management for legitimate false-positive patterns

**Owned Responsibilities:**
- Secret redaction from all LLM context payloads
- Credential leak prevention before AI model context window injection

**Inputs:**
  Mandatory:
    - Context payload (any format): Content to be scanned before LLM injection
    - references/secret-patterns.yaml: Regex pattern library for known credential formats

**Outputs:**
- Sanitised context payload: Input with all detected secrets replaced by typed placeholders
- secret-shield-redaction.log: Append-only redaction event log
- POD Lead alert: On block or multi-secret detection

**Dependencies:**
- None (SecretShield is a gate through which all other build agents pass their payloads)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Always active; does not require explicit invocation — runs before every context payload injection
- Pattern matching produces false positives on high-entropy strings; weekly POD Lead log review required to tune whitelist
- Does not scan binary files; binary context injection must be flagged by DevCopilot
- Does not validate whether a redacted credential is still valid; rotation is a human decision

**Summary:** Silently scans and redacts credentials and secrets from all LLM context payloads using regex and entropy analysis, preventing credential leaks into AI model context windows before every context injection.

---

## SimLab

**Skill Name:** SimLab

**Purpose:** Validates that every built component meets its Non-Functional Requirements under realistic stress conditions — generating load test scripts, injecting failure scenarios, and validating circuit-breaker behavior — before deployment.

**Phase:** 03-Platform-Enablement

**Capabilities:**
- NFR target extraction from openspec.yaml with HITL elicitation if absent
- k6 load test script generation per endpoint with parameterized NFR thresholds (no hardcoded values)
- Failure injection scenario generation: dependency unavailable, degraded, rate-limited, partial failure, cascade failure
- Circuit-breaker validation (time-to-open, fallback response correctness, recovery time)
- Edge case simulation: minimum/maximum input, concurrent duplicates, rapid successive requests
- NFR pass/fail verdict: PASS / WARN / FAIL per metric

**Owned Responsibilities:**
- NFR validation under load and chaos conditions
- Circuit-breaker and resilience verification

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: NFR targets (latency percentiles, concurrency, error rate, availability, circuit-breaker config)
    - artifacts/deploy-manifest.yaml: Integration endpoint list for load targeting
  Optional:
    - artifacts/task-breakdown.yaml: Edge case scenarios from acceptance criteria
    - artifacts/context.yaml: Delivery context for environment assumptions

**Outputs:**
- tests/load/: Generated k6 load test scripts (one per endpoint)
- tests/chaos/: Generated failure injection test scripts
- artifacts/simlab-results.json: Raw metrics per endpoint and scenario
- artifacts/nfr-verdict.md: Human-readable NFR pass/fail with Release gate input

**Dependencies:**
- None (InsightOps consumes simlab-results.json)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Simulations run against staging environment; infrastructure differences can produce false-pass results
- POD Lead must confirm staging-production equivalence before results are treated as valid
- Generates k6 scripts by default; alternate framework specified in openspec.yaml nfr.test_framework
- Chaos scenarios simulate via mock responses, not actual network fault injection (requires Toxiproxy or equivalent separately)

**Summary:** Generates and executes load, chaos, and resilience tests against staged components, validating NFR compliance and blocking release on any FAIL verdict.

---

## spec-api

**Skill Name:** spec-api

**Purpose:** Defines and maintains the complete backend API specification — all REST endpoints, request/response schemas, authentication strategy, error contract, and FastAPI implementation patterns — serving as the primary contract for backend and frontend pod implementation.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- API foundation definition: base URL, versioning strategy, authentication, CORS
- Endpoint design derived from knowledge.md domain entities and workflows
- Request/response conventions: pagination, date format, enum representation, null handling
- Error and non-functional contract: status code conventions, rate limiting, timeout policy
- FastAPI implementation pattern templates with Pydantic v2 schemas
- Endpoint definition format with business rules applied reference
- Initialize Mode (new spec) and Review Mode (existing spec)

**Owned Responsibilities:**
- Backend API specification (specs/api.md)
- Endpoint definitions and Pydantic schema definitions
- Authentication and error contract

**Inputs:**
  Mandatory:
    - specs/program.md: System domains, security NFRs, compliance requirements
    - specs/knowledge.md: Entities, workflows, business rules (become endpoints)
    - specs/database.md: Table structure (drives request/response shapes)
  Optional:
    - specs/design.md: Auth mechanism, API style, framework versions
    - Existing specs/api.md: Determines Initialize vs. Review mode

**Outputs:**
- specs/api.md: Complete API specification

**Dependencies:**
- spec-knowledge: Provides knowledge.md
- spec-database: Provides database.md
- spec-design: Provides design.md (optional)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Must read all prerequisite specs before eliciting or editing
- Review Mode: flag breaking changes (removed fields, changed types, status code changes)
- Flags if spec-database needs additional indexes for new query patterns

**Summary:** Creates and maintains specs/api.md with complete endpoint definitions, Pydantic schemas, authentication strategy, and error contract derived from domain entities in knowledge.md and database.md.

---

## spec-database

**Skill Name:** spec-database

**Purpose:** Defines and maintains the complete database schema — tables, columns, data types, constraints, indexes, relationships, and migration strategy — as the authoritative source that the backend pod uses to write migrations and queries.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Database platform selection and configuration for relational (PostgreSQL, MySQL, SQLite) and document databases (MongoDB, DynamoDB, Firestore)
- Schema design derived from knowledge.md entities with full column/field definitions
- Index design, foreign key specification, and constraint definition
- Compliance handling: PII encryption fields, data retention, GDPR deletion
- Relational schema format (table columns, indexes, foreign keys) and document schema format (JSON Schema)
- Initialize Mode (new spec) and Review Mode (existing spec)

**Owned Responsibilities:**
- Database schema specification (specs/database.md)
- Migration strategy documentation
- ORM model source of truth

**Inputs:**
  Mandatory:
    - specs/program.md: System domains, compliance requirements (PCI, GDPR)
    - specs/knowledge.md: Core entities, attributes, relationships, business rules
  Optional:
    - specs/design.md: Database technology choice, ORM, migration tool
    - Existing specs/database.md: Determines Initialize vs. Review mode

**Outputs:**
- specs/database.md: Complete database schema specification

**Dependencies:**
- spec-knowledge: Provides knowledge.md
- spec-design: Provides database technology and ORM choices (optional)

**Project Types:**
- Relational databases (PostgreSQL, MySQL, SQLite) and document databases (MongoDB, DynamoDB, Firestore)

**Constraints:**
- Schema derived from knowledge.md entities; additions or deviations confirmed with user
- Business rules should have corresponding database-level enforcement where appropriate
- Flags if spec-api needs updating when new tables are added

**Summary:** Creates and maintains specs/database.md with complete schema definitions for relational or document databases derived from knowledge.md entities.

---

## spec-design

**Skill Name:** spec-design

**Purpose:** Defines and maintains the technical blueprint of the program — programming language, frameworks, libraries, infrastructure, architectural patterns, and tooling decisions — preventing pods from making independent, conflicting technology choices.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Language and runtime selection across backend, frontend, and deployment targets
- Framework and library selection: backend framework, frontend framework, ORM, auth, testing, domain libraries
- Infrastructure and deployment configuration: cloud provider, containerization, CI/CD, environments, secrets management
- Standards and conventions: code style, API style, logging and observability, branch strategy, documentation standard
- Initialize Mode (new spec) and Review Mode (existing spec)

**Owned Responsibilities:**
- Technical design specification (specs/design.md)
- Technology stack decisions as program-wide standard
- Coding standards and conventions

**Inputs:**
  Mandatory:
    - specs/program.md: System domains, NFRs, pod structure, compliance requirements
  Optional:
    - specs/knowledge.md: Entity complexity and workflow needs
    - Existing specs/design.md: Determines Initialize vs. Review mode

**Outputs:**
- specs/design.md: Complete technical blueprint

**Dependencies:**
- spec-knowledge: Provides knowledge.md (if it exists)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Must be done before any coding begins and whenever technology decisions change
- Flags downstream specs that need alignment when technology choices are updated
- Conflicts with NFRs or compliance requirements must be confirmed by user before writing

**Summary:** Creates and maintains specs/design.md defining the technology stack, infrastructure, and coding standards that all pods must follow consistently.

---

## spec-generation

**Skill Name:** spec-generation

**Purpose:** Synthesizes all program knowledge into a complete hierarchical specification — Epics → Stories → Tasks — and produces two delivery-ready output files (specs/spec.md and specs/tasks.md), where every task is scoped to 3 business days or fewer.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Epic derivation from feature categories, technical foundation requirements, data migration, UI foundation, and integration work
- Story derivation from FR-n entries, business rules, workflows, NFRs, screens, and migration steps
- Task derivation with absolute 3-business-day ceiling and task type tagging (DESIGN/BACKEND/FRONTEND/DATA/INTEGRATION/TESTING/INFRA/DOCS)
- Cross-cutting task generation: Sprint 0 foundation, security, observability, and documentation tasks
- Pre-generation source summary with prerequisite checks and proposed epic structure
- Spec review presentation before file writing with blocked task identification

**Owned Responsibilities:**
- Program specification hierarchy (Epics, Stories, Tasks)
- Delivery planning with effort estimates
- specs/spec.md and specs/tasks.md

**Inputs:**
  Mandatory:
    - knowledge.md: Business context, business rules, business workflows, constraints
    - features.md: All FR-n entries with priority signals and acceptance notes
  Recommended:
    - design.md (TO-BE sections): Architecture pattern, components, NFRs
    - uiux.md (TO-BE sections): Screen inventory, personas, navigation model
  Optional:
    - api.md (TO-BE sections): API style, auth model, endpoint inventory
    - database.md (TO-BE sections): Data model, migration strategy
    - impl.md: Tech stack, environment structure, CI/CD, pending decisions

**Outputs:**
- specs/spec.md: Epics and stories with acceptance criteria and business rule references
- specs/tasks.md: Complete task inventory with type tags, effort estimates, and blocked task list

**Dependencies:**
- design-setup: Provides design.md TO-BE content (recommended)
- knowledge-review: Provides validated knowledge.md (recommended)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- 3-business-day task ceiling is absolute; tasks exceeding this must be split
- Every task must belong to a story; every story must belong to an epic
- Every story must reference its source (FR-n, business rule, workflow, or design requirement)
- Acceptance criteria must be specific and observable; vague criteria are not acceptable
- NICE TO HAVE features excluded from spec iteration unless explicitly included

**Summary:** Synthesizes program knowledge into a complete Epics → Stories → Tasks specification in specs/spec.md and specs/tasks.md with all tasks scoped to 3 business days or fewer.

---

## SpecFlow

**Skill Name:** SpecFlow

**Purpose:** Converts a locked openspec.yaml into a parallel-ready build plan by decomposing every functional and non-functional requirement into bounded generation clusters — each a self-contained unit of code that one AI Builder can generate independently.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Requirement classification: Functional (FR), Non-Functional (NFR), Integration (IR), Data (DR)
- Cluster decomposition with module boundary identification and intra-cluster dependency satisfaction
- Directed dependency graph construction with critical path identification
- Parallel wave planning grouping clusters by dependency satisfaction order
- Provenance header injection format per stack (frontend and backend)
- Manifest update appending all new artifacts to ai-manifest.json

**Owned Responsibilities:**
- Spec-to-build decomposition
- Parallel work plan with builder wave assignments
- Cluster dependency graph

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Sprint requirements to decompose
    - artifacts/context.yaml: Enterprise context for capability deduplication (from ContextFabric)
    - artifacts/policy-catalogue.yaml: Compliance rails per cluster (from PolicyCatalog)
    - specs/spec.md: Epics and stories from prior phase
    - specs/tasks.md: Task inventory from prior phase
    - specs/design.md: Architectural patterns
    - specs/api.md: API contracts
    - specs/database.md: Schema definitions
    - specs/ui-ux.md: UI/UX spec
  Optional:
    - artifacts/ai-manifest.json: Prior sprint artifacts for iteration mode

**Outputs:**
- artifacts/task-breakdown.yaml: Cluster definitions with requirements, dependencies, wave assignments, builder assignments, effort, policy rails
- artifacts/ai-manifest.json: Updated artifact manifest with spec traceability IDs
- artifacts/parallel-work-plan.md: Human-readable wave plan for POD Lead review

**Dependencies:**
- ContextFabric: Provides context.yaml
- PolicyCatalog: Provides policy-catalogue.yaml
- spec-generation: Provides spec.md and tasks.md
- spec-design: Provides design.md
- spec-api: Provides api.md
- spec-database: Provides database.md
- spec-uiux: Provides ui-ux.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Output quality bounded by spec completeness; vague NFRs produce vague code skeletons
- If context.yaml absent, flags capability assumptions as unverified and reduces confidence scores
- Does not generate code directly; produces the plan and provenance-tagged skeletons

**Summary:** Decomposes a locked sprint spec into a parallel-ready cluster build plan with dependency graph, wave assignments, policy rails, and provenance-tagged skeleton files.

---

## SpecImpactAnalyzer

**Skill Name:** SpecImpactAnalyzer

**Purpose:** Traces the full downstream impact of a proposed openspec.yaml change across all existing artifacts, estimates regeneration and retest effort, classifies change risk, and flags any closed HITL gates that would be invalidated — giving the POD Lead a data-driven proceed/defer/escalate decision in under 10 minutes.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Diff parsing classifying changes as ADDITIVE, MODIFICATIVE, DESTRUCTIVE, or NFR CHANGE
- Ripple tracing through traceability-report.md with transitive dependency expansion
- Effort estimation per affected artifact (code regeneration, test regeneration, integration retest, gate re-attestation) with ±30% variance range
- Risk classification: IN-SPRINT SAFE / DEFER TO NEXT SPRINT / SCOPE RISK / ESCALATE
- Rework scope patch generation when change is approved

**Owned Responsibilities:**
- Spec change downstream impact analysis
- Artifact ripple detection across clusters and tests

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml (current): Locked sprint spec
    - artifacts/openspec-proposed.yaml OR inline diff: Proposed change
    - artifacts/ai-manifest.json: All existing artifacts with spec IDs (from SpecFlow)
    - artifacts/traceability-report.md: Artifact dependency graph (from TraceGraph)
    - artifacts/task-breakdown.yaml: Current task assignments (from SpecFlow)
    - artifacts/decision-ledger.md: Closed HITL gates to check for invalidation
    - specs/spec.md: Master specification
  Optional:
    - tests/*.feature: For test regeneration estimation

**Outputs:**
- artifacts/impact-analysis.md: Affected artifacts, HITL gate impact, effort estimate, risk classification, recommendation
- artifacts/rework-scope-patch.yaml: Re-queue list for Conductor (generated only if change is approved)

**Dependencies:**
- SpecFlow: Provides ai-manifest.json and task-breakdown.yaml
- TraceGraph: Provides traceability-report.md
- DecisionLedger: Provides decision-ledger.md for gate invalidation check

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Effort estimates are heuristic; POD Lead makes the final proceed/defer decision
- Cannot detect semantic impact from wording changes that look minor but have large architectural implications; flag for manual review
- First sprint has no historical baseline for estimation accuracy

**Summary:** Analyzes proposed spec changes to quantify downstream artifact impact, estimate rework effort in builder-hours, classify risk, and produce a POD Lead proceed/defer/escalate recommendation.

---

## spec-knowledge

**Skill Name:** spec-knowledge

**Purpose:** Captures and maintains the domain knowledge layer of the program — business rules, domain entities, workflows, terminology, and constraints — serving as the shared vocabulary that all pods reference to build consistently without conflicting assumptions.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Domain entity elicitation with attributes and relationships
- Business rule and constraint elicitation (state transitions, validation rules, compliance constraints, edge cases)
- Glossary and workflow elicitation with step-by-step flows, actors, and triggers
- Targeted knowledge gap review and surgical update (Review Mode)
- Changelog maintenance with date-stamped history

**Owned Responsibilities:**
- Domain knowledge specification (specs/knowledge.md)
- Shared domain vocabulary for all pods
- Business rules and entity definitions

**Inputs:**
  Mandatory:
    - specs/program.md: Domain, users, system domains, and scope
  Optional:
    - Existing specs/knowledge.md: Determines Initialize vs. Review mode

**Outputs:**
- specs/knowledge.md: Domain overview, core entities, business rules, state machines, workflows, constraints, glossary, changelog

**Dependencies:**
- program-charter: Provides specs/program.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Without knowledge.md, pods make conflicting assumptions about domain behavior
- In Review Mode: never rewrites accurate sections; only targeted gap fills and corrections

**Summary:** Captures and maintains the shared domain knowledge layer including business rules, entities, workflows, and glossary in specs/knowledge.md, consumed by all pods.

---

## spec-uiux

**Skill Name:** spec-uiux

**Purpose:** Defines and maintains the UI/UX design specification — component library, design tokens, interaction patterns, and accessibility standards — created once and shared across all features and pods to prevent visual inconsistency and redundant design decisions.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Design language and token elicitation: color palette, typography scale, spacing system, border radius, elevation
- Core component definition: buttons, inputs/forms, navigation, feedback components, data display
- Motion and transition system definition: duration scale, easing, page transitions, micro-interactions
- Layout and responsive behavior: grid system, breakpoints, touch targets, safe areas
- Accessibility and internationalization standards: WCAG level, focus management, screen reader, RTL support
- Initialize Mode (new spec) and Review Mode (existing spec)

**Owned Responsibilities:**
- UI/UX design specification (specs/ui-ux.md)
- Design system definition as program-wide standard
- Accessibility standards

**Inputs:**
  Mandatory:
    - specs/program.md: Target users, devices, accessibility NFRs, design highlights
  Optional:
    - specs/design.md: Frontend framework, styling library, component approach
    - Existing specs/ui-ux.md: Determines Initialize vs. Review mode

**Outputs:**
- specs/ui-ux.md: Design tokens, component library, motion system, layout system, accessibility standards, iconography, copy and tone, changelog

**Dependencies:**
- spec-design: Provides frontend framework and styling approach (optional)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Created once and reused across all features; prevents visual inconsistency
- Flags if frontend framework or styling library in design.md needs updating to match spec

**Summary:** Creates and maintains the shared UI/UX specification governing design tokens, component library, motion system, and accessibility standards across all features and pods.

---

## TraceGraph

**Skill Name:** TraceGraph

**Purpose:** Builds and maintains a directed traceability graph linking every requirement in openspec.yaml to its implementation artifacts, test scenarios, and deployment entries — surfacing broken links, orphaned artifacts, and untraced requirements as the chain-of-custody record for all HITL gate attestations.

**Phase:** 02-Data-Readiness (also active in 03-Platform-Enablement)

**Capabilities:**
- Requirement inventory from openspec.yaml cross-referenced against specs/spec.md
- Artifact inventory from ai-manifest.json, test feature files, and deploy manifest
- Directed graph construction: REQ-ID → CLU-ID → files → tests → deployment
- Gap detection: UNTRACED REQUIREMENT (CRITICAL), ORPHANED ARTIFACT (WARNING), UNTESTED REQUIREMENT (WARNING→CRITICAL at Gate-2), BROKEN LINK (ERROR), MISSING PROVENANCE HEADER (WARNING)
- Gate attestation records for Gate-0 (cluster assignments), Gate-1 (artifact mappings), Gate-2 (test mappings)

**Owned Responsibilities:**
- Requirement-to-artifact traceability
- Chain-of-custody record for HITL gate attestations

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Requirement IDs
    - artifacts/ai-manifest.json: Artifact entries with requirement ID mappings (from SpecFlow)
    - specs/spec.md: Epics and stories for ID consistency check
    - specs/tasks.md: Task inventory
  Optional:
    - tests/*.feature: Test scenarios with @REQ-XXX annotations (Build phase)
    - artifacts/deploy-manifest.yaml: Deployed component entries (Build/Deploy phase)

**Outputs:**
- artifacts/traceability-report.md: Coverage summary, gap report by severity, full traceability graph, gate attestation record

**Dependencies:**
- SpecFlow: Provides ai-manifest.json
- spec-generation: Provides spec.md and tasks.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Only traces artifacts with correctly formatted SpecPod provenance headers and @REQ-XXX test annotations
- Manually written code without provenance appears as orphaned until annotated
- Graph accuracy bounded by completeness of ai-manifest.json; SpecFlow must run first

**Summary:** Builds a directed traceability graph from requirements to artifacts to tests, surfaces coverage gaps by severity, and produces gate attestation records for each HITL gate.

---

## TransformIQ

**Skill Name:** TransformIQ

**Purpose:** Rescores the AI opportunity backlog against the current sprint's requirements and operational signals from prior sprints, surfacing unmapped high-value candidates not yet in scope for PortfolioPrioritizer consideration.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Backlog scan identifying items already in scope vs. unmapped candidates
- Signal ingestion from prior sprint operational feedback (delivered value, underdelivery patterns, recurring pain points)
- Composite rescoring with five dimensions weighted by POD Lead strategic priorities
- Prior sprint calibration adjusting scores based on actual delivery vs. forecast
- Candidate surfacing above configurable value-density threshold
- Top-5 quick wins summary for business lead consumption

**Owned Responsibilities:**
- AI opportunity backlog rescoring per sprint
- Unmapped value candidate surfacing for PortfolioPrioritizer

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Current sprint requirements for already-in-scope identification
    - specs/features.md: Features already planned
    - specs/program.md: Programme objectives for strategic fit scoring
    - references/opportunity-catalogue.yaml: Full AI opportunity backlog with historical scores
  Optional:
    - artifacts/feedback-loop-triggers.yaml: Prior sprint operational signals

**Outputs:**
- artifacts/opportunity-backlog-rescored.md: Rescored backlog with current sprint items, candidate additions above threshold, value density top-5 summary, and descored items

**Dependencies:**
- PortfolioPrioritizer: Receives opportunity-backlog-rescored.md as mandatory input

**Project Types:**
- AI-native projects with an opportunity backlog

**Constraints:**
- Scoring accuracy depends on richness of operational feedback from prior sprints
- First sprint scores are approximations based on strategic weights alone
- Surfaces candidates only; PortfolioPrioritizer and POD Lead make the final inclusion decision

**Summary:** Rescores the AI opportunity backlog against current sprint context and prior sprint operational signals, surfacing top-value unmapped candidates for PortfolioPrioritizer consideration.

---

## TrustFabric

**Skill Name:** TrustFabric

**Purpose:** Enforces data contract governance and PII compliance at code generation time as an inline gate — validating every generated module that accesses a data entity against registered data contracts before acceptance into the sprint.

**Phase:** 03-Platform-Enablement (also active in 04-AI-Solution-Deployment for data governance attestation)

**Capabilities:**
- Data contract registry loading from data-contracts/*.yaml files
- Sprint data entity profiling identifying all entities accessed and checking contract registration
- Generated code validation: PII exposure, missing contract, role violation, retention breach, logging violation, unmasked display, missing encryption
- PII taxonomy enforcement across seven classification levels (IDENTITY, CONTACT, FINANCIAL, BEHAVIORAL, HEALTH, INTERNAL, NON-PII)
- Unclassified field flagging for POD Lead contract definition
- Release phase data governance attestation

**Owned Responsibilities:**
- Data contract governance at code generation time
- PII compliance enforcement before code acceptance
- Data governance attestation for Release gate

**Inputs:**
  Mandatory:
    - specs/database.md: Schema definitions with all tables and fields
    - specs/api.md: API response schemas
    - artifacts/openspec.yaml: Sprint requirements with data access scope
    - artifacts/policy-catalogue.yaml: Compliance and privacy policies
    - data-contracts/*.yaml: Field-level PII classification and handling rules per entity
    - Generated code modules: Code submitted for governance review

**Outputs:**
- data-contract-compliance-report.md: Per-module violations, unclassified fields, compliant fields
- data-contract-violations.yaml: Machine-readable violations for PolicyCatalog and NexusDeploy
- unclassified-fields-report.md: New fields requiring POD Lead contract definition
- Release Phase attestation: Signed data governance sign-off

**Dependencies:**
- KnowledgeMesh: Provides data contract and schema context chunks
- DevCopilot: Upstream trigger submitting generated code for validation

**Project Types:**
- Projects with data entities containing personally identifiable information or sensitive data

**Constraints:**
- Cannot classify fields with no data contract definition; new entities require human contract definition before enforcement
- Does not perform runtime data sampling; classification based on schema and contract definitions only
- New fields in generated code without a contract entry block the module until POD Lead defines the contract

**Summary:** Validates generated code modules against registered data contracts, blocking PII exposure and contract violations at code generation time rather than discovering them at QA.

---

## ValueModeler

**Skill Name:** ValueModeler

**Purpose:** Quantifies the expected business value of each sprint requirement before a single line of code is written — calculating per-requirement value forecasts and a sprint-level ROI estimate — making ROI accountability visible at the spec level on Monday morning.

**Phase:** 02-Data-Readiness

**Capabilities:**
- Requirement value classification: direct value, enabling value, quality value, experience value, technical value
- Per-requirement value quantification with formulas for time saved, revenue enablement, error reduction, and qualitative proxies
- Sprint-level ROI calculation with confidence range (±15% high / ±30% medium / ±50% low)
- Low-value flagging for requirements where annual value < 2× allocated sprint investment
- Value baseline record creation for ValueTracker post-sprint comparison

**Owned Responsibilities:**
- Sprint ROI forecasting
- Per-requirement value quantification
- Value baseline record for post-sprint measurement

**Inputs:**
  Mandatory:
    - artifacts/openspec.yaml: Sprint requirements
    - artifacts/task-breakdown.yaml: Effort estimates per cluster (from SpecFlow)
    - specs/features.md: Feature context
    - specs/program.md: Programme objectives
    - references/opportunity-catalogue.yaml: Opportunity context
    - Baseline metrics (time saved, error rates, revenue at risk): Elicited from POD Lead
  Optional:
    - Prior sprint ValueTracker actuals: For calibration

**Outputs:**
- artifacts/roi-brief.md: Sprint ROI summary, per-requirement value forecast, defer candidates, value baseline record for ValueTracker

**Dependencies:**
- SpecFlow: Provides task-breakdown.yaml with effort estimates
- PortfolioPrioritizer: Receives roi-brief.md as mandatory input
- ScenarioPlanner: Receives roi-brief.md as mandatory input

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Requires consistent baseline metric inputs from the business; garbage in, garbage out
- Accuracy improves over 3–5 sprints as ValueTracker actuals accumulate
- Technical and experience value use qualitative proxies; treat as directional, not accountable figures
- Proposed status: integration with ValueTracker requires further design; baseline metrics must be agreed before first use

**Summary:** Calculates forecasted business value and ROI per sprint requirement, flags low-value candidates for PortfolioPrioritizer, and produces a locked ROI baseline for ValueTracker post-sprint comparison.

---

## ValueTracker

**Skill Name:** ValueTracker

**Purpose:** Closes the ROI accountability loop by comparing actual post-deployment business metric performance against ValueModeler forecasts per requirement, identifying over/under-performing features, and feeding calibration data back to ValueModeler to improve future forecast accuracy.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- ROI forecast parsing from roi-brief.md with per-feature value predictions and metric mappings
- Baseline vs. actuals comparison engine with delta and variance calculation
- Feature classification: over-performing, on-track, under-performing, insufficient-data
- Realised ROI percentage vs. forecasted ROI calculation
- ValueModeler calibration output generation (if enabled) for progressive forecast improvement
- Baseline capture script generation for pre-deployment metric collection

**Owned Responsibilities:**
- Post-deployment ROI realisation measurement
- ValueModeler forecast calibration over successive sprints

**Inputs:**
  Mandatory:
    - artifacts/roi-brief.md: Sprint ROI forecast with predicted values and metric names (from ValueModeler)
    - artifacts/openspec.yaml: Feature definitions and acceptance criteria
    - artifacts/sprint-scope-ranked.md: Priority context (from PortfolioPrioritizer)
    - artifacts/deploy-manifest.yaml: Deployment timestamp for measurement window start
    - Business metrics source: Elicited (database, REST API, analytics platform, etc.)
    - Pre-deployment baseline metrics: Must be captured before deployment

**Outputs:**
- operate/value-tracker/value-tracker-config.yaml: All configuration including metric mappings
- operate/value-tracker/baseline-capture.py: Pre-deployment baseline capture script
- operate/value-tracker/value-tracker-fetcher.py: Post-deployment metric fetcher
- operate/value-tracker/value-comparator.py: Actual vs. forecast comparison engine
- operate/value-tracker/value-realization-report.md: Per-feature actual vs. forecast ROI
- operate/value-tracker/baseline-metrics.yaml: Captured pre-deployment baseline
- operate/value-tracker/value-modeler-calibration.yaml: Calibration data for ValueModeler (if enabled)

**Dependencies:**
- ValueModeler: Provides roi-brief.md
- PortfolioPrioritizer: Provides sprint-scope-ranked.md

**Project Types:**
- AI-native production systems with measurable business metrics and analytics instrumentation

**Constraints:**
- Pre-deployment baseline metrics required; without them, actuals vs. forecast comparison is impossible
- Insufficient data (< 100 data points) marks feature as insufficient-data, not under-performing
- Business metrics must be instrumented before deployment; generates instrumentation guide if not yet in place
- Proposed status: metrics integration with business systems needs further design; business metrics must be instrumented before first use

**Summary:** Measures actual post-deployment business value against ValueModeler forecasts per feature, classifying performance and generating calibration data to progressively improve ROI forecast accuracy across sprints.

---

## SkillFlow

**Skill Name:** SkillFlow

**Purpose:** Analyzes a project's completed Phase 01 initialization artifacts and the skill catalog to produce an evidence-backed recommendation plan determining which Phase 02+ skills to execute, enhance, skip, or extend — before execution begins.

**Phase:** 01-Establish-Strategy

**Capabilities:**
- Skill recommendation classification: Required, Recommended, Optional, Not Recommended
- Skill enhancement recommendation generation with specific placement guidance
- Phase assignment for each recommendation derived from catalog Phase field and dependency chains
- Coverage analysis of Phase 01 artifacts (Complete / Partial / Missing / Contradictory per artifact section)
- Confidence scoring across five factors: evidence strength, requirement coverage, catalog alignment, dependency certainty, input completeness
- Capability Classification Framework for gap resolution (Skill Enhancement vs. Candidate New Skill)
- End-to-end traceability from each recommendation to artifact evidence and requirement IDs

**Owned Responsibilities:**
- Phase 02+ skill execution planning
- Recommendation report and summary generation
- Skill enhancement identification against Phase 01 artifact gaps
- Capability gap classification and risk flagging

**Inputs:**
  Mandatory:
    - catalog/skill_catalog.md: Authoritative skill catalog — sole source for all skill knowledge during recommendation analysis
    - specs/program.md: Program charter from Phase 01
    - specs/knowledge.md: Domain knowledge specification from Phase 01
    - specs/design.md: Technical design specification from Phase 01
    - specs/database.md: Database schema specification from Phase 01
    - specs/api.md: API specification from Phase 01
    - specs/ui-ux.md: UI/UX specification from Phase 01
  Optional:
    - specs/features.md: Feature requirements list for higher-precision gap mapping
    - specs/impl.md: Implementation guidance for technology-specific recommendations
    - recommendation_report.md (prior run): For planning continuity and avoiding duplication
    - recommendation_summary.md (prior run): For planning continuity
    - Additional project artifacts: Architecture decision records, prototype documents
    - Customer documents: Requirements specs, BRDs, compliance documentation
    - Meeting outputs: Stakeholder notes and transcripts for implicit requirement surfacing

**Outputs:**
- recommendation_report.md: Decision-support artifact with all recommendations, confidence scores, rationale, and traceability (1,000–2,000 words)
- recommendation_summary.md: Concise execution planning artifact with minimal viable execution plan and phase overview

**Dependencies:**
- program-charter: Provides specs/program.md
- spec-knowledge: Provides specs/knowledge.md
- spec-design: Provides specs/design.md
- spec-database: Provides specs/database.md
- spec-api: Provides specs/api.md
- spec-uiux: Provides specs/ui-ux.md

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- All six Phase 01 artifacts must be present before execution; no partial runs permitted
- Uses skill_catalog.md exclusively for skill knowledge; never reads raw skill files during recommendation generation
- Does not create, modify, or execute skills; plans execution only
- Candidate New Skills identified as gaps are flagged in Risks & Gaps but not created (Version 1 limitation)
- Re-run required when Phase 01 artifacts are materially updated or when the catalog is refreshed with new skills
- Phase 01 skills (program-charter, spec-knowledge, spec-design, spec-database, spec-api, spec-uiux) are never included in recommendation output — their execution is assumed complete

**Summary:** Analyzes completed Phase 01 initialization artifacts and the skill catalog to produce an evidence-backed recommendation plan classifying each Phase 02+ skill as Required, Recommended, Optional, or Not Recommended, with skill enhancement opportunities, confidence scores, and a minimal viable execution plan.

---

## skill-orchestrator

**Skill Name:** skill-orchestrator

**Purpose:** Deterministic dispatch-mode workflow engine that executes an entire SpecPod sprint as a governed pipeline — planning → build → validate — orchestrating all skill tasks and HITL gates in dependency-ordered waves. The engine computes what to run next (order, parallelism, rework routing, gate outcomes); Claude Code executes each action (spawning a subagent per skill, routing each gate to its human reviewer) and feeds results back. Offers a plan mode (think first, act later) that analyzes requirements against a workflow spec without invoking any skill, estimates tokens and cost, raises clarifying questions, recommends skills to include or exclude, and persists a finalized run config ready for execution.

**Phase:** Cross-Phase (02-Data-Readiness → 03-Platform-Enablement)

**Capabilities:**
- Wave-based scheduling: packs independent skill tasks into parallel waves up to configurable `max_parallelism`; gates and exclusive tasks run solo
- Artifact-derived dependency wiring: automatically derives task dependencies from `consumes`/`produces` file contracts — explicit `depends_on` rarely needed
- HITL gate enforcement: gate tasks block all downstream tasks until approved; rejected gates with `rework_targets` ripple rework forward through already-completed dependents and re-fire the gate against fresh artifacts
- Rework loops: skill tasks are retried within a configurable `rework_budget`; `suggested_skill` redirects retry to a focused remediation skill
- Time-budget awareness: under time pressure, rework budget is curbed and optional tasks are dropped — completing the list beats perfecting it
- Plan mode — two-pass: first pass surfaces open questions (`needs_input`); second pass with answers prunes/keeps skills and persists a finalized run config (`ready`)
- Cost estimation: base and worst-case-with-rework token + cost estimates from each task's `token_budget` and a configurable price book
- Skill recommendation: include/exclude analysis based on requirement keywords and artifact graph (e.g. drop `prompt-bench` when no AI features declared)
- Resumable across turns: state persists as JSON after every `record` call
- Governance telemetry: per-phase rollups of FTR rate, rework cycles, token spend, gate outcomes, and makespan; integrates with vendored `skill_governor` SDK for per-skill telemetry

**Owned Responsibilities:**
- Sprint-level workflow scheduling and dispatch
- HITL gate routing and rework ripple management
- Pre-run plan analysis, cost estimation, and skill scoping
- Per-phase governance reporting (FTR, tokens, makespan)

**Inputs:**
  Mandatory:
    - workflow spec JSON: Flat task list with phase, kind (skill/gate), consumes/produces contracts, token budgets, and reviewer assignments
  Conditional:
    - answers JSON (plan mode, second pass): User answers to clarifying questions that prune or keep skills
    - state.json (run mode): Persisted workflow state from prior `record` calls — required for `next`/`record`/`status`/`report`
  Optional:
    - price book JSON: Per-model token rates overriding default estimates
    - governor DB (SQLite): Path for per-skill `skill_governor` telemetry persistence

**Outputs:**
- state.json: Full workflow run state (persisted after every `record`)
- plan-report.md: Wave-by-wave schedule, cost estimate, clarifying questions, skill recommendations (plan mode)
- run-config.json: Finalized pruned spec with plan provenance block — consumed directly by `init` (plan mode, second pass)
- Governance report (stdout or JSON): Per-phase FTR rate, rework cycles, token spend, gate outcomes, makespan

**Dependencies:**
- All SpecPod skills (as orchestration targets — list is spec-driven, not hardcoded): ContextFabric, PolicyCatalog, ResearchCopilot, SpecFlow, DevCopilot, Guardian, RedTeamX, and all others declared in the workflow spec
- skill_governor (vendored SDK): Provides TokenUsage, TaskRecord, SkillRun telemetry primitives

**Project Types:**
- Any project using the SpecPod Framework sprint model (planning / build / validate phases with HITL gates)
- Any multi-skill workflow with artifact dependencies, parallel execution, and gate checkpoints

**Constraints:**
- Engine is deterministic Python — it never calls a model; all LLM execution is delegated to Claude Code subagents
- Does not execute skills itself; Claude Code must spawn each subagent and route each gate to a human reviewer
- Cost estimates are approximations — token budgets and default price book rates are heuristic; set contracted rates in a price book file
- Keyword detection for plan-mode questions is heuristic (cannot parse negation like "no AI features") — always confirm recommendations with the user
- `enforce_phase_order: true` (default) rejects any dependency on a later-phase task at build time
- Rework ripple re-runs all completed dependents of reopened tasks — gate rejections can trigger cascading re-runs

**Summary:** Dispatch-mode workflow engine for the full SpecPod sprint (29 skills, 6 HITL gates across planning/build/validate). The engine owns scheduling, dependency wiring, rework loops, and gate routing; Claude Code owns execution. Plan mode analyzes requirements without invoking any skill, estimates tokens and cost, and produces a finalized run config. Governance reports FTR rate, rework cycles, token spend, and makespan per phase.

---

## ToolSurfaceAuditor

**Skill Name:** ToolSurfaceAuditor

**Purpose:** Audits enabled MCP servers and tool schemas against 30-day usage telemetry, produces disable/keep recommendations per tool, and quantifies standing-context token reclaim by identifying idle tool descriptions consuming permanent context every session.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Tool inventory loading with per-tool token cost (description + schema)
- 30-day telemetry ingestion: calls_30d, last_called, error_rate, latency_ms
- Usage scoring per tool: (calls_per_session × 0.5) + (recency_score × 0.3) + ((1 − error_rate) × 0.2)
- Classification into four tiers: active (>0.4), occasional (0.1–0.4), dormant (0.0–0.1 with calls), never-used (0 calls)
- Server-level consolidation recommendation when ≥80% of a server's tools are dormant or never-used
- Token impact projection: before/after context window size, monthly savings at 1K sessions/day
- Disable configuration generation (env var snippets + JSON) for human review before apply

**Owned Responsibilities:**
- MCP tool usage audit and disable recommendation
- Standing-context token reclaim from idle tool schemas
- Tool surface sizing against configurable ceilings (≤10 MCP servers, ≤80 total tools)

**Inputs:**
  Mandatory:
    - input/enabled-tools.json: Current MCP server and tool inventory with token costs
    - input/usage-telemetry.json: 30-day tool call telemetry
    - input/audit-config.json: Ceilings and thresholds

**Outputs:**
- output/tool-audit-report.json: Per-tool scores, classification, recommendation (sorted by score)
- output/disabled-mcps-config.md: Env var + JSON disable snippets — requires human confirmation before apply
- output/token-impact-report.json: Before/after token counts and monthly savings estimate

**Dependencies:**
- None (integrates with MCP configuration management)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Target ceilings: ≤10 MCP servers, ≤80 total tools; flags if exceeded
- Recency bias: tools called during incidents score low in quiet windows — apply zero-call-zero-error safety rule before disabling
- Telemetry window must match tool cycle (monthly billing tool needs ≥30-day window)
- All disable recommendations require human confirmation and staged rollout; never auto-applied

**Summary:** Identifies tool schema bloat via usage telemetry and recommends disabling idle MCP tools to reclaim standing-context tokens. At typical metrics, disabling never-used tools can free 5–15% of context window. All disable decisions require human confirmation.

---

## PromptSlimmer

**Skill Name:** PromptSlimmer

**Purpose:** Audits system prompts and rules files for redundancy, overlapping intent, and verbosity, produces a minimized prompt with a structured diff, and routes critical sections through Opus review and human sign-off before any changes are applied.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Phase 1 Audit: parses all directives, flags duplicates, semantic duplicates, superseded rules, and contradictions
- Phase 2 Merge: collapses redundancy while preserving intent; dead rules dropped with reason
- Phase 3 Compress: rewrites verbose directives minimally; skips protected critical directives
- Phase 4 Classify: safe (auto-apply), review (human spot-check), critical (Opus drift-check + human sign-off)
- Phase 5 Diff: produces side-by-side markdown with TOKENS_SAVED per directive
- Protected phrases copied byte-for-byte; contradictions surfaced but never auto-resolved

**Owned Responsibilities:**
- System prompt redundancy detection and minimization
- Critical section routing to Opus for drift-check before any change is applied

**Inputs:**
  Mandatory:
    - --system-prompt: System prompt file to slim
    - --rules-files: One or more .mdc / rules files
    - --criticality-flags: Sections marked as critical for Opus routing
    - --output-dir: Output directory

**Outputs:**
- output/system-prompt-slimmed.md: Safe changes applied; critical changes staged pending sign-off
- output/prompt-diff.md: Side-by-side diff with TOKENS_SAVED annotation per directive
- output/slimming-report.json: Per-directive disposition, token delta, classification

**Dependencies:**
- claude-opus-4-7 (external model): Read-only drift-check for critical sections — not a catalog skill

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Critical sections require Opus confirmation + explicit human APPROVED mark before application
- Contradictions block merging until human resolves
- Protected phrases never paraphrased; original prompt preserved in audit record
- Token counting flagged as estimate if tokenizer unavailable

**Summary:** Reduces system prompt bloat through five deterministic phases — audit, merge, compress, classify, diff. Safe changes auto-apply; critical sections require Opus drift-check and human sign-off. A 60% reduction on a 950-token prompt at 1K calls/day saves ~$1.14/day without changing behaviour.

---

## BudgetGovernor

**Skill Name:** BudgetGovernor

**Purpose:** Enforces token and dollar budgets on AI agent task graphs before execution and at every loop iteration using pure-arithmetic cost accounting, preventing runaway costs and surprise bills without invoking any LLM.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Deterministic cost forecast from task graph: token estimates × pricing-table per model per step
- Comparison against tiered caps: task-level, session-level, sprint-level
- Gate decisions: proceed, warn (approaching cap), block (cap would be exceeded)
- Highest-cost step identification with model-downgrade suggestions routed to ModelRouter
- Running spend ledger: append-only per-step cost record for transparency
- Loop runaway detection: mid-iteration budget breach halts execution before the next loop turn

**Owned Responsibilities:**
- Pre-execution cost gate for agentic pipelines
- Budget cap enforcement at task, session, and sprint tiers
- Spend ledger maintenance

**Inputs:**
  Mandatory:
    - input/task-graph.json: Agent task graph with per-step token estimates
    - input/pricing-table.json: Per-model token prices
    - input/budget-caps.json: Configured caps at task, session, and sprint tiers

**Outputs:**
- output/cost-forecast.json: Per-step projected cost, gate decision (proceed/warn/block)
- output/spend-ledger.json: Append-only per-step actual spend record

**Dependencies:**
- ModelRouter: Receives remediation suggestions when BudgetGovernor emits warn or block on a step

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Forecast accuracy bounded by upstream I/O token estimates; assumes 0% cache hit rate conservatively
- Does not observe actual mid-step token usage; reconciles post-step only
- Loop runaway detection requires the task graph to expose iteration boundaries

**Summary:** BudgetGovernor gates agentic pipelines with pure-arithmetic cost accounting, never invoking an LLM. It prevents budget breaches by comparing projected spend against tiered caps, routing high-cost steps to ModelRouter for transparent downgrade, and maintaining an append-only ledger. Canonical use case: multi-step agentic loops with risk of runaway token consumption.

---

## SemanticCache

**Skill Name:** SemanticCache

**Purpose:** Eliminates redundant model invocations by returning stored results for inputs that are identical (exact hash match) or semantically equivalent (cosine similarity ≥ threshold) to previously-answered queries — the first interceptor in the optimization pipeline.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Step 1: Input normalization (strip, lowercase, collapse whitespace) + SHA-256 hash
- Step 2: Exact lookup — zero tokens, ~1–3 ms; returns cached result if not expired
- Step 3: Semantic path on miss — compute embedding via text-embedding-3-small (~200–400 tokens)
- Step 4: Nearest-neighbor search (FAISS flat index ≤100K entries; HNSW for larger)
- Step 5: Semantic hit decision at configurable cosine_sim threshold (default 0.92) with mandatory verification warning
- Step 6: Cache miss — compute result, seed into cache with TTL and source tags
- Session metrics: hit rate, tokens avoided, latency savings

**Owned Responsibilities:**
- First-stage interception before all downstream agents
- Exact and semantic cache hit/miss routing
- PII-safe caching with never-cache pattern enforcement

**Inputs:**
  Mandatory:
    - prompt / file / artifact: Raw input to check
    - cache_store: JSON file or vector index (FAISS/HNSW)
    - similarity_threshold: Default 0.92 (configurable)
  Optional:
    - content_hash (SHA-256): Pre-computed hash to skip normalization

**Outputs:**
- CacheResult: hit (exact or semantic) | miss
- hit_metadata: cache_type, similarity score, tokens_saved, latency_ms, verification warning (semantic hits)
- session_metrics: aggregate hit_rate, tokens_avoided this session

**Dependencies:**
- None — SemanticCache is the first agent in the optimization pipeline; all downstream agents (ModelRouter, Model) are called only on miss

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Semantic hits carry mandatory warning: `warning: semantic_match_verify_appropriateness` — require human review or lightweight classifier before use in high-stakes contexts
- Never cache PII patterns: customer_id, account_number, email, real-time balance
- TTL by category: static FAQ 72h, policy rules 24h, dynamic data 1h
- Version-based cache segmentation required on model upgrade to prevent stale hits

**Summary:** SemanticCache is the first-stage interceptor, checking for exact (hash) and semantic (embedding) matches before any downstream agent runs. Exact hits cost zero tokens (~1–3 ms). Semantic hits cost only the embedding (~300 tokens). At 71.7% hit rate over 12,450 requests/month, ~7.5M tokens avoided. Semantic hits carry mandatory verification flags; PII is never cached.

---

## ModelRouter

**Skill Name:** ModelRouter

**Purpose:** Routes each task step to the least expensive model capable of meeting its quality bar by classifying reasoning depth across six dimensions and applying budget-pressure overrides from BudgetGovernor.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Six-dimension classification per task: reasoning_depth, ambiguity_level, domain_expertise, multi_step_planning, safety_criticality, output_precision (each 1–10, weighted composite)
- Tier mapping: MECHANICAL composite 1–3.4 → Haiku; STANDARD 3.5–6.4 → Sonnet; DEEP 6.5–10 → Opus
- Low-confidence escalation: classification_confidence < 0.7 → upgrade to Sonnet
- Budget-pressure override: ≥90% utilization forces Haiku except safety_criticality ≥7 (Sonnet floor)
- Escalation logging: original model, escalated model, cost delta — for offline tier calibration
- Escalation frequency monitoring: >15% for a task type triggers tier promotion in routing policy

**Owned Responsibilities:**
- Per-task model tier selection
- Budget-pressure downgrade with safety_criticality floor enforcement
- Escalation audit trail for routing policy calibration

**Inputs:**
  Mandatory:
    - input/task-metadata.json: Task description, type, estimated tokens
    - input/routing-policy.json: Tier thresholds and dimension weights
    - input/budget-signal.json: Current utilization % from BudgetGovernor

**Outputs:**
- output/routing-decisions.json: Per-task model assignment with composite score and rationale
- output/routing-decisions-budget-pressure.json: Decisions made under budget pressure override
- output/escalation-log.json: Escalation events with original/escalated model and cost delta

**Dependencies:**
- BudgetGovernor: Provides budget-signal.json with current utilization %

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Classifier confidence threshold 0.70; below this, upgrades to Sonnet regardless of composite score
- Escalation limited to 2 per task to prevent loops
- High-confidence signal patterns are domain-specific and improve over time with calibration data
- Does not override routing when safety_criticality ≥7 even at full budget pressure

**Summary:** ModelRouter is a lightweight Haiku classifier that routes tasks to Haiku, Sonnet, or Opus based on six reasoning dimensions. It is the largest cost lever in the optimization layer — proper routing cuts model spend several-fold. Budget pressure can force downgrades, but safety_criticality ≥7 anchors a Sonnet floor.

---

## RegexLLMRouter

**Skill Name:** RegexLLMRouter

**Purpose:** Assesses text-parsing tasks across five structural regularity dimensions and routes each to regex/parser, hybrid, or LLM execution — eliminating wasteful LLM spend on tasks solvable deterministically in code.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Five-dimension scoring per parsing task: schema_consistency, delimiter_reliability, ambiguity_level, error_tolerance, volume (each 1–5)
- Route mapping by total score: 20–25 → regex; 13–19 → hybrid; 0–12 → LLM
- Hybrid detail: regex handles structured majority; LLM handles ambiguous residual; fallthrough rate monitored (promote if <10%, demote if >60%)
- Regex pattern emission: working Python patterns with capture groups, ≥3 positive and 2 negative test cases, known failures documented
- Pre-scored taxonomy for customer-service domain: order IDs, email, amounts → always regex; sentiment, intent → always LLM

**Owned Responsibilities:**
- Parse-task routing between deterministic and LLM execution
- Regex pattern generation for routed-to-code tasks

**Inputs:**
  Mandatory:
    - input/parsing-tasks.json: Tasks to route with sample inputs
    - input/routing-config.json: Domain taxonomy overrides and fallthrough thresholds

**Outputs:**
- output/routing-decisions.json: Per-task route (regex/hybrid/LLM) with score breakdown
- output/regex-patterns.json: Generated patterns with test cases for regex-routed tasks
- output/hybrid-strategy.json: Fallthrough rules and monitoring thresholds for hybrid-routed tasks

**Dependencies:**
- None

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Regexes must be syntactically valid; known failures must be documented — no silent pattern gaps
- Hybrid fallthrough logged and monitored; high fallthrough rate triggers tier demotion
- Volume dimension bias: low volume may not justify regex engineering time even at high total score

**Summary:** RegexLLMRouter eliminates wasteful LLM spend on tasks solvable in code. For every parsing task, it scores structural regularity and routes to deterministic regex (cost ~$0), hybrid (regex with LLM fallback), or full LLM. Pre-scored taxonomy handles common customer-service patterns.

---

## ContextProfiler

**Skill Name:** ContextProfiler

**Purpose:** Measures the token footprint of every context segment — system prompt, tool schemas, conversation history, injected files, memory blocks — and fires threshold alerts that trigger downstream compaction or pruning, making silent context pressure visible before it becomes catastrophic.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Independent tokenization of five context segments: system_prompt, tool_schemas, conversation_history, injected_files, memory_blocks
- Utilization percentage and headroom calculation against model window (default 200K, configurable)
- Threshold alerts: warn (approaching limit), critical (near capacity), emergency (overflow imminent)
- Downstream recommendations: StrategicCompactor at warn/critical; RelevancePruner at emergency
- Optional Haiku narration of findings for human-readable context health report
- Versioned snapshot: preserves prior context-budget.json as context-budget-\<timestamp\>.json

**Owned Responsibilities:**
- Context window utilization measurement
- Alert firing to trigger StrategicCompactor and RelevancePruner
- Context segment breakdown for audit

**Inputs:**
  Mandatory:
    - input/conversation-transcript.md: Current conversation history
    - input/system-prompt.md: Active system prompt
    - input/mcp-tools.json: Enabled tool schemas
  Optional:
    - input/memory-blocks.json: Active memory blocks
    - input/injected-files.json: Injected file contents
    - model_window_size: Override (default 200K tokens)

**Outputs:**
- output/context-budget.json: Per-segment token counts, utilization %, headroom, alert level, recommendations
- output/context-budget-\<timestamp\>.json: Versioned prior snapshot

**Dependencies:**
- StrategicCompactor: Triggered at warn and critical alert levels
- RelevancePruner: Triggered at emergency alert level

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Uses character-based heuristic (÷3.8 for prose, ÷3.5 for JSON); conservative bias — cannot claim byte-exact token counts
- If a source segment is missing, treats as 0 tokens with a logged warning
- Overflow classified as emergency halt regardless of other thresholds
- Tool schemas are often the hidden cost: 8 Salesforce tools can consume 12–15K tokens silently

**Summary:** ContextProfiler is a deterministic accounting agent that measures context window pressure without invoking an LLM (except optionally for narration via Haiku). It surfaces the silent context tax of tool schemas and conversation history, and recommends targeted compaction or pruning before context pressure causes failures.

---

## RelevancePruner

**Skill Name:** RelevancePruner

**Purpose:** Scores candidate context chunks against the current task query by combining semantic similarity, recency, and source authority, then greedily packs the highest-scoring survivors into a token budget — typically producing 20–50% smaller prompts.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Composite relevance scoring: (semantic_similarity × 0.6) + (recency_weight × 0.2) + (source_authority × 0.2)
- Semantic similarity via cosine distance of text-embedding-3-small embeddings
- Recency decay: exponential with 6-month half-life from created_at timestamp
- Source authority defaults: knowledge_base=0.9, faq=0.75, prior_turn=0.65, user_generated=0.3 (all overridable)
- Greedy packing: sort by relevance, protect safety-critical chunks (customer_id, ticket_id, commitment_made patterns), fill budget sequentially
- Full drop log for threshold calibration: every dropped chunk logged with score and reason

**Owned Responsibilities:**
- Context pool filtering to highest-value slice before reasoning
- Safety-critical chunk protection regardless of relevance score

**Inputs:**
  Mandatory:
    - input/candidate-chunks.json: Context chunks with metadata (source, created_at, content)
    - input/task-query.md: Current task or question to score against
    - input/pruning-config.json: threshold, max_tokens, weights, protected_patterns

**Outputs:**
- output/pruned-context.json: Kept chunks ordered by relevance score
- output/dropped-chunks-log.json: Dropped chunks with scores and reasons
- output/pruning-summary.json: Aggregate stats — chunks kept/dropped, tokens before/after

**Dependencies:**
- None (upstream of StrategicCompactor — pruning removes chunks; compaction summarizes them)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Protected chunks immune to threshold dropping; if protected chunks alone exceed budget, sets budget_exceeded_by_protection: true and includes them anyway
- Never mutates chunk content — selection and rejection only
- Threshold calibration requires monitoring dropped-chunks-log.json over multiple sessions

**Summary:** RelevancePruner filters large candidate-context pools (KB articles, CRM notes, prior turns) to the highest-value slice before reasoning. It scores by semantic similarity, recency, and source authority, protects safety-critical chunks, and greedily packs within budget. All dropped chunks are logged for threshold calibration.

---

## RollingSummarizer

**Skill Name:** RollingSummarizer

**Purpose:** Maintains a bounded, predictable context size across long-running sessions by folding newly accumulated turns into a compact rolling summary on a regular cadence — every ≥10 turns or ≥3K new tokens — preserving all actionable state while aggressively discarding exploratory chatter.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Cadence trigger: turns_since_last_summary ≥10 OR token_count_of_new_turns >3K
- Haiku default; escalates to Sonnet on legal_language, formal_commitment, regulatory_compliance, or dispute_escalation content
- Folding logic: identifies new facts, updates/appends existing sections, deduplicates — never discards verbatim commitments
- Six-section rolling summary: ## Session Context, ## Customer Profile, ## Issue Summary, ## Actions Taken, ## Pending Items, ## Commitments Made
- Token budget enforcement (max 800 tokens default): compresses Session Context first, then Issue Summary — never Commitments Made or Customer Profile
- Context replacement: removes raw accumulated turns and inserts updated summary in their place

**Owned Responsibilities:**
- Cadence-based conversation history compaction
- Commitment and key-ID preservation across compaction cycles

**Inputs:**
  Mandatory:
    - input/recent-turns.md: New conversation turns since last summary
    - input/prior-summary.md: Prior rolling summary or seed
    - input/summarizer-config.json: Cadence thresholds, max_summary_tokens, escalation triggers

**Outputs:**
- Updated rolling-summary.md block (replaces raw accumulated turns in context)

**Dependencies:**
- StrategicCompactor: Optional — for pressure-based compaction between cadence cycles
- MemoryPersistence: Optional — for cross-session state continuity

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Escalation to Sonnet required for formal commitments and legal language; escalation_reason logged
- commitment_text never compressed — preserved verbatim regardless of budget pressure
- Max summary token budget strictly enforced; truncation logged to persistence-log.json

**Summary:** RollingSummarizer proactively folds conversation history into a compact rolling digest on a schedule (Haiku by default, Sonnet for legal/formal commitments). It preserves IDs, amounts, and commitments verbatim while aggressively compressing exploratory context. Context replacement removes old raw turns and inserts the updated summary in their place.

---

## StrategicCompactor

**Skill Name:** StrategicCompactor

**Purpose:** Transforms long, stale conversation history into a compact, structured digest that preserves all actionable state — IDs, decisions, constraints, open threads — while aggressively discarding exploratory chatter and superseded attempts, reclaiming 40–70% of history tokens.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Turn classification: ANCHOR (verbatim preserve), LIVE (summarize, keep intent), STALE (collapse into count), DISCARD (drop entirely)
- Six-section digest: Task State, Decisions Made, Open Threads, Key IDs & References, Constraints, Discarded Material
- Collapse-exploration-loops rule: discard intermediate steps, keep final result + pivot decision
- Greedy compaction calibrated by ContextProfiler alert level: warn → ~50–60% reduction; critical → ~65–75% reduction
- Audit trail: retained-anchor-manifest.json records every kept item with its classification reason
- Quality checklist before output: anchors preserved, open threads retained, constraints verbatim, tokens saved 40–80%

**Owned Responsibilities:**
- Pressure-triggered history compaction
- ANCHOR-class item preservation with zero paraphrase
- Audit trail of all retained and discarded content

**Inputs:**
  Mandatory:
    - full-session.md: Conversation history to compact
    - keep-anchors.json: Values that MUST be preserved verbatim (IDs, amounts, commitments)
    - context-profiler-alert.json: Utilization % and alert level from ContextProfiler

**Outputs:**
- output/compacted-context.md: Structured six-section digest
- output/retained-anchor-manifest.json: Per-item audit with classification and preservation reason
- output/token-delta.json: Pre/post token counts, reduction %, quality assessment tier

**Dependencies:**
- ContextProfiler: Provides alert level and utilization % as trigger and calibration signal

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- No ANCHOR-classified turn may be paraphrased beyond recognition
- Monetary amounts must not be rounded; status must not be invented
- Distinct decisions kept separate — no merging of unrelated decisions
- All IDs preserved verbatim; no abbreviation permitted

**Summary:** StrategicCompactor is a lossy-but-aware history digest that collapses stale context while preserving all load-bearing state. It classifies turns into ANCHOR/LIVE/STALE/DISCARD, produces a six-section digest with an audit trail, and calibrates reduction aggressiveness to the ContextProfiler alert level (warn ~50–60%, critical ~65–75%).

---

## IterativeRetrieval

**Skill Name:** IterativeRetrieval

**Purpose:** Retrieves only the minimum context needed to answer a question by loading the smallest relevant slice first and fetching additional chunks only when a reasoning gap is detected — typically cutting input tokens 5–10× versus full-context loading.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Task decomposition into retrieval dimensions: entities, intent, domain, constraints, unresolved conditions
- Initial retrieval: top-3 most relevant chunks from document index
- Confidence scoring after each round (0.0–1.0): halts at ≥0.85, max 5 rounds, or 12K token budget exhausted
- Gap-detection heuristics: explicit uncertainty markers, implicit dead-ends, customer-service-specific triggers (e.g. policy lookups, order state transitions)
- Targeted follow-up retrieval based on detected gap type
- Auditable trace: per-round queries, chunks retrieved, confidence scores, gap-detection reasoning

**Owned Responsibilities:**
- Minimum-context knowledge retrieval
- Confidence-gated iterative fetch loop

**Inputs:**
  Mandatory:
    - task-spec.md: Task or question to answer
    - document-index.json: Vector-store or keyword index over knowledge base
    - retrieval-config.json: Confidence threshold, max rounds, token budget, domain heuristics

**Outputs:**
- output/grounded-answer.md: Answer with inline citations to source chunks
- output/retrieval-trace.json: Per-round audit — query, chunks, confidence, gap detected
- output/coverage-report.json: Final confidence score, rounds used, budget consumed

**Dependencies:**
- Document index quality (external): Weak embeddings force more rounds and may exhaust budget

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Latency: each additional round adds a network trip to the vector store
- Non-decomposable questions (requiring synthesis across all documents) require full-context loading — not appropriate for iterative retrieval
- Stop criteria (confidence threshold, max rounds) are per-task-type and require calibration

**Summary:** IterativeRetrieval exploits the fact that most queries need only a small fraction of available documents. It retrieves top-3 chunks, scores confidence, detects gaps, and fetches targeted slices on demand. A heuristic-based gap-detection engine drives the loop, halting as soon as confidence reaches 0.85 or budget exhausts. Produces an auditable per-round trace.

---

## MemoryPersistence

**Skill Name:** MemoryPersistence

**Purpose:** Saves session state at session end and rehydrates a capped context block at session start — eliminating cold-start re-explanation and preserving decision continuity across sessions without reintroducing context bloat.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- MODE 1 SAVE: Serializes session state into structured JSON (Haiku default; escalates to Sonnet for complex multi-threaded sessions with >3 open threads or interdependencies)
- MODE 2 REHYDRATE: Loads prior state, validates staleness (fresh <24h, potentially_stale 24–168h, stale >168h), caps to 6,000 chars in priority order: commitments > open_decisions > active_task > constraints > context_notes
- PII scrubbing: strips auth tokens, passwords, credit card numbers before persistence
- Versioned snapshots: prior sessions archived to session-history/ for auditing
- Staleness warnings surfaced on rehydration when state is >24h old

**Owned Responsibilities:**
- Cross-session state serialization and rehydration
- PII-safe persistence with cap enforcement
- Session history archive

**Inputs:**
  Mandatory (SAVE):
    - Session-end conversation context
  Mandatory (REHYDRATE):
    - .claude/memory/\<agent_id\>/session-state.json: Prior persisted state
    - rehydration-config.json: Cap size, staleness thresholds, priority order

**Outputs:**
  SAVE:
    - .claude/memory/\<agent_id\>/session-state.json: Current session state
    - .claude/memory/\<agent_id\>/session-history/: Versioned prior sessions
  REHYDRATE:
    - rehydration-block.md: Injected as first system message — capped state block

**Dependencies:**
- StrategicCompactor: Optional complement in multi-session workflows for in-session compaction

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Escalation to Sonnet on: >3 open threads, >2 interdependencies, state_complexity="high", or commitment deadline <12h
- PII must be explicitly scrubbed before persistence; truncation at cap is logged to persistence-log.json
- Staleness warning required on rehydration when state is >24h old; stale state (>168h) flagged prominently

**Summary:** MemoryPersistence bridges sessions by extracting actionable state (commitments, open decisions, IDs, constraints) and reinjecting a capped block at session start. Complex multi-threaded sessions escalate from Haiku to Sonnet. The rehydration block is the first system message, preserving decision context without the full prior conversation.

---

## EvalHarness (Optimization Layer)

**Skill Name:** EvalHarness (Optimization Layer)

**Purpose:** Runs structured evaluation passes over agent output artifacts in checkpoint or continuous modes, catches failures and regressions before downstream propagation, and gates pipeline progression using grader suites and optional adversarial Opus red-team.

**Phase:** 05-Simplified-AI-Operations

**Note:** This is a distinct skill from the validate-phase EvalHarness (`eval-harness/`). This optimization-layer version (`EvalHarness/`) operates within running agent pipelines as a quality gate — not as a sprint-level evaluation framework. Both exist independently and serve different purposes.

**Capabilities:**
- Checkpoint mode: full grader suite + adversarial Opus red-team on safety-critical outputs
- Continuous mode: lightweight regex/heuristic graders every N turns for drift detection
- Weighted pass@k scoring across grader suites with critical grader override
- Adversarial triggering when stakes are high: customer-facing, financial commitments, PII, enterprise tier
- Failure routing upstream with structured fix instructions
- Loop detection: halts infinite rework cycles when failure persists beyond retry threshold

**Owned Responsibilities:**
- Quality gate between agent output and downstream consumption
- Defect propagation prevention via structured failure routing
- Adversarial safety evaluation for high-stakes outputs

**Inputs:**
  Mandatory:
    - artifact: File path or inline artifact to evaluate
    - acceptance_criteria: JSON grader suite definition
    - eval_config: Mode (checkpoint/continuous), thresholds, adversarial flags

**Outputs:**
- eval-results.json: Per-grader scores and PASS/FAIL verdict
- gate-attestation.md: Pipeline progression authorization
- adversarial-findings.json: Adversarial findings (if adversarial mode enabled)
- failure-analysis.json: Structured fix instructions (on FAIL)

**Dependencies:**
- Upstream agent re-invocation on FAIL (loop with fix instructions)

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Checkpoint mode: ~12K tokens (full suite with adversarial); Continuous mode: ~800 tokens (regex only)
- pass@k cost multiplies both generation and grader cost — reserve for high-stakes artifacts
- Critical graders override weighted average: a single critical grader FAIL yields overall FAIL
- Adversarial reserved for customer-facing financial commitments and regulated data

**Summary:** EvalHarness (Optimization Layer) is the quality gate between agent output and downstream consumption, using Sonnet for graders and Opus for adversarial red-team. It prevents defect propagation by re-routing failures upstream with structured fix instructions. Supports checkpoint (end-of-phase) and continuous (drift-detection) modes.

---

## PatternExtractor

**Skill Name:** PatternExtractor

**Purpose:** Mines session transcripts and artifacts for recurring decision patterns, tool call sequences, and reasoning chains, scores confidence, clusters into candidate skills, and queues high-confidence patterns for human promotion review.

**Phase:** 05-Simplified-AI-Operations

**Capabilities:**
- Five pattern types extracted: tool_sequence, reasoning_chain, phrasing, decision_heuristic, artifact
- Confidence scoring: min(1.0, (occurrences − 1) × 0.25 + consistency_score × 0.5)
- Anti-pattern detection: patterns correlated with quality-failure sessions flagged regardless of confidence
- Candidate skill clustering: related patterns grouped by Jaccard ≥0.4 step overlap
- Overlap check against existing skill library: >60% step overlap → suggest enhance vs. new
- SKILL-\<id\>-candidate.md stub generation: trigger, instructions, examples, caveats

**Owned Responsibilities:**
- Tacit knowledge harvesting from sessions
- Candidate skill stub generation for human review
- Anti-pattern flagging from failure-correlated patterns

**Inputs:**
  Mandatory:
    - input/session-transcript.md: Session transcript to mine
    - input/session-artifacts.json: Artifacts produced (git diff format)
    - input/existing-skill-library.json: Current skill library for overlap detection

**Outputs:**
- output/pattern-catalogue.json: All extracted patterns with scores and type classifications
- output/SKILL-\<pattern_id\>-candidate.md: One stub per promotable pattern (≥0.50 confidence)
- output/promotion-queue.json: Ready (≥0.75) and needs-more-evidence (0.50–0.74) patterns
- output/extraction-report.json: Summary statistics and anti-pattern flags

**Dependencies:**
- Human reviewer: Final promotion gate — no pattern is auto-promoted to a live skill

**Project Types:**
⚠️ MISSING — field not declared in skill source

**Constraints:**
- Confidence ≥0.75 queues as ready; 0.50–0.74 as needs-more-evidence; <0.50 stored only
- Single-session bias cap: ≥0.75 confidence requires evidence from at least 2 sessions
- Anti-patterns flagged for explicit human override — never auto-suppressed
- No automatic promotion; human review is mandatory for all candidate skills

**Summary:** PatternExtractor harvests tacit knowledge from sessions — tool sequences, phrasing, heuristics — and packages them into reviewable skill candidate stubs. Confidence scoring surfaces patterns needing more evidence vs. ready for promotion. Anti-pattern detection flags patterns correlated with quality failures. All promotion requires explicit human review.

---

# Catalog Quality Report

## SkillGenerator

**Skill Name:** SkillGenerator

**Purpose:** Materializes unresolved SkillFlow recommendations into actual skill files. Consumes `recommendation_report.md` produced by SkillFlow and creates or patches `.claude/` skill files — generating new `SKILL.md` and `README.md` for Candidate New Skills, and inserting enhancements into existing skill files — then updates `skill_catalog.md` to keep the catalog in sync after every change. Rejected skills are written to `skillflow_skip.md` so prompt files can gate execution without being modified.

**Phase:** Post-SkillFlow (pre-Phase-02 execution)

**Capabilities:**
- Recommendation extraction from recommendation_report.md (Skill Enhancements and Candidate New Skills)
- User-gated recommendation review with per-item accept/reject control
- Assumptions review per accepted item before any generation begins
- New SKILL.md generation from confirmed assumptions and SkillFlow evidence chain
- New README.md generation alongside every new skill
- Precision enhancement patching into existing SKILL.md at confirmed placement location
- README.md update for enhanced skills
- skill_catalog.md entry addition for new skills
- skill_catalog.md entry update for enhanced skills
- skillflow_skip.md maintenance for rejected skills
- skill_generation_report.md production as a run audit log

**Owned Responsibilities:**
- Candidate New Skill file creation (.claude/<skill-name>/SKILL.md and README.md)
- Skill Enhancement application to existing skill files
- Skill catalog synchronization after every creation or enhancement
- Execution skip list management via skillflow_skip.md

**Inputs:**
  Mandatory:
    - recommendation_report.md: Produced by SkillFlow. Must contain Skill Enhancements and/or Candidate New Skills.
    - skill_catalog.md: Current skill catalog. Must be present and valid before catalog updates are made.
  Optional:
    - recommendation_summary.md: Used for cross-reference when report content is ambiguous.
    - skillflow_skip.md (prior run): Loaded to avoid overwriting existing skip decisions.

**Outputs:**
- .claude/<skill-name>/SKILL.md: New skill definition file (new skills only)
- .claude/<skill-name>/README.md: New or updated README for the skill
- skill_catalog.md: Updated with new entries or modified existing entries
- skillflow_skip.md: Updated with names of skills the user chose to skip
- skill_generation_report.md: Audit log of the run — created, modified, skipped, errors

**Dependencies:**
- SkillFlow: Produces recommendation_report.md — required upstream input
- skill-catalog-generator: Produces skill_catalog.md — required before catalog updates can be made

**Project Types:**
- All project types that use the SkillFlow planning framework

**Constraints:**
- No file is written without explicit user confirmation at the Phase 6 final review gate
- No content is generated without confirmed assumptions from the user at Phase 3
- skillflow_skip.md is only written with explicit user permission
- Does not create or modify prompt files — original prompt files are never touched
- skill_catalog.md must be present and valid; this skill does not generate the catalog from scratch

**Summary:** Executes the unresolved recommendations from SkillFlow by creating new skill files, applying enhancements to existing ones, keeping the catalog in sync, and maintaining the execution skip list — all with user confirmation gates before any file is written.

---

## Generation Summary
  Total skills discovered: 67
  Total entries generated: 67
  Entries with all fields complete: 23
  Entries with flagged fields: 44
  Unreadable skill files: 0

  Skills added in Version 2 (15 new):
    SkillFlow — was present on disk but missing from Version 1 catalog
    BudgetGovernor, ContextProfiler, EvalHarness (Optimization Layer), IterativeRetrieval,
    MemoryPersistence, ModelRouter, PatternExtractor, PromptSlimmer, RegexLLMRouter,
    RelevancePruner, RollingSummarizer, SemanticCache, StrategicCompactor, ToolSurfaceAuditor
    — 14 optimization-layer skills added

  Note on EvalHarness duplication:
    Two distinct EvalHarness skills exist and are intentionally kept as separate entries:
    (1) EvalHarness — validate-phase skill at .claude/eval-harness/; provides shared LLM-as-Judge rubric for sprint validation agents
    (2) EvalHarness (Optimization Layer) — optimization-layer skill at .claude/eval-harness/; quality gates agent pipeline outputs with grader suites and adversarial red-team

## Validation Results
  V-CAT-01 (one entry per skill): PASS — 66 skills discovered, 66 entries generated, no skill omitted
  V-CAT-02 (all fields present): FLAGS — 44 entries have Project Types flagged as MISSING (see Flagged Entries below)
  V-CAT-03 (no duplicate names): PASS — all 66 Skill Names are unique; EvalHarness and EvalHarness (Optimization Layer) are distinct entries by design
  V-CAT-04 (valid dependencies): PASS — all dependency references resolve to skills present in the inventory; external model dependencies (e.g. claude-opus-4-7 in PromptSlimmer) are noted as external, not catalog skills
  V-CAT-05 (no unsupported assumptions): PASS — all field values traced to source skill file content; no assumptions introduced
  V-CAT-06 (missing fields flagged): confirmed — all 44 missing Project Types fields carry the ⚠️ MISSING flag with reason
  V-CAT-07 (catalog_metadata.md version matches skill_catalog.md): FLAG — catalog_metadata.md still carries Version 1; update catalog_metadata.md to Version 2 to restore alignment

## Flagged Entries
  AssumptionTracker | Project Types | field not declared in skill source
  BudgetGovernor | Project Types | field not declared in skill source
  code-extraction | Project Types | field not declared in skill source
  Conductor | Project Types | field not declared in skill source
  ContextFabric | Project Types | field not declared in skill source
  ContextProfiler | Project Types | field not declared in skill source
  DecisionLedger | Project Types | field not declared in skill source
  design-setup | Project Types | field not declared in skill source
  doc-extraction | Project Types | field not declared in skill source
  EvalHarness (Optimization Layer) | Project Types | field not declared in skill source
  ExperienceStudio | Project Types | field not declared in skill source
  ExperimentOps | Constraints (Status: Proposed) | noted as proposed — stakeholder alignment required before production use
  Guardian | Project Types | field not declared in skill source
  InsightOps | Project Types | field not declared in skill source
  IterativeRetrieval | Project Types | field not declared in skill source
  KnowledgeMesh | Project Types | field not declared in skill source
  knowledge-review | Project Types | field not declared in skill source
  meeting-extraction | Project Types | field not declared in skill source
  MemoryPersistence | Project Types | field not declared in skill source
  ModelRouter | Project Types | field not declared in skill source
  ParityChecker | Project Types | field not declared in skill source
  PatternExtractor | Project Types | field not declared in skill source
  PortfolioPrioritizer | Constraints (Status: Proposed) | noted as proposed — scoring model requires stakeholder alignment
  program-charter | Project Types | field not declared in skill source
  PromptSlimmer | Project Types | field not declared in skill source
  RedTeamX | Project Types | field not declared in skill source (AI-native with AI-facing components stated; Project Types as a named field is absent)
  RegexLLMRouter | Project Types | field not declared in skill source
  ReleaseIntel | Project Types | field not declared in skill source
  RelevancePruner | Project Types | field not declared in skill source
  requirements-elicitation-charter | Project Types | field not declared in skill source
  ResearchCopilot | Project Types | field not declared in skill source
  ReviewPilot | Project Types | field not declared in skill source (Python/FastAPI and TypeScript/React stated in content; no explicit Project Types field)
  RollingSummarizer | Project Types | field not declared in skill source
  RolloutAdvisor | Project Types | field not declared in skill source
  RunbookSynth | Project Types | field not declared in skill source
  ScenarioPlanner | Project Types | field not declared in skill source
  SecretShield | Project Types | field not declared in skill source
  SemanticCache | Project Types | field not declared in skill source
  SimLab | Project Types | field not declared in skill source
  SkillFlow | Project Types | field not declared in skill source
  spec-api | Project Types | field not declared in skill source
  spec-design | Project Types | field not declared in skill source
  spec-generation | Project Types | field not declared in skill source
  spec-knowledge | Project Types | field not declared in skill source
  spec-uiux | Project Types | field not declared in skill source
  SpecFlow | Project Types | field not declared in skill source
  SpecImpactAnalyzer | Project Types | field not declared in skill source
  StrategicCompactor | Project Types | field not declared in skill source
  ToolSurfaceAuditor | Project Types | field not declared in skill source
  TraceGraph | Project Types | field not declared in skill source
  ValueModeler | Project Types | field not declared in skill source

## Unreadable Files
  None

## Version 1 Limitations Disclosure
  - Targeted single-entry catalog refresh is not supported. All regenerations are full regenerations.
  - The skill does not automatically detect whether a skill file change is material. That judgment belongs to the user or the invoking system.
  - Continuous catalog monitoring is not supported. The catalog must be manually refreshed when changes occur.
  - Skill creation, skill modification, skill execution, and skill versioning are out of scope.
  - These limitations are tracked for resolution in future versions.
