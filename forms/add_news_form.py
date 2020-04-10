from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, MultipleFileField, TextAreaField
from wtforms.validators import DataRequired

class AddNewsForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    data = TextAreaField()
    files = MultipleFileField()
    submit = SubmitField()