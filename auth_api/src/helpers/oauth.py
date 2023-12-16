import httpx
from functools import lru_cache
from fastapi import HTTPException, Depends
from src.core.config import settings
from src.models.token import YaToken, YaUser
from src.services.users import UserService, get_user_service
from src.core.config import settings


@lru_cache()
def get_oauth_service(code):
    return YaOauthService(code)


class OAuthService:
    def __init__(self, code, provider):
        self.code = code
        self.provider = provider
        provider_settings = settings.oauth_provider[provider]
        self.url_token = provider_settings['access_token_url']
        self.data_token = {
            'grant_type': 'authorization_code',
            'code': self.code,
            'client_id': provider_settings['client_id'],
            'client_secret': provider_settings["client_secret"],
        }
        self.url_login = provider_settings['url_login']
        self.url_auth = provider_settings['url_auth']

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
        social_user = YaUser.parse_raw(response['body'])
        await user_service.create_user(login=social_user.login, password=self.code)
        return social_user.login

    async def ya_auth(self):
        async with httpx.AsyncClient() as client:
            return await client.get(self.url_auth, data=settings.yandex_client_id)
