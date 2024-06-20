from fastapi import HTTPException


from app.models.questions import Question
from app.models.users import User


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
