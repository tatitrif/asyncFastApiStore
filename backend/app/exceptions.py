from fastapi import status, HTTPException

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION_TYPE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate type Access Token",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION_EXPIRED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_USER = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token dont have an user",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_USER_DB = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User dont exist already in db",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_LOGOUT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Logout failed",
    headers={"WWW-Authenticate": "Bearer"},
)

AUTH_EXCEPTION_WRONG_PARAMETER = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Wrong parameter",
)

AUTH_EXCEPTION_CONFLICT_USERNAME = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username already registered",
)

AUTH_EXCEPTION_CONFLICT_EMAIL = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username already registered",
)

AUTH_EXCEPTION_CREATE_USER = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad request",
)

USER_EXCEPTION_NOT_FOUND_USER = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)
USER_EXCEPTION_NOT_FOUND_PAGE = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User Page not found ",
)

ITEM_EXCEPTION_NOT_FOUND_ITEM = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found",
)
ITEM_EXCEPTION_NOT_FOUND_PAGE = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item Page not found ",
)
ITEM_EXCEPTION_IMAGE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cant upload image",
)
