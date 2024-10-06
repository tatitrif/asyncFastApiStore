from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase


class MappedBase(AsyncAttrs, DeclarativeBase):
    """
    Declarative base class, the original DeclarativeBase class,
    exists as the parent class of all base classes or data model classes

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__
    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    """

    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    created: Mapped[datetime] = mapped_column(
        doc="Time of creation", server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        doc="Time of last modification", server_default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Automatically generate table name from class name."""
        return cls.__name__.lower()

    def __repr__(self):
        cols = []
        repr_cols_num = 3
        repr_cols = tuple()
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in repr_cols or idx < repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Message(BaseModel):
    message: str
