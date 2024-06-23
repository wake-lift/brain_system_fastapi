from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import asyncio as aioredis
from slowapi import Limiter
from slowapi.util import get_remote_address


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_api_title: str = 'BrainAPI'
    app_api_description: str = ('Сервис для работы с базой вопросов '
                                'для интеллектуальных игр.')
    app_pages_title: str = 'Brain System'
    app_pages_description: str = ('Страницы сайта, посвященного'
                                  'созданию брейн-системы.')
    static_dir: str = 'app/static'
    templates_dir: str = 'app/templates'
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_db_host: str
    postgres_db_port: str
    sqlite_database_url: str
    auth_token_secret: str
    session_middleware_secret_key: str
    csrf_middleware_secret_key: str
    redis_host: str
    redis_port: str
    redis_password: str


settings = Settings()

templates = Jinja2Templates(directory=settings.templates_dir)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url((
        f'redis://:{settings.redis_password}@{settings.redis_host}'
        f':{settings.redis_port}'
    ))
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    yield
