from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from .utils.settings import PAGE_START, PAGE_SIZE, GENRE_NOT_FOUND, INVALID_QUERY, UUID_ERROR
from .utils.helpers import check_params
from src.models.orjson_mixin import GenreModel
from src.services.genre import get_genre_service
from src.services.service import Service

router = APIRouter()


@router.get('/', response_model=list[GenreModel])
async def genre_search(
        genre_service: Service = Depends(get_genre_service),
        page_number: Annotated[int, Query(PAGE_START, ge=0, alias='page_number')] = PAGE_START,
        page_size: Annotated[int, Query(PAGE_SIZE, ge=1, le=100, alias='page_size')] = PAGE_SIZE
) -> list[GenreModel]:
    check_params(page_number=page_number, page_size=page_size)

    genres = await genre_service.get_by_query(page_number, page_size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)

    return genres


@router.get('/{genre_id}', response_model=GenreModel)
async def genre_details(
        genre_id: Annotated[UUID, Path(...)],
        genre_service: Service = Depends(get_genre_service)) -> GenreModel:
    if not genre_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=UUID_ERROR)
    genre = await genre_service.get_by_id(str(genre_id))
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return GenreModel.parse_obj(genre)
