from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
import uuid
from src.books import models
from typing import List


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )
    email: str
    username: str
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    role: str = Field(sa_column=Column(pg.VARCHAR(
        10), nullable=False, server_default="user"))
    books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))

    def __repr__(self):
        return f"User <{self.username}>"
