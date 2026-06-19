---
description: Scaffold a new spec (feature or module) from the template.
argument-hint: feature <linear-id> | module <repo>/<module>
---
$ARGUMENTS
- "feature <linear-id>": delegate to the spec-author subagent for that Linear issue.
- "module <repo>/<module>": copy specs/module.spec.template.md to <repo>/src/<module>/module.spec.md, fill what you can infer from code, leave TODOs.
