from .schema import Review, ReviewResponse
from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import ReviewService
from src.auth.dependencies import AccessTokenBearer, RoleChecker


review_router = APIRouter(prefix="/reviews", tags=["reviews"])
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(['admin', 'user']))


@review_router.post("/{book_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED,  dependencies=[role_checker])
async def add_book(book_id: str, review: Review, session: AsyncSession = Depends(get_session),
                   token_details: dict = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get("user")["email"]
    new_book = await review_service.create_review(session, review, user_id, book_id)
    return new_book


@review_router.get("/", response_model=List[ReviewResponse], status_code=status.HTTP_200_OK)
async def get_all_reviews(session: AsyncSession = Depends(get_session)) -> List[ReviewResponse]:
    return await review_service.get_all_reviews(session)


@review_router.get("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def get_review(review_id: str, session: AsyncSession = Depends(get_session)) -> ReviewResponse:
    return await review_service.get_review(session, review_id)


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_review(review_id: str, session: AsyncSession = Depends(get_session),
                        token_details: dict = Depends(access_token_bearer)):
    user_email = token_details.get("user")["email"]
    return await review_service.delete_review(session, review_id, user_email)
