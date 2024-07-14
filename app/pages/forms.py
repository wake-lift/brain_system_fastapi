from starlette_wtf import StarletteForm
from wtforms import (EmailField, IntegerField, RadioField, StringField,
                     SubmitField, TextAreaField, ValidationError)
from wtforms.validators import (DataRequired, Email, Length, NumberRange,
                                Optional)

from app.core.constants import (DEFAULT_QUESTIONS_QUANTITY, MAX_EMAIL_LENGTH,
                                MAX_FEEDBACK_LENGTH,
                                MAX_FEEDBACK_USERNAME_LENGTH,
                                MAX_QUESTIONS_QUANTITY,
                                MIN_SEARCH_PATTERN_LENGTH)


class FeedbackForm(StarletteForm):
    name = StringField(
        label='Ваше имя',
        validators=[DataRequired(message='Имя - обязательное поле'),
                    Length(1, MAX_FEEDBACK_USERNAME_LENGTH)],
    )
    email = EmailField(
        label='Если вы хотите, чтобы вам ответили - заполните это поле',
        validators=[Email(message=('Введите валидный адрес e-mail или'
                                   ' оставьте поле пустым')),
                    Length(1, MAX_EMAIL_LENGTH),
                    Optional()],
    )
    feedback_text = TextAreaField(
        label='Текст обратной связи',
        validators=[DataRequired(message=('Текст обратной связи'
                                          ' - обязательное поле')),
                    Length(1, MAX_FEEDBACK_LENGTH)],
    )
    submit = SubmitField(label='Отправить')


class RandomQuestionForm(StarletteForm):
    CHOICES = [
        ('Ч', 'Что-где-когда'),
        ('Б', 'Брейн-ринг'),
        ('Я', 'Своя игра'),
    ]
    question_type = RadioField(
        label='Тип вопроса:',
        choices=CHOICES,
        default='Ч',
    )
    search_pattern = StringField(
        label='Поиск по тексту вопроса (строгий):',
        description=f'Не менее {MIN_SEARCH_PATTERN_LENGTH} символов',
        validators=[Length(min=MIN_SEARCH_PATTERN_LENGTH), Optional()],
    )
    full_text_search_pattern = StringField(
        label='Поиск по тексту вопроса (нестрогий):',
        description=f'Не менее {MIN_SEARCH_PATTERN_LENGTH} символов',
        validators=[Length(min=MIN_SEARCH_PATTERN_LENGTH), Optional()],
    )
    questions_quantity = IntegerField(
        label=f'Количество вопросов (не более {MAX_QUESTIONS_QUANTITY}):',
        description=f'не более {MAX_QUESTIONS_QUANTITY}',
        default=DEFAULT_QUESTIONS_QUANTITY,
        validators=[DataRequired(message='Обязательное поле'),
                    NumberRange(min=1, max=MAX_QUESTIONS_QUANTITY)],
    )
    submit = SubmitField(label='Отправить')

    def validate_search_pattern(self, field):
        if field.data and self.full_text_search_pattern.data:
            raise ValidationError('Заполните только одно из полей поиска или'
                                  ' оставьте оба поля пустыми.')


class RandomPackageForm(StarletteForm):
    CHOICES = [
        ('Ч', 'Что-Где-Когда'),
        ('ЧД', 'Что-где-когда (детский)'),
        ('Б', 'Брейн-ринг'),
        ('ДБ', 'Брейн-ринг (детский)'),
    ]
    question_type = RadioField(
        label='Тип пакета:',
        choices=CHOICES,
        default='Ч',
    )
    submit = SubmitField(label='Отправить')
