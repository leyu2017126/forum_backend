# app/schemas/post.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user import UserBase  # 引用 UserBase 代替 UserOut


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
    author: UserBase  # 使用 UserBase，避免循环引用

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_forward_refs()
