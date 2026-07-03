# PatternExtractor

Mines session transcripts and artifacts for recurring decision patterns, tool call sequences, and reasoning chains. Scores each pattern by confidence, clusters related patterns into candidate skills, drafts SKILL.md stubs, and queues high-confidence candidates for human promotion review.

---

## When to Use

Run after a session to harvest tacit knowledge — lookup sequences, phrases, decision heuristics, or artifact patterns — before they are lost.

---

## Inputs

| Input | Required |
|---|---|
| Session transcript | Mandatory |
| Accompanying session artifacts | Optional |

## Outputs

- Scored pattern inventory with confidence scores
- Candidate skill stubs (SKILL.md drafts) for patterns above confidence threshold
- Promotion queue for POD Lead review

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Any session that may contain reusable patterns | Human skill promotion review |
