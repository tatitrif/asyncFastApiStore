from typing import Annotated

from fastapi import APIRouter, Request, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from core.conf import templates, logger
from dao import chat as dao
from dao import user as u_dao
from dependencies.chat import get_chat_user_by_token
from dependencies.database import get_db
from helpers.socket_manager import manager
from schemas import chat as schemas
from schemas import user as u_schemas

router = APIRouter(prefix="/chat", tags=["Websocket"])


@router.get("/")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/all_users")
async def get_all_chat_users():
    users_list = [*manager.active_connections.keys()]
    return {"users_list": users_list}


@router.get("/messages")
async def get_all_chat_messages(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[u_schemas.TokenData, Depends(get_chat_user_by_token)],
):
    messages = await dao.MessageDAO(session).get_chat(current_user.id)
    return {"messages_list": messages}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[u_schemas.TokenData, Depends(get_chat_user_by_token)],
):
    await manager.connect(websocket, current_user.username)
    try:
        while True:
            message = schemas.ReceiveMessage.parse_obj(await websocket.receive_json())
            receiver = None
            if message.receiver == "all":
                message_obj = schemas.SendMessage(
                    receiver="all", text=message.text, sender=current_user.username
                )
                await manager.broadcast(message_obj)
                await manager.send_personal_message(message_obj)
            else:
                user: u_schemas.UserResponse = await u_dao.UserDAO(
                    session
                ).find_one_or_none(username=message.receiver)
                message_obj = schemas.SendMessage(
                    receiver=message.receiver,
                    text=message.text,
                    sender=current_user.username,
                )
                await manager.send_personal_message(message_obj)
                if not user:
                    logger.error(f"{message.receiver} not found")
                else:
                    receiver = user.id

            await dao.MessageDAO(session).add_one_and_return(
                receiver_id=receiver, text=message.text, sender_id=current_user.id
            )

    except WebSocketDisconnect:
        manager.disconnect(current_user.username)
        message_dict = schemas.SendMessage(
            receiver="all", text="left the chat", sender=current_user.username
        )
        await manager.broadcast(message_dict)
