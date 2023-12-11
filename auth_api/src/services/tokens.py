import logging
from datetime import timedelta
from functools import lru_cache
from uuid import uuid4

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.abc_redis import AsyncRedis
from src.db.orm import AsyncDB
from src.db.postgres import get_session
from src.db.redis import get_redis
from src.models.db_model import User
from src.models.users import UserAuth

REFRESH_TOKEN_EXPIRES = timedelta(days=30)


@AuthJWT.load_config
def get_config():
    return settings


@lru_cache()
def get_token_service(
        session_query: AsyncSession = Depends(get_session),
        redis: AsyncRedis = Depends(get_redis)):
    return TokenService(AsyncDB(session_query), AsyncRedis(redis))


class TokenService:
    def __init__(self, db: AsyncDB, redis: AsyncRedis):
        self.db = db
        self.redis = redis

    async def _is_valid_refresh(self,
                                refresh_token):
        authorize = AuthJWT()

        token_data = await authorize.decode_token(refresh_token)
        token_jti = token_data["jti"]
        token = await self.redis.get_object(token_jti)
        if not token:
            return None
        return True

    async def exchange_tokens(self, user_id):
        logging.info(f"IN exchange_tokens user_id{user_id}")
        user_db = await self.db.scalar(User, id=user_id)
        if not user_db:
            logging.info(f'no user with id {user_id}')
            return None
        access_token, refresh_token = await self._generate_tokens(user_db)
        if not access_token:
            logging.info(f'no token comes to get_tokens from _generate_tokens')
        return access_token, refresh_token

    async def get_tokens(self, user: UserAuth):
        user_db = await self.db.scalar(User, login=user.login)
        access_token, refresh_token = await self._generate_tokens(user_db)
        if not access_token:
            logging.info(f'no token comes to get_tokens from _generate_tokens')
        return access_token, refresh_token

    async def _generate_tokens(self,
                               user: User,
                               fresh=False):
        authorize = AuthJWT()
        refresh_jti = str(uuid4())
        try:
            roles_db = user.roles
        except Exception as e:
            logging.error(e)
            roles_db = []
        if roles_db:
            roles = [role.name for role in roles_db]
        else:
            roles = ['default_role']
        additional_claims_base = {"user_id": str(user.id)}
        additional_claims_access = {**additional_claims_base, "roles": roles}
        additional_claims_refresh = {**additional_claims_base, "jti": refresh_jti}

        access_token = await authorize.create_access_token(
            subject=str(user.id), user_claims=additional_claims_access, fresh=fresh
        )

        refresh_token = await authorize.create_refresh_token(
            subject=str(user.id), user_claims=additional_claims_refresh
        )

        expires = int(REFRESH_TOKEN_EXPIRES.total_seconds())
        await self.redis.put_object(key=refresh_jti, expires=expires, user_id=str(user.id))
        return access_token, refresh_token

    async def remove_token(self, jti: str):
        await self.redis.delete_by_key(jti)
