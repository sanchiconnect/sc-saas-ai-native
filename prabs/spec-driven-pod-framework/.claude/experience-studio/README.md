# ExperienceStudio

Validates that every UI/UX design decision is causally traceable to a documented stakeholder intent in `ui-ux.md` and `openspec.yaml`. Operates as the Gate 2 design sign-off mechanism — build does not proceed until every spec user journey has a corresponding, conformant UI path.

---

## When to Use

Invoke when an AI Builder has produced or updated UI components, a design decision contradicts a documented user journey, or the POD Lead requires Gate 2 design sign-off before build continues.

**Trigger phrases:** `validate design`, `run ExperienceStudio`, `check UX conformance`

---

## Inputs

| Input | Required |
|---|---|
| `specs/ui-ux.md` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/features.md` | Mandatory |
| UI artefacts (screenshots, Figma exports, component code) | Mandatory |

## Outputs

- `artifacts/experience-conformance-report.md` — per-journey ALIGNED / DEVIATED / UNCOVERED / EXTENDED verdict
- Gate 2 attestation (if all journeys pass)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| DevCopilot produces UI components | Build continues (Gate 2) |
| | NexusDeploy |
