import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_question_allowed_for_auth_user_only(
    non_authenticated_api_client: AsyncClient
):
    response = await non_authenticated_api_client.post('/questions/add')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_delete_question_allowed_for_auth_user_only(
    non_authenticated_api_client: AsyncClient
):
    response_patch = await non_authenticated_api_client.patch('/questions/1')
    response_delete = await non_authenticated_api_client.delete('/questions/1')
    assert response_patch.status_code == 401
    assert response_delete.status_code == 401


@pytest.mark.asyncio
async def test_users_questions_allowed_for_auth_only(
    non_authenticated_api_client: AsyncClient
):
    response = await non_authenticated_api_client.patch('/users/questions')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_edit_question_status_allowed_for_superuser_only(
    regular_user_api_client: AsyncClient,
    non_authenticated_api_client: AsyncClient
):
    response_anon_user = await non_authenticated_api_client.patch(
        '/questions/1/status'
    )
    response_regular_user = await regular_user_api_client.patch(
        '/questions/1/status'
    )
    assert response_anon_user.status_code == 401
    assert response_regular_user.status_code == 401
