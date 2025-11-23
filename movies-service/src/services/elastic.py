from typing import Any, Type, Generic, TypeVar
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Request
from services.abstract import AbstractCache, AbstractDataStorage
from queries.base import BaseFilter
from urllib.parse import urlencode
from pydantic import BaseModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5
CACHE_NAMESPACE = "api_response"

M = TypeVar("M", bound=BaseModel)


class ElasticDataStorage(AbstractDataStorage, Generic[M]):
    def __init__(
            self,
            request: Request,
            cache: AbstractCache,
            elastic: AsyncElasticsearch,
            model_class: Type[M],
            index: str
    ):
        self.request = request
        self.cache = cache
        self.elastic = elastic
        self.model_class = model_class
        self.index = index

    async def get_by_id(self, model_id: str) -> M | None:
        """
        Retrieve a model by its unique identifier.

        Parameters:
        - model_id (str): The unique identifier of the model.

        Returns:
        - An instance of the model if found, otherwise None.
        """
        cache_key = self._generate_cache_key(self.request)
        cached = await self.cache.get(cache_key)
        if cached:
            return self.model_class(**cached)

        model = await self._get_model_from_elastic(model_id)
        if model:
            await self.cache.set(cache_key, model.model_dump(), CACHE_EXPIRE_IN_SECONDS)
        return model

    async def get_all(self, model_filter: BaseFilter) -> list[M]:
        """
        Retrieve multiple models based on the provided filter.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - A list of model instances that match the filter criteria.
        """
        cache_key = self._generate_cache_key(self.request)
        cached = await self.cache.get(cache_key)
        if cached:
            return [self.model_class(**item) for item in cached]

        models = await self._get_all_from_elastic(model_filter)
        if models:
            await self.cache.set(cache_key, [m.model_dump() for m in models], CACHE_EXPIRE_IN_SECONDS)
        return models

    async def _get_model_from_elastic(self, model_id: str) -> M | None:
        """
        Retrieves a model from Elasticsearch using the UUID field in documents.

        Parameters:
        - model_uuid (str): The value of the 'uuid' field to search for.

        Returns:
        - An instance of the model class if found, or None if not found.
        """
        try:
            response = await self.elastic.search(
                index=self.index,
                body={
                    "query": {
                        "term": {
                            "uuid": model_id
                        }
                    },
                    "size": 1
                }
            )
            hits = response['hits']['hits']
            if hits:
                return self.model_class(**hits[0]['_source'])
        except NotFoundError:
            return None
        return None

    async def _get_all_from_elastic(self, model_filter: BaseFilter) -> list[M]:
        """
        Retrieve multiple models from Elasticsearch based on the provided filter.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - A list of model instances that match the filter criteria.
        """
        query_body = await self._make_query(model_filter)
        try:
            doc = await self.elastic.search(index=self.index, body=query_body)
        except NotFoundError:
            return []
        return [self.model_class(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def _make_query(self, model_filter: BaseFilter) -> dict[str, Any]:
        """
        Construct the Elasticsearch query body based on the provided filter with pagination.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - The Elasticsearch query body.
        """
        return {
            "query": {
                "bool": {
                    "must": [],
                },
            },
            "size": model_filter.page_size,
            "from": (model_filter.page_number - 1) * model_filter.page_size,
        }

    async def _enrich_query_with_search(self, model_filter: BaseFilter, query_body: dict[str, Any], field: str) -> dict[
        str, Any]:
        """
        Enrich the Elasticsearch query with a fuzzy search.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing search parameters.
        - query_body (dict[str, Any]): The Elasticsearch query body.
        - field (str): The field to perform the fuzzy search on.

        Returns:
        - The modified Elasticsearch query body.
        """
        if hasattr(model_filter, "query") and model_filter.query:
            query_body["query"]["bool"]["must"].append({
                "fuzzy": {
                    field: {
                        "value": model_filter.query,
                        "fuzziness": "AUTO"
                    }
                }
            })
        return query_body

    @staticmethod
    def _generate_cache_key(request: Request) -> str:
        path = request.url.path
        query_string = urlencode(sorted(request.query_params.items()))
        return f"{CACHE_NAMESPACE}:{path}?{query_string}"
