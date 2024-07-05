import asyncio
from random import choice, randint
from typing import AsyncGenerator, Generator, List, Tuple

from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.core.db import get_async_session, Base
from app.core.users import current_superuser, current_user
from app.main import app_api
from app.models.brain_system import BoughtInProduct, ProductLink, Unit
from app.models.questions import Question
from app.models.users import User

DATABASE_URL_TEST: str = 'sqlite+aiosqlite:///db_test.sqlite'


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
    poolclass=NullPool,
)

async_session_factory_test = async_sessionmaker(async_engine_test)


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает генератор асинхронных сессий, привязанных к тестовой БД.
    """
    async with async_session_factory_test() as session:
        yield session

app_api.dependency_overrides[get_async_session] = get_async_session_test


@pytest_asyncio.fixture(autouse=True, scope='session')
async def get_test_database() -> AsyncGenerator[None, None]:
    """
    Создает пустые таблицы в тестовой базе данных.
    """
    async with async_engine_test.begin() as aconn:
        await aconn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine_test.begin() as aconn:
        await aconn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def fill_user_table(get_test_database) -> None:
    """
    Наполняет таблицу "User" тестовыми данными.
    """
    async with async_engine_test.begin() as aconn:
        await aconn.execute(
            insert(User).values([
                {'id': 1, 'username': 'regularuser',
                 'email': 'regularuser@example.com',
                 'hashed_password': '123456', 'is_active': 1,
                 'is_superuser': 0, 'is_verified': 1},
                {'id': 2, 'username': 'superuser',
                 'email': 'superuser@example.com',
                 'hashed_password': '7891011', 'is_active': 1,
                 'is_superuser': 1, 'is_verified': 1}
            ])
        )


@pytest_asyncio.fixture()
async def fill_question_table(get_test_database, fill_user_table) -> None:
    """
    Наполняет таблицу "Question" тестовыми данными.
    """
    async with async_engine_test.begin() as aconn:
        await aconn.execute(
            insert(Question).values(gen_data_for_questions_table())
        )


@pytest_asyncio.fixture()
async def fill_brain_system_tables(get_test_database) -> None:
    """
    Наполняет таблицы "Unit", "BoughtInProduct",
    "ProductLink" тестовыми данными.
    """
    unit_data, product_data, link_data = gen_data_for_brain_system_tables()
    stmt_unit = insert(Unit).values(unit_data)
    stmt_product = insert(BoughtInProduct).values(product_data)
    stmt_link = insert(ProductLink).values(link_data)
    async with async_engine_test.begin() as aconn:
        await aconn.execute(stmt_unit)
        await aconn.execute(stmt_product)
        await aconn.execute(stmt_link)


def gen_data_for_questions_table() -> List[dict]:
    """
    Полготавливает тестовые данные для наполнения таблицы "Question".
    """
    res = []
    for i in range(1, 31):
        res.append({
            'id': i,
            'package': 'package_1' if i % 2 else 'package_2',
            'question_type': choice(['Ч', 'Б', 'Я']),
            'question': f'Текст вопроса_{i}',
            'answer': f'Ответ на вопрос {i}',
            'user_id': 1 if i % 2 else 2
        })
    return res


def gen_data_for_brain_system_tables() -> Tuple[List[dict]]:
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
             'link_short_name': f'Короткое имя_{i}',
             'bought_in_product_id': randint(1, 30)}
        )
    return res_unit, res_boughtinproduct, res_productlink


@pytest_asyncio.fixture(scope='session')
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
        is_active=1,
        is_superuser=0,
        is_verified=1
    )
    app_api.dependency_overrides[current_user] = lambda: regular_user
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture()
async def superuser_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Создает генератор сессий для API от имени суперпользователя."""
    superuser = User(
        id=2,
        username='superuser',
        email='superuser@example.com',
        hashed_password=7891011,
        is_active=1,
        is_superuser=1,
        is_verified=1
    )
    app_api.dependency_overrides[current_superuser] = lambda: superuser
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac
