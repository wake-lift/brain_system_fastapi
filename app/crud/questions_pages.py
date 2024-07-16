from datetime import datetime, timezone
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Sequence, false, func, or_, select, true

from app.core.constants import REFRESH_INTERVAL, SET_FOR_RANDOMIZING
from app.models.questions import Question

MAX_SET_JEOPARDY: int | None = None
MAX_SET_BRAIN: int | None = None
MAX_SET_WWW: int | None = None
LAST_REFRESH: datetime = datetime.now(timezone.utc)


async def get_max_question_sets(
        session:  AsyncSession
) -> dict[str, int]:
    """Пересчитывает количество вопросов в БД по трем категориям через
    заданный в параметре REFRESH_INTERVAL интервал времени."""
    global MAX_SET_WWW, MAX_SET_BRAIN, MAX_SET_JEOPARDY, LAST_REFRESH
    if (
        not all([MAX_SET_JEOPARDY, MAX_SET_BRAIN, MAX_SET_WWW,])
        or (datetime.now(timezone.utc) - LAST_REFRESH > REFRESH_INTERVAL)
    ):
        query = (
            select(Question.question_type, func.count(Question.question))
            .filter(
                Question.is_condemned == false(),
                Question.is_published == true(),
            )
            .group_by(Question.question_type)
            .having(
                or_(
                    Question.question_type == 'Ч',
                    Question.question_type == 'Б',
                    Question.question_type == 'Я'
                )
            )
        )
        question_type_counts = await session.execute(query)
        counts = {_[0].value: _[1] for _ in question_type_counts.all()}
        MAX_SET_WWW = counts['Что-где-когда']
        MAX_SET_BRAIN = counts['Брейн-ринг']
        MAX_SET_JEOPARDY = counts['Своя игра']
        LAST_REFRESH = datetime.now(timezone.utc)
    return {
        'Ч': MAX_SET_WWW,
        'Б': MAX_SET_BRAIN,
        'Я': MAX_SET_JEOPARDY
    }


def get_base_query(question_type: str) -> Select:
    return select(
        Question.id,
        Question.package,
        Question.question_type,
        Question.question,
        Question.answer,
        Question.pass_criteria,
        Question.authors,
        Question.sources,
        Question.comments
    ).filter(
        Question.question_type == question_type,
        Question.is_condemned == false(),
        Question.is_published == true()
    )


async def get_initial_random_question_set(
    question_type: str, session: AsyncSession
) -> Sequence:
    """Формирует первоначальный список вопросов с учетом типа вопроса и
    заданного константой "SET_FOR_RANDOMIZING" размера выборки.
    Функция необходима для ускорения запросов к БД."""
    max_question_sets = await get_max_question_sets(session)
    questions_quantity = max_question_sets[question_type]
    randomizing_limit = questions_quantity - SET_FOR_RANDOMIZING - 1
    start_point = random.randint(
        0,
        randomizing_limit if randomizing_limit > 0 else questions_quantity
    )
    if questions_quantity < SET_FOR_RANDOMIZING:
        start_point = 0
    questions = await session.execute(
        get_base_query(question_type)
        .limit(SET_FOR_RANDOMIZING)
        .offset(start_point)
    )
    return questions.all()


async def get_random_package(
    question_type: str, session: AsyncSession
) -> Sequence:
    random_package = await session.execute(
        select(Question.package).
        group_by(Question.package, Question.question_type).
        having(Question.question_type == question_type).
        order_by(func.random())
    )
    random_package_name = random_package.first().package
    base_query = get_base_query(question_type)
    random_package = await session.execute(
        base_query.filter(Question.package == random_package_name)
    )
    return random_package.all(), random_package_name
