from datetime import datetime
from pydantic import BaseModel, EmailStr


# ── Tags ──────────────────────────────────────────────────────────────────────

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    model_config = {"from_attributes": True}


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
    title: str
    description: str | None = None

class TaskCreate(TaskBase):
    tag_names: list[str] = []

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    tag_names: list[str] | None = None

class TaskPublic(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    tags: list[Tag] = []

    model_config = {"from_attributes": True}


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
