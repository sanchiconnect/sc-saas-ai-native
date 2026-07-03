---
name: skill-flow
description: "This skill runs after Phase 01 (Init) is complete. It consumes the Phase 01 artifact set and the skill catalog to produce a structured recommendation plan for Phase 02 and beyond."
---

# SkillFlow Engine

## Skill Metadata

```
name: skill-flow
version: 1.0.0
type: planning
layer: pre-execution
scope: project-wide
```

---

## Execution Context

This skill runs after Phase 01 (Init) is complete. It consumes the Phase 01 artifact set and the skill catalog to produce a structured recommendation plan for Phase 02 and beyond.

| | |
|---|---|
| **Runs after** | Phase 01 (Init) — all six Phase 01 artifacts must be present |
| **Consumes** | `skill_catalog.md` (from skill-catalog-generator) + `program.md`, `knowledge.md`, `design.md`, `database.md`, `api.md`, `ui-ux.md` |
| **Produces** | `recommendation_report.md` · `recommendation_summary.md` |
| **Purpose** | Determine which Phase 02+ skills to execute, skip, or enhance — before execution begins |

---

## Framework Flow

```
Phase 01 — Init
  └─ program-charter · spec-knowledge · spec-design · spec-database · spec-api · spec-uiux

skill-catalog-generator
  └─ produces skill_catalog.md

skill-flow-engine          ← this skill
  └─ produces recommendation_report.md · recommendation_summary.md

skill-generator            ← runs immediately after skill-flow
  └─ materializes new skills and enhancements from recommendation_report.md
  └─ writes skillflow_skip.md (gates all Phase 02+ prompts)

Phase 02+ — Execute recommended skills  ← skillflow_skip.md gate active from here
```

---

## Objective

Analyze a project's Phase 01 initialization artifacts and produce a traceable, evidence-backed recommendation plan that determines which skills from Phase 02 onward should be executed, enhanced, skipped, or extended:

- Which skills from Phase 02 onward must be executed (Required)
- Which skills from Phase 02 onward are beneficial but not mandatory (Recommended)
- Which skills from Phase 02 onward are low-impact (Optional)
- Which skills from Phase 02 onward are irrelevant or counterproductive (Not Recommended)
- Which existing skills should be enhanced and how (Skill Enhancements)
- Where each recommendation belongs in the execution lifecycle (Phase Assignment)
- How every recommendation maps to project artifacts and requirements (Traceability)

The engine does not create skills, modify skills, execute skills, version recommendations, or restructure the framework autonomously. These are deferred to future versions.

---

## Version Scope

### In Scope — Version 1

- Skill Recommendation
- Skill Enhancement Recommendation
- Phase Assignment
- Skill Relevance Analysis
- Recommendation Reporting
- Recommendation Traceability

### Out of Scope — Version 1

- Automatic skill creation
- Automatic skill modification
- Continuous re-planning
- Recommendation versioning
- Autonomous framework restructuring

---

## Inputs

### Mandatory Inputs

All mandatory inputs are required before the engine may proceed. If any is absent, the engine must halt and output the appropriate error message. No partial execution is permitted.

#### skill_catalog.md

The authoritative machine-readable catalog produced by skill-catalog-generator.md. Contains structured metadata for every framework skill including capabilities, owned responsibilities, dependencies, constraints, project types, and phase information.

The Recommendation Engine relies on this catalog for all recommendation decisions. Recommendation generation must not proceed without a valid catalog. If skill_catalog.md is absent, inaccessible, or marked invalid, halt and instruct the user to run skill-catalog-generator.md before retrying.

#### program.md

The program charter produced by the program-charter skill during Phase 01. Contains the program name, problem statement, goals, scope, success metrics, system domains, architecture decisions, NFRs, pod structure, design highlights, timeline, and stakeholder information.

#### knowledge.md

The domain knowledge specification produced by the spec-knowledge skill during Phase 01. Contains domain entities, business rules, state machines, workflows, constraints, compliance requirements, and the domain glossary.

#### design.md

The technical design specification produced by the spec-design skill during Phase 01. Contains the technology stack, frameworks, libraries, infrastructure, architectural patterns, coding standards, and observability strategy.

#### database.md

The database schema specification produced by the spec-database skill during Phase 01. Contains tables or collections, column definitions, data types, constraints, indexes, relationships, and migration strategy.

#### api.md

The backend API specification produced by the spec-api skill during Phase 01. Contains endpoint definitions, request and response schemas, authentication strategy, error contract, rate limiting, and API conventions.

#### ui-ux.md

The UI/UX design specification produced by the spec-uiux skill during Phase 01. Contains design tokens, component library, interaction patterns, motion system, layout system, and accessibility standards.

---

### Optional Inputs

Optional inputs increase recommendation precision and confidence. Their absence does not block execution but must reduce confidence scores for affected recommendations.

#### features.md

The feature requirements list produced during knowledge capture. When provided, used to identify specific feature-level capability gaps and map requirements to skill responsibilities with greater precision.

#### impl.md

The implementation guidance document produced during design setup. When provided, used to refine technology-specific skill recommendations and identify gaps in the technical execution plan.

#### recommendation_report.md (prior run)

A recommendation report produced by a previous run of the Recommendation Engine for this project. When provided, used to identify which recommendations have already been acted upon and avoid recommending skills already included in the execution plan.

#### recommendation_summary.md (prior run)

A recommendation summary produced by a previous run of the Recommendation Engine for this project. When provided, used alongside the prior recommendation report to assess planning continuity.

#### Additional project artifacts

Any other project artifacts produced before or during Phase 01. Examples: architecture decision records, domain model diagrams, meeting notes, prototype documents. When provided, used to validate capability coverage and refine recommendations.

#### Customer documents

Customer-provided documents such as requirements specifications, business requirement documents, process documentation, or compliance documentation. When provided, used to strengthen requirement evidence and increase confidence scores for affected recommendations.

#### Meeting outputs

Notes, transcripts, or summaries from customer or stakeholder meetings. When provided, used to surface implicit requirements and strengthen evidence for recommendations that might otherwise have weaker support from artifact content alone.

Note: catalog_metadata.md (produced by skill-catalog-generator.md alongside skill_catalog.md) is included under additional project artifacts. When provided, it is used to populate catalog traceability fields in both recommendation artifacts. When absent, catalog version and generation date are derived from the skill_catalog.md header if available, or recorded as "Not available."

---

## Outputs

### Primary Artifacts

#### recommendation_report.md

The concise decision-support artifact for technical leads and architects. Contains all recommendations with their type, phase, confidence score, and brief rationale. Designed to be read in under five minutes. Internal traceability evidence, confidence narratives, and capability classification analysis are produced by the engine during analysis but are not printed in the report.

#### recommendation_summary.md

The concise execution planning artifact. Contains only the minimum viable execution plan, critical flags, and phase overview. Significantly shorter than the report. Intended for project leads and execution planning.

---

## Catalog Dependency

All recommendation decisions — skill matching, capability mapping, ownership analysis, dependency resolution, and phase assignment — are made using **skill_catalog.md** content only. The engine must not read raw skill files at any point.

If a skill is not present in the catalog, it cannot be recommended. That absence is treated as a catalog gap, not a trigger to read skill files directly.

**catalog_metadata.md** (optional companion artifact) provides catalog version and generation date for recommendation traceability. When absent, these values are derived from the skill_catalog.md header.

---

## Workflow

