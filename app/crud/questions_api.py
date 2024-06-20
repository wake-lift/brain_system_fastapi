from datetime import datetime, timezone
import random
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import REFRESH_INTERVAL, SET_FOR_RANDOMIZING
from app.core.db import get_async_session
from app.models.questions import Question
from app.models.users import User
from app.schemas.questions import QuestionCreate

max_sets: dict[str, int | None] = {
    'Б': None,
    'ДБ': None,
    'И': None,
    'Л': None,
    'Ч': None,
    'ЧБ': None,
    'ЧД': None,
    'Э': None,
    'Я': None,
    'total': None
}

LAST_REFRESH: datetime = datetime.now(timezone.utc)


async def get_max_question_type_quantity(
        session: AsyncSession
) -> dict[str, int | None]:
    """Пересчитывает количество вопросов в БД по категориям вопросов через
    заданный в параметре REFRESH_INTERVAL интервал времени."""
    global max_sets, LAST_REFRESH
    if (
        not all(max_sets.values())
        or (datetime.now(timezone.utc) - LAST_REFRESH > REFRESH_INTERVAL)
    ):
        query = (
            select(Question.question_type, func.count())
            .select_from(Question)
            .filter(Question.is_condemned == 0, Question.is_published == 1)
            .group_by(Question.question_type)
        )
        qunatities = await session.execute(query)
        for counted_question_type in qunatities.all():
            max_sets[counted_question_type[0].name] = counted_question_type[1]
        total_quantity = await session.execute(
            select(func.count()).select_from(Question)
        )
        max_sets['total'] = total_quantity.scalars().first()
        LAST_REFRESH = datetime.now(timezone.utc)
    return max_sets


async def get_initial_query(
        session: AsyncSession,
        question_type: str | None
) -> Select[tuple[Question]]:
    """Формирует первоначальный список вопросов с учетом типа вопроса и
    заданного константой "SET_FOR_RANDOMIZING" размера выборки.
    Функция необходима для ускорения запросов к БД."""
    max_question_type_dict = await get_max_question_type_quantity(session)
    max_question_type_quantity = max_question_type_dict['total']
    query = select(Question).filter(
        Question.is_condemned == 0,
        Question.is_published == 1
    )
    if question_type:
        query = query.filter(Question.question_type == question_type)
        max_question_type_quantity = max_question_type_dict[question_type]
    if max_question_type_quantity <= SET_FOR_RANDOMIZING:
        start_point = 0
    else:
        start_point = random.randint(
            0,
            max_question_type_quantity - SET_FOR_RANDOMIZING - 1
        )
    query = query.offset(start_point).limit(SET_FOR_RANDOMIZING)
    return query


async def get_valid_question_or_404(
        question_id: int,
        session: AsyncSession,
) -> Question:
    """
    Возвращает объект модели, если вопрос найден в Базе и разрешен к выдаче.
    В противном случае вызывает исключение 404.
    """
    question = await session.execute(
        select(Question).filter(
            Question.id == question_id,
            Question.is_condemned == 0,
            Question.is_published == 1
        )
    )
    question = question.scalars().first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail='Вопрос с таким id не найден в Базе.'
        )
    return question


async def get_question_or_404(
        question_id: int,
        session: AsyncSession,
) -> Question:
    """
    Возвращает объект модели, если вопрос найден в Базе.
    В противном случае вызывает исключение 404.
    """
    question = await session.execute(
        select(Question).filter(
            Question.id == question_id,
        )
    )
    question = question.scalars().first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail='Вопрос с таким id не найден в Базе.'
        )
    return question


async def get_random_package(session: AsyncSession) -> list[Question]:
    """
    Возвращает список всех вопросов, относящихся к одному случайно
    выбранному пакету.
    """
    random_package = await session.execute(
        select(Question.package)
        .group_by(Question.package)
        .order_by(func.random())
        .limit(1)
    )
    random_package = random_package.scalar_one()
    package_set = await session.execute(
        select(Question)
        .filter(Question.package == random_package)
    )
    return package_set.scalars().all()


async def create_question(
    question: QuestionCreate,
    user: User,
    session: AsyncSession,
) -> Question:
    """Создает новую запись в Базе."""
    question_data = question.model_dump()
    question_data['user_id'] = user.id
    question_obj = Question(**question_data)
    session.add(question_obj)
    await session.commit()
    await session.refresh(question_obj)
    return question_obj


async def edit_question(
    question: Question,
    update_data: BaseModel,
    session: AsyncSession = Depends(get_async_session),
) -> Question:
    """Модифицирует вопрос в Базе."""
    initial_data = jsonable_encoder(question)
    update_data = update_data.model_dump(exclude_unset=True)
    for field in initial_data:
        if field in update_data:
            setattr(
                question,
                field,
                update_data[field] if update_data[field] != '' else None
            )
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question
