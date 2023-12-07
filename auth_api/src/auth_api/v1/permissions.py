import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.helpers.auth import roles_required
from src.models.roles import PermissionApi
from src.services.roles import get_role_service, RoleService
from .utils.settings import PERMISSION_NOT_CREATE, PERMISSION_NOT_FOUND

router = APIRouter()


@router.post('/',
             status_code=HTTPStatus.CREATED,
             summary='Создание прав',
             description='Создает права по параметрам name',
             tags=['Права']
             )
@roles_required(roles_list=['superuser'])
async def create_permission(
        permission: PermissionApi,
        role_service: RoleService = Depends(get_role_service)
):
    permission_id = await role_service.create_permission(permission)

    if not permission_id:
        return HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=PERMISSION_NOT_CREATE)
    return permission_id


@router.get('/{permission_id}',
             response_model=PermissionApi,
             status_code=HTTPStatus.OK,
             summary='Получение прав',
             description='Получить права по uuid',
             tags=['Права']
             )
@roles_required(roles_list=['superuser'])
async def get_permission(
        permission_id: uuid.UUID,
        role_service: RoleService = Depends(get_role_service)
) -> PermissionApi:
    permission = await role_service.get_permission(permission_id)

    if not permission:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERMISSION_NOT_FOUND)
    return permission


