# Data Readiness

> **Execution Gate:** Before executing any prompt in this file, read `skillflow_skip.md`.
> If the skill name for that prompt appears in `skillflow_skip.md`, skip it and log: `Skipped: <skill-name>`

---

## Output Policy — STRICT

The only content you may present inline in the chat is:

1. **Pre-generation summary** — 3–5 bullet points presented before the NEXT gate.
2. **Post-generation report** — A concise list of what was created or updated, presented after artifact generation.
3. **Phase completion summary** — At the end of each multi-phase skill, a maximum of 8 bullet points summarizing what was done across all phases. Nothing more.
4. **Blocker notice** — If a required input file is missing or a DESIGN BLOCKER is unresolved, state what is needed and stop.
5. **Confirmation** - After generation, wait for CONFIRM before proceeding to the next prompt.

Do NOT display any other content inline — no section content, no checklists, no intermediate findings, no context summaries, no per-step or per-domain output. All reading, analysis, and assessment runs internally before the pre-generation summary.

---

Execute the prompts in this file sequentially, in the order they appear.

For each prompt:

Execute the prompt exactly as written.

Wait for the user to reply NEXT before generating artifacts.

After generation, wait for CONFIRM before proceeding to the next prompt.

Do not skip, reorder, merge, or modify prompts.

After the final prompt has been executed, display:

Data Readiness Complete

---

> **Confirmation Block — not a prompt. Execute this silently before Prompt 1 runs.**

### Check Block A: `artifacts/openspec.yaml` and `artifacts/sprint-capacity.yaml`

Silently check whether both files exist:
- `artifacts/openspec.yaml`
- `artifacts/sprint-capacity.yaml`

**If both exist:** proceed directly to Prompt 1.

**If either is missing**, for each missing file ask the user:

> "`<file-name>` is needed before execution of `context-fabric`. Do you want it to be generated from existing information?"

- **If yes:** run `.claude/artifacts-generation/create-openspec.md`. That skill generates whichever of the two files are absent — do not re-ask per file, one invocation covers both. Once generation is complete, present the generated file(s) inline and ask:
  > "Please review the generated content. Would you like to add or update any information before we continue?"
  Wait for the user to respond. Apply any changes they request. Then ask:
  > "Confirm to proceed to Prompt 1."
  Wait for confirmation before continuing.

- **If no:** ask the user to provide the missing file(s), then wait. Do not proceed to Prompt 1 until both files are present.

---

## Prompt 1

Run the `context-fabric` skill.

### Inputs
- Skill definition: `.claude/context-fabric/SKILL.md`
- Authoritative requirement source:
  - `artifacts/openspec.yaml`
- Supporting context:
  - `specs/knowledge.md`
  - `specs/design.md`
  - `specs/ui-ux.md`
  - `specs/database.md`
  - `specs/api.md`
- Existing context snapshot (if present):
  - `artifacts/context.yaml`
- Prior sprint manifest (if present):
  - `artifacts/ai-manifest.json`
- Enterprise API documentation, schema files, or integration specifications (if provided)
- Change signals, incident logs, or drift reports (if provided)

### Execution
Read `artifacts/openspec.yaml`, `specs/knowledge.md`, `specs/design.md`, `specs/ui-ux.md`, `specs/database.md`, and `specs/api.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Capability Inventory
- Phase 2: Change Detection
- Phase 3: Requirement-to-Capability Mapping
- Phase 4: Gap Report
- Phase 5: Context Snapshot

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Scope boundary
- Last refresh date
- Known changes since the last refresh
- Tribal knowledge entries
- Capability gap handling preference

### Capability Inventory
Build a structured capability inventory by identifying:
- API endpoints, including paths, methods, parameters, and authentication requirements
- Database entities, including tables or collections, key fields, and relationships
- UI components and reusable interface elements described in the specifications
- Business logic modules, rules, and algorithms
- Integration points and external system connections

If `artifacts/ai-manifest.json` is available, include previously generated artifacts as confirmed capabilities.

Append any manually provided tribal knowledge entries as `MANUAL` annotations.

### Change Detection
If `artifacts/context.yaml` exists:
- Compare the current capability inventory against the previous snapshot.
- Classify capability changes as:
  - `ADDED`
  - `REMOVED`
  - `MODIFIED`
- Annotate capabilities affected by incident logs, drift reports, or other change signals if provided.

### Requirement-to-Capability Mapping
For each requirement in `artifacts/openspec.yaml`:
- Identify all dependent capabilities.
- Classify each dependency as:
  - `EXISTS`
  - `EXISTS_MODIFIED`
  - `GAP`
  - `ASSUMED`

Ensure:
- Existing capabilities are marked for reuse rather than regeneration.
- Modified capabilities are flagged for potential update work.
- Capability gaps are explicitly identified.
- Assumed capabilities are surfaced for POD Lead review.

### Gap Analysis
For every identified `GAP`:
- Describe the missing capability.
- Estimate complexity using:
  - `LOW` (≤2 hours)
  - `MEDIUM` (2–8 hours)
  - `HIGH` (>8 hours)
- Recommend adding a corresponding cluster to `task-breakdown.yaml` through SpecFlow.

### Outputs
Generate or update the following artifact:

- `artifacts/context.yaml`

Ensure the artifact contains:
- Version information
- Generation timestamp
- Scope definition
- Capability inventories
- Manual annotations
- Changes since the previous refresh
- Requirement-to-capability mappings
- Source references
- Confidence levels
- Verification dates

Generate a Capability Gap Report containing:
- GAPS requiring new build effort
- EXISTS_MODIFIED capabilities requiring review
- Coverage confidence flags

Infer capabilities only when reasonably supported by the available artifacts. Do not invent undocumented capabilities.

Follow all constraints, processing rules, and execution behavior defined in the `ContextFabric` skill.

Before generating `artifacts/context.yaml`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

---

> **Confirmation Block — not a prompt. Execute this silently before Prompt 2 runs.**

### Check Block B: `references/policy-library.md`

Silently check whether the file exists:
- `references/policy-library.md`

**If it exists:** proceed directly to Prompt 2.

**If it is missing**, ask the user:

> "`references/policy-library.md` is needed before execution of `policy-catalog`. Do you want it to be generated from existing information?"

- **If yes:** run `.claude/artifacts-generation/create-policy-library.md`. That skill reads available specs and generates the file automatically. Once generation is complete, present a summary of the frameworks and policy count included, and ask:
  > "Please review the generated policy library. Would you like to add or update any information before we continue?"
  Wait for the user to respond. Apply any changes they request. Then ask:
  > "Confirm to proceed to Prompt 2."
  Wait for confirmation before continuing.

- **If no:** ask the user to provide `references/policy-library.md`, then wait. Do not proceed to Prompt 2 until the file is present.

---

## Prompt 2

Run the `policy-catalog` skill.

### Inputs
- Skill definition: `.claude/policy-catalog/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `specs/database.md`
  - `specs/api.md`
  - `specs/features.md`
  - `references/policy-library.md`

