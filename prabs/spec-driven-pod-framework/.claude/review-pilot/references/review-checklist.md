# Review Checklist — ReviewPilot

## Pre-Review Checklist
Before starting any PR review, confirm:
- [ ] PR diff received (changed files + line diffs)
- [ ] Provenance headers present in changed files (extract `@spec:` IDs)
- [ ] `openspec.yaml` loaded for the requirement IDs in this PR
- [ ] `.cursorrules` and `AGENTS.md` loaded
- [ ] TrustFabric flags available (or flag that PII review will be manual)

---

## Finding Classification Criteria

### BLOCKING (must fix before merge)
| Category | Examples |
|----------|---------|
| SPEC_FAIL | Acceptance criterion not implemented; returns wrong HTTP status; wrong field in response |
| SECURITY | `print(email)`, PII in log, raw SQL without parameterisation, no auth guard on protected route |
| MISSING_PROVENANCE | No `@spec:` header in changed file |
| CONVENTION_CRITICAL | No exception handling in route; `any` type in security-critical code; SQL injection vector |
| TRUST_VIOLATION | PII field in API response without masking; unclassified field accessed |

### ADVISORY (should fix; POD Lead must explicitly defer if not fixed)
| Category | Examples |
|----------|---------|
| MISSING_TEST | New service/component added without test file |
| CONVENTION_STANDARD | Missing type annotation; `console.log` in non-critical path; no docstring |
| STRUCTURAL | Business logic in route handler (should be in service layer); direct DB access from route |
| PARTIAL_SPEC | Acceptance criterion partially satisfied (happy path only, no error path) |

### INFORMATIONAL (awareness only; no action required)
| Category | Examples |
|----------|---------|
| SUGGESTION | Alternative implementation that would be more idiomatic or performant |
| DOCUMENTATION | Missing or incomplete inline comments for complex logic |
| FUTURE_DEBT | Technical debt item to track for future sprint |

---

## Spec Conformance Evaluation Guide

For each acceptance criterion in `openspec.yaml`, apply this evaluation:

**For functional criteria** (e.g. "Returns 409 on duplicate email"):
- Find the code path that handles this case
- Trace: request → handler → service → response
- Verify the correct status code/payload is returned
- Check: is the error case actually reachable, or is it dead code?

**For NFR criteria** (e.g. "p95 < 300ms"):
- Static review cannot verify runtime latency
- Mark as UNTESTABLE — flag for load test during QA phase
- Check that no obviously slow operations are in the hot path (synchronous DB call in a loop, missing async/await)

**For security criteria** (e.g. "Never returns password_hash in response"):
- Locate the response Pydantic schema / TypeScript interface
- Verify the field is absent
- Check that no serialisation shortcut (`.dict()`, `model_dump(include='__all__')`) could accidentally include it

---

## Common False Positive Traps

1. **Type: any in test files** — Test utilities sometimes use `any` legitimately. Only flag ADVISORY if in production code.
2. **console.log in dev-only code** — Check if file is in a `__tests__` directory or has `.test.ts` extension before flagging.
3. **Missing docstring on simple getters** — Only flag INFORMATIONAL, not ADVISORY, for trivial one-liner functions.
4. **Raw SQL in migration files** — Alembic migrations use `op.execute()` with raw SQL by design. Not a CR-007 violation.
