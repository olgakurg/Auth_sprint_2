import logging
from contextlib import asynccontextmanager
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import persons, genres, films
from src.core.config import Settings
from src.db import redis, elastic

settings = Settings()
logging.basicConfig(level=logging.INFO, filename="api_log.log", filemode="w")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    elastic.es = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'])
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix='/api/v1/films')
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
