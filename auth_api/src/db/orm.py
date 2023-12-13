import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.db_model import Base
from .abc import AbstractDB


class AsyncDB(AbstractDB):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, object: Base):
        self.session.add(object)
        await self.commit()
        return object.id

    async def delete(self, object: Base):
        await self.session.delete(object)
        await self.session.commit()

    async def select_one(self, table: Base, id: uuid.UUID):
        object = await self.session.get(table, id)
        return object

    async def scalar(self, table: Base, id: uuid.UUID = None, login: str = None, relation: Base = None):
        if relation:
            object = await self.session.scalar(select(table).where(table.id == id).options(selectinload(relation)))
        elif id:
            object = await self.session.scalar(select(table).where(table.id == id))
        elif login:
            object = await self.session.scalar(select(table).where(table.login == login))
        else:
            object = None
        return object

    async def select_all(self, table: Base, relation: Base = None):
        if relation:
            query = select(table).options(selectinload(relation))
        else:
            query = select(table)
        result = await self.session.execute(query)
        objects = result.scalars().all()
        return objects

    async def get_by_uid(self, table: Base, user_id: uuid.UUID = None):
        object = await self.session.select(table).where(table.user_id == user_id)
        return object

    async def get_by_provider_id(self, table: Base, provider_id: str):
        object = await self.session.select(table).where(table.provider_id == provider_id)
        return object

    async def flush(self):
        await self.session.flush()

    async def commit(self):
        await self.session.commit()
