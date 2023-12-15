import asyncio

import aiohttp
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models.db_model import Role, User
from .settings import test_settings
from .testdata.data import user_db, test_role


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def get_engine():
    dsn = f'postgresql+asyncpg://{test_settings.db_user}:{test_settings.db_password}@{test_settings.db_host}:{test_settings.db_port}/{test_settings.db_name}'
    engine = create_async_engine(dsn, echo=False, future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture(scope='session')
async def load_data(get_engine):
    async with get_engine.begin() as conn:
        new_user = User(login=user_db['name'], password=user_db['password'])
        new_role = Role(name=test_role['name'], desription=test_role['description'])
        new_user.roles.append(new_role)
        conn.add(new_user)
        await conn.commit()
        yield
        async with conn.begin():
            await conn.run_sync(User.query.delete)
            await conn.run_sync(Role.query.delete)


@pytest_asyncio.fixture(scope='function')
async def client_session():
    session = aiohttp.ClientSession(f'http://{test_settings.app_host}:{test_settings.app_port}')
    yield session
    await session.close()


@pytest.fixture
def api_request(client_session: aiohttp.ClientSession):
    async def inner(table: str, id: str = '', params: dict = {}, headers: dict = {}, method: str = 'get'):
        url = f'/{test_settings.api_version}/{table}/{id}'

        methods = {
            'get': client_session.get(url, headers=headers),
            'post': client_session.post(url, json=params, headers=headers),
            'put': client_session.put(url, json=params, headers=headers),
            'delete': client_session.delete(url, headers=headers)
        }

        async with methods[method] as response:
            body = await response.json()
            headers = response.headers
            status = response.status

        return {'body': body, 'status': status, 'headers': headers}

    return inner
