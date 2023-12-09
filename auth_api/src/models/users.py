import uuid

from pydantic import BaseModel


class UserRolesApi(BaseModel):
    id: uuid.UUID
    roles: list[uuid.UUID]


class RoleInDB(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    id: uuid.UUID
    login: str
    name: str
    roles: list[RoleInDB]

    class Config:
        from_attributes = True

class UserApi(BaseModel):
    login: str
    password: str
    name: str


class UserAuth(BaseModel):
    login: str
    password: str
