from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')
    db_user: str
    db_password: str
    db_name: str

    db_host: str
    db_port: str

    app_host: str = 'test_api'
    app_port: str = '8000'

    redis_host: str = 'test_redis'
    redis_port: str = '6379'
    api_version: str = '/auth_api/v1'


test_settings = TestSettings(_env_file='.env')
