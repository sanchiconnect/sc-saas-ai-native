---
name: skill-generator
description: "Consume a recommendation_report.md produced by the SkillFlow Engine and materialize its unresolved recommendations into actual files. Handles two recommendation types: - Candidate New Skills — creates a new SKILL.md and README.md under .claude/<skill-name>/ - Skill Enhancements — patches the existing SKILL.md and updates the existing R..."
---

# Skill Generator

## Skill Metadata

```
name: skill-generator
version: 1.0.0
type: execution
layer: post-planning
scope: project-wide
```

---

## Purpose

Consume a `recommendation_report.md` produced by the SkillFlow Engine and materialize its unresolved recommendations into actual files. Handles two recommendation types:

- **Candidate New Skills** — creates a new `SKILL.md` and `README.md` under `.claude/<skill-name>/`
- **Skill Enhancements** — patches the existing `SKILL.md` and updates the existing `README.md` under `.claude/<skill-name>/`

After every creation or enhancement, updates `skill_catalog.md` to keep the catalog in sync.

Rejected skills are written to `skillflow_skip.md` so prompt files can skip them during execution without being modified.

---

## When to Run

Run this skill after the SkillFlow Engine has produced `recommendation_report.md` and the project team is ready to act on its Candidate New Skill and Skill Enhancement recommendations.

Do NOT run this skill:
- Before `recommendation_report.md` exists
- Before `skill_catalog.md` exists and is valid
- As a substitute for SkillFlow (this skill executes; SkillFlow plans)

---

## Inputs

### Mandatory

| Input | Description |
|---|---|
| `recommendation_report.md` | Produced by SkillFlow. Must contain a Skill Enhancements section and/or Candidate New Skills in Risks & Gaps. |
| `skill_catalog.md` | The current skill catalog. Must be present and valid before any catalog updates are made. |

### Optional

| Input | Description |
|---|---|
| `recommendation_summary.md` | Used for cross-reference when report content is ambiguous. |
| `skillflow_skip.md` | If a prior run exists, loaded to avoid overwriting existing skip decisions. |

---

## Outputs

| Output | Description |
|---|---|
| `.claude/<skill-name>/SKILL.md` | New skill definition file (new skills only) |
| `.claude/<skill-name>/README.md` | New or updated README for the skill |
| `skill_catalog.md` | Updated with new entries or modified existing entries |
| `skillflow_skip.md` | Updated with names of skills the user chose to skip |
| `skill_generation_report.md` | Summary of everything created, modified, and skipped in this run |

---

## Workflow

---

### Phase 0 — Input Validation

**Purpose:** Confirm all mandatory inputs are present before any work begins.

**Steps:**

1. Confirm `recommendation_report.md` is present and non-empty.
2. Confirm `skill_catalog.md` is present and not marked as invalid.
3. Check `recommendation_report.md` for at least one of:
   - A Skill Enhancements section with one or more entries
   - A Risks & Gaps section containing one or more Candidate New Skill entries
4. Log presence or absence of optional inputs.

**Halt Conditions:**

- If `recommendation_report.md` is absent: halt. Output: "recommendation_report.md is required. Run the SkillFlow Engine first."
- If `skill_catalog.md` is absent: halt. Output: "skill_catalog.md is required. Run skill-catalog-generator before proceeding."
- If neither Skill Enhancements nor Candidate New Skills are found: halt. Output: "No actionable recommendations found in recommendation_report.md. Nothing to generate."

**Outputs:** Validated input set. Optional input log.

---

### Phase 1 — Recommendation Extraction

**Purpose:** Parse the report and build the two work lists that drive all subsequent phases.

**Steps:**

1. Parse every **Skill Enhancement** entry from the Skill Enhancements section. For each entry extract:
   - Target skill name (the existing skill being enhanced)
   - Enhancement description (what is being added or changed)
   - Suggested placement (the exact section, phase, or step within the existing skill)
   - Recommendation ID (REC-XXX)
   - Confidence score

2. Parse every **Candidate New Skill** entry from the Risks & Gaps section. For each entry extract:
   - Skill name
   - Capability gap it addresses
   - Evidence chain (requirement IDs and artifact references from the report)
   - Recommendation ID (REC-XXX)

3. Build two lists:
   - `enhancements[]` — one entry per Skill Enhancement
   - `new_skills[]` — one entry per Candidate New Skill

4. If a Skill Enhancement names a target skill that does not exist in `.claude/`, flag it as a conflict. Do not silently skip — present it to the user in Phase 2 for a decision.

**Outputs:** `enhancements[]`. `new_skills[]`. Conflict flags list.

---

### Phase 2 — Recommendation Review (User Gate)

**Purpose:** Give the user full visibility and control over what will be executed before any file is touched.

