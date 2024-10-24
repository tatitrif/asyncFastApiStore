from typing import Annotated

from fastapi import HTTPException, status, Depends

from helpers.security import oauth2_scheme, get_user_token
from schemas import user as schemas


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    user = get_user_token(token)
    return user


def get_current_active_user(
    current_user: Annotated[schemas.TokenData, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def check_admin_role(
    user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
