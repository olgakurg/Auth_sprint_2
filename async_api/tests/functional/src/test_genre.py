import pytest
import math
import time

from functional.settings import IndexChoice
from functional.testdata.data import GENRE_COUNT

GENRE_INDEX = IndexChoice.GENRES

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'page_size',
    [
        1,
        math.ceil(GENRE_COUNT / 5),
        math.ceil(GENRE_COUNT / 3),
        math.ceil(GENRE_COUNT / 2),
        math.ceil(GENRE_COUNT)
    ]
)
async def test_list_genres(api_request, page_size):
    params = {'page_size': page_size}
    response = await api_request(index=GENRE_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200
    assert len(body) == page_size


@pytest.mark.parametrize(
    'id',
    [
        '3fc58c13-32ea-404a-ba83-976f38e607cc',
        'e4b4e84a-0292-4c01-b360-0588ced918a9',
    ]
)
async def test_get_genre(api_request, id):
    response = await api_request(index=GENRE_INDEX, id=id)
    status = response['status']
    body = response['body']

    assert status == 200
    assert body['id'] == id


@pytest.mark.parametrize(
    'id',
    [
        'a7f5c2b8-a41c-43c5-ac56-3103f86315e5',
        '58447f4d-1664-4b7b-8810-3fd9fa506436',
    ]
)
async def test_get_film_cache(api_request, id):
    t1_start = time.perf_counter()
    response_1 = await api_request(index=GENRE_INDEX, id=id)
    t1_end = time.perf_counter()
    t1_result = t1_end - t1_start

    assert response_1['status'] == 200
    assert response_1['body']['id'] == id

    t2_start = time.perf_counter()
    response_2 = await api_request(index=GENRE_INDEX, id=id)
    t2_end = time.perf_counter()
    t2_result = t2_end - t2_start

    assert response_2['status'] == 200
    assert response_2['body']['id'] == id

    assert t1_result > t2_result
