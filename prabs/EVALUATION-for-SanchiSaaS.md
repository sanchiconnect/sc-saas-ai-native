# Should SanchiSaaS adopt the `prabs/` (SpecPod) framework?

*An evaluation of `prabs/spec-driven-pod-framework` against how this workspace already operates.*

---

## 1. What it actually is (one paragraph)

A 69-skill Claude Code toolkit built around one idea: keep product truth in files
(`specs/*.md`), lock a week's work into `openspec.yaml`, build against that locked
scope, and run a *separate* AI verifier pass (conformance score ≥ 0.90, zero
critical failures) before a human approves at a gate. It assumes a dedicated pod
of 3–4 people running formal weekly sprints (Mon: plan/lock, Tue–Thu: build,
Fri: validate/release).

---

## 2. Where SanchiSaaS already overlaps with it

You are **not starting from zero** — `CLAUDE.md` already encodes the same
philosophy in lighter form:

| SpecPod concept | Your equivalent today |
|---|---|
| `specs/*.md` domain files | `specs/features/*.spec.md`, per-repo `module.spec.md` |
| `openspec.yaml` sprint lock | Spec frontmatter status: `draft→approved→in-progress→in-review→done` |
| Gate 0–3 human checkpoints | Your approval step before `/spec-implement` |
| Conformance verifier | `/audit-contract`, `/trace-flag`, `/check-isolation` gates |
| Pod Lead / AI Builders | You + Claude Code agents (`spec-author`, `spec-implementer`) |
| `code-extraction` (brownfield) | Not present — you hand-wrote specs via parallel agent sweeps |
| `decision-ledger` | Not present |
| Conformance scoring, red-team, drift-guard | Not present |

So the real question isn't "adopt or not" — it's **which of the 20% of SpecPod
you're missing is worth bolting onto the 80% you already built.**

---

## 3. Pros (as applied to a 7-repo poly-repo like yours)

- **Brownfield spec extraction (`code-extraction`)** is a genuine gap-filler. Three
  of your repos (`ai-startups-analyzer`, `sanchiconnect-saas-tenants-admin`,
  `sc-saas-3rdparty-webservices`) are newer/untracked and have thinner spec
  coverage than the other four — this generates `knowledge.md` / `api.md` /
  `database.md` straight from the code instead of manual agent sweeps.
- **Decision ledger.** With 7 independently-deployed repos and cross-repo
  invariants (flags, API contract, auth), "why was this changed" currently lives
  in commit messages and your memory. An append-only ledger is cheap and pays off
  exactly at month 3–6, which is your stated pain point already (flag drift,
  contract drift).
- **Drift/parity checking.** You already gate contract drift with
  `/audit-contract`; SpecPod's `drift-guard`/`parity-checker` is the same idea
  extended to *production* behavior vs. spec, which you don't currently check
  post-deploy.
- **LLM safety net (`red-team-x`, eval/golden-reference skills).** You run a real
  LLM feature (`ai-startups-analyzer`, multi-provider scoring). Prompt-injection
  testing and golden-reference regression are risk you're currently carrying
  uncovered — this is the single highest-value piece in the whole package for you.
- **Test-from-spec (`guardian`).** Your feature specs already have acceptance
  criteria; auto-generating Gherkin tests from them (instead of from the code) is
  a stronger oracle than what you have now.
- **It's designed to be partially adopted.** The framework's own docs say a
  project rarely needs all 69 skills and recommends starting with a small tier —
  this isn't a system you have to swallow whole to get value from.

## 4. Cons / risks (be honest about these before adopting anything)

