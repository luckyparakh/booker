from pydantic import BaseModel
from datetime import datetime, date
import uuid


class Book(BaseModel):
    title: str
    author: str
    publisher: str
    language: str
    page_count: int
    published_date: date
    uid: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookResponse(BaseModel):
    title: str
    author: str
    publisher: str
    language: str
    published_date: date
