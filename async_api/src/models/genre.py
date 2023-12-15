from .orjson_mixin import GenreModel, OrjsonModel


class Genre(GenreModel):
    """Represents genre as  uuid, name and list of films in this genre"""
    films: list[OrjsonModel]
