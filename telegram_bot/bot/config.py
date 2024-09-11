from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    telegram_token: SecretStr
    database_type: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_db_host: str
    postgres_db_port: str
    postgres_db: str
    sqlite_db_path: str


settings = Settings()
