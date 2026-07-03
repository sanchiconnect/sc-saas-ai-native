# Sample PR Diff — ReviewPilot Input
# PR: feature/user-registration | Sprint: SP-007

## Changed Files
1. `src/api/routes/users.py` (new file)
2. `src/services/user_service.py` (new file)
3. `src/schemas/user.py` (new file)
4. `alembic/versions/001_create_users.py` (new file)

---

## src/api/routes/users.py (NEW)
```python
# @spec: REQ-API-003 | @task: TASK-042 | @generated: 2025-09-16 | @builder: Builder-1
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    try:
        user = await service.create_user(payload)
        return UserResponse.model_validate(user)
    except ValueError:
        raise HTTPException(status_code=500, detail="User creation failed")
        # BUG: Should be 409 CONFLICT on duplicate email, not 500
```

---

## src/services/user_service.py (NEW)
```python
# @spec: REQ-API-003 | @task: TASK-042 | @generated: 2025-09-16 | @builder: Builder-1
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, payload: UserCreate) -> User:
        existing = await self.db.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("EMAIL_ALREADY_EXISTS")
        
        print(f"Creating user with email: {payload.email}")  # BUG: PII in stdout + CR-002 violation

        user = User(
            email=payload.email,
            password_hash=pwd_context.hash(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

---

## src/schemas/user.py (NEW)
```python
# @spec: REQ-API-003 | @task: TASK-042 | @generated: 2025-09-16 | @builder: Builder-1
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    first_name: str
    # password_hash correctly excluded
    created_at: datetime
```
