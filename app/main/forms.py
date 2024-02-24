from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FileField
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

class EditProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[Length(0, 64)])
    other_names = StringField('Other name(s)', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[Length(0, 64)])
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')
    category = StringField('Category', validators=[Length(0, 64)])
    image = FileField('Image')

    