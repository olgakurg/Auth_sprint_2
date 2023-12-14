from functools import wraps

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.users import UserInDB
from src.services.users import UserService


class AuthRequest(Request):
    custom_user: UserInDB


def roles_required(roles_list: list[str]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: UserInDB = kwargs.get('request').custom_user
            if not user or user.role not in [x.value for x in roles_list]:
                return status.HTTP_403_FORBIDDEN
            return await function(*args, **kwargs)
        return wrapper
    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
            self, request: Request,
            db: AsyncSession = Depends(get_session)) -> UserInDB | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        user_id = await authorize.get_jwt_subject()
        if not user_id:
            return None
        user_service = UserService(db)
        user = user_service.get_user(user_id)
        return UserInDB.from_orm(user)


async def get_current_user_global(request: AuthRequest, user: AsyncSession = Depends(JWTBearer())):
    request.custom_user = user
