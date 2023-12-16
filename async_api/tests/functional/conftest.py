import pytest_asyncio
import pytest
import aiohttp
import asyncio
import json

from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings
from functional.testdata.data import data, films_data, genres_data, persons_data


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_client():
    hosts = f'{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}'
    client = AsyncElasticsearch(hosts=hosts, validate_cert=False, use_ssl=False)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_create_bd(es_client):
    for index in test_settings.ELASTIC_INDEX:
        # Подгружаем схему в эластик всех индексов
        with open(f'./tests/functional/testdata/{index}_schema.json', 'r') as f:
            schema = json.load(f)
        await es_client.indices.create(index=index, body=schema)

        # Формируем тестовые данные
        bulk_query = []
        for row in data[index]:
            bulk_query.extend([
                json.dumps({'index': {'_index': index, '_id': row['id']}}),
                json.dumps(row)
            ])
        str_query = '\n'.join(bulk_query) + '\n'

        # Загружаем данные в эластик
        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    yield
    for index in test_settings.ELASTIC_INDEX:
        await es_client.indices.delete(index=index)


@pytest_asyncio.fixture(scope='function')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def api_request(client_session: aiohttp.ClientSession):
    async def inner(index: str, id: str = '', search: bool = False, params: dict = {}):
        query = ''
        search_suffix = ''
        if search:
            search_suffix = 'search/'
        if params:
            query += '?'
            for key, value in params.items():
                query += key + '=' + str(value) + '&'
        if id:
            search_suffix = ''
            query = id

        url = f'http://{test_settings.APP_HOST}:{test_settings.APP_PORT}/api/v1/{index}/{search_suffix}{query}'

        async with client_session.get(url) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

        return {'body': body, 'status': status, 'headers': headers}

    return inner
