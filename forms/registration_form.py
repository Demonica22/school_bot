from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    surname = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    repeat_password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()

