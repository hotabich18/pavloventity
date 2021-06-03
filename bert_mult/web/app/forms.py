from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email


class EditType(FlaskForm):
    name = StringField("B-Имя: ", validators=[DataRequired()])
    i = StringField("I-Имя: ", validators=[DataRequired()])
    color = StringField("Цвет", validators=[DataRequired()])
    description = StringField("Описание", validators=[DataRequired()])
    submit = SubmitField("Изменить")