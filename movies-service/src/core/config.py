import os
from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    redis_host: str = Field('redis', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    redis_db: str = Field('movies', alias='REDIS_MOVIES_DB')

    elastic_schema: str = Field('http://', alias='ELASTIC_SCHEMA')
    elastic_host: str = Field('elasticsearch', alias='ELASTIC_HOST')
    elastic_port: int = Field(9200, alias='ELASTIC_PORT')
    elastic_movies_index: str = Field('movies', alias='ELASTIC_MOVIES_INDEX')


# Создание экземпляра настроек
settings = Settings()
