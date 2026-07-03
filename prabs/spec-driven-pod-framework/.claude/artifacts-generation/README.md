# artifacts-generation

A collection of on-demand artifact generator utilities for the SpecPod framework. Each generator runs automatically from existing specs — no human input required unless gaps are found that cannot be inferred.

Invoke any generator individually when its target artifact is missing or needs to be regenerated. These are not tied to any execution phase and do not run as part of the sequential prompt files.

---

## Generators

| File | Skill Name | Generates |
|---|---|---|
| `create-openspec.md` | CreateOpenspec | `artifacts/openspec.yaml` · `artifacts/sprint-capacity.yaml` |
| `create-policy-library.md` | CreatePolicyLibrary | `references/policy-library.md` |
| `create-cursorrules.md` | CreateCursorrules | `.cursorrules` (project root) |
| `create-agents.md` | CreateAgents | `AGENTS.md` (project root) |
| `create-data-contracts.md` | CreateDataContracts | `data-contracts/<entity>.yaml` (one per database entity) |

---

## When to Use

| Generator | Invoke When |
|---|---|
| CreateOpenspec | Conductor, SpecFlow, or any downstream skill reports `openspec.yaml` or `sprint-capacity.yaml` absent |
| CreatePolicyLibrary | PolicyCatalog reports `references/policy-library.md` missing |
| CreateCursorrules | `.cursorrules` is absent at project root, or tech stack changes |
| CreateAgents | `AGENTS.md` is absent at project root, or program context changes |
| CreateDataContracts | TrustFabric requires data contracts and `data-contracts/` folder is absent or incomplete |

---

## Inputs (shared across all generators)

All generators read from the Phase 01 specification set. The specific files each generator requires are defined in its own skill file.

Common inputs:
- `specs/program.md`
- `specs/knowledge.md`
- `specs/design.md`
- `specs/database.md`
- `specs/api.md`
- `specs/impl.md` (where present)

---

## Framework Position

These generators are invoked on-demand by other skills or directly by the user. They do not appear in any sequential prompt file and have no phase dependency. Any skill that requires one of the above artifacts may invoke the corresponding generator as a prerequisite.
