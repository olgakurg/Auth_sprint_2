from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from src.services.film import get_film_service
from src.services.service import Service
from .utils.access_control import PermissionService, get_permission_service
from .utils.helpers import check_params
from .utils.models import FilmShort, FilmDetail
from .utils.settings import PAGE_START, PAGE_SIZE, FILM_NOT_FOUND, UUID_ERROR, INVALID_QUERY

router = APIRouter()


@router.get('/',
            response_model=list[FilmShort],
            summary='Главная страница',
            description='по умолчанию пагинация по 50, сортировка по imdb_rating',
            response_description='id, рейтинг, название',
            tags=['Фильмы']
            )
async def film_list(
        page_number: Annotated[int, Query(PAGE_START, alias='page_number', ge=1)] = PAGE_START,
        page_size: Annotated[int, Query(PAGE_SIZE, alias='page_size', ge=1, le=100)] = PAGE_SIZE,
        sort: Annotated[str | None, Query(None, max_length=50)] = None,
        filters: Annotated[str | None, Query(None, max_length=100)] = None,
        film_service: Service = Depends(get_film_service)
):
    check_params(page_number=page_number, page_size=page_size)
    films = await film_service.get_by_query(page_number=page_number, page_size=page_size,
                                            sort=sort, filters=filters)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return [FilmShort(uuid=film.id, title=film.title,
                      imdb_rating=film.imdb_rating) for film in films]


@router.get('/search',
            response_model=list[FilmShort] | None,
            summary='Поиск по фильмам',
            description='Полнотекстовый поиск по ключевому слову'
                        'по умолчанию пагинация по 50, сортировки нет',
            response_description='id, рейтинг, название',
            tags=['Фильмы']
            )
async def film_list(
        page_number: Annotated[int, Query(PAGE_START, alias='page_number', ge=1)] = PAGE_START,
        page_size: Annotated[int, Query(PAGE_SIZE, alias='page_size', ge=1, le=100)] = PAGE_SIZE,
        sort: Annotated[str | None, Query(None, max_length=50)] = None,
        filters: Annotated[str | None, Query(None, max_length=100)] = None,
        query: str | None = None,
        film_service: Service = Depends(get_film_service)
):
    check_params(page_number=page_number, page_size=page_size)

    films = await film_service.get_by_query(page_number=page_number, page_size=page_size,
                                            sort=sort, filters=filters, query=query)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return [FilmShort(uuid=film.id, title=film.title,
                      imdb_rating=film.imdb_rating) for film in films]


@router.get('/{film_id}',
            response_model=FilmDetail | None,
            summary='Полная информация по фильму',
            description='Детальное описание фильма.',
            response_description='id,рейтинг,  название,  описание, жанры, каст фильма.',
            tags=['Фильмы']
            )
async def film_details(
        film_id: Annotated[UUID, Path(...)],
        token: Annotated[str, Path(...)],
        film_service: Service = Depends(get_film_service),
        permission_service: PermissionService = Depends(get_permission_service)
):
    if not film_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=UUID_ERROR)
    if not token:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=INVALID_QUERY)
    permissions = await permission_service.get_permissions(token)
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    if permission_service.has_permissions(permissions, film):
        return FilmDetail(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            genre=film.genre,
            description=film.description,
            actors=film.actors,
            writers=film.writers,
            directors=film.directors)
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
