import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.conf import settings


def get_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_title,
        description=settings.project_description,
        default_response_class=ORJSONResponse,
    )

    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=settings.port,
        reload=settings.reload,
    )
