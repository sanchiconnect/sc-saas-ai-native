---
name: prompt-slimmer
description: "Audits system prompts and rules files for redundancy, overlapping intent, and verbosity. Produces a minimized prompt set plus a reviewable diff — never a silent rewrite. Critical sections (compliance, escalation, legal) require Opus review and human sign-off before any change is applied."
---

**name:** prompt-slimmer

**description:** Audits system prompts and rules files for redundancy, overlapping intent, and verbosity. Produces a minimized prompt set plus a reviewable diff — never a silent rewrite. Critical sections (compliance, escalation, legal) require Opus review and human sign-off before any change is applied.


# PromptSlimmer

Structural minimization of standing instructions for AI agents. Every token removed from a
system prompt compounds across every subsequent call. A single 60 % reduction on a 950-token
prompt at 1 000 calls/day saves roughly $1.14/day at $2/MTok — without changing behaviour.

---

## Inputs

| Field | Type | Description |
|---|---|---|
| `system_prompt` | string / path | The full system prompt to minimize |
| `rules_files` | JSON path | Additional rules files (CLAUDE.md equivalents) |
| `criticality_flags` | JSON path | Per-category safety classification and protected phrases |
| `output_dir` | path | Where to write slimmed artifacts (default: `./output/`) |

---

## Five-Phase Process

### Phase 1 — Audit

Goal: build a complete directive inventory before touching anything.

1. Parse the system prompt into discrete directives. A directive is any sentence or bullet that
   instructs the model to do, avoid, prefer, or prioritize something.
2. Group directives by topic cluster (tone, formatting, tool-use, escalation, compliance, etc.).
3. Within each cluster, flag:
   - **Exact duplicates** — identical wording appearing more than once.
   - **Semantic duplicates** — different wording, identical intent (e.g., "always be polite" and
     "maintain a courteous tone at all times").
   - **Superseded rules** — directives that reference removed features, deprecated tools, or
     workflows that no longer exist in the codebase.
   - **Contradictions** — directives that conflict; surface both and ask the human to resolve
     before proceeding.
4. Emit an audit manifest: each directive with its cluster, duplicate_of reference (if any),
   and an initial criticality guess based on the criticality_flags input.

### Phase 2 — Merge

Goal: collapse redundancy without altering any directive's intent.

Rules:
- When two or more directives share identical intent, keep the most specific / most recently
  authored version and discard the others. If authorship is unknown, keep the version that
  most closely mirrors the criticality_flags vocabulary.
- Dead rules (superseded by feature removal) are dropped entirely. Document each removal with
  the reason "feature no longer present."
- Contradictions are NOT auto-resolved. They are surfaced in the diff as `NEEDS_HUMAN_RESOLUTION`
  and block the merge phase for that cluster.
- Protected phrases (from `criticality_flags.protected_phrases`) must survive the merge
  verbatim — do not paraphrase, shorten, or reorder words within them.

### Phase 3 — Compress

Goal: rewrite verbose directives in minimal phrasing that preserves full semantic intent.

Techniques:
- Replace multi-sentence preambles with a single imperative sentence.
- Replace "You should always make sure that you…" with "Always…".
- Collapse parenthetical qualifiers that restate the main clause.
- Remove hedging filler ("please", "kindly", "it is important that", "remember to").
- Convert paragraph blocks to bullet lists where 3+ separate instructions are joined by prose.
- Never compress a directive that has been classified `critical`. Route it to the Opus model
  for a read-only review to confirm no semantic drift before leaving it unchanged.

Compression is applied only to directives classified `safe` or `review`. See criticality rules
below.

### Phase 4 — Classify

Every change produced by Phases 2 and 3 receives one of three classifications:

| Classification | Criteria | Required approval |
|---|---|---|
| `safe` | Formatting, tone phrasing, response-length hints, stylistic rewrites with zero behavioural impact | None — auto-apply |
| `review` | Tool-use rules, retry logic, data-handling instructions, output-structure requirements | Human spot-check — diff shown, apply after 24 h unless rejected |
| `critical` | Compliance language, escalation procedures, legal disclaimers, SLA commitments, safety/harm guardrails, PII handling | Opus review + explicit human sign-off required before any change |

Additional rules:
- If a directive contains a phrase in `criticality_flags.protected_phrases`, the entire
  directive is auto-elevated to `critical` regardless of its cluster.
