from fastapi import APIRouter, Depends,  HTTPException, status
from .schema import UserCreateSchema, UserSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .models import User

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
user_service = UserService()


@auth_router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    # data_dict = data.model_dump()
    # email_id = data_dict["email"]
    email_id = data.email
    user_exist = await user_service.get_user_by_email(email_id, session)
    if user_exist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with Email ID:{email_id} is present.")
    new_user = await user_service.create_user(data, session)
    return new_user
