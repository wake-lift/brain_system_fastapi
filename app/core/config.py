from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()

templates = Jinja2Templates(directory=settings.templates_dir)
