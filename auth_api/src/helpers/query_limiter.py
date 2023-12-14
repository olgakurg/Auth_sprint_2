import time
from functools import wraps
from http import HTTPStatus
from typing import Callable
from fastapi import Request
from src.db.abc_redis import AsyncRedis
from src.db.redis import get_redis


def get_login(request: Request):
    return request.query_params.get('login')


class Limiter:
    def __init__(self, key_func: Callable):
        self.db = get_redis()
        self.key_func = key_func

    async def limit(self, duration, limit):
        async def wrap(fn):
            @wraps(fn)
            async def wrapper(*args, **kwargs):
                pipeline = await self.db.get_pipeline(transaction=True)
                key = self.key_func()
                key = '{}:{}:{}'.format(key, duration,
                                        int(time.time() // duration))
                await pipeline.incr(key)
                await pipeline.expire(key, duration)
                if pipeline.execute()[0] > limit:
                    return (
                        {'error': 'too many requests'},
                        HTTPStatus.TOO_MANY_REQUESTS
                    )
                return fn(*args, **kwargs)

            return wrapper

        return wrap


limiter_login = Limiter(key_func=get_login)
