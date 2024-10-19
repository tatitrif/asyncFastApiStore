import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from core.conf import settings
from schemas import user as schemas

current_time: datetime = datetime.now(timezone.utc)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def to_bits(*args):
    return tuple(s.encode("utf-8") for s in args)


def to_str(*args):
    return tuple(b.decode("utf-8") for b in args)


def hash_pwd(pwd: str) -> str:
    salt = bcrypt.gensalt()
    return to_str(bcrypt.hashpw(*to_bits(pwd), salt))[0]


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(*to_bits(plain_pwd, hashed_pwd))


def encode_tokens(data):
    return jwt.encode(data, settings.secret_key, settings.algorithm)


def decode_tokens(data):
    return jwt.decode(data, settings.secret_key, [settings.algorithm])


def get_token_payload(
    token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
) -> dict:
    try:
        return decode_tokens(token)
    except InvalidTokenError:
        raise credentials_exception


def create_access_token(data: dict, user: schemas.TokenData):
    to_encode = data.copy()
    access_token_exp = current_time + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update(
        {**user.model_dump(), "token_type": "access", "exp": access_token_exp}
    )
    return encode_tokens(to_encode)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"token_type": "refresh"})
    return encode_tokens(to_encode)


async def get_user_token(
    user: schemas.TokenData,
    refresh_token=None,
):
    payload: dict = {"jwi": str(uuid.uuid4())}
    access_token: str = create_access_token(payload, user)
    if not refresh_token:
        refresh_token: str = create_refresh_token(payload)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
