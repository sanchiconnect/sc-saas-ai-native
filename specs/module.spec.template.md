---
module: <module name>
repo: <tenants | backend | frontend | admin>
type: module
status: draft                   # draft → approved → in-progress → in-review → done
owns:
  api: []                       # routes this module is the source of truth for
  events: []                    # events it emits
  flags: []                     # flags it defines (tenants only) or authoritatively gates
consumes:
  api: []                       # routes it calls (other modules/repos)
  flags: []                     # flags it reads
  events: []                    # events it handles
tenant_scoping: <one-line mechanism, e.g. "domain filter on every query" | "per-tenant DB via $database" | "n/a — bootstrap-config, single-tenant deploy">
updated: 2026-06-17
---

# <module> (<repo>)

## Purpose
<One paragraph: what bounded context this module owns and why it exists.>

## Public surface
<What other code depends on: exported endpoints, services, events, DTOs/types. The stable contract.>

## Internal model
<Entities/tables, key services, important state. The parts that change behind the surface.>

## Invariants
<Rules that must always hold for this module (data integrity, ordering, scoping). Tie to the workspace invariants where relevant.>

## Conventions
<Module-specific patterns: error handling, validation, naming, comment style — anything an implementer must match.>

## Watch out for
<Footguns, gotchas, non-obvious coupling, brittle integrations.>
