import time
from functools import wraps
from http import HTTPStatus
from typing import Callable
from fastapi import Request
from src.db.abc_redis import AsyncRedis
from src.db.redis import get_redis



def get_login(request: Request):
    return request.query_params.get('login')


def limiter(key_func: Callable, duration: int, limit: int):
    def wrap(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            db = get_redis()
            pipeline = await db.get_pipeline(transaction=True)
            key = key_func()
            exp = int(time.time() // duration)
            key = f"{key}:{duration}:{exp}"
            await pipeline.incr(key)
            await pipeline.expire(key, duration)
            if pipeline.execute()[0] > limit:
                return HTTPStatus.TOO_MANY_REQUESTS
            return await function(*args, **kwargs)

        return wrapper

    return wrap
