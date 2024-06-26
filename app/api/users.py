from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import limiter
import app.core.constants as const
from app.core.db import get_async_session
from app.core.users import auth_backend, current_user, fastapi_users
from app.models.questions import Question
from app.models.users import User
from app.schemas.questions import QuestionDB
from app.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['Аутентификация'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['Аутентификация'],
)


@router.get(
    '/users/questions',
    response_model=list[QuestionDB],
    response_model_exclude_none=True,
    tags=['Пользователи'],
    summary='Получить вопросы, добавленные в Базу текущим пользователем.'
)
@cache(expire=const.DEFAULT_CACHING_TIME)
@limiter.limit(const.BASE_THROTTLING_RATE)
async def get_users_questions(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)

):
    questions = await session.execute(
        select(Question).
        select_from(Question).
        filter(Question.user_id == user.id)
    )
    questions = questions.scalars().all()
    return questions


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['Пользователи'],
)