The engine executes in the following sequence. Each phase must complete before the next begins. No phase may be skipped.

---

### Phase 0: Input Validation

**Purpose:** Confirm all mandatory inputs are present and meet minimum quality thresholds before any analysis begins.

**Steps:**

1. Confirm skill_catalog.md is present and accessible.
2. Confirm program.md is present and non-empty.
3. Confirm knowledge.md is present and non-empty.
4. Confirm design.md is present and non-empty.
5. Confirm database.md is present and non-empty.
6. Confirm api.md is present and non-empty.
7. Confirm ui-ux.md is present and non-empty.
8. Log presence or absence of each optional input.
9. Record which optional inputs are absent. These absences will reduce confidence scores in subsequent phases.

**Pre-Recommendation Artifact Validation:**

If any mandatory artifact is missing, stop execution and output:

> "Phase 01 initialization artifacts are incomplete. Recommendation analysis requires all Phase 01 specifications."

Do not proceed with partial artifacts. Do not attempt to infer missing artifact content.

**Validation Rules:**

- If skill_catalog.md is absent: halt. Output: "A valid skill_catalog.md is required. Run skill-catalog-generator.md to generate the catalog, then re-run the Recommendation Engine."
- If program.md is absent: halt with the Phase 01 incomplete message above.
- If knowledge.md is absent: halt with the Phase 01 incomplete message above.
- If design.md is absent: halt with the Phase 01 incomplete message above.
- If database.md is absent: halt with the Phase 01 incomplete message above.
- If api.md is absent: halt with the Phase 01 incomplete message above.
- If ui-ux.md is absent: halt with the Phase 01 incomplete message above.
- If multiple Phase 01 artifacts are absent: halt with the Phase 01 incomplete message above, listing all missing artifacts.

**Outputs:** Validated input set. Absent optional inputs log. Quality assessment notes.

---

### Phase 1: Catalog Validation

**Purpose:** Confirm that a valid, consumable skill_catalog.md exists before recommendation analysis begins. The Recommendation Engine does not generate catalogs. Catalog generation and maintenance are exclusively the responsibility of skill-catalog-generator.md.

**Steps:**

1. Confirm skill_catalog.md is present and accessible.
2. Confirm the catalog contains at least one skill entry.
3. Confirm all required catalog fields (Skill Name, Purpose, Phase, Capabilities, Owned Responsibilities, Inputs, Outputs, Dependencies, Project Types, Constraints, Summary) are present in the catalog structure.
4. Confirm the catalog file is readable and not corrupted.
5. Confirm the catalog Validation Status is not marked FAIL. A catalog marked FAIL must not be used for recommendation decisions.

**Validation Failure Behavior:**

If any check fails, halt execution and output:

> "A valid skill_catalog.md is required before recommendations can be generated. Run skill-catalog-generator.md to generate or refresh the catalog, then re-run the Recommendation Engine."

Do not attempt to generate, rebuild, or repair the catalog. That responsibility belongs exclusively to skill-catalog-generator.md.

**Outputs:** Validated catalog reference. Catalog validation status log.

---

### Phase 1.5: Existing Coverage Analysis

**Purpose:** Analyze the Phase 01 artifacts to determine what the project already covers before generating any recommendations. Recommendations must be based on actual artifact content, not on project description alone.

**Steps:**

1. Read knowledge.md in full. Assess:
   - Which domain entities, business rules, and workflows are fully documented
   - Which sections are sparse, incomplete, or missing
   - Whether any entries contain contradictions

2. Read design.md in full. Assess:
   - Which technology stack decisions are resolved
   - Which infrastructure and deployment decisions are resolved
   - Which areas are marked as pending, deferred, or undecided

3. Read database.md in full. Assess:
   - Which entities have complete schema definitions
   - Which tables or collections lack indexes, constraints, or relationship definitions
   - Whether migration strategy is defined

4. Read api.md in full. Assess:
   - Which endpoints are fully defined with request/response schemas
   - Which endpoints lack error handling, authentication, or validation definitions
   - Whether the error contract and pagination conventions are established

5. Read ui-ux.md in full. Assess:
   - Which design tokens, components, and interaction patterns are defined
   - Which areas are stubs or incomplete
   - Whether accessibility standards are specified

6. For each artifact, classify coverage across four states:
   - **Complete:** Section is fully populated and internally consistent
   - **Partial:** Section exists but has gaps, stubs, or unresolved items
   - **Missing Information:** Section exists but critical content is absent
   - **Contradictory:** Section contains entries that conflict with each other or with other artifacts

7. Compile a coverage summary that will be used to drive recommendation decisions in Phase 4.

**Coverage-Driven Recommendation Rule:**

Recommendations generated in Phase 4 must be justified using evidence from this coverage analysis. A skill must not be recommended solely because it is generally useful. Recommendations must be traceable to:

- A specific gap identified in an artifact (missing capability)
- A specific incomplete section (partial coverage)
- A specific contradiction requiring resolution
- A specific project-phase need identified from artifact content

**Outputs:** Artifact coverage map (per artifact: Complete / Partial / Missing / Contradictory sections). Coverage-based recommendation evidence set used in Phase 4.

---

### Phase 2: Project Classification

**Purpose:** Establish the project type, domain, primary capability areas, and success factors before recommendation analysis begins.

**Steps:**

1. Classify the project type (e.g., web application, data science platform, API service, enterprise integration, mobile application, infrastructure tool, analytics system).
2. Identify the primary capability areas the project must deliver.
3. Identify the project's primary success factors — capabilities without which the project cannot reasonably succeed.
4. Identify secondary capabilities — supporting capabilities that enhance but do not define success.
5. Map capability areas to the skill catalog. For each capability area, identify which catalog entries are relevant.
6. Identify capability gaps — capability areas with no matching catalog entry.

**Hallucination Prevention:**

- Classification must be derived from the Phase 01 artifacts only.
- Do not infer capabilities not mentioned or reasonably implied by the artifact content.
- Do not apply generic best-practice assumptions unless explicitly supported by the artifacts.
- When classification is uncertain, record uncertainty and reduce downstream confidence scores.

**Outputs:** Project type. Primary capability areas. Primary success factors. Secondary capabilities. Initial catalog relevance map. Capability gaps list.

---

### Phase 3: Capability & Requirement Extraction

**Purpose:** Extract project requirements, capability needs, constraints, and execution drivers from the Phase 01 artifacts, then map them to catalog skills to identify coverage, gaps, and resolution paths.

**Steps:**

1. Extract explicit requirements from program.md (goals, scope, success metrics, NFRs, timeline constraints, stakeholder requirements, compliance obligations).
2. Extract business requirements from knowledge.md (domain entities, business rules, workflows, state machine constraints, compliance requirements, edge cases).
3. Extract technical requirements from design.md (technology stack choices, infrastructure requirements, architectural patterns, quality attributes, coding standards, security model).
4. Extract data requirements from database.md (entity definitions, schema constraints, migration requirements, data retention rules, compliance data fields, indexing requirements).
5. Extract API requirements from api.md (endpoint specifications, authentication requirements, integration contracts, error handling requirements, rate limiting requirements, versioning strategy).
6. Extract user experience requirements from ui-ux.md (accessibility requirements, interaction patterns, component specifications, layout requirements, design token constraints, internationalization requirements).
7. Create normalized requirement identifiers (R-001, R-002, etc.) for each extracted requirement. Record the source artifact for each identifier. These identifiers are used in all subsequent traceability citations.
8. For each extracted requirement, identify which catalog skills own responsibility for it. Classify coverage:
   - **Fully Covered:** At least one skill fully owns this requirement.
   - **Partially Covered:** At least one skill partially addresses this requirement but gaps remain.
   - **Uncovered:** No catalog skill owns this requirement.

