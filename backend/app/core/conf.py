import logging
from functools import lru_cache
from logging import config as logging_config
from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings
from starlette.templating import Jinja2Templates

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
logger = logging.getLogger()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
templates = Jinja2Templates(directory="templates")


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured with environment variables.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # FastAPI
    project_title: str = "Project Name"
    project_description: str = "Fastapi project description"
    version: str = "0.0.1"
    api_v1_str: str = "/api/v1"

    # uvicorn
    port: int = 8000
    reload: bool = False

    # db
    db_echo: bool = True
    sqlite_filename: str = "db_project"
    sqlite_database_uri: str = f"sqlite+aiosqlite:///./{sqlite_filename}.db"
    sqlalchemy_database_uri: str = sqlite_database_uri

    # auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
