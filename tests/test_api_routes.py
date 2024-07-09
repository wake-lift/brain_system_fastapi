import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_question_allowed_for_auth_user_only(
    non_authenticated_api_client: AsyncClient
) -> None:
    """
    Тест недоступности энедпойнта для неавторизованного пользователя.
    """
    url = '/questions/add'
    msg = (f'Обращение к эндпойнту "{url}" от анонимного пользователя'
           ' не возвращает статус 401.')
    response = await non_authenticated_api_client.post(url)
    assert response.status_code == 401, msg


@pytest.mark.asyncio
async def test_update_delete_question_allowed_for_auth_user_only(
    non_authenticated_api_client: AsyncClient
) -> None:
    """
    Тест недоступности энедпойнта для неавторизованного пользователя.
    """
    url = '/questions/1'
    msg = (f'Обращение к эндпойнту "{url}" от анонимного пользователя'
           ' не возвращает статус 401.')
    response_patch = await non_authenticated_api_client.patch(url)
    response_delete = await non_authenticated_api_client.delete(url)
    assert response_patch.status_code == 401, msg
    assert response_delete.status_code == 401, msg


@pytest.mark.asyncio
async def test_users_questions_allowed_for_auth_only(
    non_authenticated_api_client: AsyncClient
) -> None:
    """
    Тест недоступности энедпойнта для неавторизованного пользователя.
    """
    url = '/users/questions'
    msg = (f'Обращение к эндпойнту "{url}" от анонимного пользователя'
           ' не возвращает статус 401.')
    response = await non_authenticated_api_client.patch('/users/questions')
    assert response.status_code == 401, msg


@pytest.mark.asyncio
async def test_edit_question_status_allowed_for_superuser_only(
    regular_user_api_client: AsyncClient,
    non_authenticated_api_client: AsyncClient
) -> None:
    """
    Тест недоступности энедпойнта для любого пользователя
    кроме авминистратора.
    """
    url = '/questions/1/status'
    msg = (f'Обращение к эндпойнту "{url}" от пользователя, не являющегося'
           ' администратором, не возвращает статус 401.')
    response_anon_user = await non_authenticated_api_client.patch(url)
    response_regular_user = await regular_user_api_client.patch(url)
    assert response_anon_user.status_code == 401, msg
    assert response_regular_user.status_code == 401, msg
