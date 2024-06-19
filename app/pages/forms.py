from starlette_wtf import StarletteForm
from wtforms import EmailField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class FeedbackForm(StarletteForm):
    name = StringField(
        label='Ваше имя',
        validators=[DataRequired(message='Имя - обязательное поле'),
                    Length(1, 128)],
    )
    email = EmailField(
        label='Если вы хотите, чтобы вам ответили - заполните это поле',
        validators=[Email(message=('Введите валидный адрес e-mail или'
                                   ' оставьте поле пустым')),
                    Length(1, 150),
                    Optional()],
    )
    feedback_text = TextAreaField(
        label='Текст обратной связи',
        validators=[DataRequired(message=('Текст обратной связи'
                                          ' - обязательное поле')),
                    Length(1, 5000)],
    )
    submit = SubmitField(label='Отправить')
