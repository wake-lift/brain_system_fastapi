from httpx import AsyncClient
import pytest


# @pytest.mark.asyncio
# async def test_get_random_package(non_authenticated_client: AsyncClient, fill_question_table):
#     response = await non_authenticated_client.post('/questions/random-package', json={})
#     assert response.status_code == 200
#     assert len(response.json()) == 15


# @pytest.mark.asyncio
# async def test_add_question(regular_user_client: AsyncClient, fill_question_table):
#     request_body = {
#         "question_type": "Что-где-когда",
#         "question": "Текст вопроса (не менее 30-ти символов). Обязательное поле",
#         "answer": "Ответ на вопрос. Обязательное поле"
# }
#     response = await regular_user_client.post('/questions/add', json=request_body)
#     assert response.status_code == 200

