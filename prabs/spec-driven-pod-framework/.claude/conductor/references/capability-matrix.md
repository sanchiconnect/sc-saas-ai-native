# Capability Matrix — AI Builder Skill-to-Task Mapping
**SpecPod Framework v2.1.0 · Conductor Reference**

This matrix defines which skill a Builder should invoke for each task type. Conductor uses this to assign skills during dispatch.

## Task Type → Skill Mapping

| Task Type | Primary Skill | Secondary Skill | Notes |
|-----------|--------------|-----------------|-------|
| Spec decomposition | spec-flow | — | Always Opus 4 |
| Code generation (module) | spec-flow (cluster prompt) | — | Cluster prompt from task-breakdown.yaml |
| API endpoint generation | spec-api | spec-flow | API spec as context |
| Database schema/migration | spec-database | spec-flow | Database spec as context |
| UI component generation | spec-uiux | spec-flow | UI/UX spec + design tokens |
| Test scenario generation | spec-generation | — | Feature file format |
| Compliance check | policy-catalog | — | Guard prompt injection |
| Traceability verification | trace-graph | — | Run before every gate |
| Impact analysis | spec-impact-analyzer | — | On any spec change |
| Decision logging | decision-ledger | — | On every HITL event |
| ROI modelling | value-modeler | — | Monday only |
| Backlog ranking | portfolio-prioritizer | — | Monday only |
| Evidence synthesis | research-copilot | — | Monday only |
| Context refresh | context-fabric | — | Monday (Step 1) |
| Assumption scoring | assumption-tracker | — | Monday (Step 2) |
| Scenario modelling | scenario-planner | — | Monday (Step 5) |
| Opportunity rescoring | transform-iq | — | Monday (Step 1) |

## Builder Assignment Heuristics

### Builder-1 (Primary)
Preferred for: complex decomposition, code generation, integration work
Skill affinity: spec-flow, spec-api, spec-database

### Builder-2 (Secondary)
Preferred for: UI components, test generation, compliance injection, traceability
Skill affinity: spec-uiux, trace-graph, policy-catalog

## Load Balancing Rules
1. Never assign two HIGH complexity clusters to the same builder in the same wave
2. Traceability runs (trace-graph) always run before the next wave begins
3. Decision logging (decision-ledger) runs as a side-channel — does not consume builder capacity
4. Compliance checks (policy-catalog) are injected into cluster prompts — not separate tasks
