from fastapi import APIRouter, Depends,  HTTPException, status
from .schema import UserCreateSchema, UserSchema, UserLogin
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .utils import create_token, verify_password
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blocklist
from .dependencies import get_user, RoleChecker

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])
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
        data={"email": user_exist.email, "user_id": str(user_exist.uid), "role": user_exist.role})
    refresh_token = create_token(
        data={"email": user_exist.email, "user_id": str(user_exist.uid)}, expiry=timedelta(days=REFRESH_TOKEN_EXPIRES), refresh=True)
    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Logged in successfully",
            "user": {
                "email": user_exist.email,
                "user_id": str(user_exist.uid),
                "role": user_exist.role
            }
        }
    )


@auth_router.get("/refresh_token")
def refresh_token(token_data: dict = Depends(RefreshTokenBearer())):
    expiry_epoch = token_data["exp"]
    if datetime.fromtimestamp(expiry_epoch) > datetime.now():
        new_access_token = create_token(data=token_data["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired")


@auth_router.get("/logout")
async def logout(token_data: dict = Depends(AccessTokenBearer())):
    jti = token_data["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logged out successfully"})


@auth_router.get("/me", response_model=UserSchema)
async def profile(user=Depends(get_user), _: bool = Depends(role_checker)):
    return user
