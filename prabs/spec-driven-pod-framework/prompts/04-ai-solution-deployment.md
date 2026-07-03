# AI Solution Deployment

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

AI Solution Deployment Complete

---

## Prompt 1

Run the `release-intel` skill.

### Inputs
- Skill definition: `.claude/release-intel/SKILL.md`
- Authoritative inputs:
  - `artifacts/release/deploy-manifest.yaml` (if present)
  - `artifacts/sprint-board.md`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/traceability-report.md`
  - `artifacts/scenario-matrix.md`
  - `artifacts/assumption-log.md`
  - `artifacts/decision-ledger.md`
  - `specs/spec.md`

### Execution
Read all available artifacts and execute the skill exactly as defined.

Execute the following steps in order:
- Step 1: Input Audit
- Step 2: Deployment Scope Extraction
- Step 3: Readiness Signal Synthesis
- Step 4: Blast Radius Quantification
- Step 5: Open Issues List
- Step 6: Release Verdict
- Step 7: Write Output

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Deployment scope and how it was derived.
- Artifact completeness and freshness.
- Release readiness signals.
- Blast radius assessment for all in-scope components.
- Open issues and their priority.
- Gate 3 release readiness status.

### Step 1 — Input Audit
Verify the availability of:
- `artifacts/release/deploy-manifest.yaml`
- `artifacts/sprint-board.md`
- `artifacts/task-breakdown.yaml`
- `artifacts/traceability-report.md`
- `artifacts/scenario-matrix.md`
- `artifacts/assumption-log.md`
- `artifacts/decision-ledger.md`
- `specs/spec.md`

Internally record:
- Files found versus missing.
- Any stale artifacts (sprint mismatch or outdated timestamps).
- Whether deployment scope can be established.

If both `artifacts/sprint-board.md` and `artifacts/task-breakdown.yaml` are unavailable:
- Halt execution.
- Prompt exactly as defined in the skill.
- Do not continue until deployment scope is provided.

### Step 2 — Deployment Scope Extraction
Determine the release scope using the following precedence:
1. `artifacts/release/deploy-manifest.yaml`
2. Inferred scope from `artifacts/sprint-board.md`
3. Cross-reference with `artifacts/task-breakdown.yaml`

For all identified release items:
- Extract components, services, APIs, UI features, and tasks.
- Record task status:
  - `DONE`
  - `IN REVIEW`
  - `IN PROGRESS`
  - `BLOCKED`
- Flag any task not marked `DONE` or `IN REVIEW` as an open item requiring POD Lead disposition.

If `deploy-manifest.yaml` exists:
- Compare it against the inferred scope.
- Document any discrepancies.

If deployment scope is inferred rather than explicitly defined:
- State this assumption clearly in the report.

### Step 3 — Readiness Signal Synthesis
Synthesize readiness evidence from available artifacts.

From `artifacts/traceability-report.md`, determine:
- Requirements coverage percentage.
- Requirements with zero test coverage.
- Requirements descoped during the sprint.

From `artifacts/scenario-matrix.md`, determine:
- HIGH or CRITICAL scenarios without mitigation.
- Scenarios whose trigger conditions may occur during deployment.

From `artifacts/assumption-log.md`, determine:
- Unresolved HITL blockers.
- Open assumptions affecting release scope.

From `artifacts/decision-ledger.md`, determine:
- ADRs marked `PENDING` or `CONTESTED`.
- Decisions whose consequences are not reflected in the implementation.

Apply the thresholds defined in `references/readiness-thresholds.md`.

### Step 4 — Blast Radius Quantification
For every component within the deployment scope, assess:

- User Segments
- Dependent Features
- Integration Points
- Data Risk
- Rollback Complexity

Rate each dimension as:
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Determine the composite blast radius using the skill rules:
- Any `CRITICAL` dimension → overall `CRITICAL`
- Two or more `HIGH` dimensions → overall `HIGH`
- Otherwise apply the readiness threshold guidance.

Every rating must cite its supporting artifact evidence.

### Step 5 — Open Issues List
Compile a consolidated issue list and classify each item as:

- `P0 — DEPLOY BLOCKER`
- `P1 — HIGH RISK`
- `P2 — MEDIUM RISK`
- `P3 — LOW RISK`

For each issue include:
- Identifier.
- Description.
- Source artifact.
- Impacted components or requirements.
- Recommended action.
- Owner.

### Step 6 — Release Verdict
Apply the Gate 3 decision rules.

Return exactly one verdict:

- ✅ **READY TO DEPLOY**
  - Zero P0 blockers.
  - P1 items accepted by the POD Lead.
  - Blast radius assessment completed.

- ❌ **NOT READY — BLOCKED**
  - One or more P0 blockers exist.
  - Explicitly list each blocker.

Provide a concise executive summary supporting the verdict.

### Step 7 — Write Output
Generate:
- `artifacts/release/release-intel-report.md`

The report must include:
- Executive summary.
- Binary release verdict at the top.
- Deployment scope.
- Readiness signals.
- Blast radius table.
- Risk-ranked open issues.
- Gate 3 attestation evidence.
- POD Lead action recommendations.

Before generating the report, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt
---

## Prompt 2

Run the `parity-checker` skill.

### Inputs
- Skill definition: `.claude/parity-checker/SKILL.md`
- Authoritative inputs:
  - `artifacts/release/env-config-staging.yaml`
  - `artifacts/release/env-config-production.yaml`
- Reference files:
  - `references/classification-rules.md`
  - `references/output-schema.md`

### Execution
Read all available artifacts and execute the skill exactly as defined. :contentReference[oaicite:0]{index=0}

Determine the run mode before proceeding:

- If both environment config files exist:
  - Run in **DIFF MODE**.
- If either file is missing:
  - Run in **ELICITATION MODE**, generate the missing YAML files, then continue to diff execution.

Execute the following steps in order:
- Step 1: Run Mode Detection
- Step 2: First-Run Elicitation (if required)
- Step 3: Generate Environment Config YAML Files (if required)
- Step 4: Config Diff and Classification
- Step 5: Write Output

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

Determine and document:
- Active run mode.
- Environment configuration completeness.
- Critical, notable, and expected drift counts.
- Gate 3 parity status.

### Step 1 — Run Mode Detection
Check whether the following files exist:
- `artifacts/release/env-config-staging.yaml`
- `artifacts/release/env-config-production.yaml`

If both exist:
- Announce:
  - "I found existing environment config files. Running in diff mode."
- Proceed directly to Step 4.

If either file is absent:
- Announce:
  - "No environment config files found. Starting first-run elicitation."
- Proceed to Step 2.

### Step 2 — First-Run Elicitation (ELICITATION MODE only)
Conduct a structured interview one dimension at a time.

Collect staging and production values for:

1. Runtime & Infrastructure
2. Application Dependencies
3. Database & Data Services
4. External Services & API Versions
5. Feature Flags
6. Secrets & Environment Variables
7. Monitoring & Observability
8. Network & Security

Do not ask all dimensions simultaneously.

For secrets:
- Collect names only.
- Never request, store, or log secret values.

### Step 3 — Generate Environment Config YAML Files (ELICITATION MODE only)
Generate:
- `artifacts/release/env-config-staging.yaml`
- `artifacts/release/env-config-production.yaml`

Use the schema defined in the skill.

Ensure:
- Secret names only are stored.
- Secret values are excluded.
- Missing variable lists are populated during diff processing.

After generation, confirm:
- Environment configuration files have been created.
- Future parity checks can reuse these files.
- Proceed automatically to the diff stage.

### Step 4 — Config Diff and Classification
Compare all fields across the following eight dimensions:

- Runtime
- Dependencies
- Database
- External Services
- Feature Flags
- Environment Variables
- Monitoring
- Network

Classify every detected difference as exactly one of:

- `CRITICAL_DRIFT`
- `NOTABLE_DRIFT`
- `EXPECTED_DIFF`

Apply the classification rules defined by the skill, including:

- Runtime version mismatches.
- Dependency lockfile mismatches.
- Migration state mismatches.
- Feature flag inconsistencies.
- External service endpoint/version mismatches.
- Environment variable presence mismatches.
- Monitoring differences.
- TLS expiry thresholds.
- CORS violations.
- Resource allocation differences.

For any uncovered scenario:
- Classify as `CRITICAL_DRIFT` if the difference could reasonably cause staging success and production failure.

Calculate and document:
- Total `CRITICAL_DRIFT` findings.
- Total `NOTABLE_DRIFT` findings.
- Total `EXPECTED_DIFF` findings.

Determine Gate 3 parity status:
- Gate passes only if `CRITICAL_DRIFT = 0`.

### Step 5 — Write Output
Generate:
- `artifacts/release/parity-check-report.md`

If generated during this execution, also create:
- `artifacts/release/env-config-staging.yaml`
- `artifacts/release/env-config-production.yaml`

Ensure the parity report includes:
- Active run mode.
- Executive summary.
- Drift classification summary.
- Detailed diff table.
- Critical findings.
- Expected differences with rationale.
- Gate 3 parity verdict.
- POD Lead acknowledgement requirements.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

## Prompt 3

Run the `rollout-advisor` skill.

### Inputs
- Skill definition: `.claude/rollout-advisor/SKILL.md`
- Authoritative inputs:
  - `artifacts/release/release-intel-report.md`
  - `artifacts/release/parity-check-report.md`
  - `artifacts/scenario-matrix.md`
  - `artifacts/sprint-board.md`
  - `artifacts/task-breakdown.yaml`
  - `artifacts/release/deploy-manifest.yaml` (if present)
- Reference files:
  - `references/output-schema.md`

### Execution
Read all available artifacts and execute the skill exactly as defined. :contentReference[oaicite:0]{index=0}

Execute the following steps in order:
- Step 1: Risk Profile Synthesis
- Step 2: User Impact Elicitation
- Step 3: Rollout Method Recommendation
- Step 4: Trigger Threshold Definition
- Step 5: Rollback Plan Generation
- Step 6: Monday Smoke Test Checklist
- Step 7: Write Outputs

Collect the mandatory user inputs defined by the skill only if they cannot be inferred from the available artifacts. Otherwise, use the inferred values and explicitly state the assumptions made.

### Step 1 — Risk Profile Synthesis
Review the release artifacts and determine:

From `artifacts/release/release-intel-report.md`:
- Overall blast radius rating.
- P0 blocker count and details.
- Accepted P1 risks.
- Components with HIGH or CRITICAL blast radius.

From `artifacts/release/parity-check-report.md`:
- Critical drift count.
- Acknowledged notable drift items.
- Any migration, feature flag, or connection pool concerns.

From `artifacts/scenario-matrix.md`:
- HIGH or CRITICAL deployment scenarios.
- Scenarios likely to activate during or shortly after deployment.

Determine the composite risk tier using the skill rules:

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

If ReleaseIntel or ParityChecker indicates unresolved blockers:
- Continue execution.
- Clearly mark all outputs as **DRAFT ONLY**.
- State that rollout execution is contingent on Gate 3 blockers being resolved.

### Step 2 — User Impact Elicitation
Ask only for information that cannot be inferred.

Elicit the following five questions:

1. Deployment window:
   - Planned Monday deployment time.
   - Active user segments.
   - Approximate percentage of users active.

2. Feature flag availability:
   - Whether a feature flag service exists.
   - Whether all released components are flag-protected.

3. Prior incident history:
   - Whether previous post-deploy incidents occurred.
   - Brief causes, if applicable.

4. Infrastructure rollback capability:
   - Support for blue-green deployment.
   - Support for canary deployment.
   - Whether only rolling updates are available.

5. Monday on-call coverage:
   - Named engineer availability.
   - Two-hour post-deployment coverage confirmation.

Accept partial responses and document conservative assumptions where answers are unavailable.

### Step 3 — Rollout Method Recommendation
Recommend the rollout strategy using the skill decision rules.

Select the appropriate primary and alternative approach from:

- Feature-Flag Toggle
- Canary
- Blue-Green
- Direct Deploy

Define:
- Traffic progression phases.
- Hold durations.
- Preconditions for phase advancement.

Document the rationale linking the recommendation to:
- Composite risk tier.
- Infrastructure capability.
- Feature flag availability.

### Step 4 — Trigger Threshold Definition
Define progression and rollback thresholds appropriate to the selected risk tier.

Include:

Progression triggers:
- Error rates.
- p95 latency behaviour.
- Health check status.
- Critical log validation.

Rollback triggers:
- 5xx error thresholds.
- p95 latency degradation.
- Health check failures.
- Database connection failures.
- Feature-specific failures.

Include component-specific thresholds for HIGH or CRITICAL blast-radius components when applicable.

### Step 5 — Rollback Plan Generation
For every component in deployment scope, define:

- Trigger conditions.
- Rollback method.
- Step-by-step rollback procedure.
- RTO target.
- Data recovery requirements.
- Verification steps.

Also define:
- Cross-component rollback sequencing.
- Database rollback ordering.
- Composite RTO target.

### Step 6 — Monday Smoke Test Checklist
Generate an executable smoke test checklist covering:

- Critical user journeys.
- Primary component functionality.
- Integration validation.
- High-risk deployment scenarios.
- Drift-sensitive areas identified by ParityChecker.

For each checklist item include:
- Component validated.
- Expected outcome.
- Pass/fail criteria.
- Estimated execution time.

### Step 7 — Write Outputs
Generate:

- `artifacts/release/rollout-strategy.md`
- `artifacts/release/rollback-plan.md`

Ensure the outputs include:
- Executive summary.
- Draft status warning when applicable.
- Recommended rollout approach.
- Phase gates and hold periods.
- Trigger thresholds.
- Rollback procedures.
- Monday smoke test checklist.
- POD Lead sign-off section.

Before generating the outputs, present a bulleted summary with 3–5 bullet points.

**Expected Action from User**
Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

After completion, report what was created or updated.

ask for confirmation before moving on to next prompt

---

**AI Solution Deployment Complete**
