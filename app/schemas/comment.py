from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .user import UserOut


class CommentBase(BaseModel):
    content: str


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None  # 添加 parent_id 属性，允许为空

    class Config:
        orm_mode = True  # 如果你使用 ORM 映射（如 SQLAlchemy）


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    author: UserOut

    model_config = ConfigDict(from_attributes=True)
