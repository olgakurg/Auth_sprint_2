import time
from functools import wraps
from http import HTTPStatus
from typing import Callable
from fastapi import Request, Depends

from src.models.users import UserAuth


async def get_login(request: Request):
    body = await request.json()
    return body['login']


class Limiter:
    def __init__(self, redis, key_func: Callable):
        self.db = redis
        self.key_func = key_func

    async def limit(self, duration, limit):
        async def wrap(fn):
            @wraps(fn)
            async def wrapper(*args, **kwargs):
                pipeline = await self.db.get_pipeline(transaction=True)
                user: UserAuth = kwargs.get('request')
                key = user.login
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



