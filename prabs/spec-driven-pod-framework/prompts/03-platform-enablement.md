# Platform Enablement

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

Platform Enablement Complete

---

## Prompt 1

Run the `knowledge-mesh` skill.

### Inputs
- Skill definition: `.claude/knowledge-mesh/SKILL.md`
- Authoritative inputs:
  - `specs/knowledge.md`
  - `specs/design.md`
  - `specs/api.md`
  - `specs/database.md`
  - `specs/features.md`
  - `specs/impl.md`
  - `artifacts/openspec.yaml`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/decision-ledger.md`
- Additional inputs (if available):
  - `artifacts/ai-manifest.json`
- Reference files:
  - `references/chunking-strategy.md`
  - `references/relevance-scoring.md`
  - `sample_input/sample-knowledge-query.yaml`
  - `sample_output/sample-retrieval-response.yaml`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Index Construction

Do not execute:
- Step 2: Query Handling
- Step 3: Invalidation Management
- Step 4: Coverage Assessment

Only execute these phases if they are explicitly triggered later in the sprint.

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Sprint identifier
- Source artifact versions used
- Whether a prior `artifacts/ai-manifest.json` was available
- Any assumptions required to complete indexing

### Step 1 — Index Construction

Validate the existence of all REQUIRED artifacts.

Verify the existence of:
- `specs/knowledge.md`
- `specs/design.md`
- `specs/api.md`
- `specs/database.md`
- `specs/features.md`
- `specs/impl.md`
- `artifacts/openspec.yaml`
- `artifacts/task-breakdown.yaml`
- `artifacts/decision-ledger.md`

If any REQUIRED artifacts are missing:
- List every missing artifact.
- Halt execution.
- Do not proceed with index generation.

If `artifacts/ai-manifest.json` is unavailable:
- Continue execution.
- Explicitly document that no prior generated artifact inventory was available.
- Exclude manifest-derived entries from the index summary.

Parse all available input files.

### Chunking

Chunk all indexed artifacts according to the strategy defined in the skill and supporting references.

Target chunk size:
- Approximately 300–500 tokens per chunk.

Apply the following chunking rules:

- `artifacts/openspec.yaml`
  - One chunk per requirement block.

- `specs/api.md`
  - One chunk per endpoint definition.

- `specs/database.md`
  - One chunk per table or entity definition.

- `specs/design.md`
  - One chunk per architectural layer or major section.

- `specs/knowledge.md`
  - One chunk per system domain or major knowledge section.

- `artifacts/decision-ledger.md`
  - One chunk per ADR or decision entry.

- `specs/features.md`
  - One chunk per feature group, epic, or capability grouping.

- `specs/impl.md`
  - One chunk per implementation area or major implementation concern.

- `artifacts/task-breakdown.yaml`
  - One chunk per cluster or logical task grouping.

- `artifacts/ai-manifest.json` (if available)
  - One chunk per generated artifact entry.

### Metadata Tagging

For every generated chunk, assign metadata containing:
- `chunk_id`
- `source_file`
- `section_heading`
- `requirement_ids`
- `sprint_id`
- `version_hash`
- `status`
- `chunk_type`

Populate metadata using the following rules:

- `requirement_ids`
  - Extract associated REQ identifiers where available.
  - Use an empty array if none exist.

- `status`
  - Default to `CURRENT`.

- `chunk_type`
  - Classify as appropriate:
    - `requirement`
    - `endpoint`
    - `entity`
    - `architecture`
    - `knowledge`
    - `decision`
    - `feature`
    - `implementation`
    - `task_cluster`
    - `generated_artifact`

Generate a flat index using the structure:

chunk_id → {
  content,
  metadata
}

### Index Validation

Calculate and document:
- Total chunk count
- Chunk count by source file
- Chunk count by chunk type
- Requirement coverage statistics
- Number of requirements with indexed context
- Number of chunks without requirement associations
- Number of chunks originating from prior generated artifacts
- Version hashes used during index generation

Identify and flag:
- Duplicate chunk identifiers
- Missing requirement mappings
- Empty sections that could not be indexed
- Documents that produced zero chunks

### Output Generation

Generate `knowledge-mesh-index.md`.

Ensure it contains:
- Sprint identifier
- Generation timestamp
- Index generation assumptions
- Input artifact inventory
- Chunk inventory summary
- Source distribution summary
- Chunk type distribution
- Requirement coverage map
- Version hash summary
- Chunk metadata catalogue
- Missing or low-context observations
- Index generation notes

Generate a Requirement Coverage section containing:
- Requirement ID
- Number of associated chunks
- Source files contributing context
- Coverage status

Generate a Chunk Metadata Catalogue containing:
- Chunk ID
- Source file
- Section heading
- Chunk type
- Requirement associations
- Status

### Constraints

Follow all processing rules, chunking rules, limitations, and execution behaviour defined in the `KnowledgeMesh` skill.

Do not:
- Execute retrieval requests.
- Perform relevance scoring.
- Generate retrieval responses.
- Process invalidation events.
- Produce `knowledge-coverage-report.md`.
- Produce `knowledge-mesh-invalidation.log`.

These capabilities remain dormant until explicitly triggered later in the sprint.

### Outputs
Generate or update:
- `knowledge-mesh-index.md`

Ensure `knowledge-mesh-index.md` contains:
- Sprint identifier
- Generation timestamp
- Input artifact inventory
- Index assumptions
- Chunk inventory summary
- Source distribution
- Chunk type distribution
- Requirement coverage map
- Version hash summary
- Chunk metadata catalogue
- Missing or low-context observations
- Index generation notes

Before generating the artifact, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 2

Run the `secret-shield` skill.

### Inputs
- Skill definition: `.claude/secret-shield/SKILL.md`
- Authoritative inputs:
  - All context payloads and source files that will be injected into LLM context windows during this sprint
- Reference files:
  - `references/secret-patterns.yaml`
  - `references/secret-whitelist.yaml`
  - `references/entropy-scoring.md`
  - `sample_input/sample-payload-with-secrets.txt`
  - `sample_output/sample-sanitised-payload.txt`
- Environment assumptions:
  - Multi-provider environment enabled (Claude, OpenAI, and other supported providers)

### Execution
Read all available context payloads and source files and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Pattern Matching (Regex)
- Step 2: Semantic / Entropy Analysis
- Step 3: Disposition Decision
- Step 4: Logging

SecretShield is a mandatory security gate.

Apply the scan before any payload is injected into an LLM context window.

Collect user inputs only if mandatory information required by the skill cannot be inferred from the available artifacts. Otherwise, use inferred values and explicitly state the assumptions made.

Determine and document:
- Total payloads scanned
- Source files scanned
- Context payload identifiers scanned
- Whether whitelist rules were applied
- Number of redactions performed
- Number of blocked payloads
- Number of advisory entropy findings

### Scope of Scanning

Scan all context payloads intended for injection into:
- DevCopilot
- KnowledgeMesh
- PromptBench
- ExperienceStudio
- Any other accelerator or build agent participating in the sprint

Apply scanning to:
- File contents passed as context
- `.env` files
- `.yaml` files
- `.json` files
- `.py` files
- `.ts` files
- `.sql` files
- Configuration files
- Code snippets
- API response payloads
- Database connection strings
- Shell command outputs
- Inline text payloads
- Any configuration-like content

### Step 1 — Pattern Matching (Regex)

Load and apply all patterns defined in:
- `references/secret-patterns.yaml`

Scan for all known credential formats, including:

- Anthropic API Keys
- OpenAI API Keys
- AWS Access Keys
- AWS Secret Keys
- JWT Tokens
- PostgreSQL Connection Strings
- Generic Secrets and Passwords
- Private Key Blocks
- GitHub Tokens
- Slack Tokens
- Google API Keys
- Bearer Tokens

For every high-confidence pattern match:

Determine:
- Pattern category
- Detection location
- Character position
- Severity level

Replace detected values using the defined placeholders:

- `[REDACTED:ANTHROPIC_API_KEY]`
- `[REDACTED:OPENAI_API_KEY]`
- `[REDACTED:AWS_ACCESS_KEY]`
- `[REDACTED:AWS_SECRET_KEY]`
- `[REDACTED:JWT_TOKEN]`
- `[REDACTED:DB_CONNECTION_STRING]`
- `[REDACTED:GENERIC_SECRET]`
- `[REDACTED:PRIVATE_KEY_BLOCK]`
- `[REDACTED:GITHUB_TOKEN]`
- `[REDACTED:SLACK_TOKEN]`
- `[REDACTED:GOOGLE_API_KEY]`
- `[REDACTED:BEARER_TOKEN]`

### Step 2 — Semantic / Entropy Analysis

For strings that do not match known patterns:

Perform semantic entropy analysis.

Calculate Shannon entropy.

Flag candidate strings satisfying all conditions:

- Entropy greater than 3.5 bits per character
- Length greater than or equal to 20 characters
- Not present in the whitelist

Classify these findings as:
- `[POSSIBLE_SECRET:HIGH_ENTROPY]`

For every advisory finding:

Determine:
- Detection location
- Entropy score
- Severity level
- Recommended review action

### Step 3 — Disposition Decision

Apply the following disposition rules exactly as defined by the skill.

For high-confidence pattern matches:
- Redact silently and continue payload delivery.

For high-confidence matches within context-critical payloads:
- Redact.
- Alert the POD Lead.
- Continue delivery using sanitised payloads.

For payloads containing multiple high-confidence detections:
- Block payload delivery.
- Prevent LLM injection.
- Alert the POD Lead immediately.

For high-entropy findings:
- Redact as possible secrets.
- Continue delivery.
- Record advisory findings.

For whitelist matches:
- Allow pass-through.
- Record whitelist usage.

For every payload processed:

Determine and document:
- Final disposition
- Whether payload delivery continued
- Whether the payload was blocked
- Whether POD Lead notification was required

### Step 4 — Logging

Generate append-only redaction records.

Log every detection event to:
- `secret-shield-redaction.log`

Do not log:
- Secret values
- Credential contents
- Original payload values

Each log entry must contain:
- Timestamp
- Severity
- File path or context identifier
- Pattern type
- Character position
- Action taken

Use the format defined by the skill.

### POD Lead Alerts

For every blocked payload or multi-secret detection:

Generate an immediate POD Lead alert containing:
- Context identifier or file path
- Number of detections
- Detection categories
- Action taken
- Recommended remediation
- Credential rotation recommendation where applicable

### Whitelist Management

Load and apply:
- `references/secret-whitelist.yaml`

Respect all whitelist definitions.

Document:
- Whitelist rules invoked
- False positives bypassed
- Reasons for pass-through

### Constraints

Follow all processing rules, limitations, escalation behaviour, and execution logic defined in the `SecretShield` skill.

Never:
- Log actual secret values.
- Expose credential contents.
- Include redacted values in reports.
- Bypass SecretShield processing for any payload destined for LLM injection.

Document any limitations encountered, including:
- Binary files that could not be scanned.
- Unsupported payload types.
- Ambiguous detections requiring manual review.

### Outputs

Generate or update:
- Sanitised context payloads
- `secret-shield-redaction.log`
- POD Lead alerts (when applicable)

Ensure sanitised payload outputs:
- Preserve original structure.
- Replace detected secrets with typed placeholders.
- Clearly indicate blocked payloads.

Ensure `secret-shield-redaction.log` remains append-only and contains:
- Timestamp
- Severity
- File path or context identifier
- Pattern category
- Character position
- Action taken

Ensure POD Lead alerts contain:
- Context identifier
- Detection count
- Detection categories
- Action taken
- Recommended remediation

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

### Check Block — data-contracts/

Silently check whether the `data-contracts/` folder exists and contains at least one `.yaml` file.

If it exists and is populated: proceed to Prompt 3 immediately.

If it does not exist or is empty, ask:

> "`data-contracts/` is needed before execution of `trust-fabric`. Do you want it to be generated from existing information?"

- If **yes**: run the skill at `.claude/artifacts-generation/create-data-contracts.md`. Once generated, ask the user to review the output and confirm whether any information should be added or updated. After review and any updates are made, ask for confirmation to proceed to Prompt 3.
- If **no**: ask the user to provide the `data-contracts/` folder with at least one entity contract file before proceeding. Do not continue to Prompt 3 until the folder is present and populated.

---

## Prompt 3

Run the `trust-fabric` skill.

### Inputs
- Skill definition: `.claude/trust-fabric/SKILL.md`
- Authoritative inputs:
  - `specs/database.md`
  - `specs/api.md`
  - `artifacts/openspec.yaml`
  - `artifacts/policy-catalogue.yaml`
  - All files in `data-contracts/`
- Additional inputs (if available):
  - `artifacts/task-breakdown.yaml`
  - Generated code modules submitted by DevCopilot
- Reference files:
  - `references/data-contract-schema.md`
  - `references/pii-taxonomy.md`
  - `references/pii-handling-rules.md`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Load Data Contract Registry
- Step 2: Profile Data Sources Used in Sprint
- Step 3: Validate Generated Code
- Step 4: Generate Compliance Report
- Step 5: Flag Unclassified Fields

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

### Key Validations
- Load and validate all data contracts from `data-contracts/`.
- Identify all data entities accessed within sprint scope.
- Treat entities without registered contracts as build blockers.
- Validate generated modules against the registered contracts and PII handling requirements.
- Apply all blocking rules, escalation rules, and compliance checks defined in the skill.
- Escalate all unclassified entities and fields to the POD Lead.
- Do not infer final classifications where contract definitions are missing.

### Outputs
Generate or update:
- `data-contract-compliance-report.md`
- `data-contract-violations.yaml`
- `unclassified-fields-report.md`

If invoked during Release, generate the TrustFabric governance attestation as defined in the skill.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 4

Run the `performance-optimizer` skill.

### Inputs
- Skill definition: `.claude/performance-optimizer/SKILL.md`
- Authoritative inputs:
  - `artifacts/task-breakdown.yaml`
  - `artifacts/openspec.yaml`
  - `artifacts/sprint-capacity.yaml`
- Additional inputs (if available):
  - Live token consumption data from agents/builders
  - PromptBench results
- Reference files:
  - `references/routing-matrix.md`
  - `references/budget-calibration.md`
  - `sample_input/sample-sprint-capacity.yaml`
  - `sample_output/sample-routing-decisions.yaml`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Task Profiling
- Step 2: Model Routing Decision
- Step 3: Budget Monitoring
- Step 4: Cost Reduction Recommendations

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

### Key Validations
- Profile every generation task by:
  - Complexity
  - Context size
  - Output type
- Apply the routing matrix exactly as defined in the skill.
- Apply any `quality_tier: premium` overrides found in `artifacts/openspec.yaml`.
- Generate a routing decision for every task in `artifacts/task-breakdown.yaml`.
- Initialise sprint token budget monitoring using `artifacts/sprint-capacity.yaml`.
- Calculate current budget status and projected consumption using available usage data.
- Apply all alert thresholds, escalation behaviour, and budget controls defined in the skill.
- Generate cost reduction recommendations whenever projected budget risk exceeds defined thresholds.

### Outputs
Generate or update:
- Routing decisions for all sprint tasks
- Initial Sprint Token Budget Dashboard

Generate `token-consumption-report.yaml` if end-of-sprint reporting is applicable.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 5

Run the `experience-studio` skill.

### Inputs
- Skill definition: `.claude/experience-studio/SKILL.md`
- Authoritative inputs:
  - `specs/ui-ux.md`
  - `artifacts/openspec.yaml`
  - `specs/design.md`
  - `specs/features.md`
- Additional inputs:
  - UI artefacts under review (screenshots, Figma exports, component code)
- Reference files:
  - `references/ux-elicitation-questions.md`
  - `references/journey-mapping-guide.md`
  - `references/conformance-scoring-rubric.md`
  - `sample_input/sample-ui-spec.md`
  - `sample_output/sample-conformance-report.md`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Parse Intent Hierarchy
- Step 2: Analyse Design Under Review
- Step 3: Conformance Evaluation
- Step 4: Produce Report

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

If `specs/ui-ux.md` is missing or insufficient, follow the elicitation protocol defined in the skill and ask the required questions one at a time before proceeding.

### Key Validations
- Extract all documented user journeys, experience goals, and stakeholder intent statements from `specs/ui-ux.md`.
- Map journeys to corresponding requirement IDs in `artifacts/openspec.yaml`.
- Build the journey-to-requirement coverage matrix.
- Evaluate every provided UI artefact against the documented journeys and requirements.
- Classify each journey as exactly one of:
  - `ALIGNED`
  - `DEVIATED`
  - `UNCOVERED`
  - `EXTENDED`
- Identify and document the specific intent clause violated for every `DEVIATED` journey.
- Flag all `EXTENDED` behaviours for POD Lead decision.
- Enumerate blocking revision requests for every `DEVIATED` and `UNCOVERED` journey.
- Issue Gate 2 attestation only if all journeys are `ALIGNED`.

### Outputs
Generate or update:
- `experience-conformance-report.md`

Ensure the report includes:
- Sprint identifier
- Review date
- Reviewer attribution
- Gate 2 status
- Journey-to-requirement coverage matrix
- Revision requests with journey and requirement references
- Notes for all `EXTENDED` items
- Gate 2 attestation or blocking rationale, as applicable

Before generating the report, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

### Check Block — .cursorrules

Silently check whether `.cursorrules` exists at the project root.

If it exists: proceed to the AGENTS.md check below.

If it does not exist, ask:

> "`.cursorrules` is needed before execution of `dev-copilot`. Do you want it to be generated from existing information?"

- If **yes**: run the skill at `.claude/artifacts-generation/create-cursorrules.md`. Once generated, ask the user to review the output and confirm whether any information should be added or updated. After review and any updates are made, proceed to the AGENTS.md check below.
- If **no**: ask the user to provide `.cursorrules` at the project root before proceeding. Do not continue until it is available.

---

### Check Block — AGENTS.md

Silently check whether `AGENTS.md` exists at the project root.

If it exists: proceed to Prompt 6 immediately.

If it does not exist, ask:

> "`AGENTS.md` is needed before execution of `dev-copilot`. Do you want it to be generated from existing information?"

- If **yes**: run the skill at `.claude/artifacts-generation/create-agents.md`. Once generated, ask the user to review the output and confirm whether any information should be added or updated. After review and any updates are made, ask for confirmation to proceed to Prompt 6.
- If **no**: ask the user to provide `AGENTS.md` at the project root before proceeding. Do not continue to Prompt 6 until it is available.

---

## Prompt 6


### Inputs
- Skill definition: `.claude/dev-copilot/SKILL.md`
- Authoritative inputs:
  - `artifacts/task-breakdown.yaml`
  - `artifacts/openspec.yaml`
  - `artifacts/ai-manifest.json`
  - `specs/design.md`
  - `specs/api.md`
  - `specs/database.md`
  - `artifacts/policy-catalogue.yaml`
  - `.cursorrules`
  - `AGENTS.md`
- Client org standards (if present): `context/org-standards.md`
- Context and governance inputs:
  - KnowledgeMesh retrieval results relevant to the assigned task
  - TrustFabric flags and data contract constraints relevant to the entities accessed
- Reference files:
  - `references/coding-conventions.md`
  - `references/stack-patterns.md`
  - `references/provenance-header-spec.md`
  - `references/ambiguity-escalation-guide.md`
  - `sample_input/sample-task-context.yaml`
  - `sample_output/sample-generated-module.py`

### Context Check
Before beginning task context assembly, check whether `context/org-standards.md` exists.
- If it exists: load it as hard constraints for dimension D4 (Convention Compliance), taking precedence over `.cursorrules` and `AGENTS.md` where they conflict. No user prompt needed — proceed directly.
- If it does not exist: ask the user once — *"Would you like to provide an org standards document in `context/org-standards.md` before code generation begins? (Yes / No)"* — and wait for their answer before continuing.

### Execution
Ask the user:

> "Would you like to implement epic-wise or task-wise?
**epic-wise:** 

Run the `DevCopilot` skill to implement ALL tasks under EXACTLY ONE epic: <EPIC_ID>.

<inputs>
Load and treat the following as authoritative, in this precedence order
(higher overrides lower on conflict):
1. AGENTS.md            — engineering conventions, constraints, operating rules
2. spec/spec.md         — product & technical specification (source of truth for intent)
3. spec/tasks.md        — task breakdown; locate ALL tasks belonging to <EPIC_ID>
4. Existing codebase    — current patterns, modules, and contracts to extend/reuse
</inputs>

<scope>
- Implement ONLY the tasks whose epic is <EPIC_ID>. Do not implement tasks from other
  epics, or "obvious next steps", unless they are explicit, in-scope dependencies.
- Enumerate the in-scope tasks first and confirm the set is complete before proceeding.
- If a task in <EPIC_ID> depends on a task OUTSIDE the epic that is unimplemented,
  STOP and report it as a blocking dependency (see Clarification Gate).
- Resolve and respect intra-epic dependency order. If ordering is ambiguous or cyclic,
  treat it as BLOCKING and ask.
</scope>

<no-assumption-rule>
Do NOT proceed on assumptions for anything that materially affects correctness, interfaces,
or design. This includes (non-exhaustive): file paths/locations, module or function names,
API contracts (routes, payloads, status codes), data schemas, library/framework choices,
auth model, error-handling strategy, config/env values, acceptance criteria, AND any
contract SHARED across tasks in the epic (a shared schema, interface, or module used by
more than one task must be unambiguous before generation).

Classify every unknown as:
  - BLOCKING  → cannot be inferred unambiguously from <inputs>. You MUST ask.
  - DEFERRABLE → a low-risk, reversible default exists. State it explicitly as an
                 assumption in your plan; do not ask, but flag it for review.

If in doubt whether something is BLOCKING, treat it as BLOCKING and ask.
Never invent values to fill a gap.
</no-assumption-rule>

<workflow>
1. Resolve <EPIC_ID> in spec/tasks.md and ENUMERATE every task under it (ID + title).
   If the epic is not found, has zero tasks, or the membership is ambiguous, STOP and ask.
2. For EACH task, build a requirement model: intended behavior, in/out scope, dependencies,
   and acceptance criteria (cite the spec/tasks lines you derived them from).
3. Run ONE consolidated gap analysis across ALL tasks. Deduplicate shared unknowns so the
   user answers each question once. Separate BLOCKING from DEFERRABLE.
4. CLARIFICATION GATE:
   - If ANY BLOCKING unknowns exist → output ONLY the Clarification Request below and STOP.
     Generate NO code or artifacts.
   - If NO BLOCKING unknowns exist → output the Epic Implementation Plan below and AWAIT "NEXT".
5. On "NEXT" → generate artifacts in dependency order. By default, generate task-by-task and
   pause after each for review; if the user replies "ALL", generate the remaining tasks
   without intermediate pauses.
</workflow>

<output-formats>
[A] CLARIFICATION REQUEST (when blocking unknowns exist):
  - One-line restatement of the epic + the enumerated task list.
  - Numbered questions, each with: the unknown, which task(s) it affects, why it blocks,
    and 2–3 candidate options if proposable. Order by impact (epic-wide blockers first).
  - End with: "Answer the numbered questions above; I will not generate until resolved."

[B] EPIC IMPLEMENTATION PLAN (when ready to generate):
  - Enumerated task list in planned dependency/build order.
  - 3–5 bullets summarizing the overall approach.
  - Per task: files to be created/modified (exact paths) and the acceptance criteria it satisfies.
  - Stated assumptions (DEFERRABLE defaults) — explicitly labeled, grouped by task.
  - End with: "Reply NEXT to generate task-by-task, ALL to generate the whole epic,
    or correct any assumption/path/order above first."
</output-formats>

Begin at Workflow step 1 for <EPIC_ID> = EPIC-002.

**If task-wise:**

Run the `DevCopilot` skill to implement EXACTLY ONE task: <TASK_ID>.

<inputs>
Load and treat the following as authoritative, in this precedence order
(higher overrides lower on conflict):
1. AGENTS.md            — engineering conventions, constraints, operating rules
2. spec/spec.md         — product & technical specification (source of truth for intent)
3. spec/tasks.md        — task breakdown; locate the single task matching <TASK_ID>
4. Existing codebase    — current patterns, modules, and contracts to extend/reuse
</inputs>

<scope>
- Implement ONLY <TASK_ID>. Do not implement sibling tasks, the parent epic,
  or "obvious next steps" unless they are explicit, in-scope dependencies of <TASK_ID>.
- If <TASK_ID> depends on an unimplemented task, STOP and report the blocking dependency
  (see Clarification Gate). Do not silently implement the dependency.
</scope>

<no-assumption-rule>
Do NOT proceed on assumptions for anything that materially affects correctness, interfaces,
or design. This includes (non-exhaustive): file paths/locations, module or function names,
API contracts (routes, payloads, status codes), data schemas, library/framework choices,
auth model, error-handling strategy, config/env values, and acceptance criteria.

Classify every unknown as:
  - BLOCKING  → cannot be inferred unambiguously from <inputs>. You MUST ask.
  - DEFERRABLE → a low-risk, reversible default exists. State it explicitly as an
                 assumption in your plan; do not ask, but flag it for review.

If in doubt whether something is BLOCKING, treat it as BLOCKING and ask.
Never invent values to fill a gap.
</no-assumption-rule>

<workflow>
1. Resolve <TASK_ID> in spec/tasks.md. If not found or ambiguous, STOP and ask.
2. Build a requirement model for the task: intended behavior, in/out scope,
   dependencies, and acceptance criteria (cite the spec/tasks lines you derived them from).
3. Run a gap analysis against <no-assumption-rule>. Separate BLOCKING from DEFERRABLE.
4. CLARIFICATION GATE:
   - If ANY BLOCKING unknowns exist → output ONLY the Clarification Request below and STOP.
     Generate NO code or artifacts.
   - If NO BLOCKING unknowns exist → output the Implementation Plan below and AWAIT "NEXT".
5. On receiving "NEXT" → generate the implementation artifacts for <TASK_ID>.
</workflow>

<output-formats>
[A] CLARIFICATION REQUEST (when blocking unknowns exist):
  - Restate the task in one line (with its tasks.md ID/title).
  - Numbered questions, each with: the unknown, why it blocks, and 2–3 candidate options
    if you can propose them. Order by impact.
  - End with: "Answer the numbered questions above; I will not generate until resolved."

[B] IMPLEMENTATION PLAN (when ready to generate):
  - 3–5 bullets: what will be built and the approach.
  - Files to be created/modified (exact paths).
  - Stated assumptions (DEFERRABLE defaults) — explicitly labeled.
  - Acceptance criteria this implementation will satisfy.
  - End with: "Reply NEXT to generate, or correct any assumption/path above first."
</output-formats>

Begin at Workflow step 1 for <TASK_ID> = <FILL IN>.

Before generating the implementation, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 7

Run the `prompt-bench` skill.

### Inputs
- Skill definition: `.claude/prompt-bench/SKILL.md`
- Required inputs:
  - Candidate prompt variants provided by the AI Builder
  - POD Lead-curated query sample set
  - `artifacts/openspec.yaml`
  - Target model list
- Evaluation inputs:
  - Evaluation criteria (provided by POD Lead or derived from the specification)
- Reference files:
  - `references/evaluation-methods.md`
  - `references/model-pricing.md`
  - `references/sample-set-guidance.md`
  - `sample_input/sample-benchmark-request.yaml`
  - `sample_output/sample-bench-report.md`

### Execution
Read all required artifacts and execute the skill exactly as defined.

Benchmark the supplied prompt variants against the selected models and representative query set.

Execute the following steps in order:
- Step 1: Benchmark Matrix Construction
- Step 2: Execute Benchmark Runs
- Step 3: Aggregate Metrics
- Step 4: Ranking
- Step 5: Winner Recommendation

Collect the mandatory inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Prompt variants under evaluation
- Query sample size and characteristics
- Models included in the benchmark
- Evaluation methodology used
- NFR thresholds derived from `openspec.yaml`

### Input Validation
Verify that the following inputs are available:

- Candidate prompt variants (2–5 variants)
- Query sample set (10–50 representative queries)
- Target model list
- Evaluation method
- `artifacts/openspec.yaml`

If any required input is missing:
- List all missing inputs.
- Halt execution.
- Do not proceed with benchmarking until they are supplied.

### Step 1 — Benchmark Matrix Construction
Construct the benchmark matrix using:

Rows:
- Each query from the curated sample set

Columns:
- Every prompt variant × model combination

For each matrix cell, capture:
- Generated response
- Quality score
- Latency (ms)
- Input tokens
- Output tokens
- Cost (USD)

### Step 2 — Execute Benchmark Runs
For every `(prompt variant, model, query)` combination:

Execute the benchmark and record:
- Response output
- Latency in milliseconds
- Input token count
- Output token count
- Estimated or actual cost

Evaluate response quality using the selected evaluation method:

- LLM-as-judge
- Exact-match against ground truth
- Human-defined rubric

Document the scoring methodology applied.

If live API execution is not explicitly authorised:
- Use simulated or recorded benchmark execution.
- Clearly state that results are simulated.

### Step 3 — Aggregate Metrics
For each `(variant, model)` pair, calculate:

- `quality_avg`
- `quality_p10`
- `latency_p50`
- `latency_p95`
- `cost_per_1k`
- `nfr_quality_pass`
- `nfr_latency_pass`
- `nfr_cost_pass`

Evaluate pass/fail status against NFR targets extracted from `artifacts/openspec.yaml`.

### Step 4 — Ranking
Rank all evaluated combinations using:

1. Best Quality
   - Highest `quality_avg` among NFR-passing combinations.

2. Best Cost
   - Lowest `cost_per_1k` among NFR-passing combinations.

3. Best Balanced
   - Composite score:
     `0.5 × quality_norm + 0.3 × cost_norm_inv + 0.2 × latency_norm_inv`

Identify:
- Top-performing combinations
- NFR failures
- Borderline candidates

### Step 5 — Winner Recommendation
Recommend the default production candidate using the Best Balanced ranking.

For the recommended winner, provide:
- Variant identifier
- Model name
- Balanced score
- NFR status
- Rationale for recommendation

For all rejected candidates:
- Explain why they were not selected.
- Identify specific NFR failures where applicable.

### Outputs
Generate:
- `prompt-bench-report.md`
- `prompt-bench-nfr-evidence.yaml`

Ensure `prompt-bench-report.md` contains:
- Feature identifier
- Sprint identifier
- Benchmark date
- Sample size
- Variants tested
- Models tested
- Recommended winner
- Recommendation rationale
- NFR thresholds
- Results matrix
- Variant descriptions
- Failure analysis
- Model routing recommendation

Ensure `prompt-bench-nfr-evidence.yaml` contains:
- Every variant/model combination evaluated
- Aggregated metrics
- NFR pass/fail evidence
- Structured release-gate evidence suitable for downstream consumption.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 8

Run the `review-pilot` skill.

### Inputs
- Skill definition: `.claude/review-pilot/SKILL.md`
- Required inputs:
  - PR diff (changed files + line diffs)
  - `artifacts/openspec.yaml`
- Additional inputs (if available):
  - `.cursorrules`
  - `AGENTS.md`
  - TrustFabric compliance flags
  - `artifacts/ai-manifest.json`
  - `specs/design.md`
- Reference files:
  - `references/review-checklist.md`
  - `references/spec-conformance-guide.md`
  - `sample_input/sample-pr-diff.md`
  - `sample_output/sample-review-report.md`

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Extract PR Metadata
- Step 2: Spec Conformance Check
- Step 3: Convention Compliance Check
- Step 4: Structural Analysis
- Step 5: Classification and Output

Collect the mandatory inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- PR identifier
- Changed files under review
- Requirement IDs affected
- TrustFabric review status
- Available architecture and convention context

### Input Validation
Verify that the following inputs are available:

- PR diff (changed files and line diffs)
- `artifacts/openspec.yaml`

If any minimum required inputs are missing:
- List every missing input.
- Halt execution.
- Do not proceed with review.

Document which enhancement inputs are available:
- `.cursorrules`
- `AGENTS.md`
- TrustFabric compliance flags
- `artifacts/ai-manifest.json`
- `specs/design.md`

If enhancement inputs are unavailable:
- Continue the review.
- Explicitly document the reduced review scope.

### Step 1 — Extract PR Metadata
From the PR diff:

1. Identify all changed files.
2. Extract provenance headers from each changed file:
   - `@spec:`
   - `@task:`
3. Build the traceability map:

```
file → requirement_id → acceptance_criteria
```

Validate provenance compliance.

If any changed file lacks provenance headers:
- Create a `MISSING_PROVENANCE` finding.
- Classify it as `BLOCKING`.

Document:
- File path
- Missing header details
- Required remediation.

### Step 2 — Spec Conformance Check
For each requirement ID identified:

1. Load the associated acceptance criteria from `artifacts/openspec.yaml`.
2. Review the implementation against every criterion.
3. Assign one of the following verdicts:

- `PASS`
- `FAIL`
- `PARTIAL`
- `UNTESTABLE`

For every acceptance criterion reviewed, document:
- Requirement ID
- Acceptance criterion
- Verdict
- Supporting notes.

Apply classification rules:

- `FAIL`
  → BLOCKING

- `PARTIAL`
  → ADVISORY

- `UNTESTABLE`
  → INFORMATIONAL requiring POD Lead review.

Generate a spec conformance verdict for each requirement.

### Step 3 — Convention Compliance Check
Review all changed files against `.cursorrules`.

#### Python Checks
Evaluate:

- No `print()` statements (CR-002)
- All parameters type annotated (CR-001)
- No raw SQL strings (CR-007)
- Route handlers contain exception handling (CR-003)
- PII fields absent from response schemas (CR-004)
- Functions contain docstrings

Classify findings exactly as defined:

- BLOCKING:
  - `print()`
  - raw SQL
  - missing exception handling
  - PII exposure

- ADVISORY:
  - missing type annotations

- INFORMATIONAL:
  - missing docstrings

#### TypeScript / React Checks
Evaluate:

- No `console.log` statements (CR-T001)
- No `any` usage (CR-T003)
- API access via `api-client.ts` only (CR-T002)
- Loading states for async operations (CR-T006)
- Error states for async operations (CR-T006)
- Props interfaces defined (CR-T007)

Classify findings exactly as defined:

- BLOCKING:
  - `console.log`
  - direct API calls outside `api-client.ts`

- ADVISORY:
  - `any` usage
  - missing loading/error states
  - missing props interfaces

### Step 4 — Structural Analysis
Validate structural conformance using `specs/design.md`.

Detect and report:

- Files located in inappropriate architectural layers
- Business logic implemented directly in route handlers
- Direct database access from route layers
- Missing service-layer abstractions
- Missing tests for new components or services
- Circular imports (Python)
- Duplicate implementations already registered in `artifacts/ai-manifest.json`

For each issue identified:
- Describe the violation.
- Reference the applicable architectural rule.
- Assign severity:
  - BLOCKING
  - ADVISORY
  - INFORMATIONAL

### Step 5 — Classification and Output
Aggregate all findings.

Classify every finding as:
- BLOCKING
- ADVISORY
- INFORMATIONAL

Calculate:
- Total blocking findings
- Total advisory findings
- Total informational findings

Determine the overall review verdict:

- APPROVED
  → No blocking findings.

- CHANGES_REQUIRED
  → One or more blocking findings exist.

- POD_LEAD_REVIEW_REQUIRED
  → No blockers, but unresolved UNTESTABLE findings remain.

### Outputs
Generate:
- `pr-review-report.md`
- `review-verdict.yaml`

Ensure `pr-review-report.md` contains:

- PR identifier
- Sprint identifier
- Reviewer details
- Review date
- Overall verdict
- Finding counts by severity
- Spec Conformance section
- Requirement-level verdicts
- Blocking Findings section
- Advisory Findings section
- Informational Findings section
- Final merge recommendation

For Spec Conformance, include:
- Requirement IDs reviewed
- Acceptance criteria evaluated
- PASS / FAIL / PARTIAL / UNTESTABLE verdicts
- Notes supporting each decision.

For Blocking Findings, include:
- Finding identifier
- Category
- File and line reference
- Description
- Required remediation.

For Advisory Findings, include:
- Recommendation
- Suggested follow-up actions.

For Informational Findings, include:
- Builder awareness notes.

Ensure `review-verdict.yaml` contains:
- PR identifier
- Sprint identifier
- Overall verdict
- Blocking count
- Advisory count
- Informational count
- Requirement-level verdicts
- Failing criteria references.

Before generating the review report, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 9

Run the `nexus-deploy` skill.

### Inputs
- Skill definition: `.claude/nexus-deploy/SKILL.md`
- Authoritative inputs:
  - `artifacts/task-breakdown.yaml`
  - `artifacts/openspec.yaml`
  - `artifacts/ai-manifest.json`
  - `artifacts/review-verdict.yaml`
  - `data-contract-violations.yaml`
  - `prompt-bench-nfr-evidence.yaml`
- Additional inputs:
  - Source code modules containing provenance headers
  - Infrastructure configuration files

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Build Artifact Registry
- Step 2: Completeness Validation
- Step 3: Deploy Manifest Preparation
- Step 4: Update `ai-manifest.json`

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Whether this invocation is a completeness check or deploy manifest generation.
- Any requirements explicitly deferred from completeness validation.
- The rollout strategy to apply.
- Any infrastructure sequencing requirements.

### Step 1 — Build Artifact Registry
Build the artifact registry from provenance headers.

- Parse all source files containing provenance headers.
- Extract:
  - Requirement ID
  - Task ID
  - Generated date
  - Artifact file path
  - Checksum (if available)
- Build the registry:
  - `requirement_id → [artifact_file_path, task_id, generated_date, checksum]`
- Cross-reference the registry against `artifacts/ai-manifest.json`.
- Merge prior sprint artifacts with current sprint additions.

### Step 2 — Completeness Validation
For every requirement ID in `artifacts/task-breakdown.yaml`, verify:

- At least one artifact exists with the matching requirement ID.
- `artifacts/review-verdict.yaml` indicates approval for that requirement.
- `data-contract-violations.yaml` contains no unresolved violations for that requirement.
- `prompt-bench-nfr-evidence.yaml` indicates PASS for AI-enabled requirements.

Classify each requirement using the statuses defined in the skill:
- `COMPLETE`
- `ARTIFACT_MISSING`
- `REVIEW_PENDING`
- `REVIEW_BLOCKED`
- `POLICY_VIOLATION`
- `NFR_FAIL`

Generate and document the completeness status for every requirement.

### Step 3 — Deploy Manifest Preparation
If all requirements are classified as `COMPLETE`:

- Generate `deploy-manifest.yaml`.
- Compute checksums for verified artifacts.
- Include rollout strategy details.
- Include deployment sequencing requirements.
- Build the deployment definition from the verified artifact set.

If any requirements are not `COMPLETE`:

- Generate the sprint completeness report.
- Explicitly list every blocker.
- Include recommended remediation actions.
- Do not generate `deploy-manifest.yaml`.

### Step 4 — Update Manifest
Update `artifacts/ai-manifest.json`.

- Register all verified sprint artifacts.
- Preserve provenance information.
- Mark superseded artifacts where applicable.
- Update the component index for downstream consumers.

### Outputs
Generate:
- `sprint-completeness-report.md`

Generate when all requirements are COMPLETE:
- `deploy-manifest.yaml`

Update:
- `artifacts/ai-manifest.json`

Before generating the artifacts, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 10

Run the `guardian` skill.

### Inputs
- Skill definition: `.claude/guardian/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/ai-manifest.json`
  - `artifacts/traceability-report.md`
- Additional inputs (if available):
  - Source code modules in `src/**`
  - `artifacts/eval-rubric.yaml`

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following modes in order:
- Generation Mode
- Execution + Triage Mode

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Whether `openspec.yaml` is present and locked.
- Whether source modules are available for execution mode.
- Whether any acceptance criteria require clarification before test generation proceeds.

### Gate Check
Validate that:
- `artifacts/openspec.yaml` exists.
- `openspec.yaml` is locked and approved for validation.

If `openspec.yaml` is missing or unlocked:
- Halt execution.
- Report that Gate 0 must be completed before Guardian can proceed.
- Do not generate tests or execute validation activities.

## Generation Mode

### Step G1 — Parse Acceptance Criteria
- Read `artifacts/openspec.yaml`.
- Extract all acceptance criteria.
- Map every criterion to its requirement ID using `artifacts/traceability-report.md`.
- Identify associated components using `artifacts/ai-manifest.json`.

### Step G2 — Elicit Missing Context
For each acceptance criterion, determine whether it contains:
- A measurable pass/fail condition.
- A clearly defined actor.
- Expected outcomes.
- Boundary values or thresholds where applicable.

If ambiguity exists:
- Pause generation for the affected requirement.
- Ask the POD Lead for clarification exactly as defined in the skill.
- Do not generate tests for ambiguous criteria until clarification is provided.

### Step G3 — Generate Gherkin Feature Files
Generate `.feature` files for all unambiguous requirements.

For every acceptance criterion:
- Generate at least one happy-path scenario.
- Generate at least one negative or edge-case scenario.
- Generate additional boundary scenarios for numeric thresholds.

Ensure every scenario includes:
- A matching `@REQ-[ID]` tag.
- A component tag derived from `artifacts/ai-manifest.json`.

Generate scenarios following the Gherkin structure defined in the skill, including:
- Feature description.
- Business value statement.
- Background section.
- Happy-path scenarios.
- Negative and edge-case scenarios.

### Step G4 — Initial Coverage Map
Generate the initial coverage report containing:
- Total requirements.
- Requirements covered by generated scenarios.
- Requirements without scenarios.
- Coverage percentage.
- Any identified coverage gaps.

## Execution + Triage Mode

### Step E1 — Identify Available Modules
- Scan `src/**` for available source modules.
- Cross-reference `artifacts/ai-manifest.json`.
- Identify:
  - Components.
  - Builders.
  - Associated requirement IDs.

If source modules are unavailable:
- Report that execution mode cannot proceed.
- Preserve generation outputs.

### Step E2 — Execute Tests
For all executable scenarios:
- Execute tests against available modules.
- Capture:
  - Scenario status.
  - Actual versus expected results.
  - Failure details.
  - Error messages or stack traces.
  - Execution timestamps.

### Step E3 — Failure Triage
For every failed scenario, classify the failure into exactly one category:

- `SPEC_ERROR`
- `CODE_ERROR`
- `ENV_ERROR`

Do not allow any failure to remain untriaged.

If Guardian cannot determine the classification:
- Ask the POD Lead using the clarification prompt defined in the skill.
- Finalise the report only after classification is provided.

### Step E4 — Generate Test Results
Generate `artifacts/test-results.json`.

Include:
- Sprint identifier.
- Execution timestamp.
- Summary statistics.
- Scenario-level results.
- Requirement mappings.
- Component mappings.
- Builder ownership.
- Triage classifications.
- Failure details where applicable.

### Step E5 — Final Coverage Report
Update the coverage report to include:
- Requirement-level pass rates.
- Open failures by triage category.
- Coverage percentage.
- Release gate verdict.

Determine the Release gate outcome using the skill rules:

- PASS:
  - Coverage ≥ 80%.
  - Zero untriaged failures.

- BLOCK:
  - Coverage < 80%.
  - Any untriaged failures remain.

### Outputs
Generate:
- `tests/*.feature`
- `artifacts/test-results.json`
- `artifacts/coverage-report.md`

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

### Check Block — artifacts/golden-references/

> `artifacts/golden-references/` is required to be provided and should contain ideal, human-approved output examples for each feature undergoing AI evaluation — these are the reference answers that `eval-harness` uses to score AI-generated outputs across dimensions such as accuracy, tone, completeness, conciseness, and safety. One golden reference file is required per evaluated feature. Please provide the necessary files at `artifacts/golden-references/` before proceeding.

Do not proceed to Prompt 11 until `artifacts/golden-references/` exists and contains at least one golden reference file per feature requiring evaluation.

---

## Prompt 11

Run the `eval-harness` skill.

### Inputs
- Skill definition: `.claude/eval-harness/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - Golden references in `artifacts/golden-references/`
- Additional inputs:
  - AI-generated outputs from Guardian
  - `artifacts/eval-rubric-prev.yaml` (if available)

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following phases in order:
- Phase 1: Rubric Construction
- Phase 2: Evaluation Execution
- Phase 3: Drift Detection (if prior rubric exists)

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Whether golden references exist for all features requiring evaluation.
- Whether AI-generated outputs from Guardian are available for scoring.
- Whether a prior sprint rubric exists for drift detection.

### Phase 1 — Rubric Construction

#### Step R1 — Extract Semantic Criteria
Read `artifacts/openspec.yaml` and extract all semantic evaluation dimensions, including:
- Accuracy
- Tone
- Completeness
- Conciseness
- Safety
- Groundedness
- Any custom evaluation dimensions defined in the specification

Identify the features requiring semantic evaluation.

#### Step R2 — Golden Reference Validation
Verify that golden references exist for every evaluated feature.

If a feature lacks a golden reference:
- Halt evaluation for that feature.
- Prompt the POD Lead exactly as defined in the skill to:
  - Provide a golden output example, or
  - Define minimum acceptable thresholds, or
  - Reference a prior sprint's golden output.

Do not proceed to scoring without at least one golden reference per evaluated feature.

#### Step R3 — Generate Rubric
Generate `artifacts/eval-rubric.yaml`.

For each evaluated feature:
- Define evaluation dimensions.
- Define dimension weights.
- Define minimum acceptable scores.
- Include scoring guides.
- Link the corresponding golden reference.
- Define the overall pass threshold.

### Phase 2 — Evaluation Execution

#### Step E1 — Receive Outputs for Scoring
Collect AI-generated outputs from Guardian.

Identify:
- The originating feature.
- The associated requirement or scenario.
- The matching rubric and golden reference.

#### Step E2 — Score Outputs
Evaluate each output using the rubric and golden reference.

For every output:
- Score each dimension on the 1–5 scale defined by the skill.
- Provide a one-sentence rationale for each dimension score.
- Apply the internal evaluation structure defined in the skill.

#### Step E3 — Compute Aggregate Scores
For each evaluated output:
- Calculate the weighted aggregate score.
- Determine pass or fail status.
- Verify that all safety scores meet the minimum thresholds.

Document:
- Dimension-level scores.
- Weighted scores.
- Pass/fail outcomes.

### Phase 3 — Drift Detection
If `artifacts/eval-rubric-prev.yaml` exists:

- Compare current and prior sprint dimension means.
- Identify any dimension whose mean score shifts by more than 0.5 points.
- Determine whether the shift represents:
  - Positive drift, or
  - Negative drift.
- Document the affected dimensions and magnitude of change.

If drift is detected:
- Generate `artifacts/eval-drift-alert.md`.

### Outputs
Generate:
- `artifacts/eval-rubric.yaml`
- `artifacts/eval-results.json`
- `artifacts/eval-summary.md`

Generate if drift is detected:
- `artifacts/eval-drift-alert.md`

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 12

Run the `red-team-x` skill.

### Inputs
- Skill definition: `.claude/red-team-x/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/ai-manifest.json`
  - `artifacts/eval-rubric.yaml`
  - Source prompts and handlers in `src/`
  - `references/adversarial-vector-library.yaml`
- Additional inputs:
  - `artifacts/policy-catalogue.yaml` (if available)

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step R1: Component Inventory & Risk Profiling
- Step R2: Attack Suite Generation
- Step R3: Execute Adversarial Tests
- Step R4: Remediation Recommendations
- Step R5: Compile Adversarial Test Results

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- The inventory of AI-facing components.
- The risk classification of each component.
- Whether domain-specific attack scenarios exist.
- The maximum acceptable successful attack rate.

### Step R1 — Component Inventory & Risk Profiling
Read `artifacts/ai-manifest.json` and identify all AI-facing components.

For each component:
- Determine the associated requirement IDs.
- Read the risk classification from `artifacts/openspec.yaml`.
- Classify each component as:
  - `CRITICAL`
  - `HIGH`
  - `MEDIUM`
  - `LOW`

If the following cannot be inferred from the available artifacts, collect them from the POD Lead exactly as defined in the skill:
- Safety-critical components not already identified.
- Domain-specific attack scenarios.
- Maximum acceptable successful attack rates.

### Step R2 — Attack Suite Generation
Using `references/adversarial-vector-library.yaml`, generate targeted adversarial inputs for each component.

Cover all six attack categories:
- Prompt Injection
- Jailbreak / Role Confusion
- PII Extraction Probes
- Data Exfiltration
- Boundary Manipulation
- Semantic Manipulation

Map attack vectors to component function rather than applying all vectors indiscriminately.

Generate at minimum:
- 5 attack vectors per `CRITICAL` component
- 3 attack vectors per `HIGH` component
- 2 attack vectors per `MEDIUM` component
- 1 attack vector per `LOW` component

### Step R3 — Execute Adversarial Tests
Execute the generated adversarial suite against the source prompts and handlers in `src/`.

For each adversarial input:
- Submit the input to the target component.
- Capture the complete output.
- Score the output using the safety dimension defined in `artifacts/eval-rubric.yaml`.
- Classify the response as:
  - `ROBUST`
  - `DEGRADED`
  - `VULNERABLE`

Apply the classification rules exactly as defined in the skill.

If any `VULNERABLE` finding is identified:
- Treat it as an immediate blocker.
- Surface the finding to the POD Lead before proceeding further.

### Step R4 — Remediation Recommendations
For every `VULNERABLE` or `DEGRADED` finding, generate remediation guidance including:
- Target component.
- Attack category and specific vector.
- Classification.
- Observed output.
- Why the behaviour is problematic.
- Recommended remediation options.
- Validation guidance specifying which vector must be re-run after remediation.

### Step R5 — Compile Adversarial Test Results
Compile the full adversarial testing results.

Apply the resilience classification rules:

- `SAFE`
  - Zero `VULNERABLE` findings.
  - `DEGRADED` findings ≤ 10%.

- `CONDITIONAL`
  - Zero `VULNERABLE` findings.
  - `DEGRADED` findings between 11–25%.

- `BLOCKED`
  - Any `VULNERABLE` finding.
  - `DEGRADED` findings > 25%.

Apply all HITL gates defined in the skill, including:
- Immediate POD Lead notification for `VULNERABLE` findings.
- POD Lead review for `CRITICAL` components with `DEGRADED` findings.
- Confirmation before adding novel attack vectors to the library.
- Collection of domain-specific attack vectors where applicable.

### Outputs
Generate:
- `artifacts/adversarial-test-suite.json`
- `artifacts/vulnerability-report.md`
- `artifacts/redteam-summary.md`

Ensure `artifacts/adversarial-test-suite.json` contains:
- Component inventory.
- Risk classifications.
- Attack vectors executed.
- Outputs captured.
- Safety scores.
- ROBUST / DEGRADED / VULNERABLE classifications.

Ensure `artifacts/vulnerability-report.md` contains:
- Human-readable findings.
- Remediation recommendations.
- Validation guidance.
- Blocking vulnerabilities clearly identified.

Ensure `artifacts/redteam-summary.md` contains:
- Sprint-level safety verdict.
- SAFE / CONDITIONAL / BLOCKED classification.
- Component-level summaries.
- Release gate recommendation.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 13

Run the `sim-lab` skill.

### Inputs
- Skill definition: `.claude/sim-lab/SKILL.md`
- Authoritative inputs:
  - `artifacts/openspec.yaml`
  - `artifacts/deploy-manifest.yaml`
- Additional inputs (if available):
  - `artifacts/task-breakdown.yaml`
  - `artifacts/context.yaml`

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step S1: Parse NFR Targets and Endpoint Inventory
- Step S2: Generate Load Test Scripts
- Step S3: Generate Failure Injection Scenarios
- Step S4: Generate Edge Case Simulations
- Step S5: Execute Simulations and Capture Results
- Step S6: NFR Pass/Fail Verdict

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- NFR targets.
- Endpoint inventory.
- Dependency inventory.
- Circuit-breaker expectations.
- Staging environment equivalence status.

### Step S1 — Parse NFR Targets and Endpoint Inventory
Extract NFR targets from `artifacts/openspec.yaml`, including:
- Latency targets:
  - p50
  - p95
  - p99
- Concurrency targets:
  - Target users
  - Peak users
- Error rate ceilings.
- Availability targets.
- Circuit-breaker parameters:
  - Timeout.
  - Failure threshold.
  - Recovery window.
- Test framework overrides.

Extract all integration endpoints from `artifacts/deploy-manifest.yaml`.

Build the test matrix:
- Each endpoint × each applicable NFR scenario.

If any required NFR fields cannot be inferred:
- Halt execution.
- Elicit the missing values exactly as defined in the skill.
- Do not continue until resolved.

### Step S2 — Generate Load Test Scripts
Generate k6 load test scripts for every endpoint identified.

Parameterise scripts using values extracted from `artifacts/openspec.yaml`.

For each endpoint:
- Include ramp-up.
- Include steady-state execution.
- Include peak-load execution.
- Include ramp-down.
- Apply threshold assertions using extracted NFR values.
- Include representative payload placeholders derived from the specification.

Generate one script per endpoint.

Output scripts to:
- `tests/load/`

### Step S3 — Generate Failure Injection Scenarios
Identify dependencies from `artifacts/deploy-manifest.yaml`.

Generate chaos scenarios for each dependency covering:
- Dependency unavailable.
- Dependency degraded.
- Dependency rate-limited.
- Partial failure.
- Cascade failure.

Validate:
- Circuit-breaker activation timing.
- Fallback response behaviour.
- Recovery behaviour.
- Error propagation handling.

If circuit-breaker behaviour or fallback expectations are not specified:
- Halt execution.
- Elicit the missing expectations exactly as defined in the skill.

Generate scripts and scenarios under:
- `tests/chaos/`

### Step S4 — Generate Edge Case Simulations
Using `artifacts/task-breakdown.yaml` when available, identify performance-sensitive scenarios.

Generate simulations covering:
- Minimum viable inputs.
- Maximum supported inputs.
- Concurrent duplicate requests.
- Rapid successive requests from the same user.
- Any additional performance-sensitive edge cases documented in the artifacts.

### Step S5 — Execute Simulations and Capture Results
Execute all generated scripts against the staging environment.

Capture, per endpoint:
- p50 latency.
- p95 latency.
- p99 latency.
- Requests per second.
- Error rate under normal load.
- Error rate at peak load.
- Latency degradation ratio.

Capture, per chaos scenario:
- Circuit-breaker activation time.
- Fallback response correctness.
- Recovery time.
- Error propagation counts.

Record all metrics and execution timestamps.

Output:
- `artifacts/simlab-results.json`

### Step S6 — NFR Pass/Fail Verdict
Compare captured metrics against the extracted NFR targets.

Apply verdict rules exactly as defined in the skill:

- p95 latency:
  - PASS when within target.
  - WARN when exceeding target by ≤ 20%.
  - FAIL when exceeding target by > 20%.

- Error rate:
  - PASS when within ceiling.
  - FAIL when exceeding ceiling.

- Circuit-breaker:
  - PASS when activation occurs within timeout.
  - FAIL when activation does not occur.

- Fallback behaviour:
  - PASS when matching specification.
  - FAIL when not matching specification.

Apply Release Gate rules:
- Any FAIL verdict blocks Release.
- Any WARN verdict requires POD Lead acknowledgement or remediation.

Apply all HITL gates defined in the skill, including:
- Missing NFR targets.
- Missing circuit-breaker expectations.
- Unconfirmed staging equivalence.
- WARN verdict acknowledgement.
- FAIL verdict escalation.

Document staging environment equivalence confirmation, including:
- Compute tier equivalence.
- Database representativeness.
- Dependency environment equivalence.
- Network topology equivalence.

### Outputs
Generate:
- `tests/load/`
- `tests/chaos/`
- `artifacts/simlab-results.json`
- `artifacts/nfr-verdict.md`

Ensure `tests/load/` contains:
- One generated k6 script per endpoint.
- Threshold assertions derived from NFR targets.
- Parameterised execution profiles.

Ensure `tests/chaos/` contains:
- Failure injection scenarios.
- Circuit-breaker validation scripts.
- Recovery validation scenarios.

Ensure `artifacts/simlab-results.json` contains:
- Endpoint performance metrics.
- Chaos execution results.
- Circuit-breaker observations.
- Execution timestamps.
- Raw pass/fail outcomes.

Ensure `artifacts/nfr-verdict.md` contains:
- Sprint identifier.
- NFR targets evaluated.
- Endpoint-level verdicts.
- Chaos scenario verdicts.
- WARN findings.
- FAIL findings.
- Release gate recommendation.
- Staging equivalence confirmation.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 14

Run the `policy-enforcer` skill.

### Inputs
- Skill definition: `.claude/policy-enforcer/SKILL.md`
- Authoritative inputs:
  - `artifacts/policy-catalogue.yaml`
  - All source code in `src/`
  - Configuration files
  - Runtime request/response logs in `artifacts/runtime-logs/`
- Additional inputs (if available):
  - `artifacts/deploy-manifest.yaml`
  - `artifacts/trustfabric-classification.yaml`

### Execution
Read all available artifacts and execute the skill exactly as defined.

Run both scan modes:
- Mode 1: Static Scan
- Mode 2: Runtime Scan

Execute the following steps in order:
- Step P1: Load and Validate Policy Catalogue
- Step P2: Static Source Code Scan
- Step P3: Runtime Behaviour Scan
- Step P4: Classify and Deduplicate Violations
- Step P5: Generate Policy Scan Report

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Policy catalogue validity.
- Runtime log availability.
- TrustFabric classification availability.
- Static scan scope.
- Runtime scan scope.

### Step P1 — Load and Validate Policy Catalogue
Read `artifacts/policy-catalogue.yaml`.

Validate that:
- The catalogue exists.
- All policies contain required fields.
- Severity values are valid:
  - `critical`
  - `high`
  - `medium`
  - `informational`
- Scan types are valid:
  - `static`
  - `runtime`
  - `both`
- Only policies with `enforced: true` are applied.

If the catalogue is missing or malformed:
- Halt execution.
- Prompt exactly as defined in the skill.
- Do not continue until a valid catalogue is available.

### Step P2 — Static Source Code Scan
Scan all source code and configuration files.

Apply all policies marked as:
- `static`
- `both`

Perform scans for:
- PII in log statements.
- Hardcoded secrets and credentials.
- Injection vulnerabilities.
- Insecure dependencies.
- Missing input validation patterns.
- Insecure cryptography usage.

For every finding, capture:
- Policy ID.
- Severity.
- File path.
- Line number where applicable.
- Matched content (redacted when required).
- Applicable regulation or category.
- Recommended remediation.

### Step P3 — Runtime Behaviour Scan
If runtime logs are available in `artifacts/runtime-logs/`, execute runtime scanning.

Apply all policies marked as:
- `runtime`
- `both`

Inspect runtime behaviour for:
- PII appearing in API responses outside approved specifications.
- Sensitive information appearing in URLs or query parameters.
- Authentication gaps or bypass patterns.
- Missing authentication headers on secured endpoints.
- Rate-limiting gaps.
- Error message leakage.
- Stack traces or internal implementation details exposed externally.
- Sensitive data transmitted contrary to policy requirements.

If runtime logs are unavailable:
- Explicitly document that runtime validation could not be performed.
- Continue execution using the available evidence.

### Step P4 — Classify and Deduplicate Violations
Classify every finding using the severity defined by the policy catalogue.

Apply the following severity categories:
- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `INFORMATIONAL`

Deduplicate repeated violations originating from shared implementations.

For each consolidated finding:
- List all affected locations.
- Map remediation guidance from the originating policy.
- Identify the associated policy category.

Apply Release Gate rules exactly as defined:

- Release PASSES only when:
  - Critical violations = 0
  - High violations = 0

- Release is BLOCKED when:
  - Critical violations > 0, or
  - High violations > 0

Document medium and informational findings for backlog visibility.

Apply all HITL gates defined in the skill, including:
- Missing policy catalogue escalation.
- Immediate POD Lead notification for CRITICAL findings.
- POD Lead notification for HIGH findings.
- Identification of new policy types not represented in the catalogue.
- Documentation of MEDIUM findings without blocking.

### Step P5 — Generate Policy Scan Report
Compile the complete scan results.

Summarise:
- Total findings.
- Findings by severity.
- Findings by category.
- Static versus runtime findings.
- Release gate outcome.

### Outputs
Generate:
- `artifacts/policy-scan-report.md`
- `artifacts/policy-scan-results.json`
- `artifacts/compliance-attestation.md`

Ensure `artifacts/policy-scan-report.md` contains:
- Scan metadata.
- Policy catalogue validation status.
- Static scan findings.
- Runtime scan findings.
- Deduplicated violation inventory.
- Severity breakdown.
- Remediation guidance.
- Release gate recommendation.

Ensure `artifacts/policy-scan-results.json` contains:
- Structured violation records.
- Policy identifiers.
- Categories.
- Severities.
- Locations.
- Remediation guidance.
- Runtime evidence where applicable.

Ensure `artifacts/compliance-attestation.md` contains:
- Sprint identifier.
- Critical violation count.
- High violation count.
- Medium violation count.
- Informational finding count.
- Release gate verdict.
- POD Lead action requirements.
- Compliance attestation statement.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 15

Run the `insight-ops` skill.

### Inputs
- Skill definition: `.claude/insight-ops/SKILL.md`
- Authoritative inputs:
  - `artifacts/test-results.json`
  - `artifacts/eval-results.json`
  - `artifacts/adversarial-test-suite.json`
  - `artifacts/simlab-results.json`
  - `artifacts/policy-scan-results.json`
  - `artifacts/openspec.yaml`
  - `artifacts/traceability-report.md`
- Optional inputs:
  - `artifacts/operate-metrics/`

### Execution
Read all available artifacts and execute the skill exactly as defined. :contentReference[oaicite:0]{index=0}

Execute the following steps in order:
- Step I1: Completeness and Freshness Check
- Step I2: Cross-Agent Signal Aggregation
- Step I3: Pattern Detection
- Step I4: Spec Amendment Recommendations
- Step I5: Action List Generation
- Step I6: Write Validation Report

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Validation artifact completeness.
- Validation artifact freshness.
- Requirement coverage status.
- Operate metrics availability.
- Release gate readiness.

### Step I1 — Completeness and Freshness Check
Verify that all required validation outputs exist:
- `artifacts/test-results.json`
- `artifacts/eval-results.json`
- `artifacts/adversarial-test-suite.json`
- `artifacts/simlab-results.json`
- `artifacts/policy-scan-results.json`
- `artifacts/openspec.yaml`
- `artifacts/traceability-report.md`

Validate that each artifact belongs to the current sprint by checking available timestamps and sprint identifiers.

If any required artifact is missing:
- Halt execution.
- List the missing outputs.
- Prompt exactly as defined in the skill.
- Do not continue until all required inputs are available.

If any artifact appears stale:
- Explicitly document the warning.
- Identify the originating agent.
- Continue only if the user confirms the evidence should still be used.

### Step I2 — Cross-Agent Signal Aggregation
Build a unified failure map for every requirement ID defined in `artifacts/openspec.yaml`.

For each requirement, aggregate:
- Guardian status.
- EvalHarness evaluation score.
- RedTeamX adversarial classification.
- SimLab NFR status.
- PolicyEnforcer violations by severity.

Construct the aggregate signal using the skill rules:

- `RED`
  - Any FAIL result.
  - Any VULNERABLE result.
  - Any CRITICAL or HIGH policy violation.

- `AMBER`
  - Any WARN result.
  - Any DEGRADED adversarial result.
  - Evaluation score below threshold.
  - Any MEDIUM policy violation.

- `GREEN`
  - All validation signals pass with no blocking findings.

Document the unified failure map per requirement.

### Step I3 — Pattern Detection
Analyse the unified failure map and identify cross-agent patterns.

Detect and document:

#### Cross-Agent Correlation
Identify requirements exhibiting degraded signals across multiple validation agents.

#### Component Blast Radius
Identify components associated with failures spanning multiple requirements.

#### Spec Gap Signals
Identify:
- Repeated Guardian `SPEC_ERROR` classifications.
- Underdefined requirements revealed through adversarial or validation failures.
- Requirement clusters indicating specification ambiguity.

#### Environmental Patterns
Correlate:
- Guardian `ENV_ERROR` findings.
- SimLab infrastructure failures.
- Shared environmental dependencies.

#### Regression Signals
Identify:
- EvalHarness quality regressions.
- Drift evidence.
- Declining performance compared to prior sprint evidence where available.

For each detected pattern:
- Describe the evidence.
- Explain the likely root cause.
- List the impacted requirements and components.

### Step I4 — Spec Amendment Recommendations
For every identified SPEC_ERROR or spec gap pattern:

Generate amendment recommendations that include:
- Amendment identifier.
- Triggering evidence.
- Failure pattern description.
- Affected `openspec.yaml` requirement IDs.
- Specific wording or additions recommended.
- Estimated amendment effort.
- Priority classification.

Recommendations must be concrete and directly actionable.

### Step I5 — Action List Generation
Produce a POD Lead-ready action list ordered using the following priority:

1. Release gate blockers.
2. AMBER findings and quick wins.
3. Spec amendment recommendations.
4. Informational and next-sprint improvements.

For each action item include:
- Action identifier.
- Description.
- Owner.
- Estimated effort.
- Blocking status.
- Affected files, requirements, or components.
- Recommended next step.

### Step I6 — Write Validation Report
Compile a consolidated validation report containing:
- Executive summary.
- Release gate status.
- Cross-agent findings.
- Failure patterns.
- Spec amendment recommendations.
- Ordered action list.
- Passing evidence supporting release decisions.

### Outputs
Generate:
- `artifacts/validation-report.md`
- `artifacts/spec-amendments.md`
- `artifacts/action-list.md`

If Operate phase metrics are available:
- Generate `artifacts/feedback-loop-triggers.yaml`.

If Operate phase metrics are unavailable:
- Explicitly document that feedback-loop triggers could not be generated.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

**Platform Enablement Complete**
