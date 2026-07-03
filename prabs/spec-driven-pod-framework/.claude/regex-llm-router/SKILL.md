---
name: regex-llm-router
description: "Assesses text-parsing tasks across 5 structural regularity dimensions, routes each task to regex/parser, hybrid, or LLM execution, and emits a working starter pattern when deterministic parsing wins. Eliminates LLM spend on tasks solvable in code."
---

**name:** regex-llm-router

**description:** Assesses text-parsing tasks across 5 structural regularity dimensions, routes each task to regex/parser, hybrid, or LLM execution, and emits a working starter pattern when deterministic parsing wins. Eliminates LLM spend on tasks solvable in code.


# RegexLLMRouter

## Purpose

Every time your agent calls an LLM to extract a structured value it could parse
with a regex, you pay LLM rates for CPU-grade work. This skill scores the
structural regularity of a parsing task and routes it to the cheapest correct
method: deterministic regex/parser, a hybrid pipeline, or full LLM.

The model (claude-haiku-4-5) is invoked only when the aggregate regularity
score falls in the borderline range (13–19). Below 13 the data is too
ambiguous for code; above 19 the pattern is too clear to waste tokens on.

---

## Scoring Framework

Rate the parsing task on each of the 5 dimensions below (1–5 integer). Sum
the scores to obtain the routing decision.

### Dimension 1 — Schema Consistency

> Are all input samples structurally identical?

| Score | Meaning |
|-------|---------|
| 5 | Every sample follows the same structure — field order, length, casing are constant |
| 4 | Rare structural variants (< 5 % of samples) |
| 3 | Two or three distinct structures that can be enumerated |
| 2 | Structure varies significantly across samples |
| 1 | No repeatable structure; every sample is different |

**Rule:** If the schema changes over time (data drift), revisit this score
quarterly.

### Dimension 2 — Delimiter Reliability

> Are separators, fixed-width columns, or positional anchors predictable?

| Score | Meaning |
|-------|---------|
| 5 | Single unambiguous delimiter or fixed column positions throughout |
| 4 | One primary delimiter with rare escaping edge cases |
| 3 | Two possible delimiters that can be distinguished algorithmically |
| 2 | Delimiters are user-supplied natural language words ("between", "and", "to") |
| 1 | No reliable delimiter; position is free-form |

### Dimension 3 — Ambiguity Level

> Can the target value be misread without understanding context or intent?

| Score | Meaning |
|-------|---------|
| 5 | No ambiguity — the extracted string is the value, no interpretation needed |
| 4 | Trivial normalization (casing, whitespace) but no semantic ambiguity |
| 3 | One well-defined ambiguity class that can be resolved with a lookup table |
| 2 | Multiple interpretation paths that depend on surrounding context |
| 1 | Meaning is inherently subjective or requires world knowledge |

### Dimension 4 — Error Tolerance

> How bad is an incorrect parse result in production?

| Score | Meaning |
|-------|---------|
| 5 | Cosmetic failure; user can correct inline, no downstream impact |
| 4 | Logged error, automatic retry resolves the issue |
| 3 | Degraded experience; manual review queue handles it |
| 2 | Financial or compliance data — incorrect value has real consequences |
| 1 | Catastrophic: incorrect parse triggers irreversible action (refund, deletion) |

**Note:** A high error-tolerance score (4–5) enables aggressive regex routing
even when schema consistency is moderate. A low score (1–2) should bias you
toward LLM or hybrid with validation even if patterns look clean.

### Dimension 5 — Volume

> How many parse operations will run per day?

| Score | Meaning |
|-------|---------|
| 5 | 1 000 + operations/day — LLM cost compounds significantly |
| 4 | 100–999 operations/day |
| 3 | 10–99 operations/day |
| 2 | 2–9 operations/day |
| 1 | Single-use or one-off task |

**Note:** At low volumes (score 1–2) even a high total score may not justify
the engineering time to build and maintain a regex. Use judgment.

---

## Routing Decision Table

