import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUTH_HOST: str

    class Config:
        env_file = ".env"


"""Используем локалхост в значениях по умолчанию для подключения к существующему контейнеру,
например, тестовому"""
settings = Settings(
    PROJECT_NAME=os.getenv('PROJECT_NAME', 'movies'),
    REDIS_HOST=os.getenv('REDIS_HOST', '127.0.0.1'),
    REDIS_PORT=os.getenv('REDIS_PORT', 6379),
    ELASTIC_HOST=os.getenv('ELASTIC_HOST', '127.0.0.1'),
    ELASTIC_PORT=os.getenv('ELASTIC_PORT', 9200),
    BASE_DIR=os.getenv('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
