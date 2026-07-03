# EvalHarness

Provides a shared, consistent scoring rubric for evaluating the semantic quality of every AI-generated output across the sprint. Functions as the evaluation backbone consumed by Guardian, RedTeamX, and SimLab — ensuring "quality" means the same thing regardless of which agent is evaluating.

Uses LLM-as-Judge methodology: evaluates AI outputs against human-defined golden references using structured rubrics.

---

## When to Use

Invoke to define evaluation criteria, set up scoring rubrics, create golden references, or score AI output quality against a reference standard.

**Critical prerequisite:** Cannot operate without golden references — guides the POD Lead through defining them if none exist.

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/golden-references/` | Mandatory |
| AI model outputs | Mandatory |
| `artifacts/eval-rubric-prev.yaml` (prior sprint) | Optional |

## Outputs

- `artifacts/eval-rubric.yaml` — structured scoring rubric per feature
- `artifacts/eval-results.json` — semantic quality scores per output
- `artifacts/golden-references/` — curated golden reference set

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Build phase (outputs available) | Guardian (consumes rubric) |
| | RedTeamX (consumes rubric) |
| | SimLab (consumes rubric) |
| | InsightOps (consumes eval-results) |
