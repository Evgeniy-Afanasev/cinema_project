from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    redis_host: str = Field('redis', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')

    postgres_host: str = Field('postgres', alias='POSTGRES_HOST')
    postgres_port: int = Field(5432, alias='POSTGRES_PORT')
    postgres_user: str = Field('postgres', alias='POSTGRES_USER')
    postgres_password: str = Field('postgres', alias='POSTGRES_PASSWORD')
    postgres_db: str = Field('auth_db', alias='POSTGRES_AUTH_DB')

    jwt_secret: str = Field(..., alias='JWT_SECRET')
    jwt_alg: str = Field("HS256", alias='JWT_ALG')
    access_token_exp_minutes: int = Field(30, alias='ACCESS_EXP_MIN')
    refresh_token_exp_days: int = Field(14, alias='REFRESH_EXP_DAYS')


settings = Settings()
