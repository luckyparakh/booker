from fastapi import APIRouter, Depends,  HTTPException, status
from .schema import UserCreateSchema, UserSchema, UserLogin
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .utils import create_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
user_service = UserService()
REFRESH_TOKEN_EXPIRES = 2


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


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    email_id = data.email
    user_exist = await user_service.get_user_by_email(email_id, session)
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User with these details is not present.")
    if not verify_password(data.password, user_exist.password_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User with these details is not present.")
    access_token = create_token(
        data={"email": user_exist.email, "uid": str(user_exist.uid)})
    refresh_token = create_token(
        data={"email": user_exist.email, "uid": str(user_exist.uid)}, expiry=timedelta(days=REFRESH_TOKEN_EXPIRES), refresh=True)
    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Logged in successfully",
            "user": {
                "email": user_exist.email,
                "uid": str(user_exist.uid)
            }
        }
    )
