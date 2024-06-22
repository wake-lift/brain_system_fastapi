import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

import aiosqlite
import asyncpg
from telegram import Chat, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode, UpdateType
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters)

logging.basicConfig(
    level=logging.WARNING,
    filename='main_log.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = RotatingFileHandler('bot_log.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

CORRESPONDANCE: dict = {
    'Что-Где-Когда': 'Ч',
    'Брейн-ринг': 'Б',
    'Своя игра': 'Я',
}
ANSWER_TEXT: None | str = None
CURRENT_QUESTION_TYPE: None | str = 'Ч'


def check_tokens(token) -> bool:
    """Проверяет доступность переменных окружения."""
    return bool(token)


def button_shortcut(button_names: list[list]) -> ReplyKeyboardMarkup:
    """Формирует кнопку с указанными полями."""
    return ReplyKeyboardMarkup(
        keyboard=button_names,
        resize_keyboard=True
    )


async def send_message(
        context: ContextTypes.DEFAULT_TYPE,
        chat: Chat,
        text: str,
        buttons: ReplyKeyboardMarkup,
        parse_mode=None) -> None:
    """Отправляет сообщение с указанными текстом и кнопками."""
    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True,
        parse_mode=parse_mode
    )


async def get_question(question_type: str) -> Any:
    """Генерирует случайный вопрос с учетом типа БД."""
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
        if os.getenv('DATABASE_TYPE') == 'postgres':
            conn = await asyncpg.connect(
                f'postgresql://{os.getenv('POSTGRES_USER')}'
                f':{os.getenv('POSTGRES_PASSWORD')}'
                f'@{os.getenv('POSTGRES_DB_HOST')}'
                f':{os.getenv('POSTGRES_DB_PORT')}'
                f'/{os.getenv('POSTGRES_DB')}'
            )
            question = await conn.fetchrow(query, question_type)
            await conn.close()
        if os.getenv('DATABASE_TYPE') == 'sqlite':
            async with aiosqlite.connect(os.getenv('SQLITE_DB_PATH')) as conn:
                cursor = await conn.execute(query, question_type)
                question = await cursor.fetchone()
    except Exception as error:
        logging.error(error, exc_info=True)
        return None
    if not question:
        logging.error(
            'Из бд был получен вопрос, интерпретируемый как None',
            exc_info=True
        )
        return None
    return question


async def get_parsed_question(question_type: str) -> None | dict:
    """Форматирует сгенерированный вопрос."""
    question = await get_question(question_type)
    if (
        not question[0]
        or question[0] == 'None'
        or not question[1]
        or question[1] == 'None'
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
    ANSWER_TEXT = f'<b>{answer_dict['Ответ']}</b>\n\n'
    del answer_dict['Ответ']
    ANSWER_TEXT += '\n'.join(f'<b><i>{key}:</i></b> <i>{item}</i>'
                             for key, item in answer_dict.items())
    return ANSWER_TEXT


async def handle_bd_error(context: ContextTypes.DEFAULT_TYPE,
                          chat: Chat) -> None:
    """Генерирует сообщение об ошибке запроса к API."""
    buttons = button_shortcut([['На главную'],])
    text = ('Произошла ошибка при выполнении запроса к базе данных 😳\n'
            'Попробуйте повторить попытку позже')
    await send_message(context, chat, text, buttons)


async def wake_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует начальное приветствие."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = button_shortcut([
        ['Что-Где-Когда'], ['Брейн-ринг'], ['Своя игра'], ['На главную'],
    ],)
    text = f'Здравствуйте, {name}! Выберите тип вопроса:'
    await send_message(context, chat, text, buttons)


async def handle_messages(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений от пользователя."""
    global ANSWER_TEXT, CURRENT_QUESTION_TYPE
    chat = update.effective_chat
    message = update.message.text
    if message in ('Что-Где-Когда', 'Брейн-ринг',
                   'Своя игра', 'Следующий вопрос'):
        if message == 'Следующий вопрос' and not CURRENT_QUESTION_TYPE:
            buttons = button_shortcut([['На главную'],])
            text = 'Если не было первого вопроса - не будет и следующего'
            await send_message(context, chat, text, buttons)
        else:
            parsed_question = (
                await get_parsed_question(CURRENT_QUESTION_TYPE)
                if CURRENT_QUESTION_TYPE
                else await get_parsed_question(CORRESPONDANCE[message])
            )
            if not parsed_question:
                await handle_bd_error(context, chat)
            else:
                if message != 'Следующий вопрос':
                    CURRENT_QUESTION_TYPE = CORRESPONDANCE[message]
                ANSWER_TEXT = generate_answer(parsed_question)
                buttons = button_shortcut([['Узнать ответ'], ['На главную'],])
                question = parsed_question['Вопрос']
                text = f'<i>Внимание, вопрос!</i>\n\n{question}'
                await send_message(context, chat, text,
                                   buttons, parse_mode=ParseMode.HTML)
    elif message == 'Узнать ответ':
        buttons = button_shortcut([['Следующий вопрос'], ['На главную'],])
        if ANSWER_TEXT:
            await send_message(context, chat, ANSWER_TEXT,
                               buttons, parse_mode=ParseMode.HTML)
            ANSWER_TEXT = None
        else:
            buttons = button_shortcut([['На главную'],])
            text = 'Сперва получите вопрос, на который хотите узнать ответ'
            await send_message(context, chat, text, buttons)
    elif message == 'На главную':
        CURRENT_QUESTION_TYPE = None
        ANSWER_TEXT = None
        await wake_up(update, context)
    else:
        buttons = button_shortcut([['На главную'],])
        text = ('Введите что-нибудь осмысленное, '
                'а лучше воспользуйтесь кнопками')
        await send_message(context, chat, text, buttons)


def main() -> None:
    """Start the bot."""
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not check_tokens(TELEGRAM_TOKEN):
        error_message = ('Работа бота остановлена:'
                         ' ошибка получения переменных окружения')
        logging.critical(error_message, exc_info=True)
        sys.exit(error_message)
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", wake_up))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_messages
    ))
    application.run_polling(allowed_updates=UpdateType.MESSAGE)


if __name__ == "__main__":
    main()
