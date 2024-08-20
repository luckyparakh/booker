from sqlmodel import SQLModel, Field, Column
from datetime import datetime, date
import uuid
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
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.now))

    def __repr__(self):
        return f"Book <{self.title} by {self.author}> "
