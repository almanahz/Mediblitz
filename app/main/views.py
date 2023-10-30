from datetime import datetime
from flask import render_template, session, redirect, url_for, abort
from flask_login import login_required
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')

@main.route('/secret')
@login_required
def secret():
    return 'You are authorized to access this page'

@main.route('/user/<email>')
@login_required
def user(email):
    email = User.query.filter_by(email=email).first()

    if email is None:
        abort(404)

    quizzes = ['Anatomy', 'Physiology', 'Biochemistry']
    first = {'score': 20, 'name': 'Abdulsalam'}
    second = {'score': 20, 'name': 'Abdulsalam'}
    leaderboard = [(1, first), (2, second)]
    return render_template('main/user_page.html', email=email, quizzes=quizzes, leaderboard=leaderboard)
        