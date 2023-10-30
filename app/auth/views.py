from flask import render_template
from . import auth
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm
from .forms import RegistrationForm


@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            email = request.form.get('email')
            return redirect(url_for('main.user', email=email))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        user = User(first_name=form.first_name.data,
                    other_names=form.other_names.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    gender=form.gender.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/registration.html', form=form)

