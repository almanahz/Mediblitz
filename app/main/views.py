from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, jsonify, request
from flask_login import login_required
from . import main
from .forms import NameForm
from .. import db
from ..models import User, AnatomyQuestion, PhysiologyQuestion, BiochemistryQuestion, MicrobiologyQuestion, PharmacologyQuestion
from uuid import uuid4
quiz_models = {
    'anatomy': AnatomyQuestion,
    'physiology': PhysiologyQuestion,
    'biochemistry': BiochemistryQuestion,
    'microbiology': MicrobiologyQuestion,
    'pharmacology': PharmacologyQuestion
}

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

    quizzes = {'Anatomy': url_for('main.quiz', email=email, quiz='anatomy'), 
               'Physiology': url_for('main.quiz', email=email, quiz='physiology'), 
               'Biochemistry': url_for('main.quiz', email=email, quiz='biochemistry') 
               }
    first = {'score': 20, 'name': 'Abdulsalam'}
    second = {'score': 20, 'name': 'Abdulsalam'}
    leaderboard = [(1, first), (2, second)]
    return render_template('main/user_page.html', email=email, quizzes=quizzes, leaderboard=leaderboard)

@main.route('/user/<email>/<quiz>')
@login_required
def quiz(email, quiz):
    quiz_id = str(uuid4())
    model = quiz_models.get(quiz)
    if model:
        result = model.query.order_by(db.func.rand()).limit(20).all()
        questions_list = []
        checker_list = {}
        for question in result:
            question_dict = {
                'question_id': question.id,
                'question_text': question.question,
                'option_A': question.option_A,
                'option_B': question.option_B,
                'option_C': question.option_C,
                'option_D': question.option_D,
            }

            checker_list[question.id] = question.answer

            questions_list.append(question_dict)

        session[quiz_id] = checker_list
        return render_template('main/quiz.html', questions=questions_list, quiz_id=quiz_id)
    
@main.route('/user/<email>/<quiz>/result', methods=['GET', 'POST'])
@login_required
def result(email, quiz):
    model = quiz_models.get(quiz)
    if model:
        question_ids = request.form.getlist('question_id')
        chosen_answers = {}
        for question_id in question_ids:
            chosen_answer = request.form.get(f'answer_{question_id}')
            chosen_answers[question_id] = chosen_answer
        
        score = 0
        checker_list = session.get(quiz_id)
        index = 0
        for question_id, chosen_answer in chosen_answers.items():
            if question_id in checker_list and chosen_answer == checker_list[question_id]:
                score += 1
        
        total_questions = len(question_ids)
        percentage_score = (score / total_questions) * 100
        return f'Quiz marked successfully. Your score: {percentage_score}%'