For partially covered requirements, identify the gap and determine whether it should be resolved by a Skill Enhancement or flagged as a candidate new skill need.

For uncovered requirements, apply the Capability Classification Framework to determine the appropriate resolution path.

**Outputs:** Requirement coverage map. Partially covered requirement gaps. Uncovered requirement list. Initial traceability anchors.

---

### Phase 4: Recommendation Generation

**Purpose:** Produce the full set of classified recommendations using catalog evidence and artifact coverage analysis from Phase 1.5.

**Scope Restriction:**

The following skills must never be recommended. They run before Phase 02 begins and are assumed complete by the time recommendation generation runs:

- program-charter
- spec-knowledge
- spec-design
- spec-database
- spec-api
- spec-uiux
- skill-flow (this skill)
- skill-generator

The recommendation scope begins at Phase 02 and later. If any of the above skills appear during catalog evaluation, skip them and do not generate a recommendation entry.

**Completeness Requirement:**

Every skill in `skill_catalog.md` that is not in the exclusion list above **must** appear in exactly one of the four classification buckets: Required, Recommended, Optional, or Not Recommended. A skill that does not fit any of those categories still belongs in Not Recommended with the reason "Not applicable to this project type." Silently omitting a catalog skill from all buckets is a validation failure.

After classifying all skills, perform a completeness check:
1. List every skill from the catalog (excluding the pre-Phase-02 exclusion list above).
2. Confirm each appears in exactly one bucket in the output report.
3. If any skill is missing from all buckets, classify it as Not Recommended and add it before finalizing the report.

**Process:**

For each catalog skill from Phase 02 onward, determine its recommendation classification by evaluating:

1. Does the project type match this skill's Project Types field?
2. Do artifact coverage gaps from Phase 1.5 map to this skill's Owned Responsibilities?
3. Do any primary success factors (derived from artifact content) align with this skill's Capabilities?
4. Are this skill's dependencies satisfied or satisfiable in this project?
5. Do any constraints in the artifacts eliminate or restrict this skill?

**Classification Decision Logic:**

Recommendation decisions must prioritize evidence from the Phase 01 artifacts. Recommendations must not be generated solely because a skill is generally useful.

Priority order for recommendation justification:

1. Missing capabilities identified in Phase 1.5 coverage analysis
2. Incomplete specifications in the Phase 01 artifacts
3. Capability gaps derived from artifact content
4. Project-specific needs evidenced in the artifacts
5. Future project phase requirements identifiable from the artifacts

```
Evaluate skill against Phase 01 artifact content and coverage analysis:

  Artifact gap or missing capability + primary success factor alignment
  → Required

  Partial artifact coverage + secondary capability alignment
  → Recommended

  Low-priority artifact gap + weak project need
  → Optional

  No artifact gap + no requirement alignment + constraints conflict
  → Not Recommended
```

**For each classification decision:**

- Assign a unique Recommendation ID (REC-001, REC-002, etc.) in sequence.
- Record which requirements supported the decision.
- Record which catalog fields supported the decision.
- Record which constraints influenced the decision.
- Assign confidence score per the Confidence Model.
- Write confidence explanation.

**Outputs:** Classified recommendation set. Decision evidence log.

---

### Phase 5: Skill Enhancement Analysis

**Purpose:** Identify specific, actionable improvements to existing skills that address requirement gaps, partial coverage, or project-specific capability needs.

**Process:**

1. Review all partially covered requirements from Phase 3.
2. Review all capability gaps identified in Phase 2 that were classified as Skill Enhancements via the Capability Classification Framework.
3. For each gap or partial coverage, apply the Capability Classification Framework to confirm the correct resolution is a Skill Enhancement and not a candidate new skill.
4. For confirmed Skill Enhancements, produce a complete enhancement recommendation per the Skill Enhancement Requirements definition.

**Quality Rules:**

- Every enhancement must be specific and actionable.
- Do not recommend vague enhancements such as "improve API design" or "add more detail."
- Each enhancement must name the exact existing skill, describe precisely what should be added or changed, explain why it is needed, and cite the source requirement.

**Outputs:** Skill Enhancement recommendation set.

---

### Phase 6: Phase Assignment

**Purpose:** Assign every recommendation to its correct place in the project execution lifecycle.

**Rules:**

1. Phase assignment is derived from the catalog's Phase field for the skill.
2. When the catalog Phase field is ambiguous or absent, phase is inferred from dependency chains — a skill that depends on outputs of another skill cannot precede that skill.
3. Skill Enhancements are assigned to the same phase as the skill they enhance.
4. Every phase assignment must include a written justification citing the catalog Phase field or dependency rationale.
5. No phase assignment may be arbitrary.

**Dependency Validation:**

- Identify all dependency relationships between recommended skills.
- Confirm no recommended skill is placed in a phase before its dependencies are satisfied.
- Flag any circular dependencies as a Risk item.

**Outputs:** Phase-assigned recommendation set. Dependency validation log.

---

### Phase 7: Traceability Matrix Construction

**Purpose:** Produce the complete evidence map linking every recommendation to its supporting project inputs and catalog entries.

**Rules:**

- Every recommendation must have at least one Artifact Evidence citation.
- Every recommendation must have at least one Requirement Evidence citation.
- Every recommendation must have at least one Catalog Evidence citation.
- A recommendation with no requirement evidence must be demoted in confidence and flagged.
- A recommendation with no catalog evidence must be demoted in confidence and flagged.
- A recommendation with no artifact evidence must be demoted in confidence and flagged.

**Format:**

For each recommendation in the traceability matrix:

```
Recommendation ID: [REC-XXX]
Recommendation Name: [name]
  Artifact Evidence: [quote or reference from one or more Phase 01 artifacts; cite artifact name and section]
  Requirement Evidence: [requirement ID(s) and text excerpt; IDs assigned during Phase 3]
  Catalog Evidence: [skill name, field cited, field value excerpt]
  Confidence Impact: [any confidence adjustments from evidence gaps]
```

**Outputs:** Complete traceability matrix.

---

### Phase 8: Report Generation

**Purpose:** Produce the two final artifacts.

**recommendation_report.md generation:** Follow the Report Artifact Definition.

**recommendation_summary.md generation:** Follow the Summary Artifact Definition.

**Validation before output:**

- Confirm internal traceability is complete for all recommendations (not printed in the report).
- Confirm every recommendation has a confidence score.
- Confirm no recommendation is present without a phase assignment.
- Confirm no recommendation is present without a classification.
- Confirm Execution Plan section is present and ordered by phase then dependency sequence.
- Confirm Risks & Gaps section is present.

**Outputs:** recommendation_report.md. recommendation_summary.md.

---

## Capability Classification Framework

When a capability is identified that is not fully owned by an existing skill, the framework must determine whether it should be classified as a Skill Enhancement or a Candidate New Skill Recommendation.

This determination must always be made explicitly. No capability may be left unclassified.

---

### Rule 1: Core Capability Test

Determine whether the capability is a primary success factor of the project.

**Definition of Primary Success Factor:**

