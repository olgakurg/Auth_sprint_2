from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Decodes orjson dump"""
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmShort(OrjsonModel):
    uuid: UUID
    title: str
    imdb_rating: float


class GenreModel(OrjsonModel):
    id: str
    name: str


class PersonModel(OrjsonModel):
    id: str
    full_name: str


class FilmDetail(FilmShort):
    description: str
    genre: list[GenreModel]
    actors: list[PersonModel]
    writers: list[PersonModel]
    directors: list[PersonModel]
