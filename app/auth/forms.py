from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(),
                                                       Length(1, 64)])
    other_names = StringField('Other Names', validators=[DataRequired(),
                                                         Length(1, 64),])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm_password',
                                                             message='Passwords must match.')])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                    validators=[DataRequired()])
        
    def email_validate(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

        
class Change_Password(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(),
                                            EqualTo('confirm_new_password',
                                                    message='Passwords must match.')])
    confirm_new_password = PasswordField('Confirm New password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Forgotten_Password(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                        Email()])
class Forgotten_Password_Update(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(),
                                EqualTo('confirm_new_password',
                                                    message='Passwords must match.')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Submit')



