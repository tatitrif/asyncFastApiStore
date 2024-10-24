from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import MappedBase


class User(MappedBase):
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    fullname: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=True, unique=False, default=True
    )

    messages = relationship(
        "Message", back_populates="sender", foreign_keys="Message.sender_id"
    )
    private_messages = relationship(
        "Message", back_populates="receiver", foreign_keys="Message.receiver_id"
    )
