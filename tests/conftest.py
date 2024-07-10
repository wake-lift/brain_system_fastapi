import asyncio
from random import choice, randint
from typing import AsyncGenerator, Generator, List, Tuple
from unittest import mock

from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import StaticPool

from app.core.db import get_async_session, Base
from app.core.users import current_superuser, current_user
from app.models.brain_system import BoughtInProduct, ProductLink, Unit
from app.models.questions import Question
from app.models.users import User

mock.patch(
    'fastapi_cache.decorator.cache',
    lambda *args, **kwargs: lambda f: f
).start()
# приложения должны быть импортированы после подмены декоратора кэширования
from app.main import app_api # noqa
from app.main import app_pages # noqa

DATABASE_URL_TEST: str = 'sqlite+aiosqlite:///file::memory:?cache=shared'

app_pages.user_middleware = []


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Переопределяет стандартную функцию цикла событий из pytest.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


async_engine_test = create_async_engine(
    DATABASE_URL_TEST,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

async_session_factory_test = async_sessionmaker(async_engine_test)


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает генератор асинхронных сессий, привязанных к тестовой БД.
    """
    async with async_session_factory_test() as session:
        yield session

app_api.dependency_overrides[get_async_session] = get_async_session_test
app_pages.dependency_overrides[get_async_session] = get_async_session_test


@pytest_asyncio.fixture(autouse=True, scope='session')
async def get_test_database() -> AsyncGenerator[None, None]:
    """
    Создает пустые таблицы в тестовой базе данных.
    """
    try:
        async with async_engine_test.begin() as aconn:
            await aconn.run_sync(Base.metadata.create_all)
            await aconn.execute(
                insert(User).values(gen_data_for_user_table())
            )
            await aconn.execute(
                insert(Question).values(gen_data_for_question_table())
            )
            unit_data, product_data, link_data = gen_data_for_brain_tables()
            await aconn.execute(insert(Unit).values(unit_data))
            await aconn.execute(insert(BoughtInProduct).values(product_data))
            await aconn.execute(insert(ProductLink).values(link_data))
        yield
        async with async_engine_test.begin() as aconn:
            await aconn.run_sync(Base.metadata.drop_all)
    finally:
        async with async_engine_test.begin() as aconn:
            await aconn.run_sync(Base.metadata.drop_all)


def gen_data_for_user_table() -> List[dict]:
    """
    Полготавливает тестовые данные для наполнения таблицы "User".
    """

    return [
        {'id': 1, 'username': 'regularuser',
         'email': 'regularuser@example.com',
         'hashed_password': '123456', 'is_active': True,
         'is_superuser': False, 'is_verified': True},
        {'id': 2, 'username': 'superuser',
         'email': 'superuser@example.com',
         'hashed_password': '7891011', 'is_active': True,
         'is_superuser': True, 'is_verified': True}
    ]


def gen_data_for_question_table() -> List[dict]:
    """
    Полготавливает тестовые данные для наполнения таблицы "Question".
    """
    res = []
    for i in range(1, 31):
        res.append({
            'id': i,
            'package': 'package_1' if i % 2 else 'package_2',
            'question_type': (
                'Ч' if i == 1 or i == 28 else choice(['Ч', 'Б', 'Я'])
            ),
            'question': f'Текст вопроса_{i}',
            'answer': f'Ответ на вопрос {i}',
            'is_condemned': False,
            'is_published': True,
            'user_id': 1 if i % 2 else 2
        })
    return res


def gen_data_for_brain_tables() -> Tuple[List[dict]]:
    """
    Полготавливает тестовые данные для наполнения таблиц "Unit",
    "BoughtInProduct", "ProductLink".
    """
    res_unit, res_boughtinproduct, res_productlink = [], [], []
    for i in range(1, 31):
        res_unit.append(
            {'id': i, 'name': f'Блок_{i}'}
        )
        res_boughtinproduct.append(
            {'id': i, 'name': f'Деталь_{i}', 'unit_id': randint(1, 30)}
        )
        res_productlink.append(
            {'id': i,
             'link': f'Ссылка_{i}',
             'link_short_name': f'Короткое_имя_{i}',
             'bought_in_product_id': randint(1, 30)}
        )
    return res_unit, res_boughtinproduct, res_productlink


@pytest_asyncio.fixture()
async def pages_client() -> AsyncGenerator[AsyncClient, None]:
    """Создает генератор сессий для страниц сайта."""
    async with AsyncClient(app=app_pages, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture()
async def non_authenticated_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Создает генератор анонимных сессий для API."""
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture()
async def regular_user_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Создает генератор сессий для API от имени обычного пользователя."""
    regular_user = User(
        id=1,
        username='regularuser',
        email='regularuser@example.com',
        hashed_password=123456,
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    app_api.dependency_overrides[current_user] = lambda: regular_user
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac
    app_api.dependency_overrides[current_user] = current_user


@pytest_asyncio.fixture()
async def superuser_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Создает генератор сессий для API от имени суперпользователя."""
    superuser = User(
        id=2,
        username='superuser',
        email='superuser@example.com',
        hashed_password=7891011,
        is_active=True,
        is_superuser=True,
        is_verified=True
    )
    app_api.dependency_overrides[current_superuser] = lambda: superuser
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac
    app_api.dependency_overrides[current_superuser] = current_superuser