**Steps:**

1. Present the complete work lists to the user:

```
New Skills to Create:
  - [REC-ID] skill-name — one-line capability description

Skill Enhancements to Apply:
  - [REC-ID] existing-skill → enhancement-name — one-line description

Conflicts Requiring Decision:
  - [skill-name] — enhancement target does not exist in .claude/
    Options: (a) treat as new skill, (b) skip
```

2. Ask the user: "Which of these would you like to proceed with? You may accept all, accept specific items, or reject any item."

3. Record each item as either `accepted` or `rejected`.

4. For each rejected item, add its skill name to `skillflow_skip.md`.

5. Ask the user for permission before writing to `skillflow_skip.md`. Do not write without explicit approval.

6. For conflict items, record the user's decision (treat as new skill or skip).

7. Only accepted items proceed to Phase 3.

**Outputs:** Accepted work list. Updated `skillflow_skip.md` (with permission). Conflict resolutions.

---

### Phase 3 — Assumptions Review (Per Item)

**Purpose:** Prevent the skill from generating content based on incorrect interpretations. Every accepted item is reviewed with the user before generation begins.

**This phase runs once per accepted item before that item enters Phase 4.**

---

#### For a Candidate New Skill

Present the following assumptions to the user before generating anything:

```
New Skill: [skill-name]
Based on the SkillFlow report I am assuming:

  Purpose:        [one sentence describing what this skill does]
  Scope:          [what it owns, what it does not own]
  Inputs:         [list of assumed inputs]
  Outputs:        [list of assumed outputs]
  Phases:         [assumed execution phases within the skill]
  Dependencies:   [skills or artifacts this skill depends on]
  Project Types:  [types of projects this skill applies to]
  Owned Responsibilities: [list]

Are these assumptions correct? Please confirm or correct before I proceed.
```

Do not proceed until the user confirms or provides corrections. Apply all corrections before moving to Phase 4.

---

#### For a Skill Enhancement

Present the following assumptions to the user before touching the existing file:

```
Enhancement: [existing-skill] → [enhancement-name]
Based on the SkillFlow report I am assuming:

  What is being added:  [precise description of the new content]
  Where it is placed:   [exact section, phase, or step in the existing SKILL.md]
  What changes in README: [what the README update will say]
  What changes in catalog: [which catalog fields will be updated and how]

Are these assumptions correct? Please confirm or correct before I proceed.
```

Do not proceed until the user confirms or provides corrections. Apply all corrections before moving to Phase 4.

---

**Outputs:** Confirmed specification per item. Correction log.

---

### Phase 4 — Content Generation

**Purpose:** Generate all file content based on confirmed assumptions from Phase 3.

No files are written in this phase. Content is prepared and staged for the validation gate in Phase 6.

---

#### New Skill — Generate SKILL.md

Generate a complete SKILL.md using the confirmed assumptions. The file must contain:

- Skill Metadata block: `name`, `version`, `type`, `layer`, `scope`
- Purpose section
- When to Run section (including when NOT to run)
- Inputs table (mandatory and optional)
- Outputs table
- Workflow section with numbered phases, each containing: Purpose, Steps, Halt Conditions (where applicable), Outputs
- Validation Rules section
- Success Criteria section

The content must be derived from the confirmed assumptions and the SkillFlow evidence chain. Do not invent responsibilities, inputs, or outputs not supported by confirmed assumptions.

---

#### New Skill — Generate README.md

Generate a README.md alongside the SKILL.md. The README must contain:

- Skill name and one-paragraph description
- When to use this skill
- Inputs (brief)
- Outputs (brief)
- How it fits into the framework (which skills precede and follow it)

---

#### Enhancement — Patch SKILL.md

1. Read the full existing `.claude/<skill-name>/SKILL.md`.
2. Locate the exact placement confirmed in Phase 3.
3. Insert the confirmed enhancement content at that location only.
4. Do not rewrite, reorder, or reformat any surrounding content.
5. Do not duplicate content already present in the file.

---

#### Enhancement — Update README.md

1. Read the existing `.claude/<skill-name>/README.md`.
2. Update only the sections affected by the enhancement — capabilities, outputs, or when-to-use sections if the enhancement changes them.
3. Do not rewrite unaffected sections.

---

**Outputs:** Staged SKILL.md content (new or patched). Staged README.md content (new or updated). Per-item generation log.

---

### Phase 5 — Skill Catalog Update

**Purpose:** Keep `skill_catalog.md` in sync with every item processed in Phase 4.

**Steps:**

**For a new skill:**
1. Generate a new catalog entry using the confirmed assumptions and generated SKILL.md content.
2. The entry must include all standard catalog fields: Skill Name, Purpose, Phase, Capabilities, Owned Responsibilities, Inputs, Outputs, Dependencies, Project Types, Constraints, Summary.
3. Stage the new entry for addition to `skill_catalog.md`.

