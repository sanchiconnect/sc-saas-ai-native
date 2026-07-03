# skill-generator

Materializes unresolved SkillFlow recommendations into actual skill files. Takes the `recommendation_report.md` produced by the SkillFlow Engine and creates or patches `.claude/` skill files, keeping `skill_catalog.md` in sync after every change.

---

## When to Use

Run after the SkillFlow Engine has produced `recommendation_report.md` and you are ready to act on its Candidate New Skill or Skill Enhancement recommendations.

---

## Inputs

| Input | Required |
|---|---|
| `recommendation_report.md` | Mandatory |
| `skill_catalog.md` | Mandatory |
| `recommendation_summary.md` | Optional |
| `skillflow_skip.md` (prior run) | Optional |

---

## Outputs

| Output | Description |
|---|---|
| `.claude/<skill-name>/SKILL.md` | New skill definition (new skills) |
| `.claude/<skill-name>/README.md` | New or updated README |
| `skill_catalog.md` | Updated catalog entries |
| `skillflow_skip.md` | Skills rejected by the user — used by prompt files as the execution gate |
| `skill_generation_report.md` | Audit log of the run |

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| SkillFlow Engine (`skill-flow`) | Phase 02+ skill execution |
| skill-catalog-generator | — |

---

## Key Behaviors

- **User gate at Phase 2** — presents all recommendations for accept/reject before touching any file
- **Assumptions review at Phase 3** — confirms interpretation of every accepted item with the user before generating content
- **Never modifies prompt files** — rejected skills are written to `skillflow_skip.md`; prompt files read that file as the skip gate
- **Catalog always updated** — every creation or enhancement is reflected in `skill_catalog.md` before the run ends
- **Nothing written without final approval** — Phase 6 presents a full write summary and waits for user confirmation