A capability is a primary success factor if, without it, the project's core value proposition cannot be delivered. A project may have multiple primary success factors but typically has a small number.

**Examples — App Development Project:**

- Basic analytics → Supporting capability → Not a primary success factor
- Basic reporting → Supporting capability → Not a primary success factor
- Simple recommendation feature → Supporting capability → Not a primary success factor

**Examples — Data Science Project:**

- Model training → Core capability → Primary success factor
- Feature engineering → Core capability → Primary success factor
- Model evaluation → Core capability → Primary success factor
- Explainability → Core capability → Primary success factor

**Decision:**

```
Capability is NOT a primary success factor
→ Lean toward Skill Enhancement
→ Proceed to Rule 2 only if ambiguous
```

---

### Rule 2: Ownership Test

Determine whether an existing skill already owns responsibility for this capability area.

**Examples:**

- Need: API rate limiting → Owned by: API Design → Decision: Skill Enhancement
- Need: Caching strategy → Owned by: Technical Design → Decision: Skill Enhancement
- Need: Authentication flow → Owned by: Security Design → Decision: Skill Enhancement

**Decision:**

```
Existing skill owns responsibility
→ Skill Enhancement

No existing skill owns responsibility
→ Proceed to Rule 3
```

---

### Rule 3: Independence Test

Determine whether the capability represents an independent workflow.

**Independence Criteria:**

- Does it have distinct inputs not shared with any other skill?
- Does it have distinct outputs that form standalone deliverables?
- Can it operate as a standalone project activity?
- Does it have a lifecycle that does not depend on any other skill completing first?

**Decision:**

```
All independence criteria met
→ Candidate New Skill

Any independence criterion not met
→ Skill Enhancement
```

---

### Final Classification Decision Tree

```
Capability Identified
        ↓
Is it a primary success factor?
        ↓
       NO
        ↓
  Skill Enhancement
  ─────────────────────────────────────────────────
        ↓
       YES
        ↓
Does an existing skill own responsibility?
        ↓
       YES
        ↓
  Skill Enhancement
  ─────────────────────────────────────────────────
        ↓
       NO
        ↓
Is it an independent workflow?
        ↓
       YES
        ↓
  Candidate New Skill (flagged; not created in v1)
  ─────────────────────────────────────────────────
        ↓
       NO
        ↓
  Skill Enhancement
```

**Version 1 Behavior for Candidate New Skills:**

In Version 1, Candidate New Skill determinations are flagged in the Risks & Gaps section of recommendation_report.md. They are not created, not executed, and not included in the execution plan. They are documented as gaps requiring future resolution.

---


## Recommendation Structure

Every recommendation is processed using all fields below. Fields are divided into two groups:

**Report Fields** — printed in recommendation_report.md and recommendation_summary.md.
**Internal Fields** — used during engine analysis but not printed in the report.

### Report Fields

```
Recommendation ID
  A unique identifier assigned to this recommendation within the current run.
  Format: REC-001, REC-002, REC-003 (incrementing integers, zero-padded to three digits).
  IDs are assigned sequentially during Phase 4 (Recommendation Generation).
  IDs must remain stable for the duration of the recommendation run.
  IDs appear in recommendation_report.md, recommendation_summary.md,
  and the internal traceability record.

Recommendation Name
  The name of the skill or enhancement being recommended.

Type
  One of: Required | Recommended | Optional | Not Recommended | Skill Enhancement

Phase
  The execution lifecycle phase this recommendation is assigned to.

Confidence
  A numeric score between 0 and 100.

Reason
  Why this recommendation was made. Maximum two short bullet points.
  Each bullet must reference specific project artifact evidence. No vague language.

Impact
  The consequence of including or excluding this recommendation.
  One sentence. Be specific about what breaks or degrades without it.
  For Not Recommended: state the consequence of inclusion rather than exclusion.

Enhancement (Skill Enhancements only)
  Specific description of what to add or change within the existing skill,
  and the exact section or step where it should be placed within that skill.
```

### Internal Fields

Used during engine analysis (Phases 3–7). Not printed in recommendation_report.md.

```
Source Requirements
  List of requirement IDs that this recommendation addresses.
  Format: R-001, R-002, etc.
  Used in internal traceability construction (Phase 7).

Phase Justification
  Why this phase was chosen. Must cite catalog Phase field or dependency rationale.
  Used in phase assignment validation (Phase 6).

Location
  For Skill Enhancements: the specific section or step within the existing skill.
  For all other types: the skill's canonical location or identifier.
  Used in enhancement placement validation.

Inputs Required
  What this recommendation needs to execute.
  Used in dependency resolution (Phase 6).

Outputs Produced
  What this recommendation will produce.
  Used in capability coverage mapping (Phase 3).

Confidence Level
  One of: High (85–100) | Medium (60–84) | Low (0–59)
  Derived from the numeric Confidence score.

Confidence Reason
  A written explanation of why this confidence score was assigned.
  Must reference evidence strength, requirement coverage, and catalog alignment.
  Must not be a generic statement.
  Used internally for confidence validation (V-REC-04).

Decision Basis
  The specific evidence used to make this recommendation.
  Format:
    Artifact Evidence: [citation from one or more Phase 01 artifacts; include artifact name and section]
    Requirement Evidence: [requirement IDs and excerpts; IDs assigned during Phase 3]
    Catalog Evidence: [skill name, field, value]
  Used in internal traceability construction (Phase 7).
```

---

## Skill Enhancement Requirements

Every Skill Enhancement recommendation must contain all of the following fields in addition to the standard Recommendation Structure.

```
Existing Skill
  The canonical name of the skill being enhanced.

Enhancement Description
  A precise description of what should be added to or changed within the existing skill.
  Must be specific enough for a practitioner to implement without ambiguity.
  No vague directives such as "add more detail" or "improve coverage."

Suggested Placement Within Skill
  The exact section, phase, step, or output within the existing skill where
  the enhancement should be introduced.
  Examples:
    "Add as a substep in Phase 3: API Contract Definition"
    "Add a new output artifact: rate-limit-policy.md"
    "Insert validation rule after Step 4 in the Input Validation phase"
```

---

## Confidence Model

### Confidence Levels

| Level  | Score Range | Meaning |
|--------|-------------|---------|
| High   | 85 – 100    | Strong evidence from multiple sources. Low uncertainty. |
| Medium | 60 – 84     | Moderate evidence. Some uncertainty remains. |
| Low    | 0 – 59      | Weak evidence. Significant uncertainty. Recommendation made with caveats. |

### Confidence Scoring Rules

1. Confidence must never be assigned arbitrarily.
2. Every score must be justified in writing in the Confidence Reason field.
3. Confidence scores are derived by evaluating five qualitative factors:

**Evidence Strength**
  How direct, specific, and unambiguous is the evidence from project inputs?
  Direct quotes or explicit requirement statements → strong.
  Inferred needs or vaguely implied requirements → weak.

**Requirement Coverage**
  How many independent requirements support this recommendation?
  Multiple requirements independently pointing to the same skill → strong.
  A single tangential or loosely related requirement → weak.

  Requirements may originate from dedicated requirements documents (if provided as optional
  inputs), or from requirements extracted during Phase 3 from program.md, knowledge.md,
  design.md, database.md, api.md, or ui-ux.md. Requirement Coverage scoring evaluates
  requirements from all of these sources.

