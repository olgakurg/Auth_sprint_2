import time
from functools import wraps
from http import HTTPStatus
from typing import Callable

from src.db.abc_redis import AsyncRedis
from src.db.redis import get_redis
from src.models.usets import UserAuth


def get_login():
    return request.args.get('login')


class Limiter:
    def __init__(self, redis: AsyncRedis, key_func: Callable) -> None:
        self.db = redis
        self.key_func = key_func

    def limit(self, duration, limit):
        def wrap(fn):
            @wraps(fn)
            async def wrapper(*args, **kwargs):
                pipeline = self.db.get_pipeline(transaction=True)
                user: UserAuth = kwargs.get('request')
                key = user.login
                key = '{}:{}:{}'.format(key, duration,
                                        int(time.time() // duration))
                pipeline.incr(key)
                pipeline.expire(key, duration)
                if pipeline.execute()[0] > limit:
                    return (
                        {'error': 'too many requests'},
                        HTTPStatus.TOO_MANY_REQUESTS
                    )
                return fn(*args, **kwargs)

            return wrapper

        return wrap


redis = get_redis()

limiter_login = LimitService(
    db=redis,
    key_func=get_login
)
