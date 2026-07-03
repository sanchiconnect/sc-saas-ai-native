# PromptSlimmer

Structural minimization of standing instructions. Detects redundant, overlapping, and verbose
directives in system prompts and rules files, then produces a minimized prompt plus a
reviewable diff — never a silent rewrite.

---

## Why This Exists

System prompts grow organically. A rule is added after an incident. A new engineer adds a
clarification. A compliance update appends a paragraph. Nobody removes anything, because
removal feels risky. After six months, the prompt is three times the size it needs to be,
and every single call pays the token cost.

A 60% reduction on a 950-token prompt at 1 000 calls/day saves $1.14/day. At 10 000 calls/day,
it saves $11.40/day. At 100 000 calls/day, $114/day. This is compounding interest — one
structural fix applied to every subsequent call forever.

---

## How to Run

### Prerequisites

- Input files in `input/`: `system-prompt-verbose.md`, `criticality-flags.json`,
  `rules-files.json`
- Claude Code with access to `claude-sonnet-4-6` (bulk) and `claude-opus-4-7` (critical review)

### Basic run (produce diff, do not apply)

```bash
/PromptSlimmer \
  --system-prompt input/system-prompt-verbose.md \
  --rules-files input/rules-files.json \
  --criticality-flags input/criticality-flags.json \
  --output-dir output/
```

This produces three files in `output/`:
- `system-prompt-slimmed.md` — safe changes applied; review/critical changes shown but not applied
- `prompt-diff.md` — full change log with type and token impact per change
- `slimming-report.json` — machine-readable audit record

### Dry run (diff only, no output files written)

```bash
/PromptSlimmer --dry-run \
  --system-prompt input/system-prompt-verbose.md \
  --rules-files input/rules-files.json \
  --criticality-flags input/criticality-flags.json
```

### Apply only safe changes

```bash
/PromptSlimmer --apply-level safe ...
```

### Apply after human review of critical items

```bash
# After annotating prompt-diff.md with APPROVED/REJECTED:
/PromptSlimmer --apply-approved \
  --diff output/prompt-diff.md \
  --output-dir output/
```

---

## Approval Workflow for Critical Changes

Critical changes (compliance, escalation, legal) require an explicit human sign-off. The
process is designed to be fast and non-blocking for safe changes while protecting the
directives that carry real risk.

### Step 1 — Initial run

Run PromptSlimmer. The output `prompt-diff.md` will contain critical items marked:

```
| STATUS | PENDING_APPROVAL |
```

### Step 2 — Opus review (automatic)

For every critical change, PromptSlimmer automatically sends the original and proposed text
to `claude-opus-4-7` with the question: "Does the rewrite preserve identical semantic and
legal intent?" The Opus verdict (PRESERVED or DRIFT + one-sentence reason) is written into
the diff row.

### Step 3 — Human review

Open `output/prompt-diff.md`. For each PENDING_APPROVAL row:
1. Read the original and slimmed text side by side.
2. Read the Opus verdict.
3. Consult the appropriate stakeholder (see table below).
4. Change the STATUS field to `APPROVED` or `REJECTED`.

| Change category | Stakeholder |
|---|---|
| Escalation procedures | CX Ops lead |
| Compliance language | Legal or Compliance officer |
| Security instructions | Security team lead |
| SLA commitments | Product + Legal |
| Crisis response language | Safety team |

### Step 4 — Apply approved changes

```bash
/PromptSlimmer --apply-approved --diff output/prompt-diff.md --output-dir output/
```

This produces the final `system-prompt-slimmed.md` with all approved changes applied.
Rejected changes are left in their original form and logged in the report.

### Step 5 — Commit the audit trail

Commit all three output files to version control. The annotated `prompt-diff.md` is your
audit record: it shows every change, who approved it, and the Opus verdict. Do not discard it.

```bash
git add output/system-prompt-slimmed.md output/prompt-diff.md output/slimming-report.json
git commit -m "chore: apply PromptSlimmer run PSR-20260603-001 (60% reduction, 1 critical approved)"
```

---

## Expected ROI at Different Call Volumes

These estimates use the Sonnet input token price of $2.00/MTok and a 570-token saving per call
(the result from the sample run in this directory).

| Daily call volume | Daily saving | Monthly saving | Annual saving |
|---|---|---|---|
| 1 000 calls/day | $0.0011 | $0.34 | $4.16 |
| 10 000 calls/day | $0.011 | $3.42 | $41.61 |
| 100 000 calls/day | $0.114 | $34.20 | $416.10 |
| 1 000 000 calls/day | $1.14 | $342.00 | $4 161.00 |

Notes:
- If your prompt is cached (Anthropic prompt caching at 0.1x cost), the baseline cost per call
  is lower, but the relative saving percentage is the same.
- These figures are input-token savings only. A shorter system prompt often produces shorter
  model outputs as well — actual savings may be higher.
- PromptSlimmer itself costs ~8 000 input tokens per run. At any call volume above ~14 calls,
  the first run pays for itself within one day.

---

## Warning: Prompt Drift

Prompt drift is the gradual growth of a system prompt over time through accretion without
deletion. It is the primary reason prompts become bloated.

Common causes:
- **Post-incident patches** — an edge case happens, a rule is added to prevent it. The rule
  is never reviewed against existing rules for overlap.
- **New engineer additions** — someone reads the prompt, thinks a case is uncovered, adds a
  clarification. The case was already covered, just less explicitly.
- **Compliance audits** — legal adds language. Nobody removes the original, less precise
  version that covered the same ground.
- **A/B test leftovers** — a prompt variant that won gets merged, but the losing variant's
  phrasing is never fully removed.

Symptoms of drift:
- The same behavioral constraint appears in 3+ different phrasings.
- The prompt references tools, features, or workflows that no longer exist.
- New engineers describe the prompt as "hard to understand" or "seems like it contradicts
  itself."
- Token cost per call has grown by more than 20% in the last three months without a
  corresponding increase in capability.

Mitigation:
- Run PromptSlimmer after every batch of 5+ prompt edits.
- Add a rule to your prompt review process: every addition must be accompanied by a check
  for redundancy with existing directives.
- Schedule a quarterly PromptSlimmer run as a maintenance task even if no explicit changes
  have been made.
- Treat the prompt as code: it lives in version control, every change is reviewed, and
  deletions are as valid as additions.

---

## What PromptSlimmer Will Never Do

- Silently rewrite a prompt. Every change is logged.
- Remove or paraphrase a critical directive without Opus confirmation and human sign-off.
- Auto-resolve a contradiction. Contradictions are surfaced and block the affected cluster.
- Change a protected phrase. Protected phrases are copied byte-for-byte.
- Apply a critical change without an explicit APPROVED annotation in the diff file.

If any of these invariants would need to be violated to achieve further compression, the
slimmer stops and reports the blocker. It does not proceed.