**Catalog Alignment**
  How closely does the skill's Owned Responsibilities match the identified need?
  Full alignment on Owned Responsibilities and Project Types → strong.
  Partial match or adjacent responsibilities → moderate.
  No match → basis for Not Recommended, not a low-confidence Required.

**Dependency Certainty**
  Are the dependencies for this recommendation known and satisfiable?
  All dependencies present in the recommendation set → strong.
  Dependencies uncertain or unresolvable → weak.

**Input Completeness**
  How complete are the inputs that inform this recommendation?
  All mandatory Phase 01 artifacts present and all relevant optional inputs provided → strong.
  Mandatory Phase 01 artifacts present but relevant optional inputs absent → moderate.
  Any mandatory Phase 01 artifact absent or insufficient → recommendation must not be generated.

4. After evaluating all five factors together, assign a level:
   - All or most factors strong → High (85–100)
   - Mixed factors, more strong than weak → Medium (60–84)
   - Most factors weak or absent → Low (0–59)

5. The minimum valid confidence score for an included recommendation is 10.
   A score of 0 indicates the recommendation is invalid and must be removed entirely.

6. When multiple factors independently converge on the same conclusion, confidence
   increases. When any critical factor (Requirement Coverage or Catalog Alignment)
   is absent or very weak, confidence must decrease regardless of other factors.

7. Confidence Reason must explain which factors were strong, which were weak,
   and why the score landed at its assigned level. Generic statements such as
   "evidence supports this recommendation" are not acceptable.

---

## Traceability Rules

### Requirements

1. Every recommendation must have a traceability entry.
2. Every traceability entry must cite at minimum one instance of each of:
   - Artifact Evidence
   - Requirement Evidence
   - Catalog Evidence
3. Traceability entries must quote or reference specific text from the source.
   General statements such as "the project needs this" are not valid evidence.
4. Requirement Evidence citations must use the requirement reference identifiers
   assigned during Phase 3 (R-001, R-002, etc.).
5. Artifact Evidence must reference one or more of the Phase 01 artifacts: program.md,
   knowledge.md, design.md, database.md, api.md, or ui-ux.md. The citation must include
   the artifact name and the specific section or content referenced.

### Hallucination Prevention in Traceability

- Do not cite evidence that is not present in the inputs.
- Do not paraphrase inputs in a way that changes their meaning to support a recommendation.
- Do not infer requirements that are not stated or reasonably implied.
- Do not use best-practice assumptions as evidence unless the user explicitly stated
  that best practices apply.

### When Evidence is Weak

When a recommendation cannot be supported by strong evidence:

1. The confidence score must reflect the weakness.
2. The Confidence Reason must state specifically what evidence is missing.
3. The recommendation must be classified as Optional or Not Recommended
   unless the evidence, though weak, points strongly to Required.
4. The recommendation must include an explicit uncertainty statement in the
   Confidence Reason field.

---

## Phase Assignment Framework

### Phase Reference Model

Phase assignment uses a standard execution lifecycle model. The phases below are reference phases. Actual phase names in use within the framework take precedence when the catalog provides them explicitly.

| Phase | Description |
|-------|-------------|
| Discovery | Requirements gathering, domain analysis, feasibility |
| Design | Architecture, technical design, API design, database design |
| Planning | Project planning, risk assessment, resource planning |
| Foundation | Infrastructure setup, environment configuration, scaffolding |
| Development | Implementation of core features and capabilities |
| Integration | Connecting components, third-party integrations |
| Testing | Verification, validation, quality assurance |
| Delivery | Deployment, release, handover |
| Operations | Monitoring, maintenance, ongoing support |

### Assignment Rules

1. The primary assignment source is the skill's Phase field in the catalog.
2. When the catalog Phase field is absent or ambiguous, phase is inferred from:
   - What the skill produces (e.g., a design document implies Design phase)
   - What the skill depends on (e.g., a skill consuming architecture outputs implies post-Design phase)
3. Skill Enhancements inherit the phase of the skill they enhance.
4. No skill may be placed in a phase before its declared dependencies are placed.
5. All phase assignments require written justification.
6. When two valid phase assignments exist, prefer the earlier phase to reduce blocking.

### Dependency Sequencing

```
For each recommended skill:
  1. List declared dependencies from catalog.
  2. Confirm all dependencies are also in the recommendation set or
     already satisfied by existing artifacts.
  3. Assign phase no earlier than the latest dependency's phase.
  4. Flag unsatisfied dependencies as risks.
```

---

## Report Artifact Definition

### recommendation_report.md

recommendation_report.md is a decision-support artifact for technical leads and architects.
It presents all recommendations in a concise, scannable format. Detailed traceability
evidence, confidence narratives, and capability classification analysis are produced
internally by the engine during analysis but are not printed in the report.

Target length: 1,000–2,000 words. Approximately 2–4 pages.

#### Structure

```
# Recommendation Report

Catalog Version: [from catalog_metadata.md, or derived from skill_catalog.md header, or: Not available]
Catalog Generated Date: [from catalog_metadata.md, or derived from skill_catalog.md header, or: Not available]

## Executive Summary
  Three to five sentences summarizing the recommendation plan.
  State: number of Required, Recommended, Optional, Not Recommended skills,
  and Skill Enhancements.
  State the minimum viable execution plan in one sentence.
  State any critical risks or gaps.

## Project Understanding
  Project Type: [classification]
  Domain: [domain]
  Primary Success Factors: [list]
  Secondary Capabilities: [list]
  Optional Inputs Present: [list]
  Optional Inputs Absent: [list with confidence impact noted]

## Phase 01 Coverage Assessment
  [For each mandatory Phase 01 artifact:]

  **Artifact Name:** [artifact filename]
  **Coverage Status:** [Complete | Partial | Missing Information | Contradictory Information]
  **Observations:** [Specific findings — name the sections, entities, or fields that are
                    complete, absent, incomplete, or contradictory.]

  [Repeat for: program.md, knowledge.md, design.md, database.md, api.md, ui-ux.md]

## Catalog Analysis
  Total skills in catalog: [number]
  Skills with strong project match: [number]
  Skills with weak or no project match: [number]
  Capability gaps identified: [number]

## Required Skills
  [For each Required skill, ordered by phase then dependency sequence.
   One entry per skill in the following format:]

  **REC-[ID] | [Skill Name] | Required | Phase: [phase] | Confidence: [score]**
  - [Reason bullet 1 — one sentence citing specific artifact evidence]
  - [Reason bullet 2 — one sentence; omit if one reason fully covers the decision]
  - Impact: [one sentence on the consequence of excluding this skill]

## Recommended Skills
  [Same format as Required Skills. Type label: Recommended.]

## Optional Skills
  [Same format. Type label: Optional.]

## Not Recommended Skills
  [Same format. Impact sentence states the consequence of including rather than excluding.]

## Skill Enhancements
  [For each Skill Enhancement, ordered by phase of the enhanced skill:]

  **REC-[ID] | [Existing Skill] → [Enhancement Name] | Skill Enhancement | Phase: [phase] | Confidence: [score]**
  - [Reason bullet 1 — one sentence]
  - [Reason bullet 2 — one sentence; omit if one reason suffices]
  - Impact: [one sentence]
  - Enhancement: [specific description of what to add or change within the existing skill,
                  and the exact section or step where it should be placed]

## Execution Plan
  [All recommendations ordered by execution phase, then by dependency sequence within
   each phase. Never sorted alphabetically.]

  Phase [A]
  - REC-001 skill-name
  - REC-002 skill-name

  Phase [B]
  - REC-003 skill-name
  - REC-004 existing-skill → enhancement-name

  [Continue for each phase that contains at least one recommendation.]
  [If a dependency ordering issue exists, note it beneath the affected item in one line.]

## Risks & Gaps
  [One line per item. Cover: unresolved capability gaps, unsatisfied dependencies,
   Candidate New Skill gaps, low-confidence Required recommendations, and constraint
   conflicts. If no items exist in a category, state it in one line.]
  - [Item]
  - [Item]
```

