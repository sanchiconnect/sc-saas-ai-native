# Stack Patterns Library — DevCopilot
## React / Python FastAPI / PostgreSQL

---

## Frontend Patterns (React + TypeScript)

### API Client Setup
```typescript
// src/lib/api-client.ts
// @pattern: API_CLIENT_SETUP | Axios with auth interceptors
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login — do not use window.location directly
      // Use router navigate from the auth context
    }
    return Promise.reject(error);
  }
);
```

### Data Fetching (React Query)
```typescript
// @pattern: DATA_FETCH | React Query with typed hooks
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export const useUser = (userId: string) =>
  useQuery({
    queryKey: ['user', userId],
    queryFn: () => apiClient.get<UserResponse>(`/api/v1/users/${userId}`).then(r => r.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreate) =>
      apiClient.post<UserResponse>('/api/v1/users', payload).then(r => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
};
```

### Form Validation (Zod + React Hook Form)
```typescript
// @pattern: FORM_VALIDATION | Zod schema + react-hook-form
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export const useLoginForm = () =>
  useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
```

---

## Backend Patterns (Python FastAPI)

### Service Layer (Business Logic)
```python
# @pattern: SERVICE_LAYER | Repository pattern with async SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, payload: UserCreate) -> User:
        # Check email uniqueness
        existing = await self.db.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("EMAIL_ALREADY_EXISTS")

        user = User(
            email=payload.email,
            password_hash=pwd_context.hash(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("User created: id=%s", str(user.id))  # Never log email
        return user
```

### Pydantic Schemas
```python
# @pattern: PYDANTIC_SCHEMAS | v2 with model_config
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
    email: str          # Never expose password_hash
    first_name: str
    created_at: datetime
```

### SQLAlchemy Model
```python
# @pattern: ORM_MODEL | SQLAlchemy 2.0 declarative with async
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from uuid import UUID
import uuid
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
```

---

## Database Patterns (PostgreSQL via Alembic)

### Migration Template
```python
# @pattern: ALEMBIC_MIGRATION | Standard migration structure
# @spec: [requirement_id] | Revision: [alembic_rev]
"""create users table

Revision ID: 001_create_users
Revises:
Create Date: 2025-09-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
```
