import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Decodes orjson dump"""
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    """Basic class for all instances, describes uuid and serialization via orjson module with decoding"""
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonModel(OrjsonModel):
    """Basic models for all persons, represents uuid and full name"""
    full_name: str


class GenreModel(OrjsonModel):
    """Basic models for genre, represents uuid and full name"""
    name: str
