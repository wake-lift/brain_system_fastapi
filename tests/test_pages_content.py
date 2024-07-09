import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bought_in_products_page(pages_client: AsyncClient) -> None:
    """Тест наполнения информацией страницы покупных деталей."""
    url = '/brain_system/bought-in-products/'
    response = await pages_client.get(url)
    response_html = response.content.decode()
    msg = (f'В таблицу на странице покупных деталей ("{url}") не передаются '
           'данные из БД')
    assert 'Деталь_1' in response_html, msg
    assert 'Блок_1' in response_html, msg
    assert 'Ссылка_1' in response_html, msg
    assert 'Короткое_имя_1' in response_html, msg


@pytest.mark.asyncio
async def test_form_exists_on_feedback_page(pages_client: AsyncClient) -> None:
    """Тест наличия форм на странице обратной связи."""
    url = '/feedback/'
    response = await pages_client.get(url)
    response_html = response.content.decode()
    msg = f'на странице "{url}" не отображается форма.'
    assert 'id="name"' in response_html, msg
    assert 'id="email"' in response_html, msg
    assert 'id="feedback_text"' in response_html, msg
    assert 'id="submit"' in response_html, msg


@pytest.mark.asyncio
async def test_form_exists_on_random_questions_page(
    pages_client: AsyncClient
) -> None:
    """Тест наличия форм на странице получения случайных вопросов."""
    url = '/questions/random-qustions/'
    response = await pages_client.get(url)
    response_html = response.content.decode()
    msg = f'на странице "{url}" не отображается форма.'
    assert 'id="question_type"' in response_html, msg
    assert 'id="search_pattern"' in response_html, msg
    assert 'id="questions_quantity"' in response_html, msg
    assert 'id="submit"' in response_html, msg


@pytest.mark.asyncio
async def test_form_exists_on_random_package_page(
    pages_client: AsyncClient
) -> None:
    """Тест наличия форм на странице получения случайного пакета."""
    url = '/questions/random-package/'
    response = await pages_client.get(url)
    response_html = response.content.decode()
    msg = f'на странице "{url}" не отображается форма.'
    assert 'id="question_type"' in response_html, msg
    assert 'id="submit"' in response_html, msg
