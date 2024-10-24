from fastapi import WebSocket

from schemas import chat as schemas


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.update({username: websocket})
        print(self.active_connections)

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_personal_message(self, message: schemas.SendMessage):
        if message.receiver == "all":
            try:
                await self.active_connections[message.sender].send_json(message.dict())
            except KeyError:
                pass
        else:
            try:
                await self.active_connections[message.receiver].send_json(
                    message.dict()
                )
                await self.active_connections[message.sender].send_json(message.dict())
            except KeyError:
                pass

    async def broadcast(self, message: schemas.SendMessage):
        for username, websocket in self.active_connections.items():
            if username != message.sender:
                await websocket.send_json(message.dict())


manager = ConnectionManager()
