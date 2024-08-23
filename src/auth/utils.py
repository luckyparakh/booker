from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from src.config import settings
import uuid
import logging

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"])


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expiry: timedelta = None, refresh: bool = False):
    to_encode={}
    to_encode["user"] = data.copy()
    expires = datetime.now(
        timezone.utc) + (expiry if expiry else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expires})
    to_encode.update({"jti": str(uuid.uuid4())})
    to_encode.update({"refresh": refresh})
    
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("Signature has expired")
        return None
    except jwt.InvalidTokenError:
        logging.error("Invalid token")
        return None
    except Exception as e:
        logging.error(e)
        return None
