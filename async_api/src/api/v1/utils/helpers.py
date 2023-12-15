from fastapi import HTTPException
from http import HTTPStatus

from .settings import INVALID_QUERY, PAGE_MAX, PAGE_MIN


def check_params(page_number, page_size):
    if page_number not in range(PAGE_MIN, PAGE_MAX + 1) or page_size not in range(PAGE_MIN + 1, PAGE_MAX + 1):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=INVALID_QUERY)
