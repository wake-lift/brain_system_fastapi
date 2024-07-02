from email.message import EmailMessage
from io import BytesIO
import smtplib
from typing import List, Tuple

from fastapi import HTTPException
import pandas as pd

from app.core.config import settings
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


def get_package_questions_list(
        package: list[Question]
) -> Tuple[List[dict], str]:
    question_list = []
    question_number = 1
    for question in package:
        question_dict = {
            'Номер вопроса': question_number,
            'Тип вопроса': question.question_type,
            'Текст вопроса': question.question,
            'Ответ на вопрос': question.answer,
            'Критерий зачета ответа': question.pass_criteria,
            'Автор(ы)': question.authors,
            'Источник(и)': question.sources,
            'Комментарий': question.comments
        }
        question_list.append(question_dict)
        question_number += 1
    try:
        package_name = question.package
    except UnboundLocalError:
        package_name = None
    return question_list, package_name


def get_package_file(
        question_list: List[dict], package_name: str = None
) -> BytesIO:
    df = pd.DataFrame(question_list)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='odf') as doc:
        df.to_excel(
            doc,
            sheet_name=(f'Пакет "{package_name}"'
                        if package_name
                        else 'Список вопросов'),
            index=False)
    return output


def get_email_msg(
        email_to: str, package_file: BytesIO, package_name: str = None
) -> EmailMessage:
    email = EmailMessage()
    email['Subject'] = (f'Пакет вопросов "{package_name}"'
                        if package_name
                        else 'Список вопросов')
    email['From'] = settings.smtp_host_user
    email['To'] = email_to
    package_file.seek(0)
    package_file_binary = package_file.read()
    email.add_attachment(
        package_file_binary,
        maintype='application',
        subtype='octet-stream',
        filename=f'{package_name}.ods' if package_name else 'Список вопросов'
    )
    return email


def send_email_message(email: EmailMessage) -> None:
    with smtplib.SMTP_SSL(
        settings.smtp_host, settings.smtp_port
    ) as server:
        server.login(
            settings.smtp_host_user, settings.smtp_host_password
        )
        server.send_message(email)
