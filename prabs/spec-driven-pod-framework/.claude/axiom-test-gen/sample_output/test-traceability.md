# Test Traceability — EP-03 / TASK-03.2

| AC ID | AC summary | Cases | Levels | Status |
|-------|-----------|-------|--------|--------|
| AC-03.2.1 | Requests at/under limit allowed; remaining reported | TC-03.2-001, 002, 009 | unit | ✅ covered |
| AC-03.2.2 | limit+1 throttled with retry_after; remaining=0 | TC-03.2-003, 004 | unit | ✅ covered |
| AC-03.2.3 | Invalid construction raises | TC-03.2-005, 006 | unit | ✅ covered |
| AC-03.2.4 | Window rollover resets counter | TC-03.2-008 | acceptance | ✅ covered |
| AC-03.2.5 | Backward clock-skew safety | — | — | ❌ uncovered (spec oracle undefined — see gap report) |
| AC-03.2.6 | Distinct client keys independent | TC-03.2-007 | unit | ✅ covered |

5 of 6 ACs covered. AC-03.2.5 is blocked on a spec decision, not a missing test.
