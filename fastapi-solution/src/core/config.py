import os
from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings
from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = 'Some project name'

    redis_host: str = ...

    redis_port: int = Field(default=6379)

    elastic_schema: str = Field('http://', alias='ELASTIC_SCHEMA')

    elastic_host: str = Field(..., alias='ELASTIC_HOST')

    elastic_port: int = Field(9200, alias='ELASTIC_PORT')


# Создание экземпляра настроек
settings = Settings()
