import httpx
from functools import lru_cache
from fastapi import HTTPException, Depends
from src.core.config import settings
from src.models.token import YaToken, YaUser
from src.services.users import UserService, get_user_service


@lru_cache()
def get_ya_oauth_service(code):
    return YaOauthService(code)


class YaOAuthService:
    def __init__(self, code):
        self.code = code
        self.url_token = 'https://oauth.yandex.ru/token'
        self.data_token = {
            'grant_type': 'authorization_code',
            'code': self.code,
            'client_id': settings.yandex_client_id,
            'client_secret': settings.yandex_client_secret,
        }
        self.url_login = "https://login.yandex.ru/info?format=json"
        self.url_auth = "https://oauth.yandex.ru/authorize?response_type=code"

    async def exchange_code(self, user_service: UserService = Depends(get_user_service)):
        if len(str(self.code)) != 7:
            raise HTTPException(status_code=403, detail="Invalid code")
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url_token, data=self.data_token)
        if response.status_code != 200:
            raise HTTPException(status_code=403, detail="Failed to get token")
        ya_token = YaToken.parse_raw(response.content)
        if not ya_token:
            raise HTTPException(status_code=404,
                                detail="This site doesnt allow you to connect to the specified social networks")

        headers = {
            "Authorization": f"OAuth {ya_token.access_token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url_login, headers=headers)
        ya_user = YaUser.parse_raw(response['body'])
        await user_service.create_user(login=ya_user.login, password=self.code)
        return ya_user.login

    async def ya_auth(self):
        async with httpx.AsyncClient() as client:
            return await client.get(self.url_auth, data=settings.yandex_client_id)
