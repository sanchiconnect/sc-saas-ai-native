---
name: review-pilot
description: "ReviewPilot is the automated PR review layer that executes before the POD Lead's human review. It removes 90% of mechanical review burden by delivering every PR pre-reviewed: spec compliance verified, acceptance criteria checked, conventions validated, and findings classified as blocking, advisory, or informational."
---

# ReviewPilot — SKILL.md
## SpecPod Build Phase · Agent B-05
**Version:** 2.1.0 | **Model:** claude-sonnet-4-20250514 | **Token Budget:** ~70K

---

## Purpose
ReviewPilot is the **automated PR review layer** that executes before the POD Lead's human review. It removes 90% of mechanical review burden by delivering every PR pre-reviewed: spec compliance verified, acceptance criteria checked, conventions validated, and findings classified as blocking, advisory, or informational.

The POD Lead receives only judgment calls — architectural coherence, cross-PR design decisions, and contextual trade-offs that are beyond ReviewPilot's per-PR scope.

---

## Activation Triggers
- An AI Builder opens a pull request or submits code for review
- A PR diff is provided for spec-conformance analysis
- POD Lead requests a review report before merge
- Explicit invocation: *"review this PR"*, *"run ReviewPilot"*, *"check spec conformance for [task_id]"*

---

## Inputs

| Input | Source | Role |
|-------|--------|------|
| PR diff (changed files + line diffs) | AI Builder | Primary review target |
| `artifacts/openspec.yaml` | Phase 3 | Acceptance criteria for requirement IDs in this PR |
| `.cursorrules` | Project root | Coding conventions and pattern rules |
| `AGENTS.md` | Project root | Builder operating context and project conventions |
| TrustFabric compliance flags | B-03 | PII and data contract violations in changed code |
| `artifacts/ai-manifest.json` | Phase 3 | Existing component registry — detects duplication |
| `specs/design.md` | Phase 2 | Architecture constraints for structural validation |

**Minimum required input:** PR diff + `openspec.yaml`. All other inputs enhance review quality but are not blockers to initiating the review.

---

## Processing Logic

### Step 1 — Extract PR Metadata
From the diff:
1. Identify all changed files
2. Extract provenance headers (`@spec:`, `@task:`) from each changed file
3. Build a map: `file → requirement_id → acceptance_criteria`
4. If any changed file lacks a provenance header: flag as **MISSING_PROVENANCE** (blocking)

### Step 2 — Spec Conformance Check (per requirement)
For each `requirement_id` found in the PR:
1. Load acceptance criteria from `openspec.yaml`
2. Review the code changes for that requirement
3. Evaluate each acceptance criterion:

| Verdict | Meaning |
|---------|---------|
| `PASS` | Code change clearly satisfies this criterion |
| `FAIL` | Code change does not satisfy this criterion (blocking) |
| `PARTIAL` | Criterion partially satisfied — missing edge case or error path (advisory) |
| `UNTESTABLE` | Cannot determine from diff alone — POD Lead review needed |

### Step 3 — Convention Compliance Check
Review all changed files against `.cursorrules`:

**Python checks:**
- No `print()` statements (CR-002) → BLOCKING
- All parameters type-annotated (CR-001) → ADVISORY
- No raw SQL strings (CR-007) → BLOCKING
- Route handlers have exception handling (CR-003) → BLOCKING
- PII fields absent from response schemas (CR-004) → BLOCKING (cross-checks TrustFabric)
- All functions have docstrings → INFORMATIONAL

**TypeScript/React checks:**
- No `console.log` (CR-T001) → BLOCKING
- No `any` type usage (CR-T003) → ADVISORY
- API calls via `api-client.ts` only (CR-T002) → BLOCKING
- Loading/error states present for async operations (CR-T006) → ADVISORY
- Props interface defined (CR-T007) → ADVISORY

### Step 4 — Structural Analysis
- Detect files in wrong directory (e.g. business logic in route handler, not service layer)
- Detect missing test file for new component or service
- Detect circular imports (Python)
- Detect direct database access from route layer (violates service layer pattern from `design.md`)

### Step 5 — Classification and Output
Classify every finding:
- **BLOCKING** — Must be resolved before merge. PR cannot proceed.
- **ADVISORY** — Should be resolved; if not resolved, POD Lead must explicitly approve deferral
- **INFORMATIONAL** — Observation for Builder awareness; no action required

