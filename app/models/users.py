from typing import List
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None]
    questions: Mapped[List['Question'] | None] = relationship(
        back_populates='user'
    )
