import logging
import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.orm import AsyncDB
from src.db.postgres import get_session
from src.models.db_model import Permission, Role
from src.models.roles import RoleApi, PermissionApi


@lru_cache()
def get_role_service(
        session_query: AsyncSession = Depends(get_session)
):
    return RoleService(AsyncDB(session_query))


class RoleService:
    def __init__(self, db: AsyncDB):
        self.db = db

    async def create_role(self, role: RoleApi):
        role_orm = Role(name=role.name, description=role.description)
        role_id = await self.db.insert(role_orm)
        role_orm = await self.db.scalar(Role, id=role_id, relation=Role.permissions)
        try:
            for id in role.permissions:
                permission = await self.db.select_one(Permission, id=id)
                role_orm.permissions.append(permission)
        except Exception as e:
            logging.error(f'role creating exception {e}')
        await self.db.commit()
        return role_id

    async def get_role(self, role_id: uuid.UUID):
        role = await self.db.scalar(Role, id=role_id, relation=Role.permissions)
        return role

    async def update_role(self, role_id: uuid.UUID, role: RoleApi):
        role_old = await self.db.scalar(Role, id=role_id, relation=Role.permissions)
        if not role_old:
            return None
        role_old.name = role.name
        role_old.description = role.description
        role_old.permissions = []
        for permissions_id in role.permissions:
            permission = await self.db.select_one(Permission, id=permissions_id)
            role_old.permissions.append(permission)
        await self.db.commit()
        return role_id

    async def delete_role(self, role_id):
        role = await self.db.scalar(Role, id=role_id, relation=Role.permissions)
        if not role:
            return None
        await self.db.delete(role)
        return role_id

    async def get_roles(self):
        roles = await self.db.select_all(Role)
        return roles

    async def create_permission(self, permission: PermissionApi):
        object = Permission(**permission.model_dump())
        permission_id = await self.db.insert(object)
        return permission_id

    async def get_permission(self, permission_id: uuid.UUID):
        permission = await self.db.scalar(Permission, permission_id)
        return permission




