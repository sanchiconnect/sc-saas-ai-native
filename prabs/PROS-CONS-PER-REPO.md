# `prabs/` (SpecPod) — pros & cons per repo, across the full SanchiSaaS product

*Not a go/no-go evaluation — this assumes some parts of the framework are worth using
(confirmed by the `ai-startups-analyzer` trial) and asks, repo by repo, what applying
it would actually look like: what it adds, what it costs, what to skip.*

Current spec coverage, verified directly against each repo (not from memory):

| Repo | `module.spec.md` files | Workspace feature specs | AS-IS extraction files (`knowledge.md`/`api.md`/`database.md`) | Test suite |
|---|---|---|---|---|
| `sanchiconnect-saas-tenants` | 7 | 4 (FT-001..004) | none | none found |
| `sc-saas-backend` | 58 | 8 (FA-001..008) | none | `test/` exists |
| `sc-saas-frontend` | 32 | 12 (FE-001..012) | none | `test.ts` scaffold |
| `sc-saas-admin` | 31 | 8 (FA-001..008, shared with backend feature specs) | none | none found |
| `ai-startups-analyzer` | 1 | 2 (FAI-001..002) | **4 — created this session** | none found |
| `sc-saas-3rdparty-webservices` | 8 | 0 dedicated (covered by backend's FA specs as a consumer) | none | `test/` exists |
| `sanchiconnect-saas-tenants-admin` | 4 | 0 dedicated | none | none found |

Every repo already has module-level spec coverage from prior work — none of these are
truly greenfield for `code-extraction`. The question per repo is whether AS-IS
extraction is worth running as a **drift check** (as it was on `ai-startups-analyzer`),
and which of the other ~68 skills fill a real gap.

---

## `sanchiconnect-saas-tenants` — control plane / cockpit

**Pros of applying prabs/ here:**
- Highest blast radius in the whole product (owns flag names + tenant provisioning; reaches all 3 downstream consumers) — the **decision-ledger** pays off most here, since flag/tenancy changes ripple furthest and are hardest to trace after the fact.
- `code-extraction` run against `TenantUsersEntity` and the provisioning flow would directly stress-test whether the 7 module specs still match the live flag list — the single most drift-prone artifact in the product per your own invariant #1.
- **`drift-guard`** is most valuable on this repo specifically, since it's the source of truth other repos silently depend on.

**Cons:**
- No test suite found — `guardian` (spec→Gherkin tests) would be generating tests for code that has zero existing regression coverage to compare against; higher risk of the generated tests just codifying current (possibly wrong) behavior instead of intended behavior.
- Highest-risk repo to run *any* automated extraction/rewrite against given its blast radius — any output must go through your existing human review bar before touching `module.spec.md`, no exceptions.
- 7 specs is a small surface — full `code-extraction` here is a half-day job, not the multi-week retrofit the framework assumes for genuinely undocumented systems.

---

## `sc-saas-backend` — business API, contract owner

**Pros:**
- Owns the API contract — **`drift-guard`/`parity-checker`** (production behavior vs. spec) is a natural extension of your existing `/audit-contract`, which only checks contract *consistency*, not runtime *drift*.
- 58 module specs is your largest, most mature spec surface — a good candidate to trial **`guardian`** (spec→test generation) since you have both specs and an existing `test/` directory to compare generated tests against.
- Has the only real test suite among your NestJS repos — lowest-risk repo to add automated spec-driven testing to.

**Cons:**
- Largest repo (58 module specs) — running `code-extraction` wholesale here would be the most expensive single trial in the product; the `ai-startups-analyzer` trial (1 module) took ~10 minutes of agent time and ~226K tokens for a single small service. Scaled to 58 modules this is a multi-hour, multi-hundred-thousand-token job for uncertain incremental value given specs are already fairly current.
- Best used narrowly: pick the modules most recently touched or most contract-sensitive (e.g. the PowerPitch external integration, per your invariant #6) rather than running extraction against the whole repo.

---

## `sc-saas-frontend` — Angular PWA

**Pros:**
- 12 feature specs (FE-001..012) is good coverage — `guardian` could generate Gherkin/Playwright-style tests from acceptance criteria you've already written, which is a genuine gap since frontend E2E coverage tends to be the first thing skipped under deadline pressure.
- Lowest cross-repo invariant risk of the four "core" repos (it consumes, not owns, contracts) — a safer place to experiment with new skills before trying them on `tenants` or `backend`.

**Cons:**
- `code-extraction`'s value here is lowest of all seven repos — Angular/NgRx state and component structure are already well-documented via your `IFeatures`/`brand.model.ts` conventions, and UI/UX work is explicitly called out in the framework's own docs as the domain where spec-driven development "has less to offer" (evaluation criteria, taste-heavy work).
- No dedicated `ai.md`/LLM-facing surface — the red-team/eval skills (your highest-value category) don't apply here at all.

---

## `sc-saas-admin` — PHP admin panel

**Pros:**
- 31 module specs already, but PHP has no test suite and no CI (per its own `CLAUDE.md`) — this is the repo where **`guardian`** could add the most net-new safety, since currently "done" here means "someone manually clicked through it."
- Directly consumes `ai-startups-analyzer` — a `drift-guard` pass here would catch the admin-side half of any future analyzer contract break (as opposed to the analyzer-side half we just checked by hand this session).

**Cons:**
- No test framework to run generated tests against — `guardian`'s output would need a testing harness stood up first (the framework's own prerequisites, Part A.2, list "a test framework" as a hard requirement you don't currently have for PHP).
- Dual-DB architecture (reads tenants DB directly + calls backend) makes `code-extraction`'s database.md output ambiguous — it would need to clearly separate "admin's own reads" from "tenants' owned schema," which the skill's template doesn't natively distinguish.

---

## `ai-startups-analyzer` — AI scoring service (trialed this session)

**Already run — concrete outcome, not a prediction:**
- `code-extraction` found real, verifiable drift: a "known bug" that was actually already fixed (lifespan re-enqueue), a security finding that was narrower than documented (CORS), two config defaults that were flatly wrong in specs (`DEFAULT_PROVIDER`, concurrency), and a route inventory with 9 phantom endpoints.
- It also surfaced two real code issues (a crash-on-upload bug, a missing-auth gap) — one was a genuine fix, the other turned out to be a false positive that would have broken production (the extraction agent doesn't know how `sc-saas-admin`'s browser JS calls this service; only reading the actual consumer code caught that).

**Lesson generalizable to every other repo above:** treat every `code-extraction` finding as a *lead to verify against the actual consumer*, never as an instruction to act on directly. The framework's own "extraction is approximate" warning is not boilerplate — it's the exact failure mode we hit.

**Cons specific to this repo:** it's your only LLM-facing service, so it's the one place the red-team/eval skills are unambiguously worth the investment — but also the one repo where "no test suite" (per its `CLAUDE.md`) means any spec-driven test generation is starting from zero.

---

## `sc-saas-3rdparty-webservices` — integration gateway (leaf node)

**Pros:**
- Stateless leaf node with no downstream blast radius — the lowest-risk repo in the product to experiment with any prabs/ skill, since a bad extraction or a wrong spec correction here can't cascade to another repo.
- 8 module specs, one per third-party integration (SMS, email, video, chat, URL shortening, docs) — a clean, small unit for testing whether `guardian` can generate meaningful tests for thin proxy/adapter code (a different shape of problem than the CRUD-heavy backend).

**Cons:**
- Low intrinsic value for `code-extraction` — it's a stateless proxy to external providers, so "as-is data model" (`database.md`) is essentially empty, and "as-is API surface" duplicates what the 8 existing module specs already say clearly.
- Because it only proxies to already-documented third-party SDKs (Twilio-style, SendGrid, etc.), most of its "business logic" is really just each provider's own contract — a `code-extraction` pass would mostly restate their public docs.

---

## `sanchiconnect-saas-tenants-admin` — tenants control-plane admin UI (leaf node)

**Pros:**
- Newer repo (added this session per prior work), only 4 module specs, no dedicated feature spec — genuinely closer to "brownfield" than any other repo, making `code-extraction` here more likely to add real net-new coverage rather than mostly cross-checking existing docs.
- Shares the tenants MySQL DB directly with `sanchiconnect-saas-tenants` (per invariant in root `CLAUDE.md`) — `code-extraction`'s `database.md` output here is a good forcing function to make the shared-schema risk explicit in writing, since right now it lives only in the root `CLAUDE.md` prose.

**Cons:**
- Being a leaf node with no downstream callers, a `decision-ledger` here has the least payoff of any repo — nothing else depends on tracing why a change happened here.
- PHP, no test suite, no CI — same `guardian` prerequisite gap as `sc-saas-admin`.

---

## Cross-repo pattern (what's true everywhere)

- **Every repo already has module specs.** `code-extraction`'s realistic job across this product is drift-detection against existing docs, not first-time documentation — set that expectation before running it anywhere else, so nobody's surprised it "just" produces a diff-like report instead of a blank-slate spec.
- **Extraction findings are leads, not conclusions**, full stop — proven directly on `ai-startups-analyzer`, where trusting the report without checking `sc-saas-admin`'s actual browser code would have shipped a production-breaking change.
- **The pod/gate/sprint ceremony still doesn't fit any of the seven repos** — you're not running weekly locked sprints on any of them; nothing above changes that conclusion.
- **Decision ledger and drift-guard scale roughly with blast radius**: highest value on `tenants` and `backend` (invariant owners), lowest on the two leaf nodes (`3rdparty-webservices`, `tenants-admin`).
- **Red-team/eval skills apply to exactly one repo** (`ai-startups-analyzer`) — it's the only LLM-facing surface in the product, so that's where 100% of that category's value concentrates.
