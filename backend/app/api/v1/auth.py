from typing import Annotated

from fastapi import APIRouter
from fastapi import HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from dao import user as dao
from dependencies.database import get_db
from helpers.security import (
    hash_pwd,
    verify_pwd,
    get_user_token,
    get_token_payload,
    credentials_exception,
    oauth2_scheme,
)
from schemas import user as schemas

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
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
        exist_email = await dao.UserDAO(session).find_one_or_none(email=info_form.email)

        if exist_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{info_form.username}' already registered",
            )
        if exist_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{info_form.email}' already registered",
            )

        if pwd_form.password == pwd_form.confirmation_password:
            data["hashed_password"] = hash_pwd(pwd_form.password)

        return await dao.UserDAO(session).add_one_and_return(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e,
        )


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
)
async def _login_pwd(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user = await dao.UserDAO(session).find_one_or_none(username=form_data.username)
    user_token_data = schemas.TokenData(**user.__dict__)
    if not user or not verify_pwd(form_data.password, user.hashed_password):
        raise credentials_exception

    tokens = await get_user_token(user_token_data)

    if await dao.UserDAO(session).update_one_by_id(
        _id=user.id, refresh_token=tokens.refresh_token
    ):
        response.set_cookie(
            key="refresh_token", value=tokens.refresh_token, httponly=True
        )

    return tokens


@router.post(
    "/refresh",
    response_model=schemas.TokenResponse,
)
async def refresh_access_token(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> schemas.UserResponse:
    try:
        payload: dict = get_token_payload(token)
        refresh_token: str = request.cookies.get("refresh_token")

        user = schemas.TokenData(**payload)

        return await get_user_token(user, refresh_token)
    except InvalidTokenError:
        raise credentials_exception
