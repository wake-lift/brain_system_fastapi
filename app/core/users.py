from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.users import User


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth_token_secret,
        lifetime_seconds=3600
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.auth_token_secret
    verification_token_secret = settings.auth_token_secret

    async def on_after_register(self, user: User, request: Request | None):
        print(f'Пользователь {user.id} успешно зарегистрирован.')

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None
    ):
        print(f"Пользователь {user.id}. Восстановление пароля. Токен: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None
    ):
        print(f"Успешная верификация пользователя {user.id}. Токен: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