---

## Capability Gap Resolution Format

The Capability Gap Resolution Format defines the internal analysis structure for every
identified capability gap. This analysis is produced by the engine during Phases 2 and 5
but is not printed in recommendation_report.md. One entry per identified gap. Candidate
New Skill gaps are summarized in the Risks & Gaps section of the report; Skill Enhancement
gaps are captured in the Skill Enhancements section. Entries for capabilities fully owned
by an existing skill with no gap are not required here — those are handled by the standard
Recommendation Structure.

```yaml
Capability Gap: [Name of the missing capability]

Evidence: [Requirement ID(s) and a brief description of the supporting evidence]

Core Capability Test: [PASS | FAIL]
  Reasoning: [Why this capability is or is not a primary success factor for the project]

Ownership Test: [PASS | FAIL | N/A]
  Reasoning: [Whether an existing skill owns responsibility for this capability.
              Mark N/A only when Core Capability Test is FAIL and the decision
              path does not reach this rule.]

Independence Test: [PASS | FAIL | N/A]
  Reasoning: [Whether this capability has distinct inputs, distinct outputs, and
              can operate as a standalone project activity.
              Mark N/A only when Core Capability Test is FAIL, or when
              Ownership Test is PASS.]

Final Decision: [Skill Enhancement | Candidate New Skill]

Reason: [One to three sentences citing the specific rule outcome that produced
         this decision. Must not be vague.]

Version 1 Note: [Required only when Final Decision is Candidate New Skill.
                 State that creation is deferred and the gap remains open.]
```

Rules for completing entries:
- Tests may be marked N/A only when the decision path in the Classification Decision
  Tree does not reach that rule.
- Every entry must cite at least one Requirement ID as evidence.
- Every Candidate New Skill entry must include a Version 1 Note.
- Reasoning fields must reference specific rule logic, not general statements.

---

## Summary Artifact Definition

### recommendation_summary.md

The summary is the primary execution roadmap for the project. It is the document
a project owner consults first and returns to throughout execution. It must be
self-contained enough that all planning decisions — what to execute, what to skip,
what to enhance, and what phases to run — can be made without opening
recommendation_report.md. The report exists for justification and audit; the
summary exists for decisions.

The summary answers: "What is the minimum set of actions needed to successfully
execute this project?" — not merely: "What recommendations were generated?"

It prioritizes decisions over analysis. No traceability matrix, no capability
classification analysis, no extended confidence narratives. Those belong in the report.

#### Structure

```
# Recommendation Summary

Catalog Version: [from catalog_metadata.md, or derived from skill_catalog.md header, or: Not available]
Catalog Generated Date: [from catalog_metadata.md, or derived from skill_catalog.md header, or: Not available]

## Project Overview
  Source: Phase 01 artifact set (program.md, knowledge.md, design.md, database.md, api.md, ui-ux.md)
  Project Type: [one line]
  Domain: [one line]
  Primary Goals: [two to four bullet points derived from program.md and knowledge.md]

## Required Skills
  [REC-ID | Skill name | Phase | One-sentence rationale]

## Recommended Skills
  [REC-ID | Skill name | Phase | One-sentence rationale]

## Optional Skills
  [REC-ID | Skill name | Phase | One-sentence rationale]

## Not Recommended Skills
  [REC-ID | Skill name | One-sentence reason for exclusion]

## Skill Enhancements
  [REC-ID | Skill name → Enhancement description | Phase | One-sentence rationale]

## Critical Flags
  [Any High-severity risks, unsatisfied dependencies, or Candidate New Skill gaps
   that the execution team must address before proceeding. If none, state: None.]

## Phase 01 Assessment Summary

  **Fully Covered Areas:**
  [Areas across the Phase 01 artifacts that are complete and require no further
   specification work before Phase 02 begins. List by domain or capability area.]

  **Partial Areas:**
  [Areas that exist in the Phase 01 artifacts but are incomplete. Identify the
   artifact and the specific section or capability that is partially specified.]

  **Identified Gaps:**
  [Capability areas or specification domains that are absent from the Phase 01
   artifacts entirely. These gaps are the primary driver of Required recommendations.]

  **Key Missing Information:**
  [The most consequential pieces of missing information across all Phase 01 artifacts.
   Ranked by impact on project execution. Feeds directly into the Minimal Design Plan
   below by identifying which Phase 02+ skills are most critical.]

## Minimal Design Plan

  The smallest viable project execution design derived exclusively from Required
  skills and critical Skill Enhancements. Organized by execution phase.
  This section is the primary planning reference. All other sections inform it.

  Phase [A]
  - [Required Skill name (REC-ID)]
  - [Required Skill name (REC-ID)]

  Phase [B]
  - [Required Skill name (REC-ID)]
  - [Enhancement: Existing Skill → Enhancement description (REC-ID)]

  Phase [C]
  - [Required Skill name (REC-ID)]

  Skills Removed
  - [Skill name] — [one-line reason]

  Critical Enhancements
  - [Existing Skill] → [Enhancement description] (REC-ID)

  Capability Gaps
  - [Gap name] — [one-line description], or: None

  Execution Rationale
  [Two to three sentences explaining why this is the minimum viable plan
   and what it enables the project to achieve.]

## Phase Overview
  [One line per phase, ordered by execution phase sequence.
   For each phase: what runs in this phase from the full recommendation set,
   including Recommended and Optional items beyond the Minimal Design Plan.
   Skills within a phase are listed in dependency order, not alphabetically.]
```

---

## Presentation and Ordering Rules

The Recommendation Engine is an execution-planning system. All presentations of skills, recommendations, enhancements, mappings, and plans must reflect execution order, not catalog or alphabetical order.

### Ordering Priority

1. Never sort skills or recommendations alphabetically unless explicitly requested by the user.
2. Always prefer ordering by:
   - Execution phase (earlier phases first)
   - Dependency sequence within a phase (prerequisites before dependents)
   - Logical execution order where no formal dependency exists

### Application by Section

**recommendation_report.md:**
- Execution Plan must be ordered by execution phase, then by dependency sequence within each phase.
- Dependency chains must follow execution order throughout the document.
- Required Skills, Recommended Skills, Optional Skills, and Not Recommended Skills sections must each be ordered by phase, then by dependency sequence within phase.

**recommendation_summary.md:**
- Minimal Design Plan must be organized by execution phase. Within each phase, list Required skills and critical enhancements in dependency order.
- Phase Overview must present phases in execution sequence. Within each phase, list skills in dependency order.
- Required Skills, Recommended Skills, Optional Skills, and Skill Enhancements tables must each be ordered by phase, then dependency sequence within phase.

**General:**
- Where multiple items exist within the same execution phase and no dependency relationship exists between them, preserve logical execution order derived from the skill catalog's Phase field and documented dependencies.
- If ordering is uncertain within a phase, prefer the order that minimizes blocking (earlier-completing skills first).

---

## Validation Rules

