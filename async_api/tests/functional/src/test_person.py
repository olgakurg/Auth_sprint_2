import pytest
import math
import time

from functional.settings import IndexChoice
from functional.testdata.data import PERSON_COUNT

PERSON_INDEX = IndexChoice.PERSONS
FILM_INDEX = IndexChoice.FILMS

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'page_size',
    [
        1,
        math.ceil(PERSON_COUNT / 5),
        math.ceil(PERSON_COUNT / 3),
        math.ceil(PERSON_COUNT / 2),
        math.ceil(PERSON_COUNT)
    ]
)
async def test_list_persons(api_request, page_size):
    params = {'page_size': page_size}
    response = await api_request(index=PERSON_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200
    assert len(body) == page_size


@pytest.mark.parametrize(
    'id',
    [
        'ff10de5a-8b34-4007-8ee9-d62bccda65db',
        '0d897e6d-2425-40ca-8f8b-5dc50ae5c92b',
    ]
)
async def test_get_person(api_request, id):
    response = await api_request(index=PERSON_INDEX, id=id)
    status = response['status']
    body = response['body']

    assert status == 200
    assert body['id'] == id


@pytest.mark.parametrize(
    'id',
    [
        '752f3e24-5bf8-4594-be1a-bd202f4df4c7',
        '0b265b02-4419-495a-9cb0-79f2435ace12',
    ]
)
async def test_get_film_cache(api_request, id):
    t1_start = time.perf_counter()
    response_1 = await api_request(index=PERSON_INDEX, id=id)
    t1_end = time.perf_counter()
    t1_result = t1_end - t1_start

    assert response_1['status'] == 200
    assert response_1['body']['id'] == id

    t2_start = time.perf_counter()
    response_2 = await api_request(index=PERSON_INDEX, id=id)
    t2_end = time.perf_counter()
    t2_result = t2_end - t2_start

    assert response_2['status'] == 200
    assert response_2['body']['id'] == id

    assert t1_result > t2_result


@pytest.mark.parametrize(
    'id',
    [
        '752f3e24-5bf8-4594-be1a-bd202f4df4c7',
        '0b265b02-4419-495a-9cb0-79f2435ace12',
        'ff10de5a-8b34-4007-8ee9-d62bccda65db',
        '0d897e6d-2425-40ca-8f8b-5dc50ae5c92b',
    ]
)
async def test_list_person_films(api_request, id):
    response = await api_request(index=PERSON_INDEX, id=id + '/film')
    status = response['status']
    body = response['body']

    assert status == 200

    for film in body:
        film_response = await api_request(index=FILM_INDEX, id=film['id'])
        film_persons_ids = [person['id'] for person in film_response['body']['actors']]
        film_persons_ids += [person['id'] for person in film_response['body']['writers']]
        film_persons_ids += [person['id'] for person in film_response['body']['directors']]
        assert id in set(film_persons_ids), \
            'В персонах фильма отстутствует искомпая персона'
