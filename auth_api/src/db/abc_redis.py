import json

from redis.asyncio import Redis
from src.db.abc import AbstractCache


class AsyncRedis(AbstractCache):

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_object(self, key: str) -> str | None:
        data = await self.redis.get(key)
        if not data:
            return None
        return data

    async def put_object(self, key: str, **kwargs):
        expires = kwargs['expires']
        await self.redis.set(key, json.dumps(kwargs), expires)

    def update_cache_expire(self, t: int):
        self._CACHE_EXPIRE_IN_SECONDS_ = t


    async def delete_by_key(self, key: str):
        await self.redis.delete(key)

    async def flush_all(self):
        await self.redis.flushall(asynchronous=True)

    async def get_pipeline(self, **kwargs):
        return await self.redis.pipeline(**kwargs)
