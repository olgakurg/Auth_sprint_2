import hashlib
import logging
import random
import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.orm import AsyncDB
from src.db.postgres import get_session
from src.models.db_model import User
from src.models.users import UserApi


@lru_cache()
def get_user_service(
        session_query: AsyncSession = Depends(get_session)
):
    return UserService(AsyncDB(session_query))


class UserService:
    def __init__(self, db: AsyncDB):
        self.db = db

    @staticmethod
    def _create_hash(password: str,  salt: str = None):
        password = password.encode('utf-8')
        if not salt:
            salt = str(random.randint(0, 100))

        kdf = hashlib.pbkdf2_hmac(
            hash_name=settings.hash_type,
            password=password,
            salt=salt.encode(),
            iterations=settings.hash_iteration,
            dklen=settings.hash_len
        )

        hashed_password = kdf.hex()
        hashed_password += f'${salt}'
        return hashed_password

    async def check_password(self, user: UserApi):
        user_orm = await self.db.scalar(User, login=user.login)
        if not user_orm:
            return False
        pass_pbkdf2 = user_orm.password
        salt = pass_pbkdf2.split('$')[1]
        password_check = self._create_hash(password=user.password, salt=salt)

        if password_check == pass_pbkdf2:
            return True
        else:
            return False

    async def create_user(self, user: UserApi):
        user.password = self._create_hash(user.password)
        logging.info(f'user {user.model_dump()}')

        user_orm = User(**user.model_dump())
        try:
            user_id = await self.db.insert(user_orm)
        except Exception:
            return 'error_unique'
        return user_id

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.db.select_one(User, id=user_id)
        return user

    async def update_user(self, user_id: uuid.UUID, user: UserApi):
        user_old = await self.db.scalar(User, id=user_id)
        if not user_old:
            return None
        user_old.name = user.name
        user_old.login = user.login
        user_old.password = user.password

        return user_id

    async def delete_user(self, user_id):
        user = await self.db.scalar(User, id=user_id)
        if not user:
            return None
        await self.db.delete(user)
        return user_id

    async def get_users(self):
        users = await self.db.select_all(User)
        return users

