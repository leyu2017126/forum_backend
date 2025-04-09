# app/schemas/post.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut  # 直接引用 UserOut


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostOut(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    view_count: int
    author: UserOut

    model_config = ConfigDict(from_attributes=True)
