from abc import ABC, abstractmethod
from typing import TypeVar

M = TypeVar('M')


class AbstractDB(ABC):

    @abstractmethod
    async def get_object(self, id: str) -> M | None:
        pass

    @abstractmethod
    async def get_list(self, **kwargs) -> list[M] | None:
        pass


class AbstractCache(AbstractDB):

    @abstractmethod
    async def put_object(self, key: str, m: M):
        pass

    @abstractmethod
    async def put_list(self, m: list[M], **kwargs):
        pass

    @abstractmethod
    async def flush_all(self):
        pass
