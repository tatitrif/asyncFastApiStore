from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from core.database import async_db_session


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Returns a database Session for use with fastapi Depends
    """

    async with async_db_session() as session:
        yield session
