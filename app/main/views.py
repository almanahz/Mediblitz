from flask import render_template, session, redirect, url_for, abort, request, flash, current_app
from flask_login import login_required
from . import main
from .forms import ContactUs
from .. import db
from ..models import User, AnatomyQuestion, PhysiologyQuestion, BiochemistryQuestion, MicrobiologyQuestion, PharmacologyQuestion, ScoreTable, GeneralQuestion, PathologyQuestion
from flask_mail import Message
from .. import mail

quiz_models = {
    'anatomy': AnatomyQuestion,
    'physiology': PhysiologyQuestion,
    'biochemistry': BiochemistryQuestion,
    'microbiology': MicrobiologyQuestion,
    'pharmacology': PharmacologyQuestion,
    'general': GeneralQuestion,
    'pathology': PathologyQuestion
}

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact_page():
    form = ContactUs()
    if form.validate_on_submit():
        msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + 'hello',
                    sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[current_app.config['MAIL_USERNAME']])
        msg.body=str(form.message.data)
        mail.send(msg)
        flash("Your Message has been delivered, Thank You!")
    return render_template('main/contact_page.html', form=form)

@main.route('/blog')
def blog():
    return render_template('error/construct.html')

@main.route('/about')
def about():
    return render_template('error/construct.html')

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
    verified = user.is_verified
    first_name = user.first_name

    if user is None:
        abort(404)

    quizzes = {'Anatomy': url_for('main.quiz', quiz='anatomy'), 
               'Physiology': url_for('main.quiz', quiz='physiology'), 
               'Biochemistry': url_for('main.quiz', quiz='biochemistry'),
               'Pathology': url_for('main.quiz', quiz='pathology'),
               'General': url_for('main.quiz', quiz='general'),
               'Microbiology': url_for('main.quiz', quiz='microbiology'),
               'Pharmacology': url_for('main.quiz', quiz='pharmacology')
               }
    
    quiz_names = ['anatomy', 'physiology', 'biochemistry', 'pharmacology', 'microbiology', 'general', 'pathology']

    leaders = {}
    for quiz_name in quiz_names:
        leaders[quiz_name] = ScoreTable.get_top_scores(quiz_name)
    return render_template('main/user_page.html', first_name=first_name, quizzes=quizzes, \
                           verified=verified, leaderboard=leaders)

@main.route('/user/<quiz>', methods=['GET', 'POST'])
@login_required
def quiz(quiz):

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

        session['quiz_name'] = quiz
        return render_template('main/quiz.html', questions=questions_list, start=False, quiz=quiz)
    
@main.route('/user/result', methods=['GET', 'POST'])
@login_required
def result():
    quiz_name = session.get('quiz_name')
    user = User.query.filter_by(id=session.get('user_id')).first()
    
    question_ids = request.form.getlist('question_id')
    
    chosen_answers = {}
    correct_answers = {}
    for question_id in question_ids:
        answer_dict = quiz_models[quiz_name].query.filter_by(id=question_id).first()
        correct_answers[question_id] = (answer_dict.question, answer_dict.answer, answer_dict.get_answer_text())
        chosen_answer = request.form.get(f'answer_{question_id}')
        chosen_answers[question_id] = (chosen_answer, answer_dict.get_chosen_answer(chosen_answer))

    
    score = 0

    for question_id, chosen_answer in chosen_answers.items():
        if question_id in correct_answers and chosen_answer[0] == correct_answers[question_id][1]:
            score += 1
   
    total_questions = len(question_ids)
    
    try:
        percentage_score = (score / total_questions) * 100
    except:
        return redirect(url_for('main.user'))

    user_score = ScoreTable(user_id=user.id, score=percentage_score, quiz_name=session.get('quiz_name'))
    db.session.add(user_score)
    db.session.commit()

    score = percentage_score
    score_remarks = {
        (0, 12.5): "Keep going! Every step counts towards progress. You've got this!",
        (12.6, 25): "Great effort! Stay determined and you'll see improvement in no time.",
        (25.1, 37.5): "Well done! You're making strides forward. Keep up the good work!",
        (37.6, 50): "Congratulations on your progress! Your hard work is paying off. Keep pushing yourself!",
        (50.1, 62.5): "Fantastic job! You're getting closer to mastery. Keep up the excellent work!",
        (62.6, 75): "Impressive work! You're doing great. Keep challenging yourself to reach new heights!",
        (75.1, 87.5): "Outstanding performance! You're truly excelling in this area. Keep up the amazing work!",
        (87.6, 100): "Incredible achievement! You're a true expert. Keep up the exceptional work and inspire others!"
    }
    remark = next((remark for (min_score, max_score), remark in score_remarks.items() \
                   if min_score <= score <= max_score), "Invalid score")

    return render_template('main/result.html', correct_answers=correct_answers,\
                           chosen_answers=chosen_answers,\
                            percentage_score=percentage_score, remark=remark)

    