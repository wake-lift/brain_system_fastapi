import sys

import aiosqlite
import asyncpg
from aiogram import types

from bot.config import settings

from . import logger

QUESTION_MAP: dict = {
    'www': 'Ч',
    'brain_ring': 'Б',
    'jeopardy': 'Я',
}


def check_secrets() -> None:
    """Проверяет доступность и правильность
    переменных окружения и возвращает их."""
    if not all(
        [
            bool(settings.telegram_token),
            (
                settings.database_type == 'postgres'
                or settings.database_type == 'sqlite'
            )
        ]
    ):
        error_message = ('Работа бота остановлена:'
                         ' ошибка получения переменных окружения')
        logger.critical(error_message, exc_info=True)
        sys.exit(error_message)


async def get_question(question_type: str) -> tuple | None:
    """Получает случайный вопрос с учетом типа БД."""
    query = """SELECT question,
                      answer,
                      pass_criteria,
                      comments,
                      authors,
                      sources
                FROM question
                WHERE NOT is_condemned AND question_type = $1
                ORDER BY random()
                LIMIT 1"""
    try:
        if settings.database_type == 'postgres':
            conn = await asyncpg.connect(
                f'postgresql://{settings.postgres_user}'
                f':{settings.postgres_password.get_secret_value()}'
                f'@{settings.postgres_db_host}'
                f':{settings.postgres_db_port}'
                f'/{settings.postgres_db}'
            )
            question = await conn.fetchrow(query, question_type)
            await conn.close()
        elif settings.database_type == 'sqlite':
            async with aiosqlite.connect(settings.sqlite_db_path) as conn:
                cursor = await conn.execute(query, question_type)
                question = await cursor.fetchone()
    except Exception as error:
        logger.error(error, exc_info=True)
        return None
    if not question:
        logger.error(
            'Из бд был получен вопрос, интерпретируемый как None',
            exc_info=True
        )
        return None
    return question


async def get_parsed_question(question_type: str) -> None | dict:
    """Форматирует сгенерированный вопрос."""
    question = await get_question(question_type)
    if (
        not question
        or (
            not question[0]
            or question[0] == 'None'
            or not question[1]
            or question[1] == 'None'
        )
    ):
        return None
    parsed_question = {'Вопрос': question[0], 'Ответ': question[1]}
    if question[2] and question[2] != 'None':
        parsed_question['Зачёт'] = question[2]
    if question[3] and question[3] != 'None':
        parsed_question['Комментарий'] = question[3]
    if question[4] and question[4] != 'None':
        parsed_question['Авторы'] = question[4]
    if question[5] and question[5] != 'None':
        parsed_question['Источники'] = question[5]
    return parsed_question


def generate_answer(parsed_question: dict) -> str:
    """Возвращает форматированную строку ответа на вопрос."""
    answer_dict = parsed_question.copy()
    del answer_dict['Вопрос']
    answer_text = f'<b>{answer_dict['Ответ']}</b>\n\n'
    del answer_dict['Ответ']
    answer_text += '\n'.join(f'<b><i>{key}:</i></b> <i>{item}</i>'
                             for key, item in answer_dict.items())
    return answer_text


def get_inline_keyboard(
        buttons: list[list[types.InlineKeyboardButton]] | None = None
) -> types.InlineKeyboardMarkup:
    """Формирует inline-кнопки."""
    if buttons is None:
        buttons = [
            [types.InlineKeyboardButton(
                text='🦉 Что-Где-Когда ', callback_data='www'
            )],
            [types.InlineKeyboardButton(
                text='🧠 Брейн-ринг ', callback_data='brain_ring'
            )],
            [types.InlineKeyboardButton(
                text='🎯 Своя игра ', callback_data='jeopardy'
            )],
        ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
