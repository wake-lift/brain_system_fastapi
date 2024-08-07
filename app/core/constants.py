from datetime import timedelta

# Минимальная длина текста вопроса
MIN_QUESTION_LENGTH: int = 30

# Ограничение количества случайных вопросов, которе может выьрать пользователь
MAX_QUESTIONS_QUANTITY: int = 100

# Количество случайных вопросов по умолчанию
DEFAULT_QUESTIONS_QUANTITY: int = 10

# Минимальное количество символов, по которым возможен посик вопросов в БД
MIN_SEARCH_PATTERN_LENGTH: int = 3

# Размер первоначальной выборки при выдаче случайного пакета вопросов
SET_FOR_RANDOMIZING: int = 5000

# Интервал времени между обновлениями количества вопросов в базе
REFRESH_INTERVAL: timedelta = timedelta(hours=24)

# Максимальная длина текста сообщения в обратной связи
MAX_FEEDBACK_LENGTH: int = 5000

# Максимальная длина имени пользователя, оставившего обратную связь
MAX_FEEDBACK_USERNAME_LENGTH: int = 128

# Максимальная длина email-адреса
MAX_EMAIL_LENGTH: int = 150

# Базовое значение ограничения количества запросов в единицу времени
BASE_THROTTLING_RATE: str = '10/minute'

# Ограничения количества запросов в единицу времени к странице обратной связи
FEEDBACK_THROTTLING_RATE: str = '3/minute'

# Ограничения количества запросов в единицу времени
# к странице экспорта списка продуктов
EXPORT_MODEL_TO_ODS_THROTTLING_RATE: str = '2/minute'

# Ограничения количества запросов в единицу времени
# к страницам выдачи вопросов
GENERATE_QUESTIONS_THROTTLING_RATE: str = '5/minute'

# Время кэширования страниц по умолчанию (в секундах)
DEFAULT_CACHING_TIME: int = 60 * 5
