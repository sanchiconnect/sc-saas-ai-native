# Journey Mapping Guide — ExperienceStudio

## Purpose
This guide defines how to extract structured user journeys from `specs/ui-ux.md` and map them to `artifacts/openspec.yaml` requirement IDs. This mapping is the foundation of the conformance matrix.

---

## Step 1 — Identify Journey Blocks in `ui-ux.md`
Look for any of these patterns:
- Explicit journey blocks: `## Journey: [name]` or `### User Flow: [name]`
- User story format: `As a [role], I want to [action] so that [outcome]`
- Task descriptions: "The user must be able to..." or "Users should..."
- Flow narratives: Sequential steps described in prose or numbered lists

If `ui-ux.md` uses unstructured prose, extract journeys using this heuristic:
> A journey begins when a user has a distinct goal and ends when that goal is either achieved, abandoned, or an error state is reached.

---

## Step 2 — Assign Journey IDs
Format: `J-[feature_prefix]-[sequence]`
Examples: `J-AUTH-001`, `J-DASH-002`, `J-SEARCH-001`

---

## Step 3 — Map to `openspec.yaml` Requirements
For each journey, find the corresponding requirement in `openspec.yaml` using:
- Matching feature area (authentication, dashboard, etc.)
- User role alignment
- Action verb match (create, view, filter, export, etc.)

Record: `journey_id → [req_id_1, req_id_2, ...]` (one journey can cover multiple requirements)

---

## Step 4 — Identify UI Components
For each journey, identify the React components that implement it:
- Look for component filenames in the PR diff or builder's active context
- Map: `journey_id → [ComponentA.tsx, ComponentB.tsx]`

---

## Step 5 — Build Coverage Matrix
```
| Journey ID   | Journey Name        | Req IDs           | Components               | Status  |
|--------------|---------------------|-------------------|--------------------------|---------|
| J-AUTH-001   | User Login          | REQ-UI-001        | LoginForm.tsx            | TBD     |
| J-DASH-001   | View KPI Dashboard  | REQ-UI-010, -011  | Dashboard.tsx, KPICard   | TBD     |
```

---

## Handling Gaps
- **Journey in spec, no requirement ID found:** Flag as orphaned journey — escalate to POD Lead. Do not attempt to assign a requirement ID yourself.
- **Requirement in openspec, no journey found:** This is a spec gap. Log it in the conformance report under "Spec Gaps" and flag to POD Lead.
- **Component exists with no journey mapping:** Mark as EXTENDED and flag for POD Lead decision.
