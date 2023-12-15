import json
from redis.asyncio import Redis

from .abs import AbstractCache, M


class AsyncRedis(AbstractCache):
    _CACHE_EXPIRE_IN_SECONDS_ = 60 * 5

    def __init__(self, redis: Redis, model: M, index: str):
        self.redis = redis
        self.model = model
        self.index = index

    async def get_object(self, key: str) -> M | None:
        data = await self.redis.get(key)
        if not data:
            return None
        return self.model(**json.loads(data))

    async def get_list(self, **kwargs) -> list[M] | None:
        key = self._get_key(**kwargs)
        data = await self.redis.get(key)
        if not data:
            return None
        return [self.model(**json.loads(m)) for m in json.loads(data)]

    async def put_object(self, key: str, m: M):
        await self.redis.set(key, m.json(), self._CACHE_EXPIRE_IN_SECONDS_)

    async def put_list(self, m: list[M], **kwargs):
        key = self._get_key(**kwargs)
        body = json.dumps([i.json() for i in m])
        await self.redis.set(key, body, self._CACHE_EXPIRE_IN_SECONDS_)

    def _get_key(self, **kwargs) -> str:
        page_size = kwargs.get('page_size')
        page_number = kwargs.get('page_number')
        query = kwargs.get('query')
        sort = kwargs.get('sort')
        filters = kwargs.get('filters')
        key = f'{self.index}:page_size={page_size}:page_number={page_number}:query={query}:sort={sort}:filters={filters}'

        return key

    def update_cache_expire(self, t: int):
        self._CACHE_EXPIRE_IN_SECONDS_ = t

    def get_cache_expire(self):
        return self._CACHE_EXPIRE_IN_SECONDS_

    async def flush_all(self):
        await self.redis.flushall(asynchronous=True)
