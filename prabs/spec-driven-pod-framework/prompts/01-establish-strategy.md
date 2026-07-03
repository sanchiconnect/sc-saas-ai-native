# Establish Strategy

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

Present the brief bulleted summary and Expected Action from User.

Wait for the user to reply NEXT before generating artifacts.

After generation, wait for CONFIRM before proceeding to the next prompt.

Do not skip, reorder, merge, or modify prompts.

After the final prompt has been executed, display:

Establish Strategy Complete

---

## Prompt 1

Execute the `program-charter` skill.

### Inputs
- Skill definition: `.claude/program-charter/SKILL.md`
- Elicitation source: `transcripts/meeting_transcript.txt` and `transcripts\meeting_summary.txt`
- Reference template: `references/program-md-template.md`

Use `transcripts/meeting_transcript.txt` and `transcripts\meeting_summary.txt` as the completed elicitation session and treat it as the authoritative source of stakeholder responses.

Extract and organize the elicitation information according to the groups defined in the skill.

### Outputs
Generate the following files:

**Fully generated:**
- `specs/program.md`

**Scaffolded as placeholder stubs:**
- `specs/knowledge.md`
- `specs/design.md`
- `specs/ui-ux.md`
- `specs/database.md`
- `specs/api.md`
- `CLAUDE.md`

Create the following folder structure:

- `src/`
- `tests/`
- `.claude/program-charter/`

Populate `specs/program.md` using the canonical structure defined in `references/program-md-template.md`.

Create all other specification files as placeholder stubs exactly as described in the skill definition.

Before generating `specs/program.md` or any scaffolded files, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt


---

## Prompt 2

Run the `spec-knowledge` skill.

### Inputs
- Skill definition: `.claude/spec-knowledge/SKILL.md`
- Primary context: `specs/program.md`
- Existing knowledge specification (if present): `specs/knowledge.md`
- Reference template: `references/knowledge-template.md`
- Example output: `sample_output/knowledge.md`

### Execution
Read `specs/program.md` first and use it as the primary source of context.

Check whether `specs/knowledge.md` already exists:
- If it exists, execute the skill in **Review Mode**.
- If it does not exist, execute the skill in **Initialize Mode**.

When initializing, derive and document the domain knowledge supported by the program charter, including:
- Domain overview
- Core domain entities and relationships
- Business rules and constraints
- Workflows and actors
- Glossary terms
- State transitions and state machines
- Compliance and regulatory considerations explicitly reflected in the charter

Infer information only when it is reasonably supported by the contents of `specs/program.md`. Do not introduce concepts that cannot be traced back to the existing program charter.

Follow the execution steps and behavior defined in the `spec-knowledge` skill.

### Outputs
Generate or update the following file using the canonical structure defined in `references/knowledge-template.md`:

- `specs/knowledge.md`

Ensure the output contains the following sections:
- Domain Overview
- Core Entities
- Business Rules
- State Machines
- Workflows
- Constraints & Compliance
- Glossary
- Changelog (Review Mode only)

Before generating the file, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt


---

## Prompt 3

Run the `spec-design` skill.

### Inputs
- Skill definition: `.claude/spec-design/SKILL.md`
- Primary context: `specs/program.md`
- Supporting context: `specs/knowledge.md`
- Existing design specification (if present): `specs/design.md`
- Reference template: `references/design-template.md`
- Example output: `sample_output/design.md`
- Client design preferences (if present): `context/design-preferences.md`

### Context Check
Before reading any spec files, check whether `context/design-preferences.md` exists.
- If it exists: read it and extract design preferences. Use them to pre-populate answers to the skill's elicitation groups. Show the user a summary of what was inferred and ask them to confirm or override before proceeding.
- If it does not exist: ask the user once — *"Would you like to provide a design preferences document in `context/design-preferences.md` before we proceed? (Yes / No)"* — and wait for their answer before continuing.

### Execution
Read `specs/program.md` and `specs/knowledge.md` first and use them as the primary sources of context.

Check whether `specs/design.md` already exists:
- If it exists, execute the skill in **Review Mode**.
- If it does not exist, execute the skill in **Initialize Mode**.

When initializing, propose a coherent technical architecture and technology stack aligned with the program goals, workflows, non-functional requirements, compliance requirements, and domain requirements documented in the prerequisite specifications.

Document and justify the following design decisions:
- System architecture and communication patterns
- Technology stack and runtime choices
- Frameworks and key libraries
- Infrastructure and deployment approach
- Coding standards and conventions
- Security design decisions
- Observability strategy

Infer technology decisions only when they are reasonably supported by the existing specifications. Do not introduce decisions that conflict with the documented program requirements, domain constraints, non-functional requirements, or compliance considerations.

Follow the execution steps and behavior defined in the `spec-design` skill.

### Outputs
Generate or update the following file using the canonical structure defined in `references/design-template.md`:

- `specs/design.md`

Ensure the output contains the following sections:
- System Architecture
- Technology Stack
- Libraries & Dependencies
- Infrastructure
- Coding Standards
- Security Design
- Observability
- Changelog (Review Mode only)

