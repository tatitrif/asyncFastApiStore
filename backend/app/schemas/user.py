import re
from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, model_validator, field_validator
from pydantic_core.core_schema import ValidationInfo
from starlette import status

from schemas.base import IdResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenData(IdResponse):
    username: str
    fullname: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None
    refresh_token: str | None = None


class User(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def check_alphanumeric(cls, field: str, info: ValidationInfo) -> str:
        if isinstance(field, str):
            if not (field.isalnum() and field.isascii()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{info.field_name} must be english alphanumeric!",
                )
        return field.lower()


class UserPasswords(BaseModel):
    password: str
    confirmation_password: str

    @field_validator("password")
    @classmethod
    def check_password(cls, field: str, info: ValidationInfo) -> str:
        special_chars = ["@", "$", "_", "-", ".", "!", "#", "%", "^", "&", "*"]
        lower_count, upper_count, special_char_count, digit_count = 0, 0, 0, 0

        if len(field) >= 8:
            for char in field:
                lower_count += int(char.islower())
                upper_count += int(char.isupper())
                digit_count += int(char.isdigit())
                special_char_count += int(char in special_chars)

        checks = [lower_count, upper_count, digit_count, special_char_count]
        if not all(checks):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insecure password.\n"
                + "Password must be at least 8 characters and "
                + "contain at least one lower, one upper case letter, one digit, and one special sign "
                + f"{special_chars}",
            )
        return field

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        print(self.password, self.confirmation_password)
        if self.password != self.confirmation_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password and confirmation password do not match",
            )
        return self


class UserUpdate(BaseModel):
    email: str | None = None
    fullname: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email_regex(cls, email: str | None, info: ValidationInfo):
        if not email:
            return None
        email = email.lower()
        email_pattern = re.compile(r"^\S+@\S+\.([a-z]{2,})+$")
        if not re.fullmatch(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="wrong email format",
            )

        return email


class UserRequest(UserUpdate, User): ...


class UserResponse(UserUpdate, User, IdResponse): ...


class UserListResponse:
    data: list[UserResponse]
