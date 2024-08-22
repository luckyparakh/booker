from fastapi.security import HTTPBearer
from fastapi import Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import verify_token
from fastapi.exceptions import HTTPException
from src.db.main import get_session
from .service import UserService
import logging
from sqlmodel.ext.asyncio.session import AsyncSession

user_service = UserService()


class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        # Token looks like this
        # {'email': 'rp@gmail.com', 'uid': '52f45fd6-8735-411b-81f1-7ea9c1520353', 'exp': 1724302963, 'jti': '4f461ff6-355b-421f-9c74-0646df1c73ab', 'refresh': False}
        token = verify_token(creds.credentials)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        if token.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        email_id = token.get("email")
        user_exist = user_service.get_user_by_email(email_id, get_session())
        if user_exist is None:
            logging.error(f"User with Email ID:{email_id} is not present.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid token")
        return token
