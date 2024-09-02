from fastapi import APIRouter, Depends,  HTTPException, status, BackgroundTasks
from .schema import UserCreateSchema, ResetPasswordModel, UserLogin, UserBooks, EmailModel, SetPasswordModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .utils import create_token, verify_password, create_url_safe_token, decode_url_safe_token
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blocklist
from .dependencies import get_user, RoleChecker
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, PasswordMismatch
from src.email import mail, create_message
from src.config import settings
from .utils import get_password_hash
from src.celery_task import send_email

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])
REFRESH_TOKEN_EXPIRES = 2


@auth_router.post("/send_email")
async def send_mail(recipients: EmailModel):
    body = "<h1>This is a test email</h1>"
    send_email.delay(recipients.emails, "Test", body)
    return {"message": "Email sent"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateSchema, bg_task: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    # data_dict = data.model_dump()
    # email_id = data_dict["email"]
    email_id = data.email
    user_exist = await user_service.get_user_by_email(email_id, session)
    if user_exist:
        raise UserAlreadyExists()
    new_user = await user_service.create_user(data, session)

    title = "Verify your Email"
    html = create_email_message(email_id, title, "verify")
    # message = create_message([email_id], "Verify Your Email", html)
    # bg_task.add_task(mail.send_message, message)
    send_email.delay([email_id], "Verify Your Email", html)
    return {
        "message": "Verification email sent. Please verify your email",
        "user": new_user
    }


@auth_router.get("/verify/{token}", status_code=status.HTTP_201_CREATED)
async def verify(token: str, session: AsyncSession = Depends(get_session)):
    user = await decode_token(token, session)
    await user_service.update_user(user, {"is_verified": True}, session)
    return {"message": "Email verified successfully"}


async def decode_token(token: str, session: AsyncSession):
    data = decode_url_safe_token(token)
    if not data:
        raise InvalidCredentials()
    user = await user_service.get_user_by_email(data['email'], session)
    if not user:
        raise UserNotFound()
    return user


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    email_id = data.email
    user_exist = await user_service.get_user_by_email(email_id, session)
    if not user_exist:
        raise UserNotFound()
    if not verify_password(data.password, user_exist.password_hash):
        raise UserNotFound()
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


@auth_router.get("/me", response_model=UserBooks)
async def profile(user=Depends(get_user), _: bool = Depends(role_checker)):
    return user


@auth_router.post("/reset_password")
async def reset_password(data: ResetPasswordModel, session: AsyncSession = Depends(get_session)):
    email_id = data.email
    user_exist = await user_service.get_user_by_email(email_id, session)
    if not user_exist:
        raise UserNotFound()
    title = "Reset Your Password"
    html = create_email_message(email_id, title, "set_password")

    # message = create_message([email_id], title, html)
    # await mail.send_message(message)
    
    send_email.delay([email_id],title, html)
    return {"message": "Password Reset Link emailed."}


@auth_router.post("/set_password/{token}")
async def set_password(token: str, data: SetPasswordModel, session: AsyncSession = Depends(get_session)):
    if data.password != data.password_again:
        raise PasswordMismatch()
    user = await decode_token(token, session)
    hashed_password = get_password_hash(data.password)
    await user_service.update_user(user, {"password_hash": hashed_password}, session)
    return {"message": "Password reset done."}


def create_email_message(email: str, title: str, path: str):
    token = create_url_safe_token({"email": email})
    link = f"http://{settings.DOMAIN}/api/v1/auth/{path}/{token}"
    html = f"""
    <h1>{title}</h1>
    <p>Please click this <a href="{link}">link</a> to {title.lower()}</p>
    """
    return html
