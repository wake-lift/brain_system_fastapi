import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.constants import REFRESH_INTERVAL
from app.models.questions import Question
from app.models.users import User

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

LAST_REFRESH = datetime.datetime.now()


async def get_max_question_type_quantity(
        session: AsyncSession
) -> dict[str, int | None]:
    """Пересчитывает количество вопросов в БД по категориям вопросов через
    заданный в параметре REFRESH_INTERVAL интервал времени."""
    global max_sets, LAST_REFRESH
    if (
        not all(max_sets.values())
        or (datetime.datetime.now() - LAST_REFRESH > REFRESH_INTERVAL)
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
        LAST_REFRESH = datetime.datetime.now()
    return max_sets


def check_superuser_or_user_who_added(
        question: Question,
        user: User
) -> None:
    """Проверка, что вопрос был добавлен в базу указанным пользователем,
    либо пользователь обладает правами администратора."""
    if question.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail=('Изменять или удалять вопрос может администратор или '
                    'пользователь, добавивший вопрос.')
        )
