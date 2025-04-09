from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .user import UserOut


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    author: UserOut

    model_config = ConfigDict(from_attributes=True)
