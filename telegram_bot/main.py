import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from bot.config import settings
from bot.utils import (QUESTION_MAP, check_secrets, generate_answer,
                       get_inline_keyboard, get_parsed_question)

answer_text: None | str = None
current_question_type: None | str = None

dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(msg: Message):
    """Генерирует начальное приветствие."""
    await msg.answer(
        (f'Здравствуйте, <b>{msg.from_user.first_name}</b>!'
         ' Выберите тип вопроса:'),
        reply_markup=get_inline_keyboard()
    )


@dp.message()
async def react_to_any_message(msg: Message):
    """Ответ на любое введенное вручную сообщение."""
    logging.info('Пользователь не использует кнопки')
    text = ('🤖 Не нужно вводить текст вручную.'
            '\nПожалуйста, пользуйтесь кнопками.')
    await msg.reply(text=text)


@dp.callback_query(F.data == 'goto_main')
async def goto_main(callback: CallbackQuery):
    global current_question_type, answer_text
    current_question_type = None
    answer_text = None
    await callback.message.answer(
        'Выберите тип вопроса:', reply_markup=get_inline_keyboard()
    )


@dp.callback_query(
    F.data.in_({'www', 'brain_ring', 'jeopardy', 'next_question'})
)
async def generate_question(callback: CallbackQuery):
    """Генерирует очередной вопрос."""
    global answer_text, current_question_type
    if callback.data == 'next_question' and not current_question_type:
        text = '🤖 Если не было первого вопроса - не будет и следующего'
        keyboard = get_inline_keyboard([
            [InlineKeyboardButton(
                text='🚀 Вернуться на главную', callback_data='goto_main'
            )],
        ])
        callback.message.answer(text, reply_markup=keyboard)
    else:
        parsed_question = (
            await get_parsed_question(current_question_type)
            if current_question_type
            else await get_parsed_question(QUESTION_MAP[callback.data])
        )
        if parsed_question is None:
            keyboard = get_inline_keyboard([
                [InlineKeyboardButton(
                    text='На главную', callback_data='goto_main'
                )],
            ])
            logging.info('Ошибка при выполнении запроса к БД')
            text = ('Произошла ошибка при выполнении запроса к базе вопросов'
                    ' 🤖\nПопробуйте повторить попытку позже.')
            await callback.message.answer(text, reply_markup=keyboard)
        else:
            if callback.data != 'next_question':
                current_question_type = QUESTION_MAP[callback.data]
            answer_text = generate_answer(parsed_question)
            keyboard = get_inline_keyboard([
                [InlineKeyboardButton(
                    text='👀 Узнать ответ', callback_data='get_answer'
                )],
                [InlineKeyboardButton(
                    text='🚀 На главную', callback_data='goto_main'
                )],
            ])
            question = parsed_question['Вопрос']
            text = f'<i>Внимание, вопрос!</i>\n\n{question}'
            await callback.message.answer(text, reply_markup=keyboard)


@dp.callback_query(F.data == 'get_answer')
async def get_answer(callback: CallbackQuery):
    """Возвращает ответ на вопрос."""
    global answer_text
    keyboard = get_inline_keyboard([
        [InlineKeyboardButton(
            text='🌍 Следующий вопрос', callback_data='next_question'
        )],
        [InlineKeyboardButton(text='🚀 На главную', callback_data='goto_main')],
    ])
    if answer_text:
        await callback.message.answer(answer_text, reply_markup=keyboard)
        answer_text = None
    else:
        keyboard = get_inline_keyboard([
            [InlineKeyboardButton(
                text='🚀 На главную', callback_data='goto_main'
            )],
        ])
        logging.info('Пользователь неправильно использует кнопки')
        text = '🤖 Сперва получите вопрос, на который хотите узнать ответ'
        await callback.message.answer(text, reply_markup=keyboard)


async def main() -> None:
    """Главная корутина бота."""
    check_secrets()
    bot = Bot(
        token=settings.telegram_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_prefer_small_media=True,
        )
    )
    logging.info('Бот начал работу')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
