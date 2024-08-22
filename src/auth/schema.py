from pydantic import BaseModel, Field, EmailStr
import uuid
from datetime import datetime


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)
    username: str = Field(max_length=8)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)


class UserSchema(BaseModel):
    uid: uuid.UUID
    email: str
    username: str
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    is_verified: bool
    created_at: datetime
    updated_at: datetime