| Total Score | Route | Action |
|-------------|-------|--------|
| 20–25 | **regex** | Emit working pattern; no LLM invocation at parse time |
| 13–19 | **hybrid** | Regex for the structured majority; LLM for ambiguous residual |
| 0–12 | **llm** | Route all instances to LLM; regex would be brittle or wrong |

### Hybrid Route Detail

When the score lands in the hybrid band:

1. Write a regex that handles the highest-confidence structural form.
2. Run the regex first on every input.
3. If the regex matches and the capture group passes a lightweight sanity check
   (length, character class, checksum), emit the deterministic result.
4. If the regex fails to match, fall through to LLM with the original input.
5. Log the fallthrough rate. If it drops below 10 %, promote to full regex.
   If it rises above 60 %, demote to full LLM and re-score the task.

---

## Customer Service Domain — Pre-scored Taxonomy

The following categories apply to the sample customer service chatbot
(React + FastAPI + PostgreSQL + Salesforce CRM).

### Always deterministic (regex / parser)

| Field | Typical Pattern | Notes |
|-------|----------------|-------|
| Order IDs | `ORD-\d{5}` | Fixed prefix + 5-digit suffix |
| Email addresses | RFC 5321 subset | Use a well-tested library pattern |
| Account numbers | `ACC-\d{7}` | System-generated, never user-typed |
| Billing amounts | `\$\d+(?:\.\d{2})?` | Dollar sign anchors extraction |
| Phone numbers | Multiple E.164 / NANP variants | Normalize to E.164 after extraction |
| CRM API JSON fields | `json.loads()` + key access | Structured API response, use JSON parse not regex |
| ISO dates in API responses | `\d{4}-\d{2}-\d{2}` | Machine-generated |

### Always LLM

| Field | Why |
|-------|-----|
| Customer sentiment | Requires semantic understanding of tone |
| Customer intent classification | "Cancel" vs "pause" vs "downgrade" need context |
| Relative date expressions | "last Tuesday", "end of next month", "between the 5th and 10th last month" |
| Free-form complaint topics | Open vocabulary, no fixed structure |

### Hybrid candidates

| Field | Regex covers | LLM covers |
|-------|-------------|-----------|
| Customer name | `My name is ([A-Z][a-z]+ [A-Z][a-z]+)` (~65 %) | Openers without "My name is" phrasing |
| Product mentions | `PROD-[A-Z]{2}\d{3}` for product codes | Free-form product names, nicknames, typos |

---

## Output Contract

This skill emits three artifacts per run:

1. **routing-decisions.json** — one decision object per task including score
   breakdown, justification, and economic impact.
2. **regex-patterns.json** — working Python patterns (with `re` module flags)
   for every task routed to regex.
3. **hybrid-strategy.json** — detailed fallthrough logic for every hybrid task.

---

## Pattern Quality Requirements

Every emitted regex pattern must:

- Be syntactically valid Python (`re.compile(pattern)` must not raise).
- Include at least 3 positive test cases and 2 negative test cases.
- Document known failures (inputs the pattern will mis-handle).
- Use non-capturing groups `(?:...)` for grouping that is not extracted.
- Use named capture groups `(?P<name>...)` for multi-field extraction.
- Be accompanied by a normalization function when the raw capture requires
  transformation (e.g., phone number reformatting).

---

## Revisiting Routing Decisions

Trigger a re-score when any of the following occur:

- **Data drift** — a new input format appears that the current pattern does not
  handle (monitor parse-failure rate; threshold: > 2 % over a 7-day window).
- **Volume change** — daily volume crosses a tier boundary (e.g., drops from
  Dimension 5 score 4 to score 1 after a product sunset).
- **Business rule change** — a field that was cosmetic (error-tolerance 5) is
  now used in billing decisions (error-tolerance 2).
- **Quarterly review** — run the scoring rubric on all hybrid tasks to check
  whether fallthrough rates have stabilized enough to promote or demote.

---

## Usage

```
/RegexLLMRouter input/parsing-tasks.json input/routing-config.json
```

The skill reads the task list and config, scores each task, and writes all
three output files. No side effects beyond the output directory.
