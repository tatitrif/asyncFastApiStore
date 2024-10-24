from typing import Annotated

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import exceptions
from dao import user as dao
from dependencies.database import get_db
from helpers.security import (
    hash_pwd,
    create_user_tokens,
    get_user_token,
    authenticate_user,
    oauth2_scheme,
)
from schemas import user as schemas

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
)
async def _create_one(
    info_form: Annotated[schemas.UserRequest, Depends()],
    pwd_form: Annotated[schemas.UserPasswords, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> schemas.UserResponse:
    data = info_form.model_dump()
    try:
        exist_username = await dao.UserDAO(session).find_one_or_none(
            username=info_form.username
        )

        if exist_username:
            raise exceptions.AUTH_EXCEPTION_CONFLICT_USERNAME

        if info_form.email:
            exist_email = await dao.UserDAO(session).find_one_or_none(
                email=info_form.email
            )
            if exist_email:
                raise exceptions.AUTH_EXCEPTION_CONFLICT_EMAIL

        if pwd_form.password == pwd_form.confirmation_password:
            data["hashed_password"] = hash_pwd(pwd_form.password)

        return await dao.UserDAO(session).add_one_and_return(**data)
    except Exception:
        raise exceptions.AUTH_EXCEPTION_CREATE_USER


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
    summary="Create access and refresh tokens for a user",
)
async def _login_pwd(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user: schemas.TokenData = await authenticate_user(
        session, form_data.username, form_data.password
    )

    user_token_data = schemas.TokenData(**user.__dict__)
    tokens = create_user_tokens(user_token_data)

    await dao.UserDAO(session).update_one_by_id(
        _id=user.id, refresh_token=tokens.refresh_token
    )
    return tokens


@router.post(
    "/refresh",
    response_model=schemas.TokenResponse,
    summary="Create new access token for user",
)
async def refresh_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user = get_user_token(token)

    user_db = await dao.UserDAO(session).find_one_or_none(username=user.username)
    if not user_db:
        raise exceptions.CREDENTIALS_EXCEPTION_USER_DB
    user_db = schemas.TokenData(**user_db.__dict__)
    return create_user_tokens(user_db)


@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user = get_user_token(token)

    user_db = await dao.UserDAO(session).find_one_or_none(username=user.username)
    if not user_db or not user_db.refresh_token:
        raise exceptions.CREDENTIALS_EXCEPTION_USER_DB
    success = await dao.UserDAO(session).update_one_by_id(
        _id=user_db.id, refresh_token=None
    )
    if not success:
        raise exceptions.CREDENTIALS_EXCEPTION_LOGOUT
    return "Logout successful"