### Execution
Read `artifacts/openspec.yaml`, `specs/database.md`, `specs/api.md`, `specs/features.md`, and `references/policy-library.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Requirement Scan
- Phase 2: Policy Matching
- Phase 3: Rail Prompt Generation
- Phase 4: Gap Analysis

Use the following predefined assumptions without additional elicitation:
- Jurisdiction: `internal-only`
- Data residency constraints: `none`
- PII present: `no`
- Classification level: `internal`
- Novel policies: `none`

### Requirement Scan
Parse all requirements from `artifacts/openspec.yaml`.

For each requirement, identify compliance-relevant signals, including:
- PII field references
- Authentication and authorization flows
- Data persistence operations
- External data transmission
- Audit logging requirements
- User consent flows
- Data deletion or retention operations

### Policy Matching
For each requirement with compliance signals:
- Match against `references/policy-library.md`.
- Assign one or more policy identifiers using the format:
  - `POL-[FRAMEWORK]-[NNN]`
- Extract the applicable compliance guard prompts.
- Flag unmatched compliance signals as `POLICY_GAP`.

Ensure:
- Requirements with applicable policies are classified as `COMPLIANT`.
- Requirements with unmatched compliance signals are classified as `POLICY_GAP`.
- Requirements with no compliance signals are classified as `EXEMPT`.

### Rail Prompt Generation
For each matched policy:
- Produce concise compliance guard prompts suitable for injection into AI Builder contexts.
- Format each rail as:

`[POL-ID] Guard: [what the builder must enforce] | Check: [what the reviewer must verify]`

Ensure:
- Guard prompts remain concise and actionable.
- Reviewer checks are specific and verifiable.

### Gap Analysis
Identify:
- Requirements containing compliance-relevant signals with no matching policies.
- Requirements exempt from compliance enforcement.
- Requirements fully covered by existing policies.

Flag all `POLICY_GAP` findings as gate blockers requiring POD Lead action before Gate-1.

Follow all constraints, processing rules, and execution behavior defined in the `PolicyCatalog` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/policy-catalogue.yaml`

Ensure the artifact contains:
- Sprint identifier
- Generation date
- Jurisdiction
- Data classification level
- PII presence status
- Requirement-to-policy mappings
- Compliance statuses
- Assigned policies
- Guard prompts
- Reviewer checks
- Policy gap details

Generate policy gap entries containing:
- Requirement identifier
- Compliance signal
- Gap reason
- Required action

Generate per-task compliance rail prompts suitable for injection into `task-breakdown.yaml` during downstream SpecFlow execution.

Before generating `artifacts/policy-catalogue.yaml`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 3

Run the `research-copilot` skill.

### Inputs
- Skill definition: `.claude/research-copilot/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `specs/knowledge.md`
  - `specs/features.md`
- Available evidence sources:
  - Stakeholder meeting notes
  - Elicitation transcripts
- Additional evidence sources (if provided):
  - Analytics exports or usage telemetry
  - Prior sprint validation reports
  - Support ticket exports

### Execution
Read `artifacts/openspec.yaml`, `specs/knowledge.md`, and `specs/features.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Requirement Extraction
- Phase 2: Evidence Indexing
- Phase 3: Cross-Reference
- Phase 4: Contradiction Detection
- Phase 5: AssumptionTracker Escalation

Use the following predefined assumptions without additional elicitation:
- Available evidence sources:
  - Stakeholder meeting notes
  - Elicitation transcripts
- Evidence recency:
  - First-sprint evidence
- Contradiction handling:
  - Flag contradictions as warnings and continue
- Minimum evidence level required to proceed:
  - `PARTIAL`

### Requirement Extraction
Extract all requirements from `artifacts/openspec.yaml`.

Load:
- `specs/knowledge.md` for domain context and prior research signals.
- `specs/features.md` for feature intent and requirement context.

Capture:
- Requirement identifiers
- Requirement descriptions
- Related feature intent

### Evidence Indexing
Process all available evidence sources.

For each evidence item:
- Extract key observations, user statements, and findings.
- Tag each observation with:
  - Source
  - Evidence type (`qualitative` or `quantitative`)
  - Date or recency marker
  - Evidence strength

Build a searchable evidence index for downstream validation.

### Cross-Reference
For each requirement:
- Search the evidence index for supporting or conflicting observations.
- Classify evidence strength as:
  - `CONFIRMED`
  - `PARTIAL`
  - `WEAK`
  - `CONTRADICTED`
  - `NO-EVIDENCE`

Apply the following definitions:
- `CONFIRMED`: Two or more independent evidence sources directly support the requirement.
- `PARTIAL`: One evidence source or indirect support exists.
- `WEAK`: Evidence is anecdotal, single-stakeholder opinion, or otherwise limited.
- `CONTRADICTED`: Available evidence suggests the requirement conflicts with observed behaviour or stakeholder input.
- `NO-EVIDENCE`: No supporting evidence exists.

Record the top two to three evidence citations for each requirement.

Allow requirements classified as `PARTIAL` to proceed without escalation.

### Contradiction Detection
For requirements classified as `CONTRADICTED`:
- Summarize the contradiction.
- Compare the stated requirement against the supporting evidence.
- Classify contradiction severity as:
  - `MINOR`
  - `MAJOR`
  - `BLOCKING`

Treat contradictions as warnings and continue processing.

Generate recommended actions for stakeholder review and resolution.

### AssumptionTracker Escalation
Flag requirements classified as:
- `WEAK`
- `CONTRADICTED`
- `NO-EVIDENCE`

For each flagged requirement:
- Estimate a confidence score between `0` and `1`.
- Recommend a resolution approach, such as:
  - Additional research
  - Stakeholder interview
  - Risk acceptance

Follow all constraints, processing rules, and execution behavior defined in the `ResearchCopilot` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/evidence-map.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Evidence source summary
- Evidence coverage summary
- Requirement evidence breakdowns
- Evidence classifications
- Supporting citations
- Contradiction analyses
- AssumptionTracker recommendations

Generate an AssumptionTracker Escalation List containing:
- Requirement identifier
- Evidence level
- Confidence score
- Recommended action

Generate a Contradiction Summary containing:
- Requirement identifier
- Contradiction severity
- Recommended action

