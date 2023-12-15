from pydantic import BaseModel


class Token(BaseModel):
    access: str
    refresh: str


class YaToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str


class YaUser(BaseModel):
    login: str
    id: int
    client_id: str
    uid: str
    psuid: str
