from .orjson_mixin import OrjsonModel, PersonModel


class Film(OrjsonModel):
    """Basic model represents movie as id, title, rating and list of roles (actor, writer etc.)"""
    title: str
    imdb_rating: float
    roles: list[str]


class Person(PersonModel):
    """Represents person and the films in which he worked"""
    films: list[Film]