The following rules must pass before any output is delivered. If a rule fails, the engine must either fix the issue or explicitly flag it in the report's Risks & Gaps section.

### Input Validation Rules

- V-IN-01: skill_catalog.md is present, accessible, and readable.
- V-IN-02: program.md is present and non-empty.
- V-IN-03: knowledge.md is present and non-empty.
- V-IN-04: design.md is present and non-empty.
- V-IN-05: database.md is present and non-empty.
- V-IN-06: api.md is present and non-empty.
- V-IN-07: ui-ux.md is present and non-empty.

### Catalog Validation Rules

- V-CAT-01: skill_catalog.md is present, accessible, and readable before recommendation generation begins.
- V-CAT-02: The catalog contains at least one skill entry with a valid Skill Name.
- V-CAT-03: The catalog Validation Status is not marked FAIL. A FAIL-status catalog must not be used for recommendation decisions.
- V-CAT-04: All Catalog Evidence citations in the internal traceability record reference field values traceable to entries in skill_catalog.md.

### Recommendation Validation Rules

- V-REC-00: Every recommendation has a unique Recommendation ID in the format REC-XXX.
- V-REC-01: Every recommendation has a classification type.
- V-REC-02: Every recommendation has a phase assignment.
- V-REC-03: Every recommendation has a confidence score between 10 and 100.
- V-REC-04: Every recommendation has a written confidence reason.
- V-REC-05: Every recommendation has at least one Requirement Evidence citation.
- V-REC-06: Every recommendation has at least one Catalog Evidence citation.
- V-REC-07: Every recommendation has at least one Artifact Evidence citation referencing one or more Phase 01 artifacts.
- V-REC-08: No recommendation has an arbitrary or unjustified phase assignment.
- V-REC-09: No Required skill has a confidence score below 60 without a Risk flag.
- V-REC-10: Every skill in `skill_catalog.md` that is not in the pre-Phase-02 exclusion list must appear in exactly one classification bucket (Required / Recommended / Optional / Not Recommended). A report that omits any catalog skill from all buckets fails validation and must not be delivered.

### Traceability Validation Rules

- V-TRC-01: Every recommendation has a traceability matrix entry.
- V-TRC-02: No traceability entry cites evidence not present in the inputs.
- V-TRC-03: Every requirement reference ID exists in the parsed requirement set.

### Skill Enhancement Validation Rules

- V-ENH-01: Every Skill Enhancement names the existing skill being enhanced.
- V-ENH-02: Every Skill Enhancement contains a specific, actionable Enhancement Description.
- V-ENH-03: Every Skill Enhancement specifies placement within the existing skill.
- V-ENH-04: No Skill Enhancement contains vague directives.

### Capability Classification Validation Rules

- V-CAP-01: Every identified capability gap has a classification decision documented.
- V-CAP-02: Every Candidate New Skill is flagged as deferred and not included in the execution plan.
- V-CAP-03: Every classification decision documents all three rules from the framework.

### Report Validation Rules

- V-RPT-01: recommendation_report.md contains all required sections: Executive Summary, Project Understanding, Phase 01 Coverage Assessment, Catalog Analysis, Required Skills, Recommended Skills, Optional Skills, Not Recommended Skills, Skill Enhancements, Execution Plan, Risks & Gaps.
- V-RPT-02: recommendation_summary.md is present and shorter than the report.
- V-RPT-03: Minimal Design Plan in summary contains only Required skills and critical enhancements, organized by phase.
- V-RPT-04: Execution Plan section covers every recommendation and is ordered by execution phase, then by dependency sequence within each phase. Not sorted alphabetically.
- V-RPT-05: Risks & Gaps section is present and non-empty.
- V-RPT-06: All recommendation lists in recommendation_report.md and recommendation_summary.md are ordered by execution phase and dependency sequence, not alphabetically.

---

## Hallucination Prevention Rules

These rules govern what the engine may and may not assert.

### Permitted Sources of Assertion

- Statements derived directly from the Phase 01 artifacts (program.md, knowledge.md, design.md, database.md, api.md, ui-ux.md).
- Statements derived directly from requirements extracted from Phase 01 artifacts during Phase 3.
- Statements derived directly from optional requirement sources (requirements documents, customer documents, meeting outputs) if provided.
- Statements derived directly from catalog entries (which themselves derive from skill files).
- Statements derived from optional inputs provided (prior recommendation artifacts, additional project artifacts).

### Prohibited Assertions

- Do not invent project requirements not present in the inputs.
- Do not invent capabilities not mentioned in the inputs or catalog.
- Do not invent ownership or responsibility assignments not supported by catalog entries.
- Do not invent dependency relationships not supported by catalog entries.
- Do not assume a project needs a capability because it is a "best practice" unless the inputs state best practices apply.
- Do not fabricate evidence to support a recommendation.
- Do not paraphrase inputs in a way that materially changes their meaning.

### When Inputs are Ambiguous

1. State the ambiguity explicitly in the recommendation's Confidence Reason.
2. Reduce the confidence score to reflect the ambiguity.
3. Do not resolve the ambiguity by assumption.
4. If the ambiguity is significant enough to change the recommendation classification, present both possible outcomes.

---

## Token Efficiency Rules

### Recommendation Generation Phase

Token efficiency IS a priority during recommendation generation.

- Use skill_catalog.md as the sole information source for all skill analysis. Do not read raw skill files.
- Reference catalog entries by Skill Name rather than repeating full catalog content in reasoning.
- Produce the report and summary in a single generation pass where possible.

---

## Success Criteria

The skill succeeds when all of the following conditions are met:

1. **Traceability Complete:** Every recommendation in the report has a populated traceability matrix entry with valid artifact evidence (from Phase 01 specifications), requirement evidence, and catalog evidence.

2. **Evidence-Backed:** No recommendation was made without supporting evidence from the Phase 01 artifacts or catalog. No recommendation is included solely because a skill is generally useful. No hallucinated evidence is present.

3. **Full Catalog Coverage:** Every skill in `skill_catalog.md` that is not in the pre-Phase-02 exclusion list appears in exactly one classification bucket. No catalog skill is silently omitted from the report.
4. **Unnecessary Skills Identified:** The Not Recommended section explicitly names skills from Phase 02 onward in the catalog that provide no value for this project based on artifact content, and explains why.

4. **Useful Enhancements Identified:** The Skill Enhancements section contains specific, actionable improvements that address real gaps identified in the Phase 01 artifacts, not generic advice.

5. **Phase Placement Justified:** Every recommendation in the Execution Plan has a phase assignment derived from the catalog Phase field or dependency rationale. No assignment is arbitrary.

6. **Hallucinations Minimized:** The Hallucination Prevention Rules were followed. No invented requirements, capabilities, ownership, or dependencies are present.

7. **Recommendation Report is Actionable:** An architect or technical lead can read the report and make concrete decisions about skill inclusion, enhancement, and sequencing without needing additional analysis.

8. **Recommendation Summary Produces a Minimal Design Plan:** The summary's Minimal Design Plan section contains the smallest set of Required skills and critical enhancements organized by phase, with no noise from Optional or Not Recommended items.

9. **Unnecessary Skill Execution Avoided:** The recommendation set prevents the project team from executing skills that are irrelevant to the project based on actual artifact content, reducing wasted effort and scope creep.

10. **Summary Is Self-Sufficient for Planning:** A project owner can read recommendation_summary.md alone and determine — without opening recommendation_report.md — what skills to execute, what skills to avoid, what enhancements to apply, what phases to run, and what capability gaps remain. The report is referenced only for justification and audit, not for decision-making.

