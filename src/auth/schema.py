from pydantic import BaseModel, Field, EmailStr
import uuid
from datetime import datetime
from typing import List
from src.books.schema import BookResponse
from src.db.models import Review


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


class UserBooks(UserSchema):
    books: List[BookResponse]
    review: List[Review]


class EmailModel(BaseModel):
    emails: List[str]
    # subject: str
    # body: str


class ResetPasswordModel(BaseModel):
    email: EmailStr = Field(max_length=40)


class SetPasswordModel(BaseModel):
    password: str = Field(min_length=6)
    password_again: str = Field(min_length=6)