Before generating `artifacts/evidence-map.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 4

Run the `assumption-tracker` skill.

### Inputs
- Skill definition: `.claude/assumption-tracker/SKILL.md`
- Authoritative inputs:
  - `artifacts/evidence-map.md`
  - `artifacts/openspec.yaml`
  - `specs/knowledge.md`
- Prior assumption history (if available):
  - `references/assumption-history.yaml`

### Execution
Read `artifacts/evidence-map.md`, `artifacts/openspec.yaml`, and `specs/knowledge.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Assumption Inventory
- Phase 2: Confidence Scoring
- Phase 3: HITL Blocker Classification
- Phase 4: Resolution Tracking
- Phase 5: Escalation to DecisionLedger

Use the following predefined assumptions without additional elicitation:
- Confidence threshold:
  - `0.4`
- Resolution deadline:
  - `2 hours before Gate-1`
- Prior sprint assumption history:
  - `none`
- Risk posture:
  - `balanced`

### Assumption Inventory
Extract and consolidate assumptions from:
- Explicit assumptions in `artifacts/openspec.yaml`
- Weak-evidence escalations from `artifacts/evidence-map.md`
- Domain-level assumptions identified in `specs/knowledge.md`

Identify assumptions originating from:
- Requirements tagged with assumption indicators.
- Requirements classified as:
  - `WEAK`
  - `CONTRADICTED`
  - `NO-EVIDENCE`

Deduplicate assumptions appearing across multiple sources and merge them into a single tracked entry.

Capture:
- Assumption description
- Source artifact(s)
- Affected requirement identifiers
- Related domain context

### Confidence Scoring
For each assumption, compute a confidence score using the heuristics defined in the skill.

Apply:
- Base score:
  - `0.5`

Apply the following scoring modifiers:

| Factor | Score Modifier |
|----------|----------------|
| Evidence strength: CONFIRMED | +0.4 |
| Evidence strength: PARTIAL | +0.2 |
| Evidence strength: WEAK | +0.0 |
| Evidence strength: NO-EVIDENCE | -0.2 |
| Evidence strength: CONTRADICTED | -0.4 |
| Prior sprint: resolved successfully | +0.2 |
| Prior sprint: unresolved / wrong | -0.2 |
| Dependency on external system/team | -0.1 |
| POD Lead domain expertise available | +0.1 |

Clamp all confidence scores to the range:
- `0.0–1.0`

Document the factors contributing to each score.

### HITL Blocker Classification
Classify assumptions according to:
- Confidence threshold:
  - `0.4`
- Risk posture:
  - `balanced`

Apply the following rules:
- Score < 0.4 → `HITL_BLOCKER`
- Score between 0.4 and 0.6 → `WARNING`
- Score ≥ 0.6 → `TRACKED`

Treat all first-sprint HITL blockers as requiring manual POD Lead review regardless of score.

Identify:
- Gate blockers
- Non-blocking warnings
- Tracked assumptions requiring monitoring

### Resolution Tracking
For each `HITL_BLOCKER`, recommend one of:
- `VALIDATE`
- `ACCEPT_RISK`
- `DEFER`
- `DESCOPE`

Specify:
- Recommended resolution approach
- Evidence required for validation
- Responsible party if identifiable
- Resolution deadline:
  - `2 hours before Gate-1`

Track assumption status as:
- `OPEN`
- `RESOLVED`

### Escalation to DecisionLedger
For assumptions resolved through `ACCEPT_RISK`, generate DecisionLedger payloads containing:
- Decision type:
  - `risk-acceptance`
- Decision statement
- Rationale
- Affected requirements
- Confidence score

Follow all constraints, processing rules, and execution behavior defined in the `AssumptionTracker` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/assumption-log.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Confidence threshold
- Resolution deadline
- Summary statistics
- HITL blocker inventory
- Warning inventory
- Tracked assumptions
- Resolved assumptions

Generate HITL blocker entries containing:
- Assumption identifier
- Description
- Source
- Affected requirements
- Confidence score
- Scoring factors
- Status
- Recommended resolution
- Resolution deadline

Generate warning entries containing:
- Assumption identifier
- Description
- Confidence score
- Affected requirements
- Recommended action

Generate tracked assumption entries containing:
- Assumption identifier
- Description
- Confidence score
- Status

Generate DecisionLedger escalation payloads for all accepted risks.

Before generating `artifacts/assumption-log.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 5

Run the `transform-iq` skill.

### Inputs
- Skill definition: `.claude/transform-iq/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `specs/features.md`
  - `specs/program.md`
  - `references/opportunity-catalogue.yaml`
- Prior operational feedback (if available):
  - `artifacts/feedback-loop-triggers.yaml`

### Execution
Read `artifacts/openspec.yaml`, `specs/features.md`, `specs/program.md`, and `references/opportunity-catalogue.yaml` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Current Backlog Scan
- Phase 2: Signal Ingestion
- Phase 3: Rescoring
- Phase 4: Candidate Surfacing
- Phase 5: Value Density Summary

Use the following predefined assumptions without additional elicitation:
- Sprint strategic theme: `reduce invoice processing time`
- Strategic weights: balanced across all dimensions
- Candidate threshold: `7`
- First sprint: `yes`

### Current Backlog Scan
Load `references/opportunity-catalogue.yaml` and `specs/features.md`.

Identify:
- Opportunity backlog items already in sprint scope.
- Opportunity backlog items not currently in scope.
- Existing mappings between requirements and opportunity catalogue entries.

Capture:
- Backlog references
- Prior scores
- Scope status

### Signal Ingestion
If `artifacts/feedback-loop-triggers.yaml` is available:
- Extract operational signals from prior sprints.
- Identify recurring user pain points.
- Identify repeated defect categories.
- Identify process bottlenecks.
- Map signals to backlog items addressing the same root causes.

If `artifacts/feedback-loop-triggers.yaml` is not available:
- Proceed using first-sprint assumptions.
- Document that scoring is approximation-based.

### Rescoring
For each backlog item, compute a composite score using the scoring method defined in the skill.

Apply:
- Balanced strategic weights across all dimensions.
- First-sprint assumptions without calibration against prior actuals.

Document that scores are directional approximations intended to support prioritization.

### Candidate Surfacing
Identify backlog items that:
- Are not currently in sprint scope.
- Meet or exceed the candidate threshold score of `7`.

For each candidate:
- Calculate effort-to-value ratio.
- Rank candidates by value density in descending order.

Identify the highest-value opportunities suitable for one-week delivery.

### Value Density Summary
Generate a business-facing summary highlighting:
- Top candidate opportunities.
- Value density rankings.
- One-line rationale for each recommendation.
- Supporting evidence where available.

