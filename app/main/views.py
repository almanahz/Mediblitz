from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, jsonify, request, flash
from flask_login import login_required
from . import main
from .forms import NameForm
from .. import db
from ..models import User, AnatomyQuestion, PhysiologyQuestion, BiochemistryQuestion, MicrobiologyQuestion, PharmacologyQuestion, ScoreTable
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

@main.route('/quiz_intro')
def quiz_intro():
    logged_in = session.get('user_id')
    return render_template('main/quiz_intro.html', logged_in=logged_in)

@main.route('/secret')
@login_required
def secret():
    return 'You are authorized to access this page'

@main.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    user = User.query.filter_by(id=session.get('user_id')).first()
    first_name = user.first_name

    if user is None:
        abort(404)

    quizzes = {'Anatomy': url_for('main.quiz', quiz='anatomy'), 
               'Physiology': url_for('main.quiz', quiz='physiology'), 
               'Biochemistry': url_for('main.quiz', quiz='biochemistry') 
               }
    
    quiz_names = ['anatomy', 'physiology', 'biochemistry', 'pharmacology', 'microbiology', 'general_questions']

    leaders = {}
    for quiz_name in quiz_names:
        leaders[quiz_name] = ScoreTable.get_top_scores(quiz_name)
    
    return render_template('main/user_page.html', first_name=first_name, quizzes=quizzes, leaderboard=leaders)

@main.route('/user/<quiz>', methods=['GET', 'POST'])
@login_required
def quiz(quiz):
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

            checker_list[question.id] = (question.question, question.answer)

            questions_list.append(question_dict)

        session['quiz_id'] = checker_list
        session['quiz_name'] = quiz
        return render_template('main/quiz.html', questions=questions_list, quiz_id=quiz_id, start=False)
    
@main.route('/user/result', methods=['GET', 'POST'])
@login_required
def result():
    user = User.query.filter_by(id=session.get('user_id')).first()
    question_ids = request.form.getlist('question_id')
    chosen_answers = {}
    for question_id in question_ids:
        chosen_answer = request.form.get(f'answer_{question_id}')
        chosen_answers[question_id] = chosen_answer
    
    score = 0
    checker_list = session.get('quiz_id')

    for question_id, chosen_answer in chosen_answers.items():
        if question_id in checker_list and chosen_answer == checker_list[question_id][1]:
            score += 1
    
    total_questions = len(question_ids)
    percentage_score = (score / total_questions) * 100
    user_score = ScoreTable(user_id=user.id, score=percentage_score, quiz_name=session.get('quiz_name'))
    db.session.add(user_score)
    db.session.commit()
    return render_template('main/result.html', questions=checker_list, chosen_answers=chosen_answers, percentage_score=percentage_score, )
    # return f'Quiz marked successfully. Your score: {percentage_score}%'