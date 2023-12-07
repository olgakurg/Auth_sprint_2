import uuid
from datetime import datetime
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
from fastapi import HTTPException

from src.core.config import settings
from src.models.session import SessionInDB
from src.models.token import Token
from src.models.users import UserApi
from src.models.users import UserAuth
from src.services.sessions import get_session_service, SessionService
from src.services.tokens import TokenService, get_token_service
from src.services.users import get_user_service, UserService
from .utils.settings import USER_NOT_CREATE, USER_NOT_FOUND, USER_ALREADY_EXISTS

router = APIRouter()


@AuthJWT.load_config
def get_config():
    return settings

@router.get('/')
async def get_root():
    return {'key': 'user root'}


@router.post('/signup',
             response_model=uuid.UUID,
             status_code=HTTPStatus.CREATED,
             summary='Регистрация пользователя',
             description='Регистрация пользователя',
             tags=['Пользователи']
             )
async def create_user(
        user: UserApi,
        user_service: UserService = Depends(get_user_service)):
    user_id = await user_service.create_user(user)

    if not user_id:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=USER_NOT_CREATE)
    elif user_id == 'error_unique':
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=USER_ALREADY_EXISTS)

    return user_id


@router.post('/signin',
             status_code=HTTPStatus.OK,
             summary='вход пользователя в аккаунт',
             description='возвращает пару токенов по данному user',
             tags=['Пользователи']
             )
async def login_user(
        user: UserAuth,
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service),
        session_service: SessionService = Depends(get_session_service)) -> Token | None:
    correct_password = await user_service.check_password(user)
    if not correct_password:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)
    session_id = await session_service.create_session(user, datetime.now())
    access_token, refresh_token = await token_service.get_tokens(user)
    token = Token(access=access_token, refresh=refresh_token)
    return token.model_dump()


@router.post('/refresh',
             summary=' выдаёт новую пару токенов в обмен на корректный refresh-токен',
             status_code=HTTPStatus.OK,
             description='параметры - login, password, итог  - пара токенов',
             tags=['Роли']
             )
async def refresh(Authorize: AuthJWT = Depends(),
                        token_service: TokenService = Depends(get_token_service)) -> Token | None:
    await Authorize.jwt_refresh_token_required()
    current_user = await Authorize.get_jwt_subject()
    access_token, new_refresh = await token_service.exchange_tokens(current_user)
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.NON_AUTHORITATIVE_INFORMATION, detail=USER_NOT_CREATE)
    token = Token(access=access_token, refresh=new_refresh)
    return token.model_dump()



@router.put('/update_user',
            status_code=HTTPStatus.OK,
            summary='изменение логина или пароля',
            description='изменение логина или пароля',
            tags=['Пользователи']
            )
async def edit_user(user: UserApi, Authorize: AuthJWT = Depends(),
                    user_service: UserService = Depends(get_user_service)):
    """Метод использует ручку для обновления данных пользователя по uuid.
     Валидация по типу данных на содержимое возвращает 400
       """
    await Authorize.jwt_refresh_token_required()
    user_id = await Authorize.get_jwt_subject()
    new_user = user_service.update_user(user_id, user)
    return new_user



@router.post('/signout',
             summary='выход пользователя из аккаунта',
             status_code=HTTPStatus.OK,
             description='параметры - токен',
             tags=['Пользователи']
             )
async def logout_token(Authorize: AuthJWT = Depends(),
                       token_service: TokenService = Depends(get_token_service)):
    await Authorize.jwt_required()
    jti = (await Authorize.get_raw_jwt())["jti"]
    await token_service.remove_token(jti)


@router.get('/session_history',
            response_model=list[SessionInDB],
            summary='получение пользователем своей истории входов в аккаунт',
            description='',
            tags=['Пользователи']
            )
async def get_user_sessions(user_id: str,
                            session_service: SessionService = Depends(get_session_service)):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.NON_AUTHORITATIVE_INFORMATION, detail=USER_NOT_FOUND)
    return session_service.get_sessions(user_id)