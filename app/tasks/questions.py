import os
import smtplib
from typing import List

from celery import Celery

from app.api.utils import get_email_msg, get_package_file


celery_api = Celery(
    'api_tasks',
    broker='pyamqp://guest@localhost//',
    broker_connection_retry_on_startup=True
)


@celery_api.task()
def send_email(
    email_to: str, package_questions_list: List[dict], package_name: str
) -> None:
    package_file = get_package_file(package_questions_list, package_name)
    email_msg = get_email_msg(email_to, package_file, package_name)
    with smtplib.SMTP_SSL(
        os.getenv('EMAIL_HOST'), os.getenv('EMAIL_PORT')
    ) as server:
        server.login(
            os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD')
        )
        server.send_message(email_msg)
