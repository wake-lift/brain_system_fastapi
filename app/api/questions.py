from random import choices

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_cache.decorator import cache
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import false, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import check_superuser_or_user_who_added
import app.core.constants as const
from app.core.db import get_async_session
from app.core.config import limiter
from app.core.users import current_superuser, current_user
from app.crud.questions_api import (create_question, edit_question,
                                    get_initial_query, get_question_or_404,
                                    get_random_package,
                                    get_valid_question_or_404)
from app.models.questions import Question, QuestionType
from app.models.users import User
from app.schemas.questions import (QuestionCreate, QuestionDB,
                                   QuestionDBWithStatus, QuestionStatusUpdate,
                                   QuestionUpdate)

router = APIRouter(
    prefix='/questions',
    tags=['База вопросов',]
)


@router.get(
    '/random-package',
    response_model=list[QuestionDB],
    response_model_exclude_none=True,
    summary='Получить случайный пакет.'
)
@limiter.limit(const.GENERATE_QUESTIONS_THROTTLING_RATE)
async def get_random_package_set(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить случайный турнирный пакет вопросов."""
    return await get_random_package(session)


@router.get(
    '/random-question',
    response_model=list[QuestionDB],
    response_model_exclude_none=True,
    summary='Получить случайные вопросы.'
)
@limiter.limit(const.GENERATE_QUESTIONS_THROTTLING_RATE)
async def get_random_questions_set(
    *,
    request: Request,
    quantity: int = Query(
        default=1,
        ge=1,
        le=const.MAX_QUESTIONS_QUANTITY,
        description='Количество случайнах вопросов'
    ),
    question_type: QuestionType | SkipJsonSchema[None] = Query(
        default=None,
        description=('Тип вопросов. Если оставить поле пустым - '
                     'будут выбраны вопросы случайных категорий.')
    ),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить случайный набор вопросов.
    Можно указать количество вопросов в выдаче, а также тип вопросов.
    """
    if question_type:
        question_type = question_type.name
    query = await get_initial_query(session, question_type)
    questions = await session.execute(query)
    questions = questions.scalars().all()
    choices_quantity = min(quantity, len(questions))
    questions = choices(questions, k=choices_quantity)
    return questions


@router.get(
    '/search',
    response_model=list[QuestionDB],
    response_model_exclude_none=True,
    summary='Поиск вопросов.'
)
@limiter.limit(const.GENERATE_QUESTIONS_THROTTLING_RATE)
async def search_questions(
    request: Request,
    search_pattern: str = Query(
        ...,
        min_length=const.MIN_SEARCH_PATTERN_LENGTH
    ),
    quantity: int = Query(
        default=const.DEFAULT_QUESTIONS_QUANTITY,
        ge=1,
        le=const.MAX_QUESTIONS_QUANTITY,
        description='Количество вопросов в выдаче.'),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Поиск по тексту вопроса. Регистр имеет значение.
    Можно указать количество вопросов в выдаче.
    """
    questions = await session.execute(
        select(Question)
        .filter(
            Question.is_condemned == false(),
            Question.is_published == true(),
            Question.question.icontains(search_pattern)
        )
        .limit(quantity)
    )
    return questions.scalars().all()


@router.post(
    '/add',
    response_model=QuestionDB,
    response_model_exclude_none=True,
    summary='Добавить вопрос.'
)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def add_question(
    request: Request,
    question: QuestionCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Добавить вопрос в Базу. Новому вопросу будет автоматически присвоен
    статус "Не опубликован". Опубликовать вопрос может только
    администратор после предварительной модерации.
    """
    new_question = await create_question(
        question, user, session
    )
    return new_question


@router.get(
    '/{id}',
    response_model=QuestionDB,
    response_model_exclude_none=True,
    summary='Получить вопрос.'
)
@cache(expire=const.DEFAULT_CACHING_TIME)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def get_question(
    *,
    request: Request,
    id: int = Path(..., gt=0, description='id вопроса в Базе.'),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить вопрос из Базы по его уникальному идентификатору.
    """
    question = await get_valid_question_or_404(id, session)
    return question


@router.patch(
    '/{id}',
    response_model=QuestionDB,
    response_model_exclude_none=True,
    summary=('Откорректировать вопрос.')
)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def modify_question(
    request: Request,
    modified_question: QuestionUpdate,
    id: int = Path(..., gt=0, description='id вопроса в Базе.'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Откорректировать вопрос. Доступно администратору или пользователю,
    добавившему этот вопрос. Для обнуления поля в Базе необходимо передать
    в соответствующем ключе пустую строку.
    """
    question = await get_question_or_404(id, session)
    check_superuser_or_user_who_added(question, user)
    question = await edit_question(question, modified_question, session)
    return question


@router.patch(
    '/{id}/status',
    response_model=QuestionDBWithStatus,
    response_model_exclude_none=True,
    summary='Изменить статус вопроса.'
)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def modify_question_status(
    request: Request,
    modified_status: QuestionStatusUpdate,
    id: int = Path(..., gt=0, description='id вопроса в Базе.'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    """
    Изменить статус вопроса. Доступно только администратору.
    "is_published" - разрешен вопрос к выдаче или нет;
    "is_condemned" - вопрос корректен, но содержит некодируемые символы,
    угловые скобки, ссылки на отсутствующие внешние изображения и т.п.
    """
    question = await get_question_or_404(id, session)
    question = await edit_question(question, modified_status, session)
    return question


@router.delete(
    '/{id}',
    summary=('Удалить вопрос.')
)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def delete_question(
    request: Request,
    id: int = Path(..., gt=0, description='id вопроса в Базе.'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> dict[str, str]:
    """
    Удалить вопрос из Базы. Доступно администратору или пользователю,
    добавившему данный вопрос.
    """
    question = await get_question_or_404(id, session)
    check_superuser_or_user_who_added(question, user)
    await session.delete(question)
    await session.commit()
    return {'message': f'Вопрос с id = {id} удален из Базы.'}
