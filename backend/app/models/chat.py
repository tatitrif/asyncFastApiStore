from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import MappedBase


class Message(MappedBase):
    text: Mapped[str] = mapped_column(String(255), nullable=True)

    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    sender = relationship(
        "User", foreign_keys=[sender_id], uselist=False, back_populates="messages"
    )

    receiver_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        uselist=False,
        back_populates="private_messages",
    )
