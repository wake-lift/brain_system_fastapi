from pydantic import BaseModel, Field

from app.models.questions import QuestionType


class QuestionDB(BaseModel):
    id: int
    package: str | None
    tour: str | None
    number: int | None
    question_type: QuestionType
    question: str
    answer: str
    pass_criteria: str | None
    authors: str | None
    sources: str | None
    comments: str | None

    class Config:
        from_attributes = True


class QuestionDBWithStatus(QuestionDB):
    is_condemned: bool
    is_published: bool


class QuestionCreate(BaseModel):
    package: str | None = Field(
        None, description='Пакет', examples=['Название пакета (опционально)',]
    )
    tour: str | None = Field(
        None, examples=['Название тура внутри пакета (опционально),']
    )
    number: int | None = None
    question_type: QuestionType = QuestionType.Ч
    question: str = Field(
        ...,
        examples=[('Текст вопроса (не менее 30-ти символов). '
                   'Обязательное поле'),],
        min_length=30
    )
    answer: str = Field(..., examples=['Ответ на вопрос. Обязательное поле',])
    pass_criteria: str | None = Field(
        None, examples=['Критерий зачета ответа (опционально)',]
    )
    authors: str | None = Field(
        None, examples=['Автор(ы) вопроса (опционально)',]
    )
    sources: str | None = Field(None, examples=['Иточник(и) (опционально)',])
    comments: str | None = Field(
        None, examples=['Комментарий (опционально)',]
    )


class QuestionUpdate(BaseModel):
    package: str | None = Field(
        None, description='Пакет', examples=['Название пакета (опционально)',]
    )
    tour: str | None = Field(
        None, examples=['Название тура внутри пакета (опционально),']
    )
    number: int | None = None
    question_type: QuestionType | None = None
    question: str | None = Field(
        None,
        examples=['Текст вопроса (не менее 30-ти символов) (опционально)',],
        min_length=30
    )
    answer: str | None = Field(
        None,
        examples=['Ответ на вопрос (опционально)',]
    )
    pass_criteria: str | None = Field(
        None, examples=['Критерий зачета ответа (опционально)',]
    )
    authors: str | None = Field(
        None, examples=['Автор(ы) вопроса (опционально)',]
    )
    sources: str | None = Field(None, examples=['Иточник(и) (опционально)',])
    comments: str | None = Field(
        None, examples=['Комментарий (опционально)',]
    )


class QuestionStatusUpdate(BaseModel):
    is_condemned: bool | None = False
    is_published: bool | None = False