- Removing a directive is always at least `review` — never auto-removed as `safe`.
- Adding a new directive (e.g., a consolidated replacement) is `safe` only when all source
  directives were `safe`.

For `critical` changes, PromptSlimmer will:
1. Send the original and proposed text to `claude-opus-4-7` with the instruction:
   "Confirm whether the proposed rewrite preserves identical semantic and legal intent.
    Reply PRESERVED or DRIFT with a one-sentence reason."
2. Include the Opus verdict in the diff report.
3. Block application until a human explicitly marks the item `APPROVED`.

### Phase 5 — Diff

Goal: produce a structured, human-readable audit trail.

Output artifacts:
1. **`system-prompt-slimmed.md`** — the minimized prompt with all `safe` changes applied,
   `review` changes staged, and `critical` changes left in their original form until approved.
2. **`prompt-diff.md`** — side-by-side diff with columns:
   ORIGINAL | SLIMMED | CHANGE_TYPE | TOKENS_SAVED
   Each row is one directive change. Summary header shows aggregate counts and token savings.
3. **`slimming-report.json`** — machine-readable audit record for pipeline integration.

---

## Criticality Classification Reference

### Safe — auto-apply

- Tone adjectives ("professional", "friendly", "warm")
- Formatting preferences (bullet vs. prose, response length guidance)
- Filler removal ("please", "kindly", "make sure that")
- Consolidating 4 "be polite" variants into 1

### Review — human spot-check

- Tool invocation rules (when to call, parameter constraints)
- Retry and fallback logic descriptions
- Output schema requirements
- Any rule referencing a named integration (Salesforce, Stripe, etc.)

### Critical — Opus review + human sign-off

- Escalation procedures (when and how to escalate to a human agent)
- Compliance language required by regulation (GDPR, CCPA, SOC 2, PCI-DSS, HIPAA)
- Legal disclaimers and liability language
- SLA commitments ("respond within 2 hours")
- Safety guardrails (what the agent must never do)
- PII handling and data retention statements
- Anything in `protected_phrases`

---

## Customer Service Context: Protected Categories

When running against a customer service chatbot prompt, the following categories receive
automatic `critical` classification regardless of phrasing:

- **Escalation rules** — any directive describing when to transfer to a human agent, open a
  ticket, or trigger an alert. Over-trimming here can strand customers without support.
- **Compliance language** — any reference to data privacy, recording consent, GDPR/CCPA rights,
  or regulatory body names.
- **SLA commitments** — any time-bound promise ("within 24 hours", "next business day").
- **Refund and compensation policies** — these carry legal and financial weight.
- **Security instructions** — rules about never sharing account credentials, PINs, or
  internal system URLs.

---

## Safety Invariants

These rules are not negotiable and override all compression goals:

1. PromptSlimmer NEVER produces a silently modified output. Every change is logged.
2. PromptSlimmer NEVER removes or rephrases a `critical` directive without Opus confirmation
   AND human sign-off. The slimmed file is never written until sign-off is recorded.
3. PromptSlimmer NEVER removes a contradiction — it surfaces both sides and halts for resolution.
4. Protected phrases are copied byte-for-byte into the output. No synonym substitution.
5. The original prompt is preserved unchanged in the audit record, regardless of outcome.
6. If token counting is unavailable, conservative estimates are used and flagged as estimates.

---

## Usage

```bash
# Basic invocation
/PromptSlimmer \
  --system-prompt input/system-prompt-verbose.md \
  --rules-files input/rules-files.json \
  --criticality-flags input/criticality-flags.json \
  --output-dir output/

# Dry-run: produce diff only, write nothing
/PromptSlimmer --dry-run ...

# Apply only safe changes (skip review/critical staging)
/PromptSlimmer --apply-level safe ...
```

---

## Approval Workflow for Critical Changes

1. PromptSlimmer writes `output/prompt-diff.md` with all critical items marked `PENDING_APPROVAL`.
2. Reviewer reads each critical row. The Opus verdict is shown inline.
3. Reviewer annotates the diff file: change `PENDING_APPROVAL` to `APPROVED` or `REJECTED`.
4. Re-run PromptSlimmer with `--apply-approved` flag. It reads the annotated diff, applies
   approved changes, skips rejected ones, and emits a final `system-prompt-slimmed.md`.
5. The annotated diff and final report are committed to version control as the audit trail.
