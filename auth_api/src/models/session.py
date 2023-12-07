from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SessionInDB(BaseModel):
    user_id: UUID
    auth_date: datetime
    last_date: Optional[datetime] = None
    creation_date: Optional[datetime] = None

    class Config:
        from_attributes = True
