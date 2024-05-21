from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str | None


class UserCreate(schemas.BaseUserCreate):
    username: str | None


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None
