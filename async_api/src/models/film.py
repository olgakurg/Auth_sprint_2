from .orjson_mixin import OrjsonModel, PersonModel, GenreModel


class Film(OrjsonModel):
    """Represents full information about movie  - id, title, description, rating,
        genres (as list of ids and names), actors, writers, directors as lists of ids and full names"""
    title: str
    imdb_rating: float
    description: str
    genre: list[GenreModel]
    genre_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    director_names: list[str]
    actors: list[PersonModel]
    writers: list[PersonModel]
    directors: list[PersonModel]
