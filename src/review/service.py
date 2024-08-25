from sqlmodel.ext.asyncio.session import AsyncSession
from .schema import Review
from src.db.models import Review as ReviewModel
from sqlmodel import select, desc
from src.books.service import BookService
from src.auth.service import UserService
from fastapi import status
from fastapi.exceptions import HTTPException

bs = BookService()
us = UserService()


class ReviewService:
    async def create_review(self, session: AsyncSession, review_data: Review, email: str, book_id: str):
        try:
            book_exist = await bs.get_book(session, book_id)
            if book_exist is None:
                raise HTTPException(
                    detail=f"Book with ID:{book_id} not found", status_code=status.HTTP_404_NOT_FOUND
                )
            user_exist = await us.get_user_by_email(email, session)
            if user_exist is None:
                raise HTTPException(
                    detail=f"User with email:{email} not found", status_code=status.HTTP_404_NOT_FOUND
                )
            data = review_data.model_dump()
            new_review = ReviewModel(**data)
            new_review.user = user_exist
            new_review.book = book_exist
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            raise HTTPException(
                detail=f"Error creating review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_all_reviews(self, session: AsyncSession):
        try:
            stmt = select(ReviewModel).order_by(desc(ReviewModel.created_at))
            reviews = await session.exec(stmt)
            return reviews
        except Exception as e:
            raise HTTPException(
                detail=f"Error fetching reviews: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_review(self, session: AsyncSession, review_id: str):
        try:
            review = await session.get(ReviewModel, review_id)
            if review is None:
                raise HTTPException(
                    detail=f"Review with ID:{review_id} not found", status_code=status.HTTP_404_NOT_FOUND
                )
            return review
        except Exception as e:
            raise HTTPException(
                detail=f"Error fetching review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def delete_review(self, session: AsyncSession, review_id: str, user_email: str):
        try:
            print("*************************ID",review_id)
            review = await self.get_review(session, review_id)
            print("*************************Review",review)
            # print("*************************",review.user.email)
            user_exist = await us.get_user_by_email(user_email, session)
            print("*************************", user_exist.email)
            if review.user_id != user_exist.uid:
                raise HTTPException(
                    detail=f"User with email:{user_email} is not authorized to delete this review",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            await session.delete(review)
            await session.commit()
            return {}
        except Exception as e:
            raise HTTPException(
                detail=f"Error deleting review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