Before generating `specs/design.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 4

Run the `spec-uiux` skill.

### Inputs
- Skill definition: `.claude/spec-uiux/SKILL.md`
- Primary context: `specs/program.md`
- Supporting context: `specs/design.md`
- Existing UI/UX specification (if present): `specs/ui-ux.md`
- Reference template: `references/uiux-template.md`
- Example output: `sample_output/ui-ux.md`
- Client UX reference (if present): `context/ux-reference.*`

### Context Check
Before reading any spec files, check whether any file named `ux-reference.*` exists in the `context/` folder (accepts `.md`, `.css`, `.pdf`, `.png`, `.jpg`, or any image format).
- If it exists: read or interpret it and extract design tokens, component styles, colors, and typography. Show the user a summary of what was inferred and ask them to confirm or override before proceeding.
- If it does not exist: ask the user once — *"Would you like to provide a UX reference file in `context/` before we proceed? (Yes / No)"* — and wait for their answer before continuing.

### Execution
Read `specs/program.md` and `specs/design.md` first and use them as the primary sources of context.

Check whether `specs/ui-ux.md` already exists:
- If it exists, execute the skill in **Review Mode**.
- If it does not exist, execute the skill in **Initialize Mode**.

When initializing, propose a UI/UX specification aligned with the target users, user journeys, accessibility requirements, design highlights, and frontend approach defined in the prerequisite specifications.

Document and define the following design decisions:
- Design tokens, including colors, typography, spacing, elevation, and border radius
- Component library standards, including variants, states, sizing, and usage guidance
- Motion and transition principles
- Layout and responsive behavior standards
- Accessibility requirements and internationalization considerations
- Iconography standards
- Copy and tone guidelines

Infer design decisions only when they are reasonably supported by the existing specifications. Do not introduce decisions that conflict with documented user needs, accessibility requirements, non-functional requirements, frontend constraints, or existing design guidance.

Follow the execution steps and behavior defined in the `spec-uiux` skill.

### Outputs
Generate or update the following file using the canonical structure defined in `references/uiux-template.md`:

- `specs/ui-ux.md`

Ensure the output contains the following sections:
- Design Tokens
- Component Library
- Motion System
- Layout System
- Accessibility Standards
- Iconography
- Copy & Tone
- Changelog (Review Mode only)

Before generating `specs/ui-ux.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 5

Run the `spec-database` skill.

### Inputs
- Skill definition: `.claude/spec-database/SKILL.md`
- Primary context: `specs/program.md`
- Supporting context: `specs/knowledge.md`
- Supporting context: `specs/design.md`
- Existing database specification (if present): `specs/database.md`
- Reference template: `references/database-template.md`
- Example output: `sample_output/database.md`

### Execution
Read `specs/program.md`, `specs/knowledge.md`, and `specs/design.md` first and use them as the primary sources of context.

Check whether `specs/database.md` already exists:
- If it exists, execute the skill in **Review Mode**.
- If it does not exist, execute the skill in **Initialize Mode**.

When initializing, derive the database specification from the existing specifications, including:
- Database platform and deployment approach
- Schema overview and entity relationships
- Table or collection definitions
- Constraints and integrity rules
- Indexing strategy and performance considerations
- Migration strategy and conventions
- Data retention and compliance requirements
- Seed and reference data requirements

Use the database technology, ORM, and migration approach defined in `specs/design.md`, and derive entities, attributes, relationships, and business rules from `specs/knowledge.md`.

Ensure that business rules documented in the existing specifications are enforced at the database level where appropriate.

Infer schema decisions only when they are reasonably supported by the existing specifications. Do not introduce entities, fields, relationships, constraints, compliance requirements, or indexing strategies that conflict with or cannot be traced back to the documented specifications.

Follow the execution steps and behavior defined in the `spec-database` skill.

### Outputs
Generate or update the following file using the canonical structure defined in `references/database-template.md`:

- `specs/database.md`

Ensure the output contains the following sections:
- Platform
- Schema Overview
- Table / Collection Definitions
- Indexes
- Constraints & Integrity
- Migrations
- Data Retention & Compliance
- Seed Data
- Changelog (Review Mode only)

Before generating `specs/database.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 6

Run the `spec-api` skill.

### Inputs
- Skill definition: `.claude/spec-api/SKILL.md`
- Primary context: `specs/program.md`
- Supporting context: `specs/knowledge.md`
- Supporting context: `specs/database.md`
- Supporting context: `specs/design.md`
- Existing API specification (if present): `specs/api.md`
- Reference template: `references/api-template.md`
- Example output: `sample_output/api.md`

### Execution
Read `specs/program.md`, `specs/knowledge.md`, `specs/database.md`, and `specs/design.md` first and use them as the primary sources of context.

Check whether `specs/api.md` already exists:
- If it exists, execute the skill in **Review Mode**.
- If it does not exist, execute the skill in **Initialize Mode**.

When initializing, derive the API specification from the existing specifications, including:
- API foundation and versioning strategy
- Authentication and authorization approach
- CORS and global API conventions
- Endpoint definitions derived from domain entities and workflows
- Request and response schemas
- Pydantic schema definitions
- Error contracts and HTTP status code conventions
- Pagination and filtering conventions
- Rate limiting and non-functional API requirements
- FastAPI implementation patterns

Use `specs/knowledge.md` to derive endpoints from domain entities, workflows, and business rules. Use `specs/database.md` to derive request and response shapes and query requirements. Use `specs/design.md` to derive framework choices, authentication mechanisms, API style, and implementation conventions.

Ensure that business rules documented in the existing specifications are reflected in endpoint validations, guards, and behavior where appropriate.

Infer API decisions only when they are reasonably supported by the existing specifications. Do not introduce endpoints, request fields, response fields, authentication mechanisms, error contracts, or implementation patterns that conflict with or cannot be traced back to the documented specifications.

Follow the execution steps and behavior defined in the `spec-api` skill.

### Outputs
Generate or update the following file using the canonical structure defined in `references/api-template.md`:

- `specs/api.md`

Ensure the output contains the following sections:
- API Foundation
- Authentication
- Error Contract
- Endpoints
- Pydantic Schemas
- Rate Limiting
- Changelog (Review Mode only)

Before generating `specs/api.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 7
Run the `SkillFlow` skill.

