import uuid
from uuid import UUID

from pydantic import BaseModel


class PermissionApi(BaseModel):
    name: str


class PermissionInDB(BaseModel):
    id: uuid.UUID
    name: str


class RoleApi(BaseModel):
    name: str
    description: str | None = None
    permissions: list[UUID] = []


class RoleInDB(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    permissions: list[PermissionInDB]

    class Config:
        from_attributes = True


class RoleShort(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
