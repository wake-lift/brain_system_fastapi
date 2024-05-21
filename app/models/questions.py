import enum
from typing import Optional

from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class QuestionType(enum.StrEnum):
    """Перечень допустимых значений типа вопроса."""
    Б = 'Брейн-ринг'
    БД = 'Брейн-ринг (резерв)'
    ДБ = 'Брейн-ринг (детский)'
    И = 'Вопросы из интернета'
    Л = 'Бескрылка'
    Ч = 'Что-где-когда'
    ЧБ = 'Что-где-когда (тренировки)'
    ЧД = 'Что-где-когда (детский)'
    Э = 'Эрудитка'
    Я = 'Своя игра'


class Question(Base):
    """Основная таблица с вопросами."""
    id: Mapped[int] = mapped_column(primary_key=True)
    package: Mapped[str | None] = mapped_column(String(256))
    tour: Mapped[str | None] = mapped_column(String(256))
    number: Mapped[int | None] = mapped_column(SmallInteger())
    question_type: Mapped[QuestionType] = mapped_column(
        default=QuestionType.Ч,
        index=True
    )
    question: Mapped[str] = mapped_column(Text(), index=True)
    answer: Mapped[str] = mapped_column(Text())
    pass_criteria: Mapped[str | None] = mapped_column(Text())
    authors: Mapped[str | None] = mapped_column(Text())
    sources: Mapped[str | None] = mapped_column(Text())
    comments: Mapped[str | None] = mapped_column(Text())
    """Вопросы, которые не годятся для выдачи: содержат ссылку на изображение,
    угловые скобки, некодируемый набор символов и т.п."""
    is_condemned: Mapped[bool] = mapped_column(default=False, index=True)
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('user.id'))
    user: Mapped[Optional['User']] = relationship(back_populates='questions')

    def __str__(self):
        return f'Вопрос id = {self.id}. Тип: {self.question_type.value} ...'
