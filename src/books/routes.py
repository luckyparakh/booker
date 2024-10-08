
from .schema import Book, BookResponse, BookCreate
from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound


book_router = APIRouter(prefix="/books", tags=["books"])
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(['admin', 'user']))


@book_router.get("/", response_model=List[BookResponse], dependencies=[role_checker])
async def get_books(session: AsyncSession = Depends(get_session),
                    token_details: dict = Depends(access_token_bearer)):
    books = await book_service.get_all_books(session)
    return books


@book_router.get("/user/{user_id}", response_model=List[BookResponse], dependencies=[role_checker])
async def get_books_by_user(user_id: str, session: AsyncSession = Depends(get_session),
                            token_details: dict = Depends(access_token_bearer)):
    # print("**************************User ID", user_id)
    books = await book_service.get_all_books_by_user(session, user_id)
    return books


@book_router.get("/user", response_model=List[BookResponse], dependencies=[role_checker])
async def get_books_by_current_user(session: AsyncSession = Depends(get_session),
                                    token_details: dict = Depends(access_token_bearer)):
    user_id = token_details.get("user")["user_id"]
    books = await book_service.get_all_books_by_user(session, user_id)
    return books


@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED,  dependencies=[role_checker])
async def add_book(book: BookCreate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get("user")["user_id"]
    new_book = await book_service.create_book(session, book, user_id)
    return new_book


@book_router.get("/{book_uid}", response_model=BookResponse,  dependencies=[role_checker])
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    book = await book_service.get_book(session, book_uid)
    if book:
        return book
    raise BookNotFound()


@book_router.patch("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK,  dependencies=[role_checker])
async def update_book(book_uid: str, book: BookResponse, session: AsyncSession = Depends(get_session),
                      token_details: dict = Depends(access_token_bearer)) -> dict:
    updated_book = await book_service.update_book(session, book_uid, book)
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book with ID:{book_uid} not found")
    return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT,  dependencies=[role_checker])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    book = await book_service.delete_book(session, book_uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book with ID:{book_uid} not found")
    return book

# Old code using a list of dictionaries
# @book_router.get("/", response_model=List[BookResponse])
# async def get_books(session: AsyncSession = Depends(get_session)):
#     return books


# @book_router.get("/{book_uid}", response_model=BookResponse)
# async def get_book(book_uid: int) -> dict:
#     book = next((book for book in books if book["id"] == book_uid), None)
#     # for book in books:
#     #     if book["id"] == book_uid:
#     #         return book
#     if book:
#         return book
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                         detail=f"Book with ID:{book_uid} not found")


# @book_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
# async def add_book(book: Book) -> dict:
#     books.append(book.model_dump())
#     return book


# @book_router.patch("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK)
# async def update_book(book_uid: int, book: BookResponse) -> dict:
#     book_index = next((index for index, book in enumerate(
#         books) if book["id"] == book_uid), None)
#     if book_index is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Book with ID:{book_uid} not found")
#     books[book_index]["title"] = book.title
#     books[book_index]["author"] = book.author
#     books[book_index]["publisher"] = book.publisher
#     books[book_index]["language"] = book.language
#     return books[book_index]


# @book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_book(book_uid: int):
#     book_index = next((index for index, book in enumerate(
#         books) if book["id"] == book_uid), None)
#     if book_index is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Book with ID:{book_uid} not found")
#     del books[book_index]
#     return None