### Inputs
- Skill definition: `.claude/skill-flow/SKILL.md`
- Authoritative catalog input: `catalog/skill_catalog.md`
- Primary context: `specs/program.md`
- Supporting context: `specs/knowledge.md`
- Supporting context: `specs/design.md`
- Supporting context: `specs/database.md`
- Supporting context: `specs/api.md`
- Supporting context: `specs/ui-ux.md`
- Existing recommendation artifacts (if present):
  - `recommendation_report.md`
  - `recommendation_summary.md`

### Execution
Use `catalog/skill_catalog.md`, `specs/program.md`, `specs/knowledge.md`, `specs/design.md`, `specs/database.md`, `specs/api.md`, and `specs/ui-ux.md` as the authoritative inputs.

Validate that all mandatory artifacts are present and non-empty before proceeding. If any mandatory artifact is missing, halt execution and follow the validation behavior defined in the skill.

Execute the skill exactly as defined, including:
- Phase 0: Input Validation
- Phase 1: Catalog Validation
- Phase 1.5: Existing Coverage Analysis
- Phase 2: Project Classification
- Phase 3: Capability & Requirement Extraction
- Phase 4: Recommendation Generation
- Phase 5: Skill Enhancement Analysis
- Phase 6: Phase Assignment
- Phase 7: Traceability Matrix Construction
- Phase 8: Report Generation

Generate recommendations for Phase 02 and later skills only. Exclude the following skills from all recommendation classifications — they run before Phase 02 begins and are assumed complete:
- `program-charter`
- `spec-knowledge`
- `spec-design`
- `spec-database`
- `spec-api`
- `spec-uiux`
- `skill-flow`
- `skill-generator`

Use only `catalog/skill_catalog.md` for all skill analysis, capability mapping, ownership analysis, dependency resolution, phase assignment, and recommendation decisions.

Do not read raw skill files for recommendation decisions. If a skill is not present in `catalog/skill_catalog.md`, treat it as a catalog gap and do not recommend it.

Ensure all recommendations are evidence-backed using the Phase 01 artifacts and catalog entries. Do not generate recommendations solely because a skill is generally useful.

Follow all validation rules, traceability rules, confidence scoring rules, hallucination prevention rules, ordering rules, and success criteria defined in the `skill-flow` skill.

### Outputs
Generate or update the following files:

- `recommendation_report.md`
- `recommendation_summary.md`

Ensure the outputs conform to the structures defined by the skill, including all mandatory sections and validations.

Before generating `recommendation_report.md` and `recommendation_summary.md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 8

Run the `skill-generator` skill.

### Inputs
- Skill definition: `.claude/skill-generator/SKILL.md`
- Primary input: `recommendation_report.md`
- Catalog input: `skill_catalog.md`
- Optional cross-reference: `recommendation_summary.md`
- Prior skip list (if present): `skillflow_skip.md`

### Execution
Read `recommendation_report.md` and `skill_catalog.md` first.

Execute the skill exactly as defined, including:
- Phase 0: Input Validation
- Phase 1: Recommendation Extraction
- Phase 2: Recommendation Review (User Gate)
- Phase 3: Assumptions Review (per accepted item)
- Phase 4: Content Generation
- Phase 5: Skill Catalog Update
- Phase 6: Validation and Final Review
- Phase 7: Output

Extract all Skill Enhancements from the Skill Enhancements section of `recommendation_report.md`.

Extract all Candidate New Skills from the Risks & Gaps section of `recommendation_report.md`.

Present the full list of new skills and enhancements to the user for accept/reject review before any generation begins.

For every rejected item, write the skill name to `skillflow_skip.md`. Ask for user permission before writing to `skillflow_skip.md`.

For every accepted item, present assumptions to the user and wait for confirmation before generating content.

Do not write any file until the user confirms the final review summary in Phase 6.

Follow all validation rules, hallucination prevention rules, and success criteria defined in the `skill-generator` skill.

### Outputs
Generate or update the following as applicable:

- `.claude/<skill-name>/SKILL.md` — for each accepted Candidate New Skill
- `.claude/<skill-name>/README.md` — for each accepted Candidate New Skill
- `.claude/<skill-name>/SKILL.md` — patched for each accepted Skill Enhancement
- `.claude/<skill-name>/README.md` — updated for each accepted Skill Enhancement
- `skill_catalog.md` — new entries added and existing entries updated
- `skillflow_skip.md` — updated with rejected skill names
- `skill_generation_report.md` — audit log of the run

Before generating any files, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Recommendation Gate — Runs immediately after Prompt 8 completes

This gate runs once, before Prompt 9. Do not skip it. Do not proceed to Prompt 9 until `skillflow_skip.md` has been written.

### Step 1 — Ask the user

Present the following question exactly as written and wait for a response before doing anything else:

---

**SkillFlow produced a recommendation plan. How would you like to proceed?**

**(A) Follow the SkillFlow plan** — only run Required and Recommended skills; Not Recommended skills are skipped.

**(B) Run everything** — ignore the plan and run all skills in the catalog.

**(C) Decide manually** — I will tell you which skills to skip.

---

### Step 2 — Handle each answer

**If the user answers A:**

Ask one follow-up question:

> **Should Optional skills be included in the run?**
> - **Yes, include optionals** — run Required + Recommended + Optional; skip only Not Recommended
> - **No, exclude optionals** — run Required + Recommended only; skip Not Recommended + Optional

Then write `skillflow_skip.md` as follows:
- Read `recommendation_report.md` and extract all skills classified as Not Recommended (and Optional, if excluded).
- Write `skillflow_skip.md` with one skill name per line.
- If no skills are being skipped, write `skillflow_skip.md` as an empty file with the header: `# skillflow_skip.md — no skills skipped`.

