# SpecPod — a spec-driven AI-development framework

A complete operating system for **spec-driven, AI-native software delivery**: a
library of 69 reusable skills, phase-by-phase runbooks, reference contracts, and a
deterministic orchestration engine. It is built for a small pod (a lead plus two
or three AI builders) running weekly sprints, where the project's truth lives in
**files in the repository** rather than in a chat, and every AI action is
manufactured from those files and checked against them.

> **Names are placeholders.** "SpecPod" (the framework) and "Acme Corp" (the
> example organisation) are neutral stand-ins introduced during sanitization.
> Replace them with your own. See `CHANGES.md` for the full record of what was
> de-branded and repaired.

## Start here

New to the ideas? Read these two documents first, in `docs/`:

1. **`docs/01-understanding-skills-and-spec-driven-development.md`** — what skills
   and spec-driven development are, and why the framework is built the way it is.
2. **`docs/02-adoption-handbook.md`** — prerequisites, a step-by-step first sprint
   for a 3–4 person pod, and how to bring the framework to existing software.

## What's in the package

| Path | What it is |
|---|---|
| `.claude/` | The 69 skills, each a `SKILL.md` procedure plus supporting scripts, references, and worked examples |
| `.claude/skill-orchestrator/` | A deterministic scheduling engine (Python, with a passing test suite and an end-to-end sprint example) |
| `prompts/` | Five sequential phase runbooks an operator executes in order |
| `references/` | Repo-level contracts: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, and reference artifacts (`openspec.yaml`, sprint capacity) |
| `skill_catalog.md` | The master catalog of every skill |
| `docs/` | The two onboarding documents above |
| `CHANGES.md` | The sanitization and repair changelog |

## The shape of the work

The specs under a project's `specs/` folder are the source of truth. Each sprint
locks a slice of them into `openspec.yaml`; skills decompose that into small tasks;
a coding agent builds each task to conform; other skills verify it against the
locked acceptance criteria; a human approves at gates. Rework ripples forward, so
the specs and the code never quietly diverge. The full lifecycle — knowledge
capture, spec generation, planning, build, validation, operations — is described
in `docs/01`.

## Verifying the orchestrator

```bash
cd .claude/skill-orchestrator
PYTHONPATH=src python3 -m pytest tests/ -q        # expect: 41 passed
cd examples/SpecPod
PYTHONPATH=../../src python3 run_sprint.py         # expect: complete = True
```

## A note on scope

The 69 skills are a superset. A given project rarely needs all of them — the
planning skill (`skill-flow`) is designed to select the relevant subset per
project, and the adoption handbook recommends starting with a small tier and
widening. Adopt the artifacts and the discipline; don't feel obliged to run every
skill on day one.
