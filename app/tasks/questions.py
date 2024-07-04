from datetime import datetime
from email.message import EmailMessage
from typing import List

from celery import Celery
from celery.schedules import crontab

from app.api.utils import get_email_msg, get_package_file, send_email_message
from app.core.config import settings
from app.crud.questions_api import get_unpublished_questions_num

broker_url = (f'pyamqp://{settings.rabbitmq_default_user}'
              f':{settings.rabbitmq_default_pass}'
              f'@{settings.rabbitmq_hostname}'
              f':{settings.rabbitmq_node_port}//')

celery_api = Celery(
    'api_tasks',
    broker=broker_url,
    broker_connection_retry_on_startup=True
)

celery_api.conf.update(
    timezone='Europe/Moscow',
    enable_utc=False,
)


@celery_api.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=10, minute=00),
        send_unpublished_questions_num.s(settings.smtp_host_user)
    )


@celery_api.task
def send_unpublished_questions_num(emai_address: str) -> None:
    questions_num = get_unpublished_questions_num()
    email = EmailMessage()
    email['Subject'] = ('Отчет о количестве неопубликованных вопросов')
    email['From'] = settings.smtp_host_user
    email['To'] = emai_address
    body = ('По состоянию на '
            f'{datetime.now().strftime("%d.%m.%y, %H.%M UTC+3")} в базе '
            f'данных имеется {questions_num} неопубликованных вопросов')
    email.set_content(body)
    send_email_message(email)


@celery_api.task()
def send_email(
    email_to: str, package_questions_list: List[dict], package_name: str = None
) -> None:
    package_file = get_package_file(package_questions_list, package_name)
    email_msg = get_email_msg(email_to, package_file, package_name)
    send_email_message(email_msg)