Follow all constraints, processing rules, and execution behavior defined in the `TransformIQ` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/opportunity-backlog-rescored.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Sprint strategic theme
- Scoring weights applied
- Current sprint items already in scope
- Candidate additions above threshold
- Value density calculations
- Value density rankings
- Top 5 quick wins
- Descored items and rationale

Generate Current Sprint Items entries containing:
- Requirement identifier
- Backlog reference
- Prior score
- New score
- Score delta
- Calibration notes

Generate Candidate Addition entries containing:
- Opportunity identifier
- Title
- Composite score
- Estimated effort
- Value density ratio
- Supporting evidence

Generate a Value Density Summary containing:
- Top 5 ranked opportunities
- One-line rationale for each recommendation

Generate an Items Descored This Sprint section containing:
- Opportunity identifier
- Prior score
- New score
- Reason for score reduction

Before generating `artifacts/opportunity-backlog-rescored.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 6

Run the `spec-flow` skill.

### Inputs
- Skill definition: `.claude/spec-flow/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/context.yaml`
  - `artifacts/policy-catalogue.yaml`
  - `specs/spec.md`
  - `specs/tasks.md`
  - `specs/design.md`
  - `specs/api.md`
  - `specs/database.md`
  - `specs/ui-ux.md`
- Prior sprint artifacts (if available):
  - `artifacts/ai-manifest.json`

### Execution
Read `artifacts/openspec.yaml`, `artifacts/context.yaml`, `artifacts/policy-catalogue.yaml`, `specs/spec.md`, `specs/tasks.md`, `specs/design.md`, `specs/api.md`, `specs/database.md`, and `specs/ui-ux.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Requirement Inventory
- Phase 2: Cluster Decomposition
- Phase 3: Dependency Graph
- Phase 4: Parallel Work Plan
- Phase 5: Provenance Injection
- Phase 6: Manifest Update

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Iteration mode
- Builder count
- Cluster granularity
- Any NFRs lacking measurable acceptance criteria

### Requirement Inventory
Parse all requirements from `artifacts/openspec.yaml`.

Cross-reference against:
- `specs/spec.md`
- `specs/tasks.md`

Classify each requirement as:
- `Functional (FR)`
- `Non-Functional (NFR)`
- `Integration (IR)`
- `Data (DR)`

Confirm scope alignment and identify any mismatches between the sprint specification and task inventory.

### Cluster Decomposition
For each requirement group:
- Identify logical module boundaries.
- Group requirements into bounded generation clusters ensuring:
  - No cluster depends on unsatisfied external dependencies.
  - Each cluster can be generated by one AI Builder in under half a day.
  - Each cluster has a clear and bounded output artifact.

For each cluster:
- Assign a cluster identifier using the format `CLU-[NNN]`.
- Define output artifacts.
- Map the required context, including relevant specifications, schema definitions, and API contracts.

### Dependency Graph
Identify dependencies between clusters.

Produce a directed dependency graph indicating cluster sequencing requirements.

Determine:
- Dependency relationships.
- The critical path.
- The longest dependency chain across the sprint.

### Parallel Work Plan
Group clusters into execution waves based on dependency constraints.

Define:
- Wave 0 clusters with no dependencies.
- Subsequent execution waves.
- Builder assignments that balance workload across waves.

Estimate effort for each cluster and execution wave.

### Provenance Injection
For every generated source artifact, ensure provenance metadata is defined containing:
- Sprint identifier
- Requirement identifier(s)
- Cluster identifier
- Generation date
- `human_reviewed: false`

Apply the provenance format defined in the skill.

### Manifest Update
Generate or update the AI artifact manifest.

Append all generated artifacts with:
- File references
- Cluster identifiers
- Requirement traceability identifiers
- Human review status
- Generation timestamps

Follow all constraints, processing rules, and execution behavior defined in the `SpecFlow` skill.

### Outputs
Generate or update the following artifacts:

- `artifacts/task-breakdown.yaml`
- `artifacts/ai-manifest.json`
- `artifacts/parallel-work-plan.md`

Ensure `artifacts/task-breakdown.yaml` contains:
- Sprint identifier
- Generation date
- Cluster definitions
- Requirement mappings
- Cluster types
- Output artifacts
- Dependency definitions
- Wave assignments
- Builder assignments
- Estimated effort
- Policy rails
- Cluster status

Ensure `artifacts/ai-manifest.json` contains:
- Sprint identifier
- Generation timestamp
- Artifact references
- Cluster identifiers
- Requirement identifiers
- Human review status
- Provenance status
- Generation timestamps

Ensure `artifacts/parallel-work-plan.md` contains:
- Sprint identifier
- Wave-by-wave execution plan
- Builder allocations
- Cluster assignments
- Estimated effort by wave
- Critical path summary

Generate dependency outputs containing:
- Cluster relationships
- Critical path analysis
- Parallel execution opportunities

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 7

Run the `trace-graph` skill.

### Inputs
- Skill definition: `.claude/trace-graph/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/ai-manifest.json`
  - `specs/spec.md`
  - `specs/tasks.md`
- Additional inputs (if available):
  - `tests/*.feature`
  - `artifacts/deploy-manifest.yaml`

