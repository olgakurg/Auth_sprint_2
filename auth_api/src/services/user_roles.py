import asyncio
import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.orm import AsyncDB
from src.models.roles import RoleApi, PermissionApi
from src.models.users import UserRolesApi
from src.models.db_model import User, Role
from src.db.postgres import get_session


@lru_cache()
def get_user_roles_service(
        session_query: AsyncSession = Depends(get_session)
):
    return UserRolesService(AsyncDB(session_query))


class UserRolesService:
    def __init__(self, db: AsyncDB):
        self.db = db

    async def add_user_roles(self, user_api: UserRolesApi):
        user_orm = await self.db.scalar(User, id=user_api.id, relation=User.roles)
        if not user_orm:
            return None

        for id in user_api.roles:
            role = await self.db.select_one(Role, id)
            user_orm.roles.append(role)
        await self.db.commit()
        return user_api.id

    async def delete_user_roles(self, user_api: UserRolesApi):
        user_orm = await self.db.scalar(User, id=user_api.id, relation=User.roles)
        if not user_orm:
            return None

        for id in user_api.roles:
            role = await self.db.select_one(Role, id)
            user_orm.roles.remove(role)
        await self.db.commit()
        return user_api.id

    async def get_user_roles(self, user_id: uuid.UUID):
        user_orm = await self.db.scalar(User, id=user_id, relation=User.roles)
        if not user_orm:
            return None, None
        return user_id, user_orm.roles

    async def get_users_roles(self):
        users_orm = await self.db.select_all(User, relation=User.roles)
        return users_orm

