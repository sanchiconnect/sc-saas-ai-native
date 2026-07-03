# Coding Conventions — DevCopilot
## .cursorrules Expansion and Rationale

---

## Python (FastAPI Backend)

### Naming
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private methods: `_leading_underscore`
- File names: `snake_case.py`

### Code Quality Rules
| Rule ID | Rule | Rationale |
|---------|------|-----------|
| CR-001 | All function parameters and return types must be type-annotated | Pydantic/SQLAlchemy rely on type hints for schema generation |
| CR-002 | No `print()` in any application code — use `import logging; logger = logging.getLogger(__name__)` | print() is not structured, not log-level aware, and leaks to stdout in production |
| CR-003 | All route handlers must have a try/except wrapping domain exceptions | Unhandled exceptions return 500 with stack traces in production |
| CR-004 | Never expose `password_hash` or any `PII:IDENTITY` field in Pydantic response schemas | TrustFabric enforcement |
| CR-005 | SQLAlchemy: always use `async with session` pattern; never use synchronous session | Async is required for FastAPI concurrency |
| CR-006 | Alembic: every migration must have a working `downgrade()` function | Rollback capability is mandatory |
| CR-007 | No raw SQL strings — use SQLAlchemy Core or ORM expressions | SQL injection prevention |
| CR-008 | All background tasks must be idempotent | Tasks may be retried |

### Import Order
```python
# Standard library
import os
import logging
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Internal (absolute imports only)
from app.db.session import get_db
from app.models.user import User
```

---

## TypeScript (React Frontend)

### Naming
- Components: `PascalCase` (file and export name must match)
- Hooks: `use` prefix, `camelCase` (e.g. `useUserProfile`)
- Types/Interfaces: `PascalCase` with descriptive suffix (`UserResponse`, `LoginFormValues`)
- Event handlers: `handle` prefix (e.g. `handleSubmit`, `handleInputChange`)
- Constants: `SCREAMING_SNAKE_CASE`

### Code Quality Rules
| Rule ID | Rule | Rationale |
|---------|------|-----------|
| CR-T001 | No `console.log` in committed code | Use dev tools; log statements reach production |
| CR-T002 | All API calls must go through `src/lib/api-client.ts` | Centralised auth, error handling, timeout config |
| CR-T003 | No `any` type — use `unknown` + type guard if type is truly unknown | Type safety throughout |
| CR-T004 | All forms must use react-hook-form + Zod schema | Consistent validation, no ad-hoc validation logic |
| CR-T005 | No `useEffect` for data fetching — use React Query | Avoids race conditions, loading state bugs |
| CR-T006 | Loading and error states must be handled for every async operation | UX requirement per ui-ux.md |
| CR-T007 | All components must have explicit TypeScript interface for props | No implicit `any` from missing prop types |

### File Structure (Frontend)
```
src/
├── components/           # Reusable UI components (no business logic)
│   └── [Feature]/
│       ├── ComponentName.tsx
│       └── ComponentName.test.tsx
├── pages/                # Route-level page components
├── hooks/                # Custom React hooks
├── lib/                  # Utilities, API client, helpers
├── stores/               # Zustand stores (client state)
├── schemas/              # Zod validation schemas
└── types/                # Shared TypeScript types
```

---

## Provenance Header Spec

### Python
```python
# @spec: REQ-API-003 | @task: TASK-042 | @generated: 2025-09-16 | @builder: Builder-1
```

### TypeScript/React
```typescript
// @spec: REQ-UI-001 | @task: TASK-015 | @generated: 2025-09-16 | @builder: Builder-2
```

### Alembic Migration
```python
# @spec: REQ-DB-001 | @task: TASK-005 | Revision: 001_create_users
```

All provenance headers must appear on **line 1** of the file (after any shebang). They are parsed by NexusDeploy to build `ai-manifest.json`.