- **Process weight mismatch.** The pod/gate/weekly-sprint ceremony, conformance
  scoring, and `openspec.yaml` locking are built for a **3–4 person pod running
  formal sprints**. You're operating more solo/small-team with Claude Code as
  the builder — importing the full ceremony would slow you down for no benefit
  (this is even called out as a cost in the framework's own docs: "it taxes
  speed," "small changes get heavier").
- **Redundant machinery.** Several skills duplicate what your `.claude/`
  slash-commands already do (`/trace-flag` ≈ flag-impact skills, `/audit-contract`
  ≈ contract-verification skills, `/check-isolation` ≈ tenant-scoping checks).
  Running both systems side by side would just be double bookkeeping.
- **Extraction is approximate, not authoritative.** `code-extraction` reads what
  the code *does*, not what it *should* do — every generated spec needs the same
  human review pass you already give your hand-written specs. It's a head start,
  not a shortcut past review.
- **Specs rot if unmaintained** — true of your current specs too, but adding more
  spec surface (ledger, extracted specs) means more surface to keep honest. Only
  worth it if you'll actually maintain what gets generated.
- **Placeholder/example content.** The package ships with "SpecPod"/"Acme Corp"
  branding and a demo accounts-payable sprint — cosmetic, but a reminder this is
  a generic template, not something written for your domain.
- **69 skills is a lot of surface to even evaluate.** Without deliberately
  scoping down, this becomes a "shiny toolkit" time sink rather than a net
  productivity gain.

---

## 5. Verdict: useful, but only in parts

**Don't adopt:** the pod/sprint ceremony, `openspec.yaml` locking, conformance
scoring, the deterministic orchestrator, gate 0–3 formalism. You already have a
working lighter-weight version of this via spec status + `/spec-implement`.

**Do adopt (in this order of value):**

1. **`code-extraction`** — run once against each of the three thin-spec repos
   (`ai-startups-analyzer`, `sanchiconnect-saas-tenants-admin`,
   `sc-saas-3rdparty-webservices`) to backfill `knowledge.md`/`api.md`/`database.md`
   drafts, then human-review them the same way you reviewed the hand-written ones.
2. **`decision-ledger`** — add one append-only ledger file per repo (or one at
   workspace root) for any change that touches a flag, contract, or invariant.
   Low effort, directly serves your existing "trace a flag / audit a contract"
   workflow.
3. **`red-team-x` + eval/golden-reference skills** — apply specifically to
   `ai-startups-analyzer` (prompt injection, provider-switch regression, the
   frozen 0–500→1–5 scoring contract). This is your actual uncovered risk.
4. **`guardian`** (spec → Gherkin tests) — optional, try it on one feature spec
   (e.g. `FAI-001-application-scoring`) to see if generated tests are better
   oracles than what you write by hand today.
5. **`drift-guard` / `parity-checker`** — later-stage, once (1)–(3) are in and
   you want production behavior checked against spec continuously.

---

## 6. How to use the adopted parts properly

- **Treat each skill as a one-off tool, not a subscribed process.** Point Claude
  Code at the specific `SKILL.md` (e.g.
  `prabs/spec-driven-pod-framework/.claude/code-extraction/SKILL.md`), give it
  the inputs it names (a repo path), let it write its outputs, then review by
  hand — exactly like you already do with `spec-author`.
- **Never let extracted/generated specs skip your existing review step.** Same
  human-validation bar as your hand-authored `specs/features/*.spec.md`.
- **Route new artifacts through your existing conventions, not new ones.** E.g.
  extracted specs go into the repo's own `module.spec.md` (per your template),
  not into a parallel `specs/` structure copied from SpecPod. A decision ledger
  entry should be one line per decision, referencing the flag/contract/invariant
  it touches — mirror the tone of your `CLAUDE.md` invariants table, not
  SpecPod's generic format.
- **Don't wire in the orchestrator, gate scoring, or sprint locking** unless you
  later grow into an actual multi-person pod — until then it's pure overhead.
- **Re-evaluate per repo, not globally.** `ai-startups-analyzer` benefits most
  right now (LLM risk + thin specs); the four mature repos (`tenants`, `backend`,
  `frontend`, `admin`) already have specs and gates — lower priority for
  extraction, higher priority for the ledger once flag/contract changes happen.

---

## 7. How this helps SanchiSaaS specifically

- Closes the **spec-coverage gap** on your three newest repos without another
  round of manual parallel-agent spec sweeps.
- Adds **historical traceability** across a 7-repo blast-radius graph where "why
  did tenants change this flag" currently isn't answerable without git archaeology.
- Adds **actual safety testing** for the one repo in your stack that talks to an
  LLM in production — currently your only unguarded surface per your own
  documented findings (CORS wide open, lifespan bug already known; injection
  testing not yet covered).
- Costs almost nothing to trial: `code-extraction` and `red-team-x` are
  read-only/additive — they don't touch your existing `/audit-contract`,
  `/trace-flag`, `/check-isolation` skills or your spec-implement pipeline.

---

*Next step: run `code-extraction` against `ai-startups-analyzer` as a trial and
review what it produces before deciding whether to run it on the other two
thin-spec repos.*
