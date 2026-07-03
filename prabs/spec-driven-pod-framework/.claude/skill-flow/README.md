# SkillFlow Engine

## Overview

The SkillFlow is a post-Init planning component of the framework.

Its purpose is to analyze initialized project artifacts, evaluate project requirements against the framework skill catalog, and generate a structured execution plan identifying which skills should be executed, skipped, or enhanced.

The engine operates exclusively on the generated skill catalog and does not inspect individual skill definitions. This ensures recommendations are driven by catalog metadata rather than implementation details.

---

## Position in Framework

The SkillFlow Engine executes after Phase 01 (Init) has completed and all mandatory project artifacts are available.

Framework Flow:

```text
01-init
→ skill-catalog-generator
→ SkillFlow Engine
→ execute recommended Phase 02+ skills
```

The engine serves as the bridge between project initialization and framework execution.

---

## Objectives

The engine is responsible for:

* Evaluating project scope, architecture, constraints, and requirements.
* Mapping project needs to available framework capabilities.
* Determining which skills are Required, Recommended, Optional, or Not Recommended.
* Identifying capability gaps and potential skill enhancements.
* Producing a phased execution roadmap.
* Generating a minimal viable execution plan.

The engine does not:

* Create new skills.
* Modify existing skills.
* Execute skills.
* Read individual skill implementations.
* Generate project deliverables.

---

## Inputs

### Mandatory Inputs

The following artifacts must be available before execution:

* skill_catalog.md
* program.md
* knowledge.md
* design.md
* database.md
* api.md
* ui-ux.md

### Optional Inputs

Additional project artifacts may be supplied if available and relevant.

---

## Catalog Dependency Model

The SkillFlow Engine uses:

```text
skill_catalog.md
```

as the sole authority for:

* Skill metadata
* Capability ownership
* Dependencies
* Phase assignments
* Status information
* Recommendation decisions

Individual skill files are intentionally not accessed during recommendation generation.

---

## Outputs

The engine generates two artifacts.

### recommendation_summary.md

Primary planning artifact intended for project leads, architects, and decision makers.

Contains:

* Project Overview
* Required Skills
* Recommended Skills
* Optional Skills
* Not Recommended Skills
* Skill Enhancements
* Critical Flags
* Phase 01 Assessment Summary
* Minimal Design Plan
* Phase Overview

### recommendation_report.md

Detailed analysis artifact intended for architects and framework maintainers.

Contains:

* Executive Summary
* Project Understanding
* Coverage Assessment
* Recommendation Analysis
* Skill Enhancements
* Execution Plan
* Risks and Gaps

---

## Recommendation Categories

### Required

Skills that are mandatory for successful project execution.

### Recommended

Skills that provide significant value but are not strictly required.

### Optional

Skills that become valuable only under specific conditions.

### Not Recommended

Skills that do not apply to the current project.

### Skill Enhancements

Recommended modifications or extensions to existing framework skills.

---

## Core Principles

The engine follows several key principles:

* Catalog-driven recommendations.
* Phase-aware execution planning.
* Evidence-based recommendation generation.
* Internal traceability for all recommendations.
* Deterministic recommendation behavior.
* No hallucinated capabilities or ownership assignments.
* Phase 01 artifacts drive all recommendation decisions.

---

## Recommended Usage

1. Complete Phase 01 (Init).
2. Generate or refresh the Skill Catalog.
3. Execute the SkillFlow Engine
4. Review recommendation_summary.md.
5. Review recommendation_report.md if additional detail is required.
6. Execute approved Phase 02+ skills according to the generated plan.

---
