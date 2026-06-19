---
description: Produce the full cross-repo plan to rename or remove a feature flag without leaving anything dangling
argument-hint: "<flag-name> rename <new-name> | <flag-name> remove"
---

Produce the safe cross-repo change plan for: $ARGUMENTS

Delegate to the `flag-impact-planner` subagent. Pass the flag and operation (`rename <old> <new>` or `remove <flag>`). Ask for: the full inventory of sites across all four repos, the deploy-safe ordering (repos ship independently), the per-repo change list, the `tenant_users` migration note, and the dangling-risk analysis. Report verbatim, then one line: is this change safe to stage as described?
