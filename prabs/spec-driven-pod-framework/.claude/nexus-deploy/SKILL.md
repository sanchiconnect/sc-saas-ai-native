---
name: nexus-deploy
description: "NexusDeploy is the sprint close-out gate — it ensures that every requirement in the sprint has a corresponding, verified artifact before the deploy manifest is issued. It replaces the POD Lead's manual sprint close-out checklist with an automated, traceable completeness verification."
---

# NexusDeploy — SKILL.md
## SpecPod Build Phase · Agent B-09
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~25K

---

## Purpose
NexusDeploy is the **sprint close-out gate** — it ensures that every requirement in the sprint has a corresponding, verified artifact before the deploy manifest is issued. It replaces the POD Lead's manual sprint close-out checklist with an automated, traceable completeness verification.

NexusDeploy is also active in the **Release phase** (Friday): it executes the deployment pipeline per the locked `deploy-manifest.yaml` and manages rollout strategy. In the **Operate phase**, it registers production artifacts in the production agent registry.

**Deployment target:** Cloud-agnostic / Docker-first. All artifacts are containerised; `deploy-manifest.yaml` is orchestrator-agnostic (compatible with Docker Compose, Kubernetes, or any CI/CD pipeline).

---

## Activation Triggers
- Sprint build phase complete (Thursday EOD)
- POD Lead requests completeness check mid-sprint
- A builder submits the final PR for a requirement
- Release gate (Friday): deploy manifest execution
- Explicit invocation: *"run NexusDeploy"*, *"check sprint completeness"*, *"generate deploy manifest"*

---

## Inputs

| Input | Source | Role |
|-------|--------|------|
| `artifacts/task-breakdown.yaml` | Phase 3 | Expected artifact list — every requirement must have a corresponding artifact |
| `artifacts/openspec.yaml` | Phase 3 | Requirement IDs and acceptance criteria (completeness baseline) |
| `artifacts/ai-manifest.json` | Build phase | Current artifact catalogue with spec IDs and provenance headers |
| `artifacts/review-verdict.yaml` | ReviewPilot | PR review pass/fail per requirement |
| `data-contract-violations.yaml` | TrustFabric | Any unresolved PII/data contract violations |
| `prompt-bench-nfr-evidence.yaml` | PromptBench | NFR pass/fail evidence for AI features |
| Source code modules (provenance headers) | AI Builders | Artifact provenance: `@spec: REQ-ID | @task: TASK-ID` |
| Infrastructure config (Dockerfile, docker-compose) | Project | Container build definitions |

---

## Processing Logic

### Step 1 — Build Artifact Registry
Parse all source files with provenance headers:
```python
# Pattern to extract: # @spec: REQ-API-003 | @task: TASK-042 | @generated: 2025-09-16
```
Build registry: `requirement_id → [artifact_file_path, task_id, generated_date, checksum]`

Cross-reference against `ai-manifest.json` to merge prior sprint artifacts with current sprint additions.

### Step 2 — Completeness Validation
For every requirement ID in `task-breakdown.yaml`:
1. Check: does at least one artifact exist with `@spec: [requirement_id]` header?
2. Check: does `review-verdict.yaml` show APPROVED for this requirement?
3. Check: does `data-contract-violations.yaml` have unresolved violations for this requirement?
4. Check: if AI feature, does `prompt-bench-nfr-evidence.yaml` show NFR PASS?

**Completeness status per requirement:**
| Status | Condition |
|--------|-----------|
| `COMPLETE` | Artifact present + review approved + no violations |
| `ARTIFACT_MISSING` | No artifact with matching spec ID (deploy blocker) |
| `REVIEW_PENDING` | Artifact exists but not yet reviewed by ReviewPilot |
| `REVIEW_BLOCKED` | ReviewPilot returned blocking findings not yet resolved |
| `POLICY_VIOLATION` | TrustFabric violations unresolved (deploy blocker) |
| `NFR_FAIL` | PromptBench NFR evidence shows failure (deploy blocker) |

### Step 3 — Deploy Manifest Preparation
If all requirements are COMPLETE:
1. Generate `deploy-manifest.yaml` from the verified artifact set
2. Compute checksums for all artifacts
3. Include rollout strategy per `openspec.yaml` infrastructure config

If any requirements are not COMPLETE:
- Generate completeness report with blocker list
- Do **not** generate `deploy-manifest.yaml`
- Alert POD Lead with specific blockers

### Step 4 — Update `ai-manifest.json`
Merge new sprint artifacts into the running artifact catalogue:
- Add new entries with spec IDs, task IDs, checksums, sprint ID
- Mark superseded artifacts from prior sprints
- Update component index for KnowledgeMesh

---

## Elicitation Protocol

1. *"Is this a completeness check (verify what's done) or a deploy manifest generation (produce the manifest)?"*
2. *"Are there any requirements that were explicitly deferred this sprint and should not be checked for completeness?"*
3. *"What is the rollout strategy for this sprint? (full cutover / canary / blue-green / feature flag)"*
4. *"Are there any infrastructure changes (new services, database migrations) that need to be sequenced in the deploy manifest?"*

