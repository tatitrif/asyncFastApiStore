from pydantic import BaseModel


class ReceiveMessage(BaseModel):
    receiver: int | str | None = None
    text: str


class SendMessage(ReceiveMessage):
    sender: str
