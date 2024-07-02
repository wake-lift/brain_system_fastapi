from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, id = {self.id}>'


if settings.database_type == 'sqlite':
    sync_engine = create_engine(settings.sync_sqlite_url, echo=True)
    async_engine = create_async_engine(settings.async_sqlite_url, echo=True)
if settings.database_type == 'postgres':
    postgres_url_tail = (
        f'://{settings.postgres_user}:'
        f'{settings.postgres_password}@{settings.postgres_db_host}:'
        f'{settings.postgres_db_port}/{settings.postgres_db}'
    )

    sync_engine = create_engine(
        'postgresql+psycopg2' + postgres_url_tail, echo=True
    )
    async_engine = create_async_engine(
        'postgresql+asyncpg' + postgres_url_tail, echo=True
    )

sync_session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)


async def get_async_session():
    async with async_session_factory() as async_session:
        yield async_session
