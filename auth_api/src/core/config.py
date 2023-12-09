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


settings = Settings(_env_file='.env')
