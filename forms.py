from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class Itemform(FlaskForm):
    description = StringField('description', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    cat_id = SelectField('Category', validators=[DataRequired()], coerce=int)
