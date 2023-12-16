import os

from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    ELASTIC_HOST: str = Field('localhost', env='ELASTIC_HOST')
    ELASTIC_PORT: str = Field('9200', env='ELASTIC_PORT')

    APP_HOST: str = Field('localhost', env='APP_HOST')
    APP_PORT: str = Field('8000', env='APP_PORT')

    REDIS_HOST: str = Field('localhost', env='REDIS_HOST')
    REDIS_PORT: str = Field('6379', env='REDIS_PORT')

    ELASTIC_INDEX: tuple = Field(('films', 'persons', 'genres'))
    API_VERSION: str = Field('/api/v1')
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_file = ".env"


test_settings = TestSettings(
    REDIS_HOST='127.0.0.1',
    REDIS_PORT='6379',
    ELASTIC_HOST='127.0.0.1',
    ELASTIC_PORT='9200',
    APP_HOST='0.0.0.0',
    APP_PORT='8000',
    API_VERSION='/app/v1',
)


class IndexChoice:
    FILMS = 'films'
    GENRES = 'genres'
    PERSONS = 'persons'