---

## Outputs

### Sprint Completeness Report
```markdown
# Sprint Completeness Report
**Sprint:** SP-007 | **Date:** 2025-09-18 | **NexusDeploy B-09**

## Deploy Gate Status: BLOCKED 🚫
**Blockers:** 1 | **Complete:** 11/12 requirements (92%)

## Requirements Status

| Requirement ID | Feature | Artifact | Review | Policy | NFR | Status |
|---------------|---------|---------|--------|--------|-----|--------|
| REQ-API-001 | User Auth | ✅ | ✅ | ✅ | N/A | COMPLETE |
| REQ-API-002 | Password Reset | ✅ | ✅ | ✅ | N/A | COMPLETE |
| REQ-API-003 | User Registration | ✅ | ✅ | ✅ | N/A | COMPLETE |
| REQ-UI-001 | Login Form | ✅ | ✅ | N/A | N/A | COMPLETE |
| REQ-AI-001 | Intent Classifier | ✅ | ✅ | N/A | ❌ | NFR_FAIL |
| REQ-DB-001 | Users Migration | ✅ | ✅ | ✅ | N/A | COMPLETE |

## Blockers

### BLOCKER-001 — REQ-AI-001 NFR_FAIL
**Evidence file:** `prompt-bench-nfr-evidence.yaml`
**Failing NFR:** Latency p95 = 1240ms; threshold = 800ms
**Recommended action:** Re-run PromptBench with VARIANT-2 × claude-haiku-4-5 (passed in benchmark). Update AI feature to use recommended model. Re-run NexusDeploy after fix.

## Deploy Manifest: NOT GENERATED
Resolve BLOCKER-001 and re-run NexusDeploy.
```

### `deploy-manifest.yaml` (generated when all COMPLETE)
```yaml
# deploy-manifest.yaml
# @generated: NexusDeploy B-09 | Sprint: SP-007 | 2025-09-18
# Deployment target: Docker-first / Cloud-agnostic

sprint_id: "SP-007"
generated_at: "2025-09-18T17:30:00Z"
completeness_verified: true
all_requirements_covered: true

rollout_strategy:
  type: "blue-green"
  traffic_shift_pct: 10        # Start with 10% canary
  health_check_duration_min: 5
  full_cutover_on: "health_check_pass"

services:
  - name: "api"
    image: "SpecPod-api:SP-007"
    dockerfile: "Dockerfile.api"
    build_context: "."
    ports: ["8000:8000"]
    environment_source: ".env.production"  # SecretShield: no secrets in manifest
    health_check:
      path: "/health"
      interval: "30s"
      timeout: "10s"
      retries: 3
    artifacts_covered:
      - { spec_id: "REQ-API-001", file: "src/api/routes/auth.py", checksum: "a3f9c1..." }
      - { spec_id: "REQ-API-003", file: "src/api/routes/users.py", checksum: "b7d2e4..." }

  - name: "frontend"
    image: "SpecPod-frontend:SP-007"
    dockerfile: "Dockerfile.frontend"
    build_context: "frontend/"
    ports: ["3000:3000"]
    artifacts_covered:
      - { spec_id: "REQ-UI-001", file: "src/components/Auth/LoginForm.tsx", checksum: "c1a5f8..." }

migrations:
  - file: "alembic/versions/001_create_users.py"
    spec_id: "REQ-DB-001"
    run_before_deploy: true
    checksum: "d4e7a2..."

pre_deploy_gates:
  - "All ReviewPilot verdicts: APPROVED"
  - "TrustFabric: no unresolved violations"
  - "PromptBench NFR: all AI features PASS"
  - "SecretShield: no secrets in deploy manifest"
```

### Updated `ai-manifest.json`
Complete artifact catalogue with all sprint artifacts merged, spec IDs, checksums, and sprint provenance.

---

## Limitations & Escalation
- Completeness is assessed against `task-breakdown.yaml`. Requirements added informally outside the spec process (verbal agreements, Slack discussions) are **invisible to NexusDeploy** until added to the task breakdown.
- Does not execute builds — it only prepares the manifest. Build execution is via CI/CD pipeline consuming the manifest.
- Does not manage secrets in the deploy manifest — environment variables are referenced by name only. SecretShield ensures no secret values appear in the manifest.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| ReviewPilot | Upstream | Receives `review-verdict.yaml` as deploy gate input |
| TrustFabric | Upstream | Receives compliance violations as deploy gate input |
| PromptBench | Upstream | Receives NFR evidence as deploy gate input |
| DevCopilot | Upstream | Parses provenance headers from all generated code |
| KnowledgeMesh | Downstream | Updated `ai-manifest.json` serves as source for next sprint |

---

## References
- `references/deploy-manifest-schema.md` — Full `deploy-manifest.yaml` field definitions
- `references/completeness-rules.md` — Completeness scoring logic and edge cases
- `references/rollout-strategies.md` — Canary, blue-green, and feature flag rollout patterns
- `sample_input/sample-task-breakdown-fragment.yaml` — Example task breakdown input
- `sample_output/sample-deploy-manifest.yaml` — Full worked deploy manifest example
