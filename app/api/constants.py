import datetime

# Ограничение количества случайных вопросов, которе может выьрать пользователь
MAX_QUESTIONS_QUANTITY: int = 100

# Размер первоначальной выборки при выдаче случайного пакета вопросов
SET_FOR_RANDOMIZING: int = 5000

# Интервал времени между обновлениями количества вопросов в базе
REFRESH_INTERVAL = datetime.timedelta(hours=24)
