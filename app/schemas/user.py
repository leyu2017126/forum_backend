# app/schemas/user.py
from __future__ import annotations
from pydantic import BaseModel, EmailStr, ConfigDict, constr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # 使用字符串字面量来定义前向引用，这里引用 PostOut（循环引用）
    posts: Optional[List["PostOut"]] = None

    # Pydantic V2 的配置
    model_config = ConfigDict(from_attributes=True)


# Token 相关类
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    model_config = ConfigDict(protected_namespaces=())
