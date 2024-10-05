import sys
from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from core.conf import settings, logger


def create_engine_and_session(
    url: str,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    try:
        engine = create_async_engine(
            url, echo=settings.db_echo, future=True, pool_pre_ping=True
        )
    except Exception as e:
        logger.error("Database connection failed {}", e)
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
        return engine, db_session


async_engine, async_db_session = create_engine_and_session(
    settings.sqlalchemy_database_uri
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Returns a database Session for use with fastapi Depends
    """

    async with async_db_session() as session:
        yield session
