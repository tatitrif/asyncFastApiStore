from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import item, user, auth, chat
from core.conf import settings, logger
from core.database import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Start configuring server...")
    await create_tables()
    logger.info("Server started and configured successfully")
    yield
    logger.info("Server shut down")


def get_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_title,
        description=settings.project_description,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    app.include_router(item.router, prefix=settings.api_v1_str)
    app.include_router(user.router, prefix=settings.api_v1_str)
    app.include_router(auth.router, prefix=settings.api_v1_str)
    app.include_router(chat.router, prefix=settings.api_v1_str)

    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=settings.port,
        reload=settings.reload,
    )
