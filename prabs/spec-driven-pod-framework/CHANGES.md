# CHANGES — sanitization and repair

This package is a cleaned, de-branded, and repaired version of an internally
developed spec-driven AI-development framework. This file records exactly what
was changed, so the diff from the original is transparent.

## 1. Branding redacted

All proprietary identity was replaced with neutral placeholders. **These are
placeholders — replace them with your own names when you adopt the framework.**

| What it was | Replaced with |
|---|---|
| The originating organisation's name | `Acme Corp` (a standard placeholder) |
| The framework's original codename (two variants) | `SpecPod` |
| The worked-example project's id / directory | `SpecPod` |

90 files were updated. WCAG accessibility levels (`AA`, `AAA`) were deliberately
left untouched — they are a technical standard, not an organisation's initials.

## 2. Broken pieces fixed

**A half-finished rename had broken the test suite.** The orchestrator's tests and
`run_sprint.py` expected the example project directory and its sprint workflow file
under one name, but the directory had been partially renamed to a second name.
Result on a fresh checkout: 7 of 41 tests failed with `FileNotFoundError` and the
integration test silently skipped. Fixed by unifying the whole token set to one
consistent name (now `examples/SpecPod/` with `SpecPod-sprint.workflow.json`) and
removing a byte-for-byte-identical duplicate workflow file left behind by the
partial rename.

- **Before:** `33 passed, 7 failed, 1 skipped`
- **After:** `41 passed`

**Every SKILL.md was missing YAML frontmatter.** All 69 skills shipped without the
`name` / `description` header that drives skill discovery and triggering. Valid
frontmatter was added to all 69. Descriptions were derived from each skill's own
authored description line or Purpose section (see limitation 4 below).

**Broken skill path references.** The phase prompts and the master catalog
referenced skills in PascalCase (`.claude/DevCopilot/`) while the directories are
kebab-case (`.claude/dev-copilot/`) — roughly 40 references that would not resolve
on a case-sensitive filesystem. All were rewritten to the real directory names.

**Directory-name inconsistencies fixed:**
- `.claude/SkillFlow/` → `.claude/skill-flow/` (the one PascalCase directory; now consistent with the rest)
- `.claude/budget-governer/` → `.claude/budget-governor/` (spelling)
- `.claude/evalharness/` → `.claude/eval-checkpoint/` (disambiguated from the distinct `eval-harness` skill — see limitation 3)

**Cruft removed:** 2 `.DS_Store` files, all `__pycache__` / `.pytest_cache`
directories and `.pyc` files, and 2 UTF-8 byte-order marks at the start of
markdown files.

## 3. Verification (post-repair)

- `41 passed` — orchestrator test suite green.
- End-to-end sprint simulation runs to `complete = True`.
- `0` residual brand strings across the package.
- `0` unresolved skill path references in prompts and catalog.
- All 69 `SKILL.md` files carry valid, parseable YAML frontmatter.

## 4. Known limitations (not fixed — flagged for the adopter)

These were left as-is because fixing them is a deployment choice, not a defect
repair. They do not affect the framework's execution.

1. **Pinned model IDs.** Skills name specific model versions (e.g.
   `claude-sonnet-4-20250514`) in their metadata. Update these to the models you
   actually use. Consider centralising them in one config rather than per-skill.
2. **Pricing table.** The cost-governance skill contains a hard-coded price table
   that may be stale. Verify against current pricing before relying on its dollar
   estimates.
3. **Two evaluation skills.** `eval-harness` (the sprint's LLM-as-judge scoring
   framework) and the renamed `eval-checkpoint` (a continuous checkpoint gate from
   the optimisation layer) overlap in territory. They are now uniquely named, but
   whether to keep both or merge them is your call.
4. **Auto-derived skill descriptions.** The frontmatter descriptions were generated
   from each skill's existing content. They are accurate and functional but are a
   sensible baseline, not hand-tuned trigger copy — refine them per deployment for
   sharper skill selection.
5. **`.claude/memory/` path.** References to `.claude/memory/<agent_id>/` in the
   memory-persistence skill and catalog are intentional *runtime data paths* (where
   session state is written), not skill-directory references. Left as designed.

---

*Everything in section 2 was verified by re-running the framework's own tests and
the end-to-end sprint after each change.*
