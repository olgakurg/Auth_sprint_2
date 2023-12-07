import uuid
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.helpers.auth import roles_required
from src.models.roles import RoleApi, RoleInDB, RoleShort
from src.services.roles import get_role_service, RoleService
from .utils.settings import ROLE_NOT_CREATE, ROLE_NOT_FOUND

router = APIRouter()


@router.post('/',
             status_code=HTTPStatus.CREATED,
             summary='Создание роли',
             description='Создает роль по параметрам name, description, permissions',
             tags=['Роли']
             )
@roles_required(roles_list=['superuser'])
async def create_role(
        role: RoleApi,
        role_service: RoleService = Depends(get_role_service)
):

    role_id = await role_service.create_role(role)

    if not role_id:
        return HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=ROLE_NOT_CREATE)
    return role_id


@router.put('/{role_id}',
            status_code=HTTPStatus.OK,
            summary='Редактирование роли',
            description='доступные для редактирование поля роли - название, описаниеб разрешения',
            tags=['Роли']
            )
@roles_required(roles_list=['superuser'])
async def update_role(
        role_id: UUID,
        role: RoleApi,
        role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.update_role(role_id, role)

    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ROLE_NOT_FOUND)


@router.get('/{role_id}',
            response_model=RoleInDB,
            summary='Чтение роли',
            description='выводит описание роли по id',
            response_description='id, название, описание, разрешения',
            tags=['Роли']
            )
@roles_required(roles_list=['superuser'])
async def get_role(
        role_id: uuid.UUID,
        role_service: RoleService = Depends(get_role_service)
) -> RoleInDB:
    role = await role_service.get_role(role_id)

    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ROLE_NOT_FOUND)
    return role


@router.delete('/{role_id}',
               status_code=HTTPStatus.OK,
               summary='Удаление роли',
               description='Удаляет роль по id',
               response_description='статус http',
               tags=['Роли']
               )
async def delete_role(
        role_id: uuid.UUID,
        role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.delete_role(role_id)

    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ROLE_NOT_FOUND)


@router.get('/',
            status_code=HTTPStatus.OK,
            response_model=list[RoleShort],
            summary='Получить все роли',
            description='Возвращает список всех доступных ролей',
            response_description='Возвращает список всех доступных ролей',
            tags=['Роли']
            )
@roles_required(roles_list=['superuser'])
async def get_role_list(role_service: RoleService = Depends(get_role_service)):
    roles = await role_service.get_roles()

    return roles
