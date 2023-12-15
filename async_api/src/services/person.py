from functools import lru_cache
from fastapi import Depends
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.db.abs_elastic import AsyncElastic
from src.db.abs_redis import AsyncRedis

from .service import Service
from src.models.person import Person


@lru_cache()
def get_person_service(
        search_cache: Redis = Depends(get_redis),
        search_engine: AsyncElasticsearch = Depends(get_elastic),
) -> Service:
    settings = {'model': Person, 'index': 'persons'}
    return Service(AsyncRedis(search_cache, **settings), AsyncElastic(search_engine, **settings))