---

**If the user answers B:**

Write `skillflow_skip.md` as an empty file with the header:

```
# skillflow_skip.md — all skills active (SkillFlow plan not followed)
```

No skills will be skipped. All Prompts 9 onward will run.

---

**If the user answers C:**

Read `recommendation_report.md` and display the full skill list grouped by classification (Required / Recommended / Optional / Not Recommended) with one line per skill.

Ask the user: *"Which skills would you like to skip? List the skill names."*

Wait for the user's response. Write `skillflow_skip.md` with exactly the skills the user named, one per line.

If the user names no skills, write `skillflow_skip.md` as an empty file with the header: `# skillflow_skip.md — no skills skipped`.

---

### Step 3 — Confirm and proceed

After writing `skillflow_skip.md`, report to the user:

```
skillflow_skip.md written.
Skills to be skipped: [list skill names, or "none"]
Proceeding to Prompt 9.
```

`skillflow_skip.md` must exist on disk before Prompt 9 begins. This is a hard requirement.

---

## Standing Instruction — Active from Prompt 9 onward

Before executing any prompt from this point forward, read `skillflow_skip.md`.
If the skill name for that prompt appears in `skillflow_skip.md`, skip it entirely and log: `Skipped: <skill-name>`.
If `skillflow_skip.md` is empty or contains only a header comment, proceed normally — no skills are skipped.
This instruction applies to every remaining prompt in this file without exception.

---

## Prompt 9

Run the `requirements-elicitation-charter` skill.

### Inputs
- Skill definition: `.claude/requirements-elicitation-charter/SKILL.md`
- Authoritative charter input: `specs/program.md`
- Existing question pack outputs (if present): `questions-[YYYY-MM-DD].md`

### Execution
Read `specs/program.md` as the authoritative charter input.

Execute the skill exactly as defined, including:
- Phase 0: Input Intake
- Phase 1: Charter Analysis
- Phase 2: Question Pack Generation
- Phase 3: Output Formatting

Extract and analyze the following from the charter:
- Program name or code
- Primary business objective
- Stated scope
- Known stakeholders
- Timeline and milestones
- Technology context
- Constraints
- Existing systems mentioned

Perform Charter Analysis and identify:
- Confirmed facts
- Implicit assumptions
- Identified gaps
- Conflict flags

Generate a domain-organized question pack aligned with the identified gaps and assumptions across the following domains:
- Business Context & Objectives
- Existing System & As-Is State
- Functional Requirements
- Technical & Integration Constraints
- Data & Migration
- UI/UX & User Expectations
- Organizational & Delivery Constraints
- Open Charter Issues

Ensure that:
- Every question is open-ended.
- Every question maps to a specific gap or assumption identified during Charter Analysis.
- Every question includes its corresponding gap reference.
- Every question includes an intent note explaining why it matters.
- Questions are specific to the charter and are not generic boilerplate.
- No domain exceeds 8–10 questions.
- Sensitive questions are marked with `[SENSITIVE]` where appropriate.
- If the charter is very thin (< 1 page equivalent), explicitly state this and ask the user whether to proceed with inference-heavy questions or wait for a fuller brief.

Follow all constraints, formatting requirements, and execution behavior defined in the `requirements-elicitation-charter` skill.

### Outputs
Generate the following artifact:

- `questions-[YYYY-MM-DD].md`

Ensure the output contains:
- Customer Discovery Questions header
- Charter Analysis Summary
- Complete Question Pack for all applicable domains
- Flagged Charter Ambiguities
- Recommended Meeting Sequence

Save the artifact as `questions-[YYYY-MM-DD].md` in the current working directory and report the saved path.

Before generating `questions-[YYYY-MM-DD].md`, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 10

