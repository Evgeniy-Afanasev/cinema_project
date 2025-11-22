from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):

    redis_host: str = Field('redis', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')

    elastic_schema: str = Field('http://', alias='ELASTIC_SCHEMA')
    elastic_host: str = Field('elasticsearch', alias='ELASTIC_HOST')
    elastic_port: int = Field(9200, alias='ELASTIC_PORT')
    elastic_movies_index: str = Field('movies', alias='ELASTIC_MOVIES_INDEX')

    postgres_host: str = Field('postgres', alias='POSTGRES_HOST')
    postgres_port: int = Field(5432, alias='POSTGRES_PORT')
    postgres_user: str = Field('postgres', alias='POSTGRES_USER')
    postgres_password: str = Field('postgres', alias='POSTGRES_PASSWORD')

    postgres_auth_db: str = Field('auth_db', alias='POSTGRES_AUTH_DB')

    movies_api_service_host: str = Field("movies-service", alias='MOVIES_API_SERVICE_HOST')
    movies_api_service_port: int = Field(8000, alias='MOVIES_API_SERVICE_PORT')

    auth_service_host: str = Field("auth-service", alias='AUTH_SERVICE_HOST')
    auth_service_port: int = Field(8001, alias='AUTH_SERVICE_PORT')

test_settings = TestSettings()
