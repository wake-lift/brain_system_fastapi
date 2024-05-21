from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_title: str = 'BrainAPI'
    app_description: str = ('Сервис для работы с базой вопросов '
                            'для интеллектуальных игр.')
    database_url: str
    auth_token_secret: str


settings = Settings()
