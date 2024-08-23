from sqlmodel.ext.asyncio.session import AsyncSession
from .schema import BookCreate, BookResponse
from .models import Book
from sqlmodel import select, desc
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_all_books_by_user(self, session: AsyncSession, user_id: str):
        statement = select(Book).where(Book.user_id == user_id).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def get_book(self, session: AsyncSession, book_uid: str):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def create_book(self, session: AsyncSession, book_data: BookCreate, user_id: str):
        data = book_data.model_dump()
        new_book = Book(**data)
        new_book.published_date = datetime.strptime(
            data['published_date'], "%Y-%m-%d")
        new_book.user_id = user_id
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(self, session: AsyncSession, book_uid: str, book_data: BookResponse):
        book = await self.get_book(session, book_uid)
        if book is not None:
            data = book_data.model_dump()
            for key, value in data.items():
                setattr(book, key, value)
            await session.commit()
            return book
        return None

    async def delete_book(self, session: AsyncSession, book_uid: str):
        book = await self.get_book(session, book_uid)
        if book is not None:
            await session.delete(book)
            await session.commit()
            return {}
        return None
