from httpx import AsyncClient
import pytest
from sqlalchemy import delete, func, insert, or_, select

from app.models.questions import Question
from tests.conftest import async_session_factory_test


@pytest.mark.asyncio
async def test_random_package(
    non_authenticated_api_client: AsyncClient
) -> None:
    """Тестирование логики генерации случайного пакета вопросов."""
    url = '/questions/random-package'
    response = await non_authenticated_api_client.post(url, json={})
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    msg = (f'Запрос на генерацию случайного пакета ("{url}") возвращает'
           'оличество записей, отличное от ожидаемого.')
    assert len(response.json()) == 15, msg
    packagename_set = {_['package'] for _ in response.json()}
    msg = (f'Запрос на генерацию случайного пакета ("{url}") возвращает'
           'записи, относящиеся к разным пакетам.')
    assert len(packagename_set) == 1, msg


@pytest.mark.asyncio
async def test_random_questions(
    non_authenticated_api_client: AsyncClient
) -> None:
    """Тестирование логики генерации случайного набора вопросов."""
    url = '/questions/random-questions'
    response = await non_authenticated_api_client.post(
        url,
        params={'quantity': 15},
        json={}
    )
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    msg = (f'Обращение к эндпойнту "{url}" возвращает количество вопросов, '
           'отличающееся от значения, переданного в параметрах запроса.')
    assert len(response.json()) == 15, msg
    response = await non_authenticated_api_client.post(
        url,
        params={'question_type': 'Что-где-когда'},
        json={}
    )
    msg = (f'Обращение к эндпойнту "{url}" возвращает тип вопроса, '
           'отличающееся от типа, переданного в параметрах запроса.')
    assert response.json()[0]['question_type'] == 'Что-где-когда', msg


@pytest.mark.asyncio
async def test_questions_search(
    non_authenticated_api_client: AsyncClient
) -> None:
    """Тестирование поиска по текста вопроса."""
    url = '/questions/search'
    response = await non_authenticated_api_client.post(
        url,
        params={'search_pattern': 'вопроса_11', 'quantity': 5},
        json={}
    )
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    msg = (f'Обращение к эндпойнту "{url}" возвращает количество найденных '
           'вопросов, отличающееся от ожидаемого.')
    assert len(response.json()) == 1, msg