Run the `doc-extraction` skill.

### Inputs
- Skill definition: `.claude/doc-extraction/SKILL.md`
- Customer-provided documents supplied during this session
- Existing knowledge base files (if present):
  - `specs/knowledge.md`
  - `specs/design.md`
  - `specs/ui-ux.md`
  - `specs/database.md`
  - `specs/api.md`

### Execution
Use any customer-provided documents (requirements specifications, architecture documents, process documents, BRDs, functional specifications, data dictionaries, compliance documents, UI/UX specifications, presentations, PDFs, Word documents, or mixed artifacts) as inputs.

Execute the skill exactly as defined, including:
- Phase 0: Document Intake
- Phase 1: Document Parse
- Phase 2: Conflict Detection
- Phase 3: knowledge.md Update
- Phase 4: design.md Update
- Phase 5: ui-ux.md Update
- Phase 6: Output Summary

Determine and record:
- Document type
- Document source
- Document recency (AS-IS, TO-BE, or Mixed)
- Availability of existing knowledge base files

Read existing knowledge files before extraction to enable conflict detection.

Classify all substantive document content into the appropriate extraction categories and target files.

Update artifacts using AS-IS content only.

Write extracted content to the appropriate files as follows:
- Program context, business objectives, stakeholder information → `specs/knowledge.md`
- Customer expectations, pain points, desired outcomes → `specs/knowledge.md`
- Existing system behavior and current workflows → `specs/knowledge.md`
- Technical architecture, infrastructure, and components → `specs/design.md`
- Data model, database schema, and data flows → `specs/design.md` and `specs/database.md`
- API descriptions and integration contracts → `specs/design.md` and `specs/api.md`
- UI screens, user workflows, and navigation → `specs/ui-ux.md`
- Constraints → `specs/knowledge.md`
- Open questions, risks, and unresolved items → `specs/knowledge.md`

Detect and classify extracted content as:
- Direct Conflict
- Extension
- Duplication
- New Content

Produce a Conflict Report listing all conflicts found. Do not silently overwrite or resolve conflicts.

Apply source attribution to all extracted items using the source document name and section or page reference.

Preserve all original language from customer documents when writing customer expectations. Do not paraphrase customer expectations.

Mark inferred content with `[INFERRED]` and document the basis for the inference.

If a document is primarily a TO-BE specification, write only a summary to `specs/knowledge.md` under expectations and do not seed design artifacts with TO-BE content.

Do not populate TO-BE sections in any design artifacts. TO-BE content is reserved for the design-setup phase.

If a document exceeds 50 pages, process it section by section and request confirmation before proceeding to the next section.

Follow all constraints, formatting requirements, and execution behavior defined in the `doc-extraction` skill.

### Outputs
Generate or update the following artifacts as applicable:

- `specs/knowledge.md`
- `specs/design.md`
- `specs/ui-ux.md`
- `specs/database.md`
- `specs/api.md`

Generate an extraction report containing:
- Document name
- Processing date
- Document type
- Document recency
- Items written by artifact
- Conflicts found
- Items skipped due to TO-BE classification
- Recommended follow-up questions

Before generating the updates, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 11

Run the `code-extraction` skill.

### Inputs
- Skill definition: `.claude/code-extraction/SKILL.md`
- Provided source artifacts, including:
  - Source code files
  - Repository contents or repository exports
  - Schema files
  - Database migration scripts
  - OpenAPI, Swagger, WSDL, or gRPC definitions
  - Configuration files
  - Infrastructure-as-code files
- Existing knowledge base files (if present):
  - `specs/knowledge.md`
  - `specs/api.md`
  - `specs/database.md`
  - `specs/design.md`

### Execution
Parse the provided legacy or existing source code, schema files, API definitions, migration scripts, configuration files, and infrastructure artifacts.

Execute the skill exactly as defined, including:
- Phase 0: Code Intake
- Phase 1: Code Analysis
- Phase 2: knowledge.md Update
- Phase 3: api.md Update
- Phase 4: database.md Update
- Phase 5: design.md Update
- Phase 6: Output Summary

Determine and document:
- Artifact type
- Technology stack
- Scope of analysis
- Availability of existing knowledge files

Read existing knowledge files before extraction to enable conflict detection and deduplication.

Analyze source code to identify:
- Application entry points
- Module and package structure
- Business logic and domain entities
- External dependencies and integrations
- Configuration patterns
- Error handling approaches
- Authentication and authorization mechanisms

Analyze API definitions to extract:
- Endpoints
- Methods
- Request schemas
- Response schemas
- Authentication requirements
- Versioning strategies
- Deprecated or unstable endpoints

Analyze database schemas and migrations to extract:
- Tables and collections
- Fields and data types
- Nullability and defaults
- Primary and foreign keys
- Constraints
- Indexes
- Entity relationships
- Soft delete patterns
- Audit fields
- Multi-tenancy patterns

Analyze infrastructure artifacts to identify:
- Cloud provider and services
- Deployment model
- Scaling approaches
- Containerization patterns
- Load balancing and CDN configurations

Update artifacts using AS-IS knowledge only.

Update `specs/knowledge.md` with:
- Component and service entries
- Business-purpose descriptions
- Observed behaviors
- External dependencies
- Technical debt observations
- Change log entries