11. **Valid Catalog Consumed:** The engine successfully reads and validates skill_catalog.md produced by skill-catalog-generator.md before any recommendation analysis begins.

12. **Catalog as Sole Skill Authority:** All recommendation decisions — skill matching, capability mapping, ownership analysis, dependency resolution, and phase assignment — are derived exclusively from skill_catalog.md entries. No raw skill files are read during recommendation generation.

13. **No Raw Skill File Reads:** The engine does not access individual skill files at any point during recommendation generation. All skill knowledge flows through the catalog.

14. **Catalog-Traceable Evidence:** Every Catalog Evidence citation in the internal traceability record references a specific field and value from a skill_catalog.md entry. No catalog evidence is invented or inferred from outside the catalog.

15. **Phase 02 Scope Enforced:** The engine recommends only skills from Phase 02 onward. Phase 01 skills (program-charter, spec-knowledge, spec-design, spec-database, spec-api, spec-uiux) are never present in any recommendation classification. Their absence from the recommendation set is correct behavior, not a gap.

16. **Recommendations Derived from Artifacts:** Every Required and Recommended classification is derived from evidence in the Phase 01 artifacts — program.md, knowledge.md, design.md, database.md, api.md, or ui-ux.md — and the coverage analysis performed in Phase 1.5. Recommendations unsupported by artifact evidence are classified as Optional or Not Recommended.

17. **Phase 01 Coverage Assessed:** The recommendation report contains a complete Phase 01 Coverage Assessment section documenting the coverage status (Complete, Partial, Missing Information, Contradictory) of each mandatory Phase 01 artifact before recommendations are generated. The recommendation summary contains a Phase 01 Assessment Summary before the Minimal Design Plan.

---

## Execution Guidance

### When to Run This Skill

Run the Skill Recommendation Engine:

- After Phase 01 (Init) has completed and all Phase 01 artifacts (program.md, knowledge.md, design.md, database.md, api.md, ui-ux.md) are present.
- When the project scope changes significantly after Phase 01 and the execution plan needs reassessment based on updated artifacts.
- When Phase 01 artifacts are materially updated and prior recommendations may no longer reflect the current artifact state.
- When the catalog has been updated (new skills added or existing skills modified) and the prior recommendations may be stale.

Do NOT run this skill:

- Before Phase 01 is complete. All six Phase 01 artifacts must exist before the engine can execute.
- In the middle of active Phase 02+ skill execution to interrupt the plan (re-planning mid-execution is out of scope for Version 1).
- As a substitute for skill execution (this skill plans; it does not execute).
- Without all mandatory Phase 01 artifacts present.

### Interaction Pattern

1. User confirms Phase 01 is complete and provides all six Phase 01 artifacts.
2. Engine validates mandatory artifacts and catalog (Phase 0).
3. Engine validates catalog (Phase 1).
4. Engine analyzes existing artifact coverage (Phase 1.5).
5. Engine classifies project using artifact content (Phase 2).
6. Engine decomposes artifact content into requirement evidence (Phase 3).
7. Engine generates recommendations for Phase 02+ skills only (Phase 4).
8. Engine analyzes enhancements (Phase 5).
9. Engine assigns phases (Phase 6).
10. Engine constructs traceability matrix (Phase 7).
11. Engine generates recommendation_report.md and recommendation_summary.md (Phase 8).
12. User reviews recommendation_summary.md to form the Phase 02+ execution plan.
13. User references recommendation_report.md for detailed justification of any specific recommendation.

### Catalog Maintenance Guidance

Catalog creation, refresh, and maintenance are handled exclusively by skill-catalog-generator.md. The Recommendation Engine consumes the catalog but does not manage it.

To create or refresh the catalog:
- Run skill-catalog-generator.md when the framework is initialized.
- Run skill-catalog-generator.md when new skills are added or existing skills are materially modified.
- Run skill-catalog-generator.md with an explicit Catalog Refresh Request at any time.

Refer to skill-catalog-generator.md for complete catalog refresh rules, staleness detection guidance, and catalog quality validation behavior.

### Handling Insufficient Inputs

If Phase 01 artifacts are present but too thin or incomplete to generate reliable recommendations:

1. The engine must identify specifically which artifact and which sections contain insufficient information.
2. The engine must output a targeted clarification request naming the missing information and its source artifact.
3. The engine must not proceed with low-quality artifact content and produce a high-confidence recommendation plan.
4. Once additional information is provided or artifacts are updated, the engine resumes from Phase 1.5 (coverage analysis) using the enriched inputs. The catalog remains unchanged.

### Version 1 Limitations Disclosure

The following limitations apply to Version 1 of this skill. They must be disclosed in any recommendation report generated:

- New skills identified as Candidate New Skills are flagged but not created.
- Recommendations are generated once per run; continuous re-planning is not supported.
- Recommendations are not versioned; re-running on the same inputs produces a new report rather than a versioned delta.
- The engine does not modify existing skills, even when enhancement recommendations are clear and unambiguous.
- These limitations are tracked for resolution in future versions.

---

## Future Re-Evaluation Triggers

This section is informational. Version 1 does not support adaptive replanning.
It documents when a new recommendation run should be initiated.

### Regeneration Required

A new recommendation run must be initiated when any of the following occur:

- **Phase 01 artifacts updated:** Phase 01 specifications (program.md, knowledge.md, design.md, database.md, api.md, or ui-ux.md) are materially updated after the initial recommendation run — adding, removing, or significantly changing requirements or capabilities. The prior plan may no longer reflect the actual artifact state.

- **Material scope change:** The project's primary goals, domain, or target deliverables
  shift in a way that would change project type classification or primary success factors.

- **Significant architecture change:** The technical approach changes in a way that
  affects which skills are relevant (e.g., switching from a monolith to microservices,
  or from on-premises to cloud).

- **Catalog refreshed with new skills:** When skill-catalog-generator.md adds new skills
  to skill_catalog.md, re-run the Recommendation Engine. Newly cataloged skills may be
  Required or Recommended for the project and were not evaluated in the prior run.

- **Catalog updated with ownership changes:** When skill-catalog-generator.md refreshes
  skill_catalog.md following material changes to a skill's Owned Responsibilities field,
  re-run the Recommendation Engine. Updated ownership may affect recommendation
  classifications for uncovered requirements.

- **Catalog updated with capability changes:** When skill-catalog-generator.md refreshes
  skill_catalog.md following significant changes to a skill's Capabilities field, re-run
  the Recommendation Engine. Expanded or contracted capabilities may shift classification
  decisions.

### Regeneration NOT Required

A new recommendation run is not required for:

- Cosmetic updates to skill files (formatting, whitespace, visual presentation).
- Wording changes to skill documentation that do not affect Owned Responsibilities,
  Capabilities, Phase, or Project Types.
- Formatting or style changes to non-catalog fields.
- Non-functional metadata updates (author notes, revision history, tags).
- Minor clarifications that do not change what the skill does or owns.

### Guidance for Future Versions

Future versions may integrate directly with skill-catalog-generator.md to detect
catalog changes automatically and prompt re-evaluation when relevant entries are
updated. Version 1 relies on the user or framework maintainer to recognize when a
trigger condition has been met, refresh the catalog using skill-catalog-generator.md,
and then re-initiate a recommendation run manually.
