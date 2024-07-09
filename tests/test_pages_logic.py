import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.models.feedback import Feedback
from tests.conftest import async_session_factory_test


@pytest.mark.asyncio
async def test_export_model_to_ods(pages_client: AsyncClient) -> None:
    """
    Тест генерации файла со списком деталей.
    """
    url = '/brain_system/export-model-to-ods/'
    response = await pages_client.get(url)
    msg = f'В ответ на запрос к адресу {url} не был возвращен файл.'
    assert response.content is not None, msg


@pytest.mark.asyncio
async def test_feedback(pages_client: AsyncClient) -> None:
    """Тест отправки фидбека в БД."""
    url = '/feedback/'
    form_data = {
        'name': 'test_user_name',
        'email': 'testuser@example.com',
        'feedback_text': 'test_user_feedback_text'
    }
    response = await pages_client.post(url, data=form_data)
    msg = f'POST-запрос по адресу "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    async with async_session_factory_test() as session:
        feedback_count = await session.scalar(
            select(func.count()).select_from(Feedback)
        )
    msg = 'Добавление нового фидбека не увеличивает количество записей в БД.'
    assert feedback_count == 1, msg


@pytest.mark.asyncio
async def test_getting_random_questions(pages_client: AsyncClient) -> None:
    """Тест выдачи случайных вопросов."""
    url = '/questions/random-qustions/'
    form_data = {
        'questions_quantity': 5
    }
    response = await pages_client.post(url, data=form_data)
    msg = f'POST-запрос по адресу "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    response_html = response.content.decode()
    msg = (f'Запрос на выдачу случайных вопросов ("{url}") возвращает '
           'неожиданное количество вопросов.')
    assert response_html.count('Текст вопроса_') == 5, msg
    form_data = {
        'search_pattern': 'Текст_вопроса_28'
    }
    response = await pages_client.post(url, data=form_data)
    response_html = response.content.decode()
    msg = (f'Запрос на поиск вопроса по тексту ("{url}") не возвращает '
           'ожидаемое количество вопросов.')
    assert response_html.count('Текст вопроса_') == 1, msg


@pytest.mark.asyncio
async def test_getting_random_package(pages_client: AsyncClient) -> None:
    """Тест выдачи случайного пакета."""
    url = '/questions/random-package/'
    response = await pages_client.post(url)
    msg = f'POST-запрос по адресу "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    response_html = response.content.decode()
    msg = (f'Запрос на выдачу случайного пакета вопросов ("{url}") не '
           'возвращает вопросов.')
    assert response_html.count('Текст вопроса_') != 0, msg