Update `specs/api.md` with:
- The AS-IS API surface
- Endpoint definitions
- Request and response summaries
- Authentication mechanisms
- Operational notes
- Deprecation findings

Update `specs/database.md` with:
- The AS-IS data model
- Table and collection documentation
- Indexes
- Relationships
- Entity relationship summaries
- Data model observations

Update `specs/design.md` with:
- The AS-IS architecture seed
- Observed technology stack
- Architectural patterns
- Design patterns
- Technical debt register
- Constraints implied by the codebase

Never overwrite existing entries. Append findings and flag conflicts only.

Detect and report:
- Conflicts with existing knowledge
- Duplicate findings
- Gaps requiring clarification
- Migration risks

Never infer business rules not evidenced in code. If logic is unclear, document it as `[INFERRED — requires validation]`.

Do not document dead code as active behavior. Record it only as technical debt where appropriate.

Do not reproduce credentials, secrets, API keys, or sensitive values found in the code. Report their existence only as security findings.

If the codebase is very large, prioritize analysis in the following order:
- Entry points
- Routing and controllers
- Domain models
- Database schema
- Service logic

Follow all constraints, formatting requirements, and execution behavior defined in the `code-extraction` skill.

### Outputs
Generate or update the following artifacts as applicable:

- `specs/knowledge.md`
- `specs/api.md`
- `specs/database.md`
- `specs/design.md`

Generate a code extraction report containing:
- Artifact name
- Processing date
- Identified technology stack
- Files analyzed
- Knowledge written by artifact
- Conflicts with existing knowledge
- Gaps requiring clarification
- Migration risk flags

Before generating the updates, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 12
Run the `meeting-extraction` skill.

### Inputs
- Skill definition: `.claude/meeting-extraction/SKILL.md`
- All available meeting artifacts, including:
  - Meeting transcripts
  - Call notes
  - Customer session records
  - AI-generated meeting summaries
  - Discovery session notes
- Existing knowledge files (if present):
  - `specs/knowledge.md`
  - `specs/features.md`
  - `specs/design.md`

### Execution
Use all available meeting transcripts, call notes, or customer session records as inputs.

Execute the skill exactly as defined, including:
- Phase 0: Transcript Intake
- Phase 1: Content Classification
- Phase 2: Meeting Brief
- Phase 3: knowledge.md Update
- Phase 4: features.md Update
- Phase 5: design.md Update
- Phase 6: Conflict Detection

Determine and document:
- Transcript type
- Meeting context
- Participants
- Meeting date
- Availability of existing knowledge files

If the transcript is raw verbatim output, filter out crosstalk, filler, scheduling logistics, repeated clarifications, and off-topic discussion.

Read existing files before extraction to enable conflict detection and deduplication.

Classify every substantive piece of content into the appropriate routing category before writing:
- Business context
- Business rules
- Business workflows
- As-is system behavior
- Pain points
- Customer expectations
- Constraints
- To-be feature requirements
- To-be technology decisions
- Decisions made
- Open items and follow-ups
- Risk signals
- Scope signals
- Stakeholder intelligence

Apply the following routing rules:
- Business context, business rules, business workflows, as-is system behavior, pain points, customer expectations, constraints, open items, and risk signals → `specs/knowledge.md`
- To-be feature requirements → `specs/features.md`
- To-be technology and architecture decisions → `specs/design.md`
- Stakeholder intelligence → Meeting Brief only

Generate a structured Meeting Brief containing:
- Meeting title or topic
- Date
- Participants
- Meeting type
- Executive Summary
- Business Knowledge Captured
- Pain Points Stated
- To-Be Features Discussed
- Technology & Architecture Discussed
- Decisions Made
- Open Items & Follow-Ups
- Scope Signals
- Risk Signals
- Stakeholder Intelligence
- Recommended Actions (Next 48 Hours)

Update `specs/knowledge.md` with:
- Business Context
- Business Rules
- Business Workflows
- As-Is System facts
- Customer Expectations
- Constraints
- Open Items
- Change Log entries

Update `specs/features.md` with:
- Functional Features
- Reporting & Analytics
- Integration Requirements
- User & Access Management
- Notifications & Alerts
- Configuration & Administration
- Uncategorized / Pending Classification
- Change Log entries

Assign feature identifiers sequentially by reading the existing `specs/features.md` and continuing the next available FR number.

Update `specs/design.md` with:
- `[TO-BE] Technology & Architecture Decisions`
- Decision or Preference
- Rationale
- Constraints implied
- Status
- Change Log entries

Preserve customer voice by quoting directly or paraphrasing minimally for expectations, business rules, and feature requirements.

Mark inference or interpretation with `[INFERRED]`.

Capture business rules precisely. If a rule is unclear, mark it as `[NEEDS CLARIFICATION]`.

Capture features as capabilities rather than implementation details.

If participant roles cannot be determined, label them as `[Unidentified speaker]`.

If transcript quality is poor, flag:
`⚠️ TRANSCRIPT QUALITY: [describe limitation]`

After all updates, perform conflict detection across all affected artifacts and generate a consolidated Conflict Report.

Follow all constraints, formatting requirements, and execution behavior defined in the `meeting-extraction` skill.

