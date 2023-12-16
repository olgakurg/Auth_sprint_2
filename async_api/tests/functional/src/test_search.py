import pytest

from functional.settings import IndexChoice

indexs = IndexChoice()
N_RECORDS = 5

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'index',
    [indexs.FILMS, indexs.PERSONS]
)
async def test_search_all(api_request, index):
    response = await api_request(index=index, search=True)
    status = response['status']
    body = response['body']

    assert status == 200
    assert len(body) == 50


@pytest.mark.parametrize(
    'index',
    [indexs.FILMS, indexs.PERSONS]
)
async def test_search_N_records(api_request, index):
    params = {'page_size': N_RECORDS}
    response = await api_request(index=index, search=True, params=params)
    status = response['status']
    body = response['body']

    assert status == 200
    assert len(body) == N_RECORDS


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'index': indexs.FILMS, 'query': 'Star Wars'},
                {'status': 200, 'length': 5}
        ),
        (
                {'index': indexs.PERSONS, 'query': 'Nik'},
                {'status': 200, 'length': 10}
        )

    ]
)
async def test_search_phrase(api_request, query_data, expected_answer):
    params = {'query': query_data['query']}
    response = await api_request(index=query_data['index'], search=True, params=params)
    status = response['status']
    body = response['body']

    assert status == expected_answer['status']
    assert len(body) >= expected_answer['length']
