from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')
    api_version: str
    project_name: str
    redis_host: str
    redis_port: int
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str
    hash_type: str
    hash_iteration: int
    hash_len: int
    authjwt_secret_key: str = "secret"
    db_echo: bool = False
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831
    enable_tracer: bool = True
    show_traces_console: bool = True
    oauth_providers = {'yandex':
        {
            "client_id": "4e111d99484e4ca39bf3867b50c32d3c",
            "client_secret": "d65035f255d34fe481f0428b6ec14a3b",
            "url_auth": "https://oauth.yandex.ru/authorize?response_type=code",
            "api_base_url": "https://oauth.yandex.ru",
            "access_token_url": "https://oauth.yandex.ru/token",
            "userinfo_endpoint": "https://login.yandex.ru/info",
            "url_login": "https://login.yandex.ru/info?format=json",
        }
    }


settings = Settings(_env_file='.env')