### Outputs
Generate or update the following artifacts as applicable:

- Meeting Brief
- `specs/knowledge.md`
- `specs/features.md`
- `specs/design.md`

Ensure the Meeting Brief includes:
- Executive Summary
- Business Knowledge Captured
- Pain Points Stated
- To-Be Features Discussed
- Technology & Architecture Discussed
- Decisions Made
- Open Items & Follow-Ups
- Scope Signals
- Risk Signals
- Stakeholder Intelligence
- Recommended Actions
- Consolidated Conflict Report

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 13

Run the `knowledge-review` skill.

### Inputs
- Skill definition: `.claude/knowledge-review/SKILL.md`
- Primary context:
  - `specs/knowledge.md`
  - `specs/features.md`

### Execution
Read `specs/knowledge.md` and `specs/features.md` first.

Execute the skill exactly as defined. All phases before the NEXT gate run internally — no section content, checklists, or findings are displayed inline.

Capture and apply:
- Customer expectation certainty: `[FIRM]`, `[EXPLORATORY]`, `[NEEDS VALIDATION]`
- Feature priority confirmations: `MUST HAVE`, `SHOULD HAVE`, `NICE TO HAVE`

### Gap Analysis
Execute the complete Knowledge Completeness Checklist defined in the skill across:
- Business Layer
- Feature Layer
- System Layer
- Technical Layer
- Compliance & Constraints
- Design Readiness

For every unchecked item:
- Capture missing information if available.
- Create an open item if genuinely unknown.
- Mark as N/A with rationale if not applicable.

### Outputs
Generate validated versions of:

- `specs/knowledge.md`
- `specs/features.md`

Incorporate:
- All confirmed entries
- All corrections
- All additions
- Closed open items with resolutions
- Expectation certainty annotations
- Feature priority updates and reclassifications
- Gap analysis findings
- New open items created during review

Add the following validation stamp to both files:

```markdown
**STATUS: REVIEWED ✓** — Reviewed by: [Pod Lead / Program Lead] on [date]
```

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 14
Run the `design-setup` skill.

### Inputs
- Skill definition: `.claude/design-setup/SKILL.md`
- Primary context:
  - `specs/knowledge.md`
  - `specs/features.md`
  - `specs/design.md`
  - `specs/ui-ux.md`
- Supporting context:
  - `specs/api.md`
  - `specs/database.md`
  - `specs/impl.md` (if present)

### Execution
Read `specs/knowledge.md`, `specs/features.md`, `specs/design.md`, and `specs/ui-ux.md` first and use them as the primary sources of context.

Execute the skill exactly as defined, including:
- Phase 0: Pre-Design Context Load
- Phase 1: Design Questionnaire
- Phase 2: Design Validation
- Phase 3: File Population
- Phase 4: Design Summary


Verify whether `specs/knowledge.md` contains:

`STATUS: REVIEWED ✓`

If the review status is missing, issue the warning defined in the skill and ask the user whether to proceed or complete knowledge review first.

### Design Session
Internally derive design decisions across the following domains using the available specifications. Do not present context or ask questions per domain. Record decisions, flag unresolved items, and capture any decision that cannot be derived as `[DESIGN DECISION PENDING]`.

Domains to cover:
- System Architecture Pattern
- Technology Stack
- Data Architecture
- API Design
- UI/UX Design Direction
- Infrastructure & Deployment
- Security & Compliance
- Cross-Cutting Concerns

For each domain:
- Derive decisions from `specs/knowledge.md`, `specs/features.md`, and pre-stated technology constraints.
- Capture rationale traceable to existing specifications.
- Record any decision that cannot be confidently derived as `[DESIGN DECISION PENDING]` with the reason.

### Design Validation
After all domains are processed, perform:
- Constraint validation against `specs/knowledge.md`
- Compatibility validation against AS-IS findings
- Migration risk assessment
- Gap analysis for unresolved decisions

### Outputs
Generate or update the following artifacts:

- `specs/design.md`
- `specs/ui-ux.md`
- `specs/api.md`
- `specs/database.md`
- `specs/impl.md`

Populate TO-BE sections only.

Preserve all existing AS-IS sections exactly as written and never overwrite them.

Update `specs/design.md` with:
- TO-BE System Architecture
- Architecture Pattern
- System Components
- Scalability & Availability
- Service Communication
- Non-Functional Requirements

Update `specs/ui-ux.md` with:
- TO-BE UI/UX Design
- Design System
- Personas and Devices
- Navigation Model
- Accessibility
- Internationalization
- Key Screen Inventory

Update `specs/api.md` with:
- TO-BE API Design
- API Style and Versioning
- Authentication and Authorization
- API Gateway
- Rate Limiting
- Backward Compatibility
- Standard Response Envelope
- Endpoint Inventory placeholder marked `[To be elaborated in Sprint 0]`

Update `specs/database.md` with:
- TO-BE Data Model
- Database Technology
- Data Architecture Pattern
- Migration Strategy
- Data Retention and Compliance
- Entity Model placeholder marked `[To be elaborated in Sprint 0]`

Update `specs/impl.md` with:
- Technology Stack Summary
- Development Standards
- Environment Configuration
- Security Standards
- CI/CD Pipeline
- Observability Stack
- Pending Design Decisions

