**name:** create-policy-library

**description:** Automatically generates `references/policy-library.md` — the master compliance rail library required by PolicyCatalog — without human input. Reads available specs to infer applicable frameworks and project context, then generates the full policy library. Invoke when PolicyCatalog reports `references/policy-library.md` is missing, or directly via phrases like "generate policy library", "create policy library", "initialize compliance library". Flags anything it cannot infer in the post-generation summary.


# SKILL: CreatePolicyLibrary
**SpecPod Framework v2.1.0 · Planning · 00a**
**Model:** claude-sonnet-4-6 · **Context Budget:** ~60K tokens
**Role:** Auto-generate the master policy library from available project context — no human input required

---

## Purpose

CreatePolicyLibrary produces `references/policy-library.md` — the file PolicyCatalog requires before it can run. It reads all available spec and artifact files to infer which regulatory frameworks apply and what internal engineering standards are in effect, then writes a complete, ready-to-use policy library. It never blocks on missing input — it generates what it can and flags gaps in the summary.

---

## Trigger

**Invoked by PolicyCatalog** when `references/policy-library.md` is absent.

**Invoked directly** via:
- `generate policy library` / `create policy library`
- `initialize compliance library`
- `run CreatePolicyLibrary`

---

## Step 0 — Context Scan

Read all available files silently before generating anything. Extract the signals listed below from each file if present. Do not halt if any file is missing — skip and note it.

| File | Signals to extract |
|------|--------------------|
| `specs/program.md` | Industry, geography/jurisdiction, stakeholders, regulatory mentions, data types handled |
| `specs/knowledge.md` | Business rules referencing compliance, PII field definitions, data classification, third-party services |
| `specs/design.md` | Security architecture, auth mechanism, encryption approach, API style, frontend stack, audit logging design |
| `specs/database.md` | Schema tables, PII columns, retention annotations, backup strategy |
| `specs/api.md` | Endpoint inventory, authentication method, external-facing surfaces |
| `artifacts/openspec.yaml` | `pii_present`, jurisdiction annotations, policy_rails already declared, module list |

---

## Step 1 — Framework Selection

Determine which regulatory frameworks to include based on context scan signals. Apply these rules automatically — no questions asked:

| Signal detected | Frameworks activated |
|-----------------|----------------------|
| EU users / GDPR mention / "data protection" / "right to erasure" | GDPR |
| SOC2 mention / "trust services" / "audit controls" / SaaS B2B product | SOC2 |
| "ISO 27001" / "information security management" / enterprise client mention | ISO 27001 |
| "health" / "medical" / "PHI" / "patient" / "clinical" / "HIPAA" / healthcare industry | HIPAA |
| Any detected internal coding standards, migration rules, or API conventions | Internal |
| No signals detected for a framework | Exclude that framework |
| No signals detected at all | Include SOC2 + Internal as safe defaults; flag in summary |

---

## Step 2 — Internal Policy Inference

For the Internal section, derive policies from the tech stack and coding standards found in the context scan rather than asking. Apply these mappings:

| Detected in specs | Internal policy to generate |
|-------------------|-----------------------------|
| REST API / external endpoints | POL-INT-001 — API Rate Limiting |
| PII fields in schema | POL-INT-002 — PII Field Classification |
| Error handling / exception patterns in design.md | POL-INT-003 — Error Handling Standards |
| Secrets / credentials / env vars mentioned | POL-INT-004 — Secrets Management |
| User input / forms / SQL / queries | POL-INT-005 — Input Validation and Injection Prevention |
| package.json / requirements.txt / dependencies | POL-INT-006 — Dependency Version Pinning |
| Schema migrations / Alembic / Flyway / database changes | POL-INT-007 — Database Migration Safety |
| HTML responses / frontend / browser / CSP | POL-INT-008 — Frontend Security Headers |

Customise each internal policy's guard prompt using the actual tech stack, library names, and conventions found in the specs (e.g., if `design.md` specifies bcrypt, name it; if it specifies Pydantic, reference it in the input validation policy). Use generic defaults where no specific tech is detected.

