# `prabs/` (SpecPod framework) — briefing for leadership

## TL;DR

We were handed a 69-skill "spec-driven AI development" toolkit. We didn't adopt it wholesale —
we tested one piece of it against a real repo, it found real bugs and real documentation drift,
we fixed what was real and rejected what wasn't. **Recommendation: adopt 2-3 specific skills as
tools, not the framework as a process.**

---

## What it is, in one paragraph

A packaged methodology + Claude Code skill library built around one idea: keep product truth in
files (specs), not in chat history, and use AI to both build against those files and check its
own work against them. It's designed for a dedicated 3-4 person pod running formal weekly
sprints with locked scope and human approval gates.

## Why this isn't a cold pitch — we already do a version of it

Before touching `prabs/`, our workspace `CLAUDE.md` already had the same DNA: per-repo module
specs, workspace feature specs, an approval-gated spec lifecycle, and cross-repo audit skills
(`/trace-flag`, `/audit-contract`, `/check-isolation`). So this wasn't "should we start doing
spec-driven development" — it was "does this specific toolkit add anything to what we already
run."

## What we actually tested (not theory — a real trial)

We ran one skill (`code-extraction` — reverse-engineers docs from live code) against
`ai-startups-analyzer`, our AI scoring service. Result:

- **It found real, verifiable drift.** Our specs said a lifespan bug was still broken — it was
  actually already fixed in code. Our specs said the LLM concurrency defaults were 16/5 — the
  code has shipped 10/3 in production for a while. Our specs said the default AI provider was
  Gemini — the code (and our own `CLAUDE.md`) says OpenAI. One module spec listed 9 API routes
  that don't exist in the codebase at all.
- **It found a real, likely-active bug**: a crash on every CSV upload in local-storage mode
  (the default), caused by a variable only being set on the S3 code path. We fixed it and
  verified the fix compiles clean.
- **It also produced a false positive that we caught before shipping it**: it flagged a
  "missing authentication" endpoint as a security gap. We initially fixed it. Checking the
  actual consumer's code first showed that endpoint is called directly from the admin panel's
  browser JavaScript by design, with no auth header — "fixing" it would have broken a live
  production feature (the progress-polling modal) for every user. We reverted the change and
  documented it as intentional instead.

**That last point is the whole argument for how to use this tool: treat every finding as a lead
to verify against the real consumer, never as an instruction to act on directly.**

## The honest cons

- The full framework (locked sprints, scoring gates, a dedicated orchestrator) is built for a
  formal multi-person pod. We don't run that cadence, and importing it would slow us down for
  no measurable gain.
- Several of its 69 skills duplicate audits we already have.
- Its output still requires the same human review our hand-written specs already get — it's a
  faster first draft, not a replacement for judgment.

## Recommendation

Don't adopt the framework. Adopt three specific tools from it, one at a time, always with a
human verifying findings against real consumer code before acting:

1. **`code-extraction`** as a periodic drift-check on repos where specs and code have likely
   diverged — proven valuable in the trial above.
2. **A decision ledger** — cheap to add, closes a real gap in traceability across our 7 repos.
3. **LLM red-teaming / eval skills** — applied specifically to `ai-startups-analyzer`, our only
   AI-facing service, which currently has no prompt-injection or regression testing at all.

## Bottom line to say out loud

*"We tried a piece of it on a real service. It surfaced two genuine issues — one bug, one stale
doc set — and one false alarm that we caught by checking the real code before acting. That's
exactly the trust model we should apply going forward: useful as a fast first pass, not as an
authority."*
