from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email


class AddType(FlaskForm):
    name = StringField("Название сущности: ", validators=[DataRequired()])
    color = StringField("Цвет", validators=[DataRequired()])
    description = StringField("Описание", validators=[DataRequired()])
    submit = SubmitField("Добавить")