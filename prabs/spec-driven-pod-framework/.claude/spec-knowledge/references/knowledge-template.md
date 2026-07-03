# Domain Knowledge Specification
**Program:** {Program Name}
**Program ID:** {PRG-ID}
**Last Updated:** {Date}
**Version:** {N}

---

## Domain Overview

{2–3 sentences describing the business domain: what industry/context this operates in, what the core
business activity is, and what makes this domain technically or logically complex.}

---

## Core Entities

### {Entity 1 Name}
**Description:** {What this entity represents in the business domain}
**Key Attributes:**
- `{attribute}` — {type} — {description / constraints}
- `{attribute}` — {type} — {description / constraints}

**Relationships:**
- Has many `{Entity}` — {nature of relationship}
- Belongs to `{Entity}` — {nature of relationship}

**Lifecycle States:** `{state1}` → `{state2}` → `{state3}`

---

### {Entity 2 Name}
*(repeat structure)*

---

## Business Rules

Rules are numbered for traceability. Reference as `BR-{N}` in other specs and code.

### {Entity / Domain Area}
- **BR-001:** {Rule statement in active voice. E.g., "A payment must be authorized before an order transitions to CONFIRMED."}
- **BR-002:** {Rule statement}
- **BR-003:** {Rule statement — include the exception or edge case if one exists}

### {Another Area}
- **BR-010:** {Rule}
- **BR-011:** {Rule}

---

## State Machines

### {Entity} States
```
{STATE_A} --[trigger / guard]--> {STATE_B}
{STATE_B} --[trigger / guard]--> {STATE_C}
{STATE_B} --[trigger / guard]--> {STATE_FAILED}
```

| State | Description | Entry Condition | Exit Transitions |
|-------|-------------|-----------------|-----------------|
| {STATE_A} | {What it means} | {How you enter} | {Triggers that move out} |
| {STATE_B} | {What it means} | {How you enter} | {Triggers that move out} |

---

## Key Workflows

### {Workflow Name}
**Actor:** {Who initiates}
**Trigger:** {What starts the workflow}
**Outcome:** {What success looks like}

1. {Step — actor does action}
2. {Step — system responds}
3. {Step — decision point or validation}
4. {Step — terminal state or handoff}

**Error Paths:**
- {Condition} → {What happens}

---

## Constraints & Compliance

| Constraint | Type | Applies To | Detail |
|------------|------|------------|--------|
| {Name} | Regulatory / Technical / Contractual | {Entity or system} | {Specific requirement} |
| {Name} | Regulatory | {Entity} | {Requirement} |

---

## Glossary

| Term | Definition | Notes |
|------|------------|-------|
| {Term} | {Canonical definition as used in this program} | {Disambiguation or origin if needed} |
| {Term} | {Definition} | |

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {Date} | 1.0 | {Name} | Initial version |