### Execution
Read `artifacts/openspec.yaml`, `artifacts/ai-manifest.json`, `specs/spec.md`, and `specs/tasks.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Requirement Inventory
- Phase 2: Artifact Inventory
- Phase 3: Graph Construction
- Phase 4: Gap Detection
- Phase 5: Gate Attestation

Use the following predefined assumptions without additional elicitation:
- Gate context: `Gate-1`
- Orphan policy: `warn`

### Requirement Inventory
Extract all requirement identifiers from `artifacts/openspec.yaml`.

Cross-reference against:
- `specs/spec.md`

Build a requirement inventory containing:
- Requirement identifier
- Description
- Requirement type
- Status

Confirm identifier consistency across artifacts and identify any mismatches.

### Artifact Inventory
Parse:
- `artifacts/ai-manifest.json`

If available, also parse:
- `tests/*.feature`
- `artifacts/deploy-manifest.yaml`

Extract:
- Artifact entries and requirement mappings
- Cluster identifiers
- Test scenario identifiers and `@REQ-XXX` annotations
- Deployment entries

Build a complete artifact inventory for traceability analysis.

### Graph Construction
Build a directed traceability graph for each requirement following the structure defined in the skill:

```
REQ-ID
  └─► CLU-ID
        └─► Artifact
              └─► Test Scenario
                    └─► Deployment Entry
```

Generate traceability relationships linking:
- Requirements
- Clusters
- Generated artifacts
- Test scenarios
- Deployment records

### Gap Detection
Identify and classify:

- `UNTRACED REQUIREMENT`
  - Requirement exists in `artifacts/openspec.yaml` but has no artifact mapping.

- `ORPHANED ARTIFACT`
  - Artifact exists in `artifacts/ai-manifest.json` without a requirement mapping.

- `UNTESTED REQUIREMENT`
  - Requirement has artifact mappings but no corresponding test scenario.

- `BROKEN LINK`
  - Requirement references artifacts that do not exist in the manifest.

- `MISSING PROVENANCE HEADER`
  - Manifest artifacts lacking the required SpecPod provenance metadata.

Apply the following classifications:
- Untraced requirements: `CRITICAL`
- Orphaned artifacts: `WARNING`
- Untested requirements: `WARNING`
- Broken links: `ERROR`
- Missing provenance headers: `WARNING`

Classify orphaned artifacts as warnings.

### Gate Attestation
Perform traceability validation for `Gate-1`.

Verify that:
- All requirements have artifact mappings.
- Gate-1 traceability conditions are satisfied.

Determine:
- PASS or FAIL status.
- Blocker count.
- Readiness to proceed.
- Reasons preventing progression if applicable.

Follow all constraints, processing rules, and execution behavior defined in the `TraceGraph` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/traceability-report.md`

Ensure the artifact contains:
- Sprint identifier
- Gate context
- Generation timestamp
- Coverage summary
- Gap report
- Full traceability graph
- Gate attestation

Generate Coverage Summary entries containing:
- Total requirements
- Fully traced requirements
- Partially traced requirements
- Untraced requirements

Generate Gap Report sections containing:
- CRITICAL findings
- WARNING findings
- ERROR findings
- Recommended actions

Generate Full Traceability Graph entries containing:
- Requirement identifiers
- Cluster identifiers
- Artifact mappings
- Test mappings
- Deployment mappings

Generate Gate Attestation containing:
- Gate name
- PASS or FAIL status
- Blocker count
- Ready to proceed determination
- Supporting rationale

Before generating `artifacts/traceability-report.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 8

Run the `spec-impact-analyzer` skill.

### Inputs
- Skill definition: `.claude/spec-impact-analyzer/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/openspec-proposed.yaml` or the provided inline specification diff
  - `artifacts/ai-manifest.json`
  - `artifacts/traceability-report.md`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/decision-ledger.md`
  - `specs/spec.md`
- Additional inputs (if available):
  - `tests/*.feature`

### Execution
Read `artifacts/openspec.yaml`, `artifacts/openspec-proposed.yaml` (or the provided inline diff), `artifacts/ai-manifest.json`, `artifacts/traceability-report.md`, `artifacts/task-breakdown.yaml`, `artifacts/decision-ledger.md`, and `specs/spec.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Diff Parsing
- Phase 2: Ripple Tracing
- Phase 3: Effort Estimation
- Phase 4: Risk Classification
- Phase 5: Rework Scope Patch

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Change description
- Sprint days remaining
- Change source
- Sprint risk posture

### Diff Parsing
If `artifacts/openspec-proposed.yaml` is available:
- Compute the structural diff against `artifacts/openspec.yaml`.

If an inline diff is provided:
- Parse the diff directly.

Identify:
- Changed requirements
- Added requirements
- Removed requirements

Classify each change as:
- `ADDITIVE`
- `MODIFICATIVE`
- `DESTRUCTIVE`
- `NFR CHANGE`

Capture the affected requirement identifiers and change categories.

### Ripple Tracing
For each affected requirement:
- Trace all downstream artifacts using `artifacts/traceability-report.md`.
- Determine whether each affected artifact requires:
  - Regeneration
  - Retesting
  - Redeployment

Expand the analysis to include transitive dependencies.

Identify:
- Dependent clusters affected by the change.
- Critical path impacts.
- Closed HITL gates referenced in `artifacts/decision-ledger.md` that would be invalidated.

Flag any invalidated gate attestations.

### Effort Estimation
Estimate rework effort using the heuristics defined in the skill:

- Code file regeneration:
  - `0.5 hours per file`
- Test scenario regeneration:
  - `0.25 hours per scenario`
- Integration retesting:
  - `1 hour per integration point`
- Gate re-attestation:
  - `0.5 hours per gate`

Calculate:
- Minimum effort estimate
- Expected effort estimate
- Maximum effort estimate using a ±30% variance range

Estimate:
- Available builder capacity remaining
- Capacity headroom

### Risk Classification
Classify the overall impact as one of:
- `IN-SPRINT SAFE`
- `DEFER TO NEXT SPRINT`
- `SCOPE RISK`
- `ESCALATE`

Base the classification on:
- Estimated effort
- Sprint risk tolerance
- Critical path impact
- Closed gate invalidation
- Complexity of required regeneration

Provide a rationale supporting the classification.

### Rework Scope Patch
If the change is classified as `IN-SPRINT SAFE` and approval conditions are met:
- Generate a rework scope patch.
- Identify clusters requiring re-queueing.
- Mark affected artifacts as stale.

Update affected artifact statuses accordingly.

Follow all constraints, processing rules, and execution behavior defined in the `SpecImpactAnalyzer` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/impact-analysis.md`

Generate `artifacts/rework-scope-patch.yaml` only when the conditions defined by the skill are satisfied.

Ensure `artifacts/impact-analysis.md` contains:
- Change title
- Sprint identifier
- Days remaining
- Generation timestamp
- Change summary
- Affected artifacts
- HITL gate impact assessment
- Effort estimates
- Capacity analysis
- Risk classification
- Recommendation

Generate Change Summary entries containing:
- Change type
- Changed requirement identifiers
- Change requester

Generate Affected Artifact entries containing:
- Artifact reference
- Cluster identifier
- Impact type
- Estimated effort

Generate HITL Gate Impact entries containing:
- Gate identifier
- Current status
- Invalidation assessment

Generate Effort Estimate entries containing:
- Minimum effort
- Expected effort
- Maximum effort
- Available builder-hours
- Capacity headroom

Generate Recommendation outputs containing:
- Proceed recommendation
- Defer recommendation
- Escalation recommendation
- Supporting rationale

If generated, ensure `artifacts/rework-scope-patch.yaml` contains:
- Sprint identifier
- Change identifier
- Approval metadata
- Re-queue instructions
- Stale artifact listings

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 9

Run the `value-modeler` skill.

### Inputs
- Skill definition: `.claude/value-modeler/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/task-breakdown.yaml`
  - `specs/features.md`
  - `specs/program.md`
  - `references/opportunity-catalogue.yaml`
- Prior value actuals (if available):
  - ValueTracker outputs from previous sprints

### Execution
Read `artifacts/openspec.yaml`, `artifacts/task-breakdown.yaml`, `specs/features.md`, `specs/program.md`, and `references/opportunity-catalogue.yaml` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Requirement Value Classification
- Phase 2: Per-Requirement Value Quantification
- Phase 3: Sprint ROI Calculation
- Phase 4: Low-Value Flagging
- Phase 5: Baseline Record

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Applicable value dimensions
- Baseline metrics
- Builder-hour estimates
- Confidence modifier

### Requirement Value Classification
For each requirement in `artifacts/openspec.yaml`:
- Classify the requirement into one or more value categories:
  - `Direct Value`
  - `Enabling Value`
  - `Quality Value`
  - `Experience Value`
  - `Technical Value`

Use:
- `specs/features.md`
- `specs/program.md`
- `references/opportunity-catalogue.yaml`

to determine the most appropriate value classification.

Document the rationale for each classification.

### Per-Requirement Value Quantification
Quantify value using the methods defined in the skill.

For Direct Value requirements:
- Estimate annual value using the prescribed time-saved calculation.

For Enabling Value requirements:
- Estimate annual value using opportunity capture assumptions derived from the opportunity catalogue.

For Quality Value requirements:
- Estimate annual value using error reduction calculations.

For Experience and Technical Value requirements:
- Apply the qualitative proxy method defined by the skill when quantitative data is unavailable.

Calculate for each requirement:
- Annual value estimate
- Builder-hour investment
- Value per builder hour

### Sprint ROI Calculation
Calculate sprint-level investment and value using the formulas defined in the skill.

Determine:
- Total builder investment
- Estimated annual value
- Sprint ROI percentage
- Payback period

Use:
- A default loaded hourly rate of `$150/hour` unless an alternative rate is available from the provided artifacts.

Apply confidence ranges based on the confidence modifier and document the assumptions used.

### Low-Value Flagging
Identify requirements that should be flagged as:
- `DEFER_CANDIDATE`
- `LOW_CONFIDENCE_VALUE`

Apply the thresholds defined in the skill.

Document:
- The rationale for each flag.
- The value-to-investment relationship supporting the recommendation.

### Baseline Record
Generate a baseline value record suitable for future comparison during the Operate phase.

Capture:
- Forecast values locked at planning time.
- Assumptions used.
- Confidence levels.
- Inputs required for future ValueTracker actual comparisons.

Follow all constraints, processing rules, and execution behavior defined in the `ValueModeler` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/roi-brief.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Confidence level
- Sprint ROI summary
- Per-requirement value forecasts
- Defer candidates
- Assumptions and confidence notes
- Value baseline record

Generate Sprint ROI Summary entries containing:
- Builder investment
- Estimated annual value
- Annual value range
- Sprint ROI percentage
- Payback period

Generate Per-Requirement Value Forecast entries containing:
- Requirement identifier
- Description
- Value category
- Annual value estimate
- Builder-hour estimate
- Value per builder hour
- Applicable flags

Generate Defer Candidate entries containing:
- Requirement identifier
- Deferral rationale
- Value-to-investment comparison

Generate Assumptions and Confidence Notes containing:
- Baseline assumptions
- Hourly rates used
- Confidence adjustments
- Calibration limitations

Generate a Value Baseline Record suitable for future ValueTracker comparison.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 10

Run the `portfolio-prioritizer` skill.

### Inputs
- Skill definition: `.claude/portfolio-prioritizer/SKILL.md`
- Authoritative inputs:
  - `artifacts/roi-brief.md`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/traceability-report.md`
  - `artifacts/opportunity-backlog-rescored.md`
  - `specs/features.md`
  - `specs/program.md`

### Execution
Read `artifacts/roi-brief.md`, `artifacts/task-breakdown.yaml`, `artifacts/traceability-report.md`, `artifacts/opportunity-backlog-rescored.md`, `specs/features.md`, and `specs/program.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Candidate Inventory
- Phase 2: Composite Scoring
- Phase 3: Must-Ship Override
- Phase 4: Dependency Cluster Locking
- Phase 5: Capacity Cut Line
- Phase 6: Defer Rationale Generation

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Sprint capacity
- Strategic weights
- Capacity buffer
- Must-ship items
- Manual overrides

### Phase 1 — Candidate Inventory
- Load all in-scope requirements from `artifacts/task-breakdown.yaml`.
- Load all TransformIQ candidate additions from `artifacts/opportunity-backlog-rescored.md`.
- Combine them into a unified candidate list containing:
  - REQ-ID or OPP-ID
  - Description
  - Estimated effort
  - ROI values
  - Dependency information

### Phase 2 — Composite Scoring
For each candidate, compute the composite score using the formula defined in the skill.

Use:
- Value scores from `artifacts/roi-brief.md`
- Urgency signals from available artifacts
- Strategic alignment from `specs/program.md`
- Dependency enablement information from `artifacts/traceability-report.md`
- Risk considerations from the available planning artifacts

Normalise all scoring dimensions and document the rationale supporting each candidate's score.

Generate for each candidate:
- Composite score
- Value contribution
- Urgency contribution
- Strategic alignment contribution
- Dependency contribution
- Risk contribution

### Phase 3 — Must-Ship Override
Identify any must-ship requirements.

Apply must-ship overrides exactly as defined by the skill:
- Insert must-ship items at the top of the ranked backlog regardless of score.
- Mark them with `OVERRIDE: MUST-SHIP`.

Apply any approved manual priority overrides and document their rationale.

### Phase 4 — Dependency Cluster Locking
Using dependency information from `artifacts/traceability-report.md`:

- Identify dependency clusters.
- Determine which requirements or opportunities must move together.
- Score dependency clusters as a unit using the rules defined in the skill.
- Apply dependency locking logic before final ranking.

Document:
- Cluster identifiers
- Included items
- Dependency impacts
- Cluster-level decisions

### Phase 5 — Capacity Cut Line
Calculate sprint capacity using the rules defined in the skill.

Determine:
- Total available builder-hours
- Reserved buffer
- Usable sprint capacity
- Allocated capacity

Sort the ranked backlog by score and apply the capacity cut line.

Classify each item as:
- `PROCEED`
- `DEFERRED`
- `BORDERLINE`

Flag any items within 10% of the cut line as requiring POD Lead judgment.

### Phase 6 — Defer Rationale Generation
For each deferred item, generate a defer rationale using the categories defined in the skill.

Classify defer reasons as:
- Low value
- Capacity constraints
- Dependency constraints

Generate concise rationale statements suitable for reuse in future sprint planning.

Follow all constraints, processing rules, and execution behavior defined in the `PortfolioPrioritizer` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/sprint-scope-ranked.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Capacity summary
- Ranked PROCEED scope
- Capacity cut line
- Deferred items
- Borderline items
- Deferred dependency clusters

Generate Capacity Summary entries containing:
- Available builder-hours
- Reserved buffer hours
- Usable capacity
- Allocated hours
- Utilisation percentage

Generate Sprint Scope — PROCEED entries containing:
- Rank
- REQ-ID
- Description
- Composite score
- Estimated hours
- Cumulative hours
- Applicable flags

Generate Deferred entries containing:
- REQ-ID
- Description
- Composite score
- Defer rationale
- Recommended next-sprint priority

Generate Borderline entries containing:
- REQ-ID
- Description
- Composite score
- Estimated hours
- Reason requiring POD Lead review

Generate Dependency Cluster entries containing:
- Cluster identifier
- Deferred items
- Reason for deferral

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 11

Run the `scenario-planner` skill.

### Inputs
- Skill definition: `.claude/scenario-planner/SKILL.md`
- Authoritative inputs:
  - `artifacts/roi-brief.md`
  - `artifacts/sprint-scope-ranked.md`
  - `artifacts/assumption-log.md`
  - `artifacts/task-breakdown.yaml`
  - `specs/program.md`

### Execution
Read `artifacts/roi-brief.md`, `artifacts/sprint-scope-ranked.md`, `artifacts/assumption-log.md`, `artifacts/task-breakdown.yaml`, and `specs/program.md` as the authoritative sources of context.

Execute the skill exactly as defined, including:
- Phase 1: Assumption Sensitivity Analysis
- Phase 2: 3-Scenario ROI Matrix
- Phase 3: Minimum Viable Scope
- Phase 4: Variance Flagging

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Best-case scenario parameters
- Expected-case assumptions
- Worst-case scenario parameters
- Scope options selected for stress-testing
- Minimum acceptable sprint ROI threshold

### Phase 1 — Assumption Sensitivity Analysis
Using `artifacts/assumption-log.md`:

- Identify all `HITL_BLOCKERS` and `WARNINGS`.
- Determine the potential ROI impact if each assumption fails.
- Estimate:
  - Value at risk
  - Potential rework effort
  - Confidence impact

Calculate sensitivity scores using the method defined in the skill.

Rank assumptions by sensitivity and identify the top contributors to sprint outcome uncertainty.

Generate:
- Top sensitivity assumptions
- Confidence levels
- Value exposure estimates
- Sensitivity rankings

### Phase 2 — 3-Scenario ROI Matrix
For each selected scope option:

Generate:
- Best-case scenario analysis
- Expected-case scenario analysis
- Worst-case scenario analysis

Calculate the scenario outputs using the formulas defined in the skill.

For each scenario determine:
- Delivery effort
- Investment required
- Value realised
- ROI percentage
- Payback period

Generate verdicts indicating whether:
- Expected ROI exceeds the minimum threshold
- Worst-case ROI remains acceptable
- The scope option remains viable.

### Phase 3 — Minimum Viable Scope
Determine the minimum viable scope by:

- Starting with must-ship requirements.
- Adding ranked items incrementally until the minimum acceptable expected ROI threshold is achieved.
- Verifying whether the resulting scope maintains positive ROI under the worst-case scenario.

Document:
- Included REQ-IDs
- Value contribution
- Effort required
- Selection rationale

Escalate if even the minimum viable scope produces unacceptable worst-case outcomes.

### Phase 4 — Variance Flagging
For each scope item:

Calculate variance ratios using the method defined in the skill.

Classify each item as:
- `HIGH_VARIANCE`
- `MEDIUM_VARIANCE`
- `LOW_VARIANCE`

Identify items with the greatest influence on sprint outcomes.

Generate recommendations for POD Lead attention where applicable.

Follow all constraints, processing rules, and execution behavior defined in the `ScenarioPlanner` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/scenario-matrix.md`

Ensure the artifact contains:
- Sprint identifier
- Generation timestamp
- Scenario parameters
- ROI scenario matrices
- Minimum viable scope analysis
- Top assumption sensitivities
- High-variance scope items
- Final recommendation

Generate Scenario Parameter entries containing:
- Best-case assumptions
- Expected-case assumptions
- Worst-case assumptions
- Probability estimates

Generate ROI Scenario Matrix entries containing:
- Scope option
- Scenario name
- Investment
- Annual value
- ROI percentage
- Payback period
- Verdict

Generate Minimum Viable Scope entries containing:
- Included REQ-IDs
- Expected ROI contribution
- Worst-case viability assessment
- Selection rationale

Generate Top Assumption Sensitivity entries containing:
- Rank
- Assumption identifier
- Confidence score
- Value at risk
- Sensitivity score

Generate High-Variance Scope Item entries containing:
- REQ-ID
- Description
- Best-case value
- Worst-case value
- Variance ratio
- Recommendation

Generate a Final Recommendation containing:
- Recommended scope option
- Supporting rationale
- Key risks requiring POD Lead attention

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 12

Run the `decision-ledger` skill.

### Inputs
- Skill definition: `.claude/decision-ledger/SKILL.md`
- Authoritative inputs (if available):
  - `artifacts/decision-ledger.md`
  - `artifacts/openspec.yaml`
  - `artifacts/impact-analysis.md`
  - `artifacts/sprint-scope-ranked.md`

### Execution
Execute the skill exactly as defined.

Determine the appropriate operating mode:
- Log Entry Mode
- Query Mode
- Sprint Summary Mode

Use the available artifacts as the authoritative sources of context.

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

### Log Entry Mode
For each decision to be recorded:

Determine and document:
- Decision type
- Decision text
- Rationale
- Approver
- Affected requirement identifiers
- Superseded decision reference, if applicable

For HITL gate clearances, additionally determine:
- Gate identifier
- Conditions or caveats

Generate a unique decision identifier using the format:
- `DEC-[SPRINT-ID]-[NNN]`

Generate timestamps using:
- `YYYY-MM-DDTHH:MM:SSZ`

If a superseded decision is identified:
- Mark the prior decision as superseded by the newly generated decision identifier.
- Preserve append-only integrity by creating a new entry rather than modifying historical content.

Append all new entries to the ledger exactly as defined by the skill.

Generate confirmation messages for each decision recorded.

### Query Mode
If a query request is detected:

Support queries by:
- Requirement identifier
- Date range
- Approver
- Decision type
- Full ledger

Return query results sorted and formatted according to the rules defined in the skill.

### Sprint Summary Mode
When requested:

Generate a business-ready sprint decision summary.

Group decisions by category, including:
- Gate clearances
- Scope decisions
- Spec changes
- Risk acceptances
- Other applicable decision categories

Follow all constraints, processing rules, and execution behavior defined in the `DecisionLedger` skill.

### Outputs
Generate or update the following artifact:

- `artifacts/decision-ledger.md`

Generate the following artifact only when applicable:

- `artifacts/decision-summary.md`

Ensure `artifacts/decision-ledger.md` contains entries including:
- Decision identifier
- Decision type
- Timestamp
- Decision statement
- Rationale
- Approver
- Affected requirements
- Gate information when applicable
- Conditions when applicable
- Status
- Supersedes reference

Generate Decision Summary entries containing:
- Gate clearances
- Scope decisions
- Deferred requirements
- Descoped requirements
- Approved specification changes
- Risk acceptances
- References to the full ledger

Maintain append-only behavior throughout execution:
- Never modify or delete existing entries.
- Corrections and updates must be represented as new entries.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt.

---

## Prompt 13

Run the `conductor` skill.

### Inputs
- Skill definition: `.claude/conductor/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/ai-manifest.json`
  - `artifacts/policy-catalogue.yaml`
  - `artifacts/traceability-report.md`
  - `artifacts/sprint-scope-ranked.md`
  - `artifacts/assumption-log.md`
  - `artifacts/decision-ledger.md`
  - `specs/tasks.md`
  - `specs/program.md`
- Additional inputs (if available):
  - `artifacts/context.yaml`
  - `artifacts/impact-analysis.md`
  - `artifacts/rework-scope-patch.yaml`
- Reference files:
  - `references/capability-matrix.md`
  - `references/gate-protocol.md`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Execute the following phases in order:
- Phase 1: Pre-flight Validation
- Phase 2: Task-to-Builder Mapping
- Phase 3: Sprint Board Generation
- Phase 4: Dispatch Log
- Phase 5: Completion Forecast

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Active builder availability
- Capacity overrides
- Gate 1 status
- Manual priority overrides

### Phase 1 — Pre-flight Validation
Validate that all REQUIRED artifacts are present.

Verify the existence of:
- `artifacts/openspec.yaml`
- `artifacts/task-breakdown.yaml`
- `artifacts/ai-manifest.json`
- `artifacts/policy-catalogue.yaml`
- `artifacts/traceability-report.md`
- `artifacts/sprint-scope-ranked.md`
- `artifacts/assumption-log.md`
- `artifacts/decision-ledger.md`
- `specs/tasks.md`
- `specs/program.md`

If any REQUIRED artifacts are missing:
- List every missing artifact.
- Halt execution.
- Do not proceed to dispatch.

Confirm that Gate 1 has been cleared.

If Gate 1 is not cleared:
- Generate a pending gate notice.
- Halt execution.

Inspect `artifacts/assumption-log.md` for OPEN `HITL_BLOCKERS`.

If blockers exist:
- List all blockers.
- Halt execution.
- Do not dispatch any tasks.

Cross-reference `artifacts/sprint-scope-ranked.md` against `artifacts/task-breakdown.yaml`.

Validate that:
- Only items classified as `PROCEED` are eligible for dispatch.
- Deferred items are excluded from execution.

### Phase 2 — Task-to-Builder Mapping
For each eligible task in `artifacts/task-breakdown.yaml`:

Determine:
- Task identifier
- Task description
- Assigned builder
- Accelerator skill
- Dependency status
- Estimated completion timing

Use `references/capability-matrix.md` to:
- Match task types to builder capabilities.
- Select the appropriate accelerator skill.

Resolve all dependency relationships.

Classify tasks as:
- `DISPATCHED`
- `BLOCKED`
- `ESCALATED`

For blocked tasks:
- Identify the blocking dependency.
- Record the waiting condition.

### Phase 3 — Sprint Board Generation
Generate the sprint board using dispatched task information.

Calculate and document:
- Total task count
- Dispatched task count
- Dependency-blocked task count
- HITL-blocked task count
- Deferred task count

Generate Task Board entries containing:
- Task ID
- Description
- Builder assignment
- Accelerator skill
- Status
- Dependency information
- ETA

Generate:
- HITL Gate Queue
- Escalation Queue

### Phase 4 — Dispatch Log
Generate append-only dispatch records.

Create dispatch entries for:
- All dispatched tasks
- All blocked tasks
- All escalated tasks

Generate timestamped entries using the formats defined in the skill.

Dispatch entries must include:
- Timestamp
- Task identifier
- Builder assignment
- Accelerator skill
- Trigger source

Blocked entries must include:
- Timestamp
- Task identifier
- Blocking reason
- Waiting dependency or gate

Escalation entries must include:
- Timestamp
- Task identifier
- Escalation reason
- Required POD Lead action

### Phase 5 — Completion Forecast
Calculate sprint completion forecasts using:
- Remaining task inventory
- Estimated task durations
- Available builder-hours

Determine:
- Builder-hours available
- Builder-hours consumed
- Estimated days remaining
- Forecast completion date

Document the assumptions supporting the forecast.

Apply all escalation rules defined in the skill, including:
- Task failure escalation
- HITL gate delay reminders
- Mid-sprint specification change handling
- Builder capacity exhaustion procedures

Follow all constraints, processing rules, and execution behavior defined in the `Conductor` skill.

### Outputs
Generate or update the following artifacts:
- `artifacts/sprint-board.md`
- `artifacts/dispatch-log.md`

Ensure `artifacts/sprint-board.md` contains:
- Sprint identifier
- Generation date
- Status summary
- Task Board
- HITL Gate Queue
- Escalation Queue
- Completion Forecast

Generate Status Summary entries containing:
- Total tasks
- Dispatched tasks
- Dependency-blocked tasks
- HITL-blocked tasks
- Deferred tasks

Generate Task Board entries containing:
- Task ID
- Description
- Builder assignment
- Accelerator skill
- Status
- Dependency information
- ETA

Generate HITL Gate Queue entries containing:
- Waiting tasks
- Required gate clearances
- Release conditions

Generate Escalation Queue entries containing:
- Task identifiers
- Escalation reasons
- POD Lead actions required

Generate Completion Forecast entries containing:
- Available builder-hours
- Consumed builder-hours
- Remaining builder-hours
- Estimated completion timeline

Ensure `artifacts/dispatch-log.md` remains append-only and contains:
- DISPATCHED events
- BLOCKED events
- ESCALATED events

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

**Data Readiness Complete**
