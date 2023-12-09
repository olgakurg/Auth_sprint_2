import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from redis.asyncio import Redis

from src.auth_api.v1 import roles, permissions, user_roles, users
from src.core.config import settings
from src.db import redis
from src.db.postgres import create_async_engine
from src.helpers.auth import get_current_user_global
from src.helpers.jaeger_tracer import configure_tracer

logging.basicConfig(level=logging.INFO, filename="api_log.log", filemode="w")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    dsn = f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    engine = create_async_engine(dsn, echo=False, future=True)

    yield
    await engine.dispose()
    await redis.redis.close()

configure_tracer()


app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan,
)

@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response

FastAPIInstrumentor.instrument_app(app)

app.include_router(roles.router, prefix=f'/auth_api/v1/roles', dependencies=[Depends(get_current_user_global)])
app.include_router(permissions.router, prefix=f'/auth_api/v1/permissions',
                   dependencies=[Depends(get_current_user_global)])
app.include_router(users.router, prefix=f'/auth_api/v1/users', dependencies=[Depends(get_current_user_global)])
app.include_router(user_roles.router, prefix=f'/auth_api/v1/user_roles',
                   dependencies=[Depends(get_current_user_global)])