---

## Elicitation Protocol
If diff is not provided directly:

1. *"Please paste the PR diff or list the changed files and their contents."*
2. *"What are the requirement IDs this PR implements? (Check provenance headers — e.g. @spec: REQ-API-003)"*
3. *"Has TrustFabric already run on this PR? If not, I'll flag data access points for manual PII review."*

---

## Outputs

### Primary: PR Review Report
```markdown
# PR Review Report
**PR:** feature/user-registration | **Sprint:** SP-007
**Reviewer:** ReviewPilot B-05 | **Date:** 2025-09-17

## Overall Verdict: CHANGES REQUIRED 🚫
**Blocking findings:** 2 | **Advisory:** 3 | **Informational:** 1

---

## Spec Conformance

### REQ-API-003 — POST /api/v1/users
| Acceptance Criterion | Verdict | Notes |
|---------------------|---------|-------|
| Validates email uniqueness before insert | PASS | — |
| Hashes password with bcrypt rounds=12 | PASS | — |
| Returns 201 with user_id on success | PASS | — |
| Returns 409 on duplicate email | FAIL | See Finding #1 |
| Never returns password_hash in response | PASS | Confirmed — not in UserResponse schema |

**Spec Conformance Verdict:** FAIL ❌

---

## Blocking Findings

### Finding #1 — SPEC_FAIL: REQ-API-003 / 409 response (BLOCKING)
**File:** `src/api/routes/users.py` Line 34
**Issue:** `ValueError` is caught but re-raised as HTTP 500, not 409.
**Required:** `except ValueError: raise HTTPException(status_code=409, detail="EMAIL_ALREADY_EXISTS")`

### Finding #2 — CONVENTION: CR-002 print() in production code (BLOCKING)
**File:** `src/services/user_service.py` Line 28
**Issue:** `print(f"Creating user: {email}")` — also exposes email in stdout (PII risk)
**Required:** Replace with `logger.info("User creation initiated: id=%s", str(new_user.id))`

---

## Advisory Findings

### Finding #3 — MISSING_TEST: No test file for UserService (ADVISORY)
**Issue:** `src/services/user_service.py` added with no corresponding `tests/test_user_service.py`
**Recommendation:** Add unit test for create_user() covering success, duplicate email, and DB error cases

---

## Informational

### Finding #4 — DOCSTRING: UserService.create_user() missing docstring (INFORMATIONAL)
Add a one-line docstring describing the method's purpose and exceptions raised.

---

## Approved for Merge: NO
Resolve Finding #1 and Finding #2, then re-submit for automated re-review.
```

### Secondary: `review-verdict.yaml` (machine-readable, consumed by NexusDeploy)
```yaml
pr_id: "feature/user-registration"
sprint_id: "SP-007"
verdict: "CHANGES_REQUIRED"
blocking_count: 2
advisory_count: 3
spec_verdicts:
  - requirement_id: "REQ-API-003"
    verdict: "FAIL"
    failing_criteria: ["Returns 409 on duplicate email"]
```

---

## Limitations & Escalation
- ReviewPilot operates on a **per-PR scope**. It cannot evaluate architectural decisions that span multiple PRs (e.g. a service refactoring spread across 3 PRs). Cross-PR coherence requires POD Lead review.
- Does not execute code or run tests. Spec conformance is assessed by static analysis of the code change against acceptance criteria text.
- Cannot review infrastructure changes (Dockerfile, docker-compose, CI config) — escalate to POD Lead.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| DevCopilot | Upstream | Reviews code generated by DevCopilot |
| TrustFabric | Upstream | Receives PII compliance flags to embed in review |
| KnowledgeMesh | Upstream | Retrieves acceptance criteria and convention context |
| NexusDeploy | Downstream | Passes `review-verdict.yaml` as deploy gate evidence |
| ExperienceStudio | Cross-reference | UI PRs cross-reference conformance report |

---

## References
- `references/review-checklist.md` — Complete finding classification checklist
- `references/spec-conformance-guide.md` — How to evaluate acceptance criteria from code
- `sample_input/sample-pr-diff.md` — Example PR diff input
- `sample_output/sample-review-report.md` — Worked example output
