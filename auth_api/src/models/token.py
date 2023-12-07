from pydantic import BaseModel


class Token(BaseModel):
    access: str
    refresh: str
