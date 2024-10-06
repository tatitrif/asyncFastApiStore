import logging
from functools import lru_cache
from logging import config as logging_config
from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
logger = logging.getLogger()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


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
    port: int = 9000
    reload: bool = False

    # db
    db_echo: bool = True
    sqlite_filename: str = "db_project"
    sqlite_database_uri: str = f"sqlite+aiosqlite:///./{sqlite_filename}.db"
    sqlalchemy_database_uri: str = sqlite_database_uri


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
