from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Review(BaseModel):
    rating: int = Field(lt=5)
    text: str = Field(max_length=1000)


class ReviewResponse(Review):
    created_at: datetime
    user_id: uuid.UUID
    book_id: uuid.UUID
    uid: uuid.UUID
