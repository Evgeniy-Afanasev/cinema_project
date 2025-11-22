from functools import lru_cache
from typing import Any
from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from fastapi import Request, Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from queries.base import BaseFilter
from queries.film import SearchFilmFilter, FilmFilter
from services.abstract import AbstractCache, AbstractDataStorage
from services.redis import RedisCache
from services.elastic import ElasticDataStorage


class FilmService(ElasticDataStorage[Film]):
    async def _make_query(self, film_filter: FilmFilter) -> dict[str, Any]:
        query_body = await super()._make_query(film_filter)
        if film_filter.sort:
            query_body["sort"] = [film_filter.sort]
        if film_filter.genre:
            query_body["query"]["bool"]["must"].append({
                "terms": {
                    "genres": [film_filter.genre]
                }
            })
        query_body = await self._enrich_query_with_search(film_filter, query_body, "title")
        return query_body


@lru_cache()
def get_film_service(request: Request, redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic),) -> FilmService:
    cache = RedisCache(redis)
    return FilmService(
        request=request,
        cache=cache,
        elastic=elastic,
        model_class=Film,
        index='movies',
    )
