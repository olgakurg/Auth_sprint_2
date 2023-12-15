from functools import lru_cache
from operator import eq, le, ge

import aiohttp
from pydantic import BaseModel

from src.core.config import settings
from src.models.film import Film
from .settings import DEGRADATION_PERMISSION, PERMISSION_URL


class Permission(BaseModel):
    field: str
    bound: str
    value: float


@lru_cache()
def get_permission_service():
    return PermissionService()


class PermissionService:

    async def get_permissions(self, token):
        url = f'http://{settings.AUTH_HOST}/{PERMISSION_URL}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=token) as response:
                if response.status == 200:
                    raw_permissions = await response.json()  # assuming the response is JSON
                    permissions = [Permission.parse_raw(raw) for raw in raw_permissions]
                elif response.status == 500:
                    permissions = [Permission.parse_raw(DEGRADATION_PERMISSION)]
                else:
                    raise aiohttp.ClientResponseError(
                        url, status=response.status, message=f"Permissions {response.status}", headers=response.headers
                    )
        return permissions

    async def has_permissions(self, permissions: list[Permission], film: Film) -> bool:
        bounds = {"equal": eq, "less": le, "more": ge}
        for permission in permissions:
            if not hasattr(film, permission.field):
                continue
            value = getattr(film, permission.field)
            if bounds[permission.bound](value, permission.value):
                return True
        return False
