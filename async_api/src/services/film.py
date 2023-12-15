from functools import lru_cache
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.abs_elastic import AsyncElastic
from src.db.abs_redis import AsyncRedis
from src.db.redis import get_redis
from src.models.film import Film

from .service import Service


@lru_cache()
def get_film_service(
        search_cache: Redis = Depends(get_redis),
        search_engine: AsyncElasticsearch = Depends(get_elastic),
) -> Service:
    settings = {'model': Film, 'index': 'films'}
    return Service(AsyncRedis(search_cache, **settings), AsyncElastic(search_engine, **settings))
