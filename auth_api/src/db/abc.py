from abc import ABC, abstractmethod
from typing import TypeVar

M = TypeVar('M')


class AbstractDB(ABC):

    @abstractmethod
    async def select_one(self, **kwargs):
        pass

    async def select_all(self, **kwargs):
        pass

    @abstractmethod
    async def delete(self, **kwargs):
        pass

    @abstractmethod
    async def insert(self, **kwargs):
        pass


class AbstractCache(ABC):

    @abstractmethod
    async def put_object(self, key: str):
        pass

    @abstractmethod
    async def get_object(self, key: str):
        pass

    @abstractmethod
    async def flush_all(self):
        pass
