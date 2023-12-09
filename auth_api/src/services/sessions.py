import datetime
import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.orm import AsyncDB
from src.db.postgres import get_session
from src.models.db_model import User, UserSession
from src.models.session import SessionInDB
from src.models.users import UserAuth


@lru_cache()
def get_session_service(
        session_query: AsyncSession = Depends(get_session)
):
    return SessionService(AsyncDB(session_query))


class SessionService:
    def __init__(self, db: AsyncDB):
        self.db = db

    async def create_session(self, user_auth: UserAuth, t=datetime.datetime):
        user_db = await self.db.scalar(User, login=user_auth.login)
        if not user_db:
            return None
        session = SessionInDB(user_id=user_db.id, auth_date=t, creation_date=datetime.datetime.now())
        session_orm = UserSession(**session.model_dump())
        try:
            session_id = await self.db.insert(session_orm)
            return session_id
        except Exception as e:
            logging.error(f'from create_session with uid {user_db.id} excepted {e}')
        return None

    async def get_sessions(self, user_id):
        sessions = await self.db.get_by_uid(UserSession, user_id=user_id)
        return sessions
