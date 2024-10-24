import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends
from fastapi import Request, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.conf import settings
from dao import user as dao
from dependencies.database import get_db
import exceptions

from schemas import user as schemas

access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)


def now_utc():
    return datetime.now(timezone.utc)


# ref : https://github.com/tiangolo/fastapi/issues/2031
class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/auth/login")


def to_bits(*args):
    return tuple(s.encode("utf-8") for s in args)


def to_str(*args):
    return tuple(b.decode("utf-8") for b in args)


def hash_pwd(pwd: str) -> str:
    salt = bcrypt.gensalt()
    return to_str(bcrypt.hashpw(*to_bits(pwd), salt))[0]


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(*to_bits(plain_pwd, hashed_pwd))


def encode_token(data):
    return jwt.encode(data, settings.secret_key, settings.algorithm)


def decode_token(data):
    return jwt.decode(data, settings.secret_key, [settings.algorithm])


def create_access_token(data: dict, user: schemas.TokenData):
    to_encode = data.copy()
    access_token_exp = now_utc() + access_token_expire
    to_encode.update(
        {**user.model_dump(), "token_type": "access", "exp": access_token_exp}
    )
    return encode_token(to_encode)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"token_type": "refresh"})
    return encode_token(to_encode)


def create_user_tokens(
    user: schemas.TokenData,
    refresh_token=None,
):
    payload: dict = {"jwi": str(uuid.uuid4())}
    access_token: str = create_access_token(payload, user)
    if not refresh_token:
        refresh_token: str = create_refresh_token(payload)

    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token)


def get_user_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
) -> schemas.TokenData:
    try:
        payload = decode_token(token)

        token_type: str = payload.get("token_type")
        if not token_type or token_type != "access":
            raise exceptions.CREDENTIALS_EXCEPTION_TYPE

        expire: int = payload.get("exp")
        if not expire or expire < now_utc().timestamp():
            raise exceptions.CREDENTIALS_EXCEPTION_EXPIRED

        user = schemas.TokenData(**payload)
        if not user:
            raise exceptions.CREDENTIALS_EXCEPTION_USER

    except jwt.PyJWTError:
        raise exceptions.CREDENTIALS_EXCEPTION
    return user


async def authenticate_user(
    session: Annotated[AsyncSession, Depends(get_db)], username, password
):
    user = await dao.UserDAO(session).find_one_or_none(username=username.lower())
    if not user or not verify_pwd(password, user.hashed_password):
        raise exceptions.AUTH_EXCEPTION_WRONG_PARAMETER
    return user
