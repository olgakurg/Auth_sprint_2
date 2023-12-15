from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from src.models.orjson_mixin import PersonModel, OrjsonModel
from src.services.person import get_person_service
from src.services.service import Service
from .utils.settings import PAGE_SIZE, PAGE_START, PERSON_NOT_FOUND, UUID_ERROR, INVALID_QUERY
from .utils.helpers import check_params

router = APIRouter()


class Film(OrjsonModel):
    roles: list[str]


class Person(PersonModel):
    films: list[Film]


class FilmPerson(OrjsonModel):
    imdb_rating: float
    title: str


@router.get('/search', response_model=list[Person])
async def person_search(
        page_number: Annotated[int, Query(PAGE_START, alias='page_number', ge=1)] = PAGE_START,
        page_size: Annotated[int, Query(PAGE_SIZE, alias='page_size', ge=1, le=100)] = PAGE_SIZE,
        sort: Annotated[str | None, Query(None, max_length=50)] = None,
        filters: Annotated[str | None, Query(None, max_length=100)] = None,
        query: str | None = None,
        person_service: Service = Depends(get_person_service)
) -> list[Person]:
    check_params(page_number=page_number, page_size=page_size)
    persons = await person_service.get_by_query(page_number=page_number, page_size=page_size,
                                                sort=sort, filters=filters, query=query)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return persons


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: Annotated[UUID, Path(...)],
                         person_service: Service = Depends(get_person_service)) -> Person:
    if not person_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=UUID_ERROR)
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    return Person.parse_obj(person)


@router.get('/{person_id}/film', response_model=list[FilmPerson])
async def person_list_film(person_id: Annotated[UUID, Path(...)],
                           person_service: Service = Depends(get_person_service)) -> list[FilmPerson]:
    if not person_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=UUID_ERROR)
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    films = [FilmPerson.parse_obj(film) for film in person.films]
    return films


@router.get('/', response_model=list[Person])
async def person_search(
        page_number: Annotated[int, Query(PAGE_START, alias='page_number', ge=1)] = PAGE_START,
        page_size: Annotated[int, Query(PAGE_SIZE, alias='page_size', ge=1, le=100)] = PAGE_SIZE,
        sort: Annotated[str | None, Query(None, max_length=50)] = None,
        filters: Annotated[str | None, Query(None, max_length=100)] = None,
        query: str | None = None,
        person_service: Service = Depends(get_person_service)
) -> list[Person]:
    check_params(page_number=page_number, page_size=page_size)
    persons = await person_service.get_by_query(page_number=page_number, page_size=page_size,
                                                sort=sort, filters=filters, query=query)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return persons
