from flask import render_template
from . import auth
from flask import render_template, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from .. import db
from ..models import User, TokenUsed
from .forms import LoginForm, RegistrationForm, Change_Password, Forgotten_Password, Forgotten_Password_Update
from ..email import send_mail, send_async_email
from itsdangerous import URLSafeTimedSerializer as Serializer

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('main.user'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()

    session_data = ['user_id', 'quiz_name', 'quiz_id']
    for data in session_data:
        if session.get(data):
            del(session[data])
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                form.email_validate(form.email)
            except:
                heading = "Email already registered"
                message = "Email has already been registered, kindly proceed to the login page to sign in"
                return render_template('auth/status.html', message=message, heading=heading)
            user = User(first_name=form.first_name.data,
                        other_names=form.other_names.data,
                        email=form.email.data,
                        password=form.password.data,
                        gender=form.gender.data)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token(user.id)
            send_mail(current_app, user.email, 'Confirm Your Account', 'auth/conf_email', user=user, token=token)
            flash('A confirmation email has been sent to your registered email address')
            flash('You can now login.')
            return redirect(url_for('auth.login'))

    return render_template('auth/registration.html', form=form)
    

@auth.route('/verification', methods=['GET', 'POST'])
@login_required
def verification():
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        token = user.generate_confirmation_token(user.id)
        send_mail(current_app, user.email, 'Confirm Your Account', 'auth/conf_email', user=user, token=token)
        flash('A confirmation email has been sent to you by your registered email')
        token = TokenUsed(token=token)
        db.session.add(token)
        db.session.commit()
        return redirect(url_for('main.user'))
    return redirect(url_for('auth.register'))

@auth.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    token_stat = TokenUsed.query.filter_by(token=token).first()
    if token_stat.is_used or token_stat is None:
        return "Link has already been used"
    conf = User.confirm(token)
    if conf:
        token_stat.is_used = True
        db.session.commit()
        heading = 'Congratulations, Your Email has been verified'
        message = 'Your email address has been successfully verified.\
                    You can now access all the features of our platform.'
        return render_template('auth/status.html', heading=heading, message=message)
    return "Invalid link or link has already expired"

@auth.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = Change_Password()
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if request.method == 'POST':
        if user.verify_password(form.current_password.data):
            user.password = form.new_password.data
            db.session.commit()
            flash("Your password has been changed succesfully")
            return redirect(url_for('main.user'))
        else:
            flash("Your current Password is incorrect")

    if user.is_verified is True:
        return render_template('auth/change_password.html')
    return "Only verified Users can change password, kindly verify your account"
            
@auth.route('/user/forgot_password/', methods=['GET', 'POST'])
def forgotten_password():
    form = Forgotten_Password()
    if request.method == 'POST':
        email = form.email.data
        try:
            user=User.query.filter_by(email=email).first()
            s = Serializer(current_app.config['SECRET_KEY'], '3600')
            if user.is_verified is True:
                token = s.dumps({'email': user.email})
                send_mail(current_app, user.email, 'Password Reset', 'auth/email_forgot_password', name=user.first_name,token=token)
                token = TokenUsed(token=token)
                db.session.add(token)
                db.session.commit()
                flash("A password reset mail has been sent to email")
            else:
                return "Account Not Yet verified"
        except AttributeError:
            return "Sorry! Email is not yet registered or Email is not Yet Verified"
        except:
            return "Sorry! There is an issue sending the email"
        
    return render_template('auth/forgotten_password.html')

@auth.route('/user/change_pword_forgotten/<token>', methods=['GET', 'POST'])
def change_pword_forgotten(token):
    if token:
        s = Serializer(current_app.config['SECRET_KEY'], '3600')
        form = Forgotten_Password_Update()
        data = s.loads(token)
        if request.method == 'POST':
            token_stat = TokenUsed.query.filter_by(token=token).first()
            if token_stat.is_used or token_stat is None:
                return "Link has already been used"
            if form.validate_on_submit():
                try:
                    data = s.loads(token)
                    email = data.get('email')
                    user=User.query.filter_by(email=email).first()
                    user.password = form.new_password.data
                    db.session.commit()
                    flash("Password Successfully changed!")
                    token_stat.is_used = True
                    db.session.commit()
                    return redirect(url_for('auth.login'))
                except:
                    return "Email has not yet been registered or Token is invalid"
        return render_template('auth/forg_new_password.html', form=form)
