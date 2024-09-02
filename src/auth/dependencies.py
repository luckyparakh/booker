from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import verify_token
from fastapi.exceptions import HTTPException
from src.db.main import get_session
from .service import UserService
import logging
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Any
from src.db.models import User
from src.errors import (InvalidToken, RevokedToken,
                        AccessTokenRequired, RefreshTokenRequired, InsufficientPermission, AccountNotVerified)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        # Token looks like this
        # {'email': 'rp@gmail.com', 'uid': '52f45fd6-8735-411b-81f1-7ea9c1520353', 'exp': 1724302963, 'jti': '4f461ff6-355b-421f-9c74-0646df1c73ab', 'refresh': False}
        token = verify_token(creds.credentials)
        if token is None:
            raise InvalidToken()
        if await token_in_blocklist(token.get("jti")):
            raise RevokedToken()

        self.verify_token_data(token)
        # print("******************************Token", token)
        return token

    def verify_token_data(self, token_data):
        raise NotImplementedError(
            "Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("refresh"):
            raise AccessTokenRequired()
        return None


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data.get("refresh"):
            raise RefreshTokenRequired()
        return None


async def get_user(token: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    email_id = token["user"]["email"]
    user_exist = await user_service.get_user_by_email(email_id, session)
    return user_exist


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()