Ensure:
- All design decisions reference the motivating constraint, expectation, business rule, or feature where applicable.
- Any conflict with customer expectations or constraints is explicitly flagged and resolved before proceeding.
- Any critical unanswered decision is recorded as `[DESIGN DECISION PENDING]` with an owner and impact.
- Endpoint inventories and detailed entity models are not fully elaborated during this phase and are deferred to Sprint 0.

Before generating the design files, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 15

Run the `spec-generation` skill.

### Inputs

* Skill definition: `.claude/spec-generation/SKILL.md`
* Authoritative inputs:

  * `specs/knowledge.md`
  * `specs/features.md`
  * `specs/design.md`
  * `specs/ui-ux.md`
  * `specs/api.md`
  * `specs/database.md`
  * `specs/impl.md`

### Execution

Read `specs/knowledge.md`, `specs/features.md`, `specs/design.md`, `specs/ui-ux.md`, `specs/api.md`, `specs/database.md`, and `specs/impl.md` as authoritative inputs.

Execute the skill exactly as defined, including:

* Phase 0: Input Validation
* Phase 1: Epic Derivation
* Phase 2: Story Derivation
* Phase 3: Task Derivation
* Phase 4: Cross-Cutting Task Generation
* Phase 5: Spec Review
* Phase 6: File Output
* Phase 7: Post-Generation Summary

### Input Validation

Extract and validate:

* Business context, business rules, workflows, constraints, customer expectations, and blockers from `specs/knowledge.md`
* All FR entries, priorities, acceptance notes, and open questions from `specs/features.md`
* TO-BE architecture, components, NFRs, and scalability requirements from `specs/design.md`
* Personas, screens, navigation, accessibility requirements, and design system information from `specs/ui-ux.md`
* TO-BE API conventions and patterns from `specs/api.md`
* TO-BE data architecture and migration information from `specs/database.md`
* Technology stack, environments, observability, and pending decisions from `specs/impl.md`

Perform prerequisite checks and report warnings for:

* Missing TO-BE design content
* Empty or insufficient feature coverage
* Missing `STATUS: REVIEWED ✓` in `specs/knowledge.md`
* Any `[DESIGN DECISION PENDING]` items

Generate the Source Summary exactly as defined in the skill, including:

* Source readiness status
* Warnings and blockers
* Proposed Epic Structure preview

Obtain user confirmation before proceeding with specification generation.

### Epic Derivation

Derive epics using:

* Feature categories from `specs/features.md`
* Technical foundation requirements from `specs/design.md`
* Data migration requirements from `specs/database.md`
* UI foundation requirements from `specs/ui-ux.md`
* Integration requirements from the source specifications

Ensure:

* Every epic represents a coherent deliverable slice.
* Epics contain approximately 3–8 stories.
* Epics exceeding 10 stories are split.
* Single-story epics are merged or demoted appropriately.

Apply:

* Epic numbering conventions
* Epic naming conventions
* Epic categorization tags

### Story Derivation

Generate stories from:

* Feature requirements
* Business rules
* Business workflows
* Technical requirements
* UI screens and workflows
* Migration activities

Ensure:

* Every story has traceable sources.
* Every story contains testable acceptance criteria.
* Dependencies are explicitly documented.
* Story complexity classifications are assigned.
* Stories remain within sprint-scale boundaries.

### Task Derivation

Generate tasks for every story.

Ensure:

* Every task belongs to a story.
* Every story belongs to an epic.
* Every task is scoped to 3 business days or fewer.
* Tasks exceeding 3 days are split.
* Tasks include:

  * Type classification
  * Effort estimate
  * Status
  * Blocking information
  * Description
  * Definition of Done
  * Technical References

Apply all task derivation heuristics defined in the skill.

### Cross-Cutting Task Generation

Generate applicable cross-cutting tasks, including:

* Sprint 0 foundation tasks
* Security tasks
* Observability tasks
* Documentation tasks

Ensure all generated tasks remain within the 3-business-day limit.

### Spec Review

Present the complete specification structure for review, including:

* Total epics
* Total stories
* Total tasks
* Estimated effort
* Epic summaries
* Blocked tasks
* Stories missing acceptance criteria
* Tasks exceeding sizing limits
* Uncovered feature requirements

Collect user feedback on:

* Epic boundaries
* Missing stories
* Deferred features
* Final approval to write files

### Outputs

Generate the following artifacts:

* `specs/spec.md`
* `specs/tasks.md`

Ensure `specs/spec.md` contains:

* Program Specification header
* Spec Summary
* Business Context
* Key Business Rules
* Epics and Stories
* Deferred Items
* Change Log

Ensure `specs/tasks.md` contains:

* Task Inventory header
* Task Summary
* Task Index
* Blocked Tasks
* Change Log

Ensure:

* The 3-business-day task ceiling is enforced without exception.
* No floating tasks exist.
* Full traceability is maintained.
* Acceptance criteria remain testable.
* Requirements are never invented.
* NICE TO HAVE items are deferred unless explicitly included.
* Both files are generated completely without placeholders, truncation, or "etc." references.

Before generating the spec files, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt


---

**Establish Strategy Complete**