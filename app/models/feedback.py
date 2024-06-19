from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Feedback(Base):
    """Таблица для сохранения данных,
    полученных через форму обратной связи."""
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(150))
    feedback_text: Mapped[str] = mapped_column(Text())
    date: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.now(timezone.utc)
    )

    def __str__(self):
        return self.name