---

## Step 3 — Generate `references/policy-library.md`

Write the full file using the structure below. Include only the frameworks determined in Step 1. Within each framework, include all standard policies for that framework — do not omit policies based on what the current sprint covers (the library is program-wide, not sprint-specific).

### File structure

```markdown
# Policy Library
**SpecPod Framework v2.1.0 · PolicyCatalog Reference**
**Generated by:** CreatePolicyLibrary
**Source context:** [list files that were read]
**Generated:** [YYYY-MM-DD]

---

## Purpose and Usage

This is the authoritative compliance rail library for PolicyCatalog. Each policy entry defines:
- **Signal keywords** — terms in requirements that trigger this policy
- **Guard prompt** — concrete instruction injected into the AI Builder's context window
- **Reviewer check** — what the POD Lead or Gate reviewer must verify before sign-off
- **Gate blocker** — whether a missing implementation of this policy blocks a HITL gate

PolicyCatalog matches requirement text and PII field annotations against signal keywords to assign policies. Requirements with compliance signals but no policy match become `POLICY_GAP` entries — these block Gate-1.

---

## Adding New Policies

1. Choose a framework prefix: `GDPR` / `SOC2` / `ISO27001` / `HIPAA` / `INTERNAL` / or a custom prefix
2. Assign the next sequential number for that framework
3. Fill all four fields: signal keywords, guard prompt, reviewer check, gate blocker
4. Restart PolicyCatalog for the change to take effect in the current sprint

---

## Framework Index

| Framework | Policies | Coverage |
|-----------|----------|----------|
[one row per included framework]

---

[one section per included framework, using the policy entry format below]
```

### Policy entry format (repeat for every policy)

```markdown
### POL-[FRAMEWORK]-[NNN] — [Short Title] ([Regulatory Article or Control ref])
**Signal keywords:** [comma-separated trigger terms]
**Guard prompt:** [Detailed, actionable instruction for the AI Builder. Reference specific libraries, thresholds, and methods drawn from the project's tech stack where available. 3–8 sentences.]
**Reviewer check:** [Numbered checklist of concrete verification steps for the POD Lead.]
**Gate blocker:** YES — [condition] | NO — [consequence if absent]
```

### Maintenance log (append at end of file)

```markdown
## Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| [YYYY-MM-DD] | Initial generation from context scan | CreatePolicyLibrary |
```

---

## Step 4 — Post-Generation Summary (in-chat only, not written to file)

After writing the file, print this summary in chat:

```
## CreatePolicyLibrary — Complete

File written: references/policy-library.md

Frameworks included:
  [list each framework and policy count]

Context read:
  [list each file read and key signals extracted]

Context not found (used defaults):
  [list any spec files that were missing]

⚠ FLAGS — review before running PolicyCatalog:
  [list any of the following that apply, or "None" if all clear]
  - No jurisdiction signals detected — defaulted to SOC2 + Internal. Confirm correct frameworks in program.md.
  - No PII fields detected in schema — PII-specific policies included but may not trigger. Verify if PII is in scope.
  - Internal policies use generic defaults — no tech stack detected in design.md. Update guard prompts with actual library names.
  - [any other specific gap found during scan]

Next step: Run PolicyCatalog → it will read this file and map sprint requirements to policies.
```

Only flag items that genuinely could not be inferred. Do not flag things that were successfully derived from context.

---

## Limitations

- Internal policy guard prompts default to generic instructions when no tech stack is detected in specs — update them after generation if specific library names matter.
- Does not add novel regulatory frameworks (IRS, FCA, MAS, etc.) — add those manually using the format in the file's "Adding New Policies" section.
- If no spec files are present at all, generates SOC2 + Internal with fully generic content and flags everything in the summary.

---

## References

- `.claude/policy-catalog/references/policy-library.md` — canonical example of a completed policy library
- `.claude/policy-catalog/SKILL.md` — how this file is consumed by PolicyCatalog
- `.claude/artifacts-generation/create-openspec.md` — generates openspec.yaml (another PolicyCatalog prerequisite)
