from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import MappedBase


class Item(MappedBase):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
