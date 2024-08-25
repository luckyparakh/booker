from sqlmodel import SQLModel, Field, Column
from typing import List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime, date
import uuid
from typing import Optional
import sqlalchemy.dialects.postgresql as pg


class Book(SQLModel, table=True):
    __tablename__ = "books"
    title: str
    author: str
    publisher: str
    language: str
    page_count: int
    published_date: date
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.uid", default=None)
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))

    def __repr__(self):
        return f"Book <{self.title} by {self.author}> "


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
    books: List[Book] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))

    def __repr__(self):
        return f"User <{self.username}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )
    user_id: uuid.UUID = Field(foreign_key="users.uid", default=None)
    book_id: uuid.UUID = Field(foreign_key="books.uid", default=None)
    rating: int = Field(lt=5) # Not effective added at Schema level
    text: str = Field(max_length=1000)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_id} by user {self.user_id}>"
