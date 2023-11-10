from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ContactUs(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Your Name*'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Your Email*'})
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=20)], render_kw={'placeholder': 'Your Message*'})
    checkbox = BooleanField('Yes, I would like to receive communications by email about octamedic services.')
    submit = SubmitField('Submit')