from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):

    project_name: str = "movies"

    redis_host: str = "redis"
    redis_port: int = 6379

    elastic_schema: str = "http://"
    elastic_host: str = "elasticsearch"
    elastic_port: int = 9200
    elastic_index: str = "movies"

    service_host: str = "fastapi"
    service_port: int = 8000

test_settings = TestSettings()