**For an enhancement:**
1. Locate the existing catalog entry for the enhanced skill.
2. Update only the fields affected by the enhancement — typically Capabilities, Owned Responsibilities, or Outputs.
3. Do not overwrite fields unaffected by the enhancement.
4. Stage the updated entry.

**Outputs:** Staged catalog additions and updates.

---

### Phase 6 — Validation and Final Review

**Purpose:** Confirm all staged content is correct and complete before any file is written. Present a final summary to the user.

**Validation Checks:**

- No duplicate skill names in `.claude/` or `skill_catalog.md`
- All new SKILL.md files contain required sections with no placeholder text
- All enhancement patches are placed at the confirmed location and contain no duplicate content
- `skillflow_skip.md` accurately reflects all user rejections from Phase 2
- All catalog entries contain all required fields

**Final Review Presentation:**

Present a summary of everything about to be written:

```
Ready to write the following:

New Files:
  - .claude/<skill-name>/SKILL.md
  - .claude/<skill-name>/README.md

Modified Files:
  - .claude/<skill-name>/SKILL.md  (enhancement applied)
  - .claude/<skill-name>/README.md (updated)
  - skill_catalog.md               (N entries added, M entries updated)
  - skillflow_skip.md              (N skills added to skip list)

Skipped:
  - <skill-name> — rejected by user
```

Ask the user: "Proceed with writing all of the above?"

Do not write any file until the user confirms.

**Outputs:** Validation report. User-confirmed write approval.

---

### Phase 7 — Output

**Purpose:** Write all confirmed files and produce the generation report.

**Steps:**

1. Write all new `.claude/<skill-name>/SKILL.md` files.
2. Write all new `.claude/<skill-name>/README.md` files.
3. Write all patched `.claude/<skill-name>/SKILL.md` files.
4. Write all updated `.claude/<skill-name>/README.md` files.
5. Write updated `skill_catalog.md`.
6. Write updated `skillflow_skip.md`.
7. Produce `skill_generation_report.md`.

**skill_generation_report.md structure:**

```
# Skill Generation Report

## Created
  - [skill-name] — SKILL.md and README.md created (REC-ID)

## Enhanced
  - [skill-name] — SKILL.md patched, README.md updated (REC-ID)

## Catalog Updates
  - [skill-name] — entry added
  - [skill-name] — entry updated (fields: [list])

## Skipped
  - [skill-name] — rejected by user (REC-ID)
  - [skill-name] — conflict: target did not exist, treated as [new skill | skip]

## Errors
  - [any items that failed validation and were not written]
```

---

## Standing Infrastructure

The following instruction must be added once to the top of each prompt file that uses this framework:

```
Before executing any prompt in this file, read skillflow_skip.md.
If the skill name for this prompt appears in skillflow_skip.md, skip it and log: Skipped: <skill-name>
```

This instruction is added once and never needs to change. `skillflow_skip.md` is the only file modified to control execution behavior.

---

## Validation Rules

- V-IN-01: `recommendation_report.md` is present and non-empty.
- V-IN-02: `skill_catalog.md` is present and not marked invalid.
- V-IN-03: At least one actionable recommendation exists in the report.
- V-GEN-01: No new SKILL.md is written without confirmed assumptions from Phase 3.
- V-GEN-02: No enhancement is applied without confirmed placement from Phase 3.
- V-GEN-03: No file is written without user approval in Phase 6.
- V-GEN-04: No content is invented that was not supported by the SkillFlow evidence chain and confirmed assumptions.
- V-CAT-01: Every new skill has a corresponding catalog entry added.
- V-CAT-02: Every enhancement has the corresponding catalog entry updated.
- V-CAT-03: No catalog field unaffected by an enhancement is overwritten.
- V-SKIP-01: `skillflow_skip.md` is only written with explicit user permission.
- V-SKIP-02: Every rejected item from Phase 2 has a corresponding entry in `skillflow_skip.md`.

---

## Success Criteria

1. Every accepted Candidate New Skill has a complete SKILL.md and README.md written to `.claude/<skill-name>/`.
2. Every accepted Skill Enhancement has been precisely inserted into the existing SKILL.md and the README.md has been updated.
3. `skill_catalog.md` reflects all creations and enhancements — no new skill or applied enhancement is absent from the catalog.
4. `skillflow_skip.md` contains all rejected skill names and prompt files use it as the execution gate.
5. No original prompt file was modified.
6. No file was written without user confirmation in Phase 6.
7. No content was generated that was not supported by SkillFlow evidence and confirmed user assumptions.
8. `skill_generation_report.md` provides a complete audit of the run.
