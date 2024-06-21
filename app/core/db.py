import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings

load_dotenv('.env')


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, id = {self.id}>'


if os.environ['DATABASE_TYPE'] == 'sqlite':
    async_engine = create_async_engine(settings.sqlite_database_url, echo=True)
if os.environ['DATABASE_TYPE'] == 'postgres':
    postgres_database_url = (
        f'postgresql+asyncpg://{settings.postgres_user}:'
        f'{settings.postgres_password}@{settings.postgres_db_host}:'
        f'{settings.postgres_db_port}/{settings.postgres_db}'
    )
    async_engine = create_async_engine(postgres_database_url, echo=True)

async_session_factory = async_sessionmaker(async_engine)


async def get_async_session():
    async with async_session_factory() as async_session:
        yield async_session
