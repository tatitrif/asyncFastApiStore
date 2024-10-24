from typing import Annotated

from fastapi import Query, WebSocketException, status

from helpers.security import get_user_token


def get_chat_user_by_token(
    token: Annotated[str | None, Query()] = None,
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    current_user = get_user_token(token)
    return current_user
