import math
import time

import pytest
from functional.settings import IndexChoice
from functional.testdata.data import FILM_COUNT

FILM_INDEX = IndexChoice.FILMS

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'page_size',
    [
        1,
        math.ceil(FILM_COUNT / 5),
        math.ceil(FILM_COUNT / 3),
        math.ceil(FILM_COUNT / 2),
        math.ceil(FILM_COUNT)
    ]
)
async def test_list_films(api_request, page_size):
    params = {'page_size': page_size}
    response = await api_request(index=FILM_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200
    assert len(body) == page_size


@pytest.mark.parametrize(
    'id',
    [
        '862dc948-d9cf-4377-8330-b0a5486f9fa1',
        '9ed2d08f-85c0-46c9-8032-2bf5710613b4',
    ]
)
async def test_get_film(api_request, id):
    response = await api_request(index=FILM_INDEX, id=id)
    status = response['status']
    body = response['body']

    assert status == 200
    assert body['uuid'] == id


@pytest.mark.parametrize(
    'id',
    [
        '2c63b3c3-7f38-4fa4-85b9-f3e7b96e80de',
        '87173343-4ae2-4686-935a-c2fbcd81c563',
    ]
)
async def test_get_film_cache(api_request, id):
    t1_start = time.perf_counter()
    response_1 = await api_request(index=FILM_INDEX, id=id)
    t1_end = time.perf_counter()
    t1_result = t1_end - t1_start

    assert response_1['status'] == 200
    assert response_1['body']['uuid'] == id

    t2_start = time.perf_counter()
    response_2 = await api_request(index=FILM_INDEX, id=id)
    t2_end = time.perf_counter()
    t2_result = t2_end - t2_start

    assert response_2['status'] == 200
    assert response_2['body']['uuid'] == id

    assert t1_result > t2_result


@pytest.mark.parametrize(
    'genre_id',
    [
        '58447f4d-1664-4b7b-8810-3fd9fa506436',
        '3fc58c13-32ea-404a-ba83-976f38e607cc',
        'e4b4e84a-0292-4c01-b360-0588ced918a9',
        'a7f5c2b8-a41c-43c5-ac56-3103f86315e5',

    ]
)
async def test_filter_film(api_request, genre_id):
    params = {
        'filters': 'genre' + '%3D' + genre_id
    }
    response = await api_request(index=FILM_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200

    for film in body:
        film_response = await api_request(index=FILM_INDEX, id=film['uuid'])
        film_genre_ids = [genre['id'] for genre in film_response['body']['genre']]
        assert genre_id in film_genre_ids, \
            'В жанрах фильма отстутствует жанр по которому проведена фильтрация'


async def test_sort_films_asc(api_request):
    params = {
        'sort': '-imdb_rating'
    }
    response = await api_request(index=FILM_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200

    prev_rating = float('inf')
    for film in body:
        film_rating = float(film['imdb_rating'])
        assert prev_rating >= film_rating
        prev_rating = film_rating


async def test_sort_films_desc(api_request):
    params = {
        'sort': '+imdb_rating'
    }
    response = await api_request(index=FILM_INDEX, params=params)
    status = response['status']
    body = response['body']

    assert status == 200

    prev_rating = float('-inf')
    for film in body:
        film_rating = float(film['imdb_rating'])
        assert prev_rating <= film_rating
        prev_rating = film_rating