@pytest.mark.asyncio
async def test_question_add(regular_user_api_client: AsyncClient) -> None:
    """Тестирование добавления вопроса в БД."""
    url = '/questions/add'
    request_body = {
        "question_type": "Что-где-когда",
        "question": "Текст вопроса (не менее 30-ти символов).",
        "answer": "Ответ на вопрос",
    }
    response = await regular_user_api_client.post(url, json=request_body)
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    async with async_session_factory_test() as session:
        questions_count = await session.scalar(
            select(func.count()).select_from(Question)
        )
        added_item = await session.scalar(
            select(Question).order_by(Question.id.desc())
        )
    msg = (f'Добавление нового вопроса (эндпойнт "{url}") не увеличивает'
           ' количество вопросов в БД.')
    assert questions_count == 31, msg
    msg = (f'Добавленный вопрос (эндпойнт "{url}") не устанавливает'
           'правильную связь с моделью "User" (поле user_id).')
    assert added_item.user_id == 1, msg
    msg = (f'Добавленный вопрос (эндпойнт "{url}") должен'
           'иметь статус "не опубликован" (поле is_published).')
    assert added_item.is_published is False
    async with async_session_factory_test() as session:
        await session.execute(
            delete(Question).filter(Question.id == 31)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_question_get(non_authenticated_api_client: AsyncClient) -> None:
    """Тестирование выдачи отдельного вопроса."""
    url = '/questions/10'
    response = await non_authenticated_api_client.get(url)
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    msg = (f'Попытка получения отдельного вопроса ("{url}") возвращает '
           'неожиданный id вопроса.')
    assert response.json()['id'] == 10, msg


@pytest.mark.asyncio
async def test_question_edit(regular_user_api_client: AsyncClient) -> None:
    """Тестирование выдачи отдельного вопроса."""
    url = '/questions/5'
    request_body = {
        "answer": "Ответ на вопрос (измененный)",
    }
    response = await regular_user_api_client.patch(url, json=request_body)
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    async with async_session_factory_test() as session:
        modified_question = await session.scalar(
            select(Question).filter(Question.id == 5)
        )
    msg = (f'Изменение вопроса ("{url}") не приводит к изменению '
           'информации в БД.')
    assert modified_question.answer == 'Ответ на вопрос (измененный)', msg
    url = '/questions/6'
    response = await regular_user_api_client.patch(url, json=request_body)
    msg = (f'Попытка откорректировать запись ("{url}") пользователем, не '
           'являющимся автором этой записи, должна быть запрещена.')
    assert response.status_code == 403, msg


@pytest.mark.asyncio
async def test_question_delete(regular_user_api_client: AsyncClient) -> None:
    """Тестирование удаления вопроса."""
    async with async_session_factory_test() as session:
        await session.execute(
            insert(Question).values({
                'id': 31,
                'package': 'package_1',
                'question_type': 'Ч',
                'question': 'Текст вопроса_31',
                'answer': 'Ответ на вопрос 31',
                'is_condemned': False,
                'is_published': True,
                'user_id': 1,
            })
        )
        await session.commit()
    url = '/questions/31'
    response = await regular_user_api_client.delete(url)
    msg = (f'Обращение автора записи к эндпойнту "{url}" возвращает статус, '
           'отличный от 200.')
    assert response.status_code == 200, msg
    async with async_session_factory_test() as session:
        questions_count = await session.scalar(
            select(func.count()).select_from(Question)
        )
    msg = 'Удаление записи не приводит к уменьшению количества записей в БД.'
    assert questions_count == 30, msg


@pytest.mark.asyncio
async def test_question_status_edit(superuser_api_client: AsyncClient) -> None:
    """Тестирование редактирования статуса вопроса."""
    url = '/questions/30/status'
    request_body = {
        "is_condemned": True,
        "is_published": False
    }
    response = await superuser_api_client.patch(url, json=request_body)
    msg = (f'Обращение администратора к эндпойнту "{url}" возвращает статус, '
           'отличный от 200.')
    assert response.status_code == 200, msg
    async with async_session_factory_test() as session:
        question_statuses = await session.scalar(
            select(Question)
            .filter(Question.id == 30)
        )
    msg = ('Редактирование статуса вопроса не приводит к изменеию полей'
           '"is_condemned" или "is_published" в БД.')
    assert question_statuses.is_condemned is True, msg
    assert question_statuses.is_published is False, msg


@pytest.mark.asyncio
async def test_users_questions(regular_user_api_client: AsyncClient) -> None:
    """
    Тестирование выдачи всех записей, принадлежащих пользователю,
    отправившему запрос.
    """
    url = '/users/questions'
    response = await regular_user_api_client.get(url)
    msg = f'Обращение к эндпойнту "{url}" возвращает статус, отличный от 200.'
    assert response.status_code == 200, msg
    msg = ('Количество записей, автором которых является текущий пользователь,'
           f' не соответствует ожидаемому ("{url}")')
    assert len(response.json()) == 15, msg
    question_id_set = {_['id'] for _ in response.json()}
    async with async_session_factory_test() as session:
        users_questions = await session.scalars(
            select(Question)
            .filter(or_(Question.id == _ for _ in question_id_set)))
    user_id_set = {_.user_id for _ in users_questions}
    msg = (f'Выборка вопросов, получаемая при запросе к эндпойнту "{url}", '
           'должна содержать только записи, автором которых является '
           'текущий пользователь')
    assert user_id_set == {1}, msg
