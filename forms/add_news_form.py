from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired

class AddNewsForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    data = StringField()
    files = MultipleFileField()
    submit = SubmitField()