from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, id = {self.id}>'


async_engine = create_async_engine(settings.database_url, echo=True)

async_session_factory = async_sessionmaker(async_engine)


async def get_async_session():
    async with async_session_factory() as async_session:
        yield async_session
