import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.helpers.auth import roles_required
from src.models.roles import RoleShort
from src.models.users import UserRolesApi, UserInDB
from src.services.user_roles import get_user_roles_service, UserRolesService
from .utils.settings import USER_NOT_FOUND

router = APIRouter()


class Permission(BaseModel):
    id: str
    name: str

class Role(BaseModel):
    id: str
    name: str
    description: str | None
    permissions: list[Permission]




@router.put('/',
            status_code=HTTPStatus.OK,
            summary='назначить пользователю роль;',
            description='назначает роль по id роли и пользователя',
            tags=['Управление доступом']
            )
@roles_required(roles_list=['superuser'])
async def put_user_roles(
        user: UserRolesApi,
        user_roles_service: UserRolesService = Depends(get_user_roles_service)):
    user = await user_roles_service.add_user_roles(user)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)




@router.delete('/',
               status_code=HTTPStatus.OK,
               summary='отобрать у пользователя роль',
               description='Удаляет роль у пользователя по id роли и пользователя',
               response_description='статусы http',
               tags=['Управление доступом']
               )
@roles_required(roles_list=['superuser'])
async def delete_user_role(
        user: UserRolesApi,
        user_roles_service: UserRolesService = Depends(get_user_roles_service)):
    """Метод использует ручку для выполнения операции по удалению роли в БД.
    Обязательные параметры - id пользователя, id роли.
    Возвращает HTTP 200 OК или 404.
    Волидация по uuid возвращает UUIDError.
     """
    user = await user_roles_service.delete_user_roles(user)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)

@router.get('/{user_id}',
            status_code=HTTPStatus.OK,
            response_model=list[RoleShort],
            summary='метод для проверки наличия прав у пользователя.',
            description='Возвращает список всех доступных ролей по id пользователя',
            response_description='...',
            tags=['Управление доступом']
            )
@roles_required(roles_list=['superuser'])
async def get_user_roles(
        user_id: uuid.UUID,
        user_roles_service: UserRolesService = Depends(get_user_roles_service)) -> list[RoleShort]:
    """Метод использует ручку для возврата 200 или 404. если роли нет.     """
    user, roles = await user_roles_service.get_user_roles(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)

    return roles


@router.get('/',
            status_code=HTTPStatus.OK,
            response_model=list[UserInDB],
            summary='Получить все роли',
            description='Возвращает список всех пользователей и ролей.',
            response_description='...',
            tags=['Управление доступом']
            )

async def get_user_list(user_roles_service: UserRolesService = Depends(get_user_roles_service)):

    """Метод использует ручку для возвращения списка пользователей с ролями
    \\ Обработки ошибок и валидации данных нет. Сортировки, пагинации нет.
     """
    users = await user_roles_service.get_users_roles()

    return users
