from pydantic import BaseModel, BaseSettings
from datetime import date


class PostgresSettings(BaseSettings):
    db_user: str
    db_pass: str
    db_name: str
    db_host: str
    db_port: int

    class Config:
        env_file = 'envFile/db.env'


class Settings(BaseSettings):
    debug: str = 'INFO'
    jsonpath: str
    batch: int = 1000
    urles: str
    index_film: str
    index_person: str
    index_genre: str
    urlparamload: str
    sleep: int = 10

    class Config:
        env_file = 'envFile/.env'


class Person(BaseModel):
    id: str
    full_name: str


class Genre(BaseModel):
    id: str
    name: str


class Movie(BaseModel):
    id: str
    imdb_rating: float
    genre: list[Genre] = []
    title: str
    description: str
    creation_date: date
    genre_names: set[str] = set()
    director_names: set[str] = set()
    actors_names: set[str] = set()
    writers_names: set[str] = set()
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float
    roles: set[str] = set()


class PersonIndex(BaseModel):
    id: str
    full_name: str
    films: list[Film] = []


class GenreIndex(BaseModel):
    id: str
    name: str
    films: list[dict] = []


class RolesChoice:
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'
