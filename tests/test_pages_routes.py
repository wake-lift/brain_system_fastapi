import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    'url', (
        '/',
        '/legal/',
        '/feedback/',
    )
)
@pytest.mark.asyncio
async def test_common_pages_availability(
    pages_client: AsyncClient, url: str
) -> None:
    """Тест доступности общих страниц."""
    msg = f'Обращение к эндпойнту "{url}" не возвращает статус 200.'
    response = await pages_client.get(url)
    assert response.status_code == 200, msg


@pytest.mark.parametrize(
    'url', (
        '/brain_system/operating-principle/',
        '/brain_system/electric-schematics/',
        '/brain_system/pcb/',
        '/brain_system/printed-parts/',
        '/brain_system/bought-in-products/',
        '/brain_system/firmware/',
        '/brain_system/export-model-to-ods/',
    )
)
@pytest.mark.asyncio
async def test_brain_system_pages_availability(
    pages_client: AsyncClient, url: str
) -> None:
    """Тест доступности страниц, посвященных брейн-системе."""
    msg = f'Обращение к эндпойнту "{url}" не возвращает статус 200.'
    response = await pages_client.get(url)
    assert response.status_code == 200, msg


@pytest.mark.parametrize(
    'url', (
        '/questions/random-qustions/',
        '/questions/random-package/',
        '/questions/telegram-bot/',
        '/questions/api/',
    )
)
@pytest.mark.asyncio
async def test_questions_pages_availability(
    pages_client: AsyncClient, url: str
) -> None:
    """Тест доступности страниц, посвященных вопросам."""
    msg = f'Обращение к эндпойнту "{url}" не возвращает статус 200.'
    response = await pages_client.get(url)
    assert response.status_code == 200, msg
