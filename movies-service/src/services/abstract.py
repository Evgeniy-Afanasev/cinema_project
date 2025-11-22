import abc
from typing import Any
from queries.base import BaseFilter


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abc.abstractmethod
    async def set(self, key: str, value: Any, expire: int) -> None:
        pass


class AbstractDataStorage(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, model_id: str) -> Any:
        pass

    @abc.abstractmethod
    async def get_all(self, model_filter: BaseFilter) -> list[Any]:
        pass
