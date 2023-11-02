#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    first_name = db.Column(db.String(64))
    other_names = db.Column(db.String(64))
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    gender=db.Column(db.Enum('male', 'female', 'other'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        print(self.password_hash)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"{self.username}"

class BaseQuestion(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option_A = db.Column(db.String(64), nullable=False)
    option_B = db.Column(db.String(64), nullable=False)
    option_C = db.Column(db.String(64), nullable=False)
    option_D = db.Column(db.String(64), nullable=False)
    answer = db.Column(db.String(64), nullable=False)


class AnatomyQuestion(BaseQuestion):
    __tablename__ = 'anatomy_questions'

class PhysiologyQuestion(BaseQuestion):
    __tablename__ = 'physiology_questions'

class PharmacologyQuestion(BaseQuestion):
    __tablename__ = 'pharmacology_questions'

class GeneralQuestion(BaseQuestion):
    __tablename__ = 'general_questions'

class BiochemistryQuestion(BaseQuestion):
    __tablename__ = 'biochemistry_questions'
 
class MicrobiologyQuestion(BaseQuestion):
    __tablename__ = 'microbiology_questions'

class ScoreTable(db.Model):
    __tablename__ = 'scoretable'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    quiz_name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = relationship('User')

    @staticmethod
    def get_top_scores(quiz_name, limit=1):
        top_scores = db.session.query(ScoreTable.score, User.first_name, User.other_names).\
            join(User, ScoreTable.user_id == User.id).\
            filter(ScoreTable.quiz_name == quiz_name).\
            order_by(desc(ScoreTable.score)).\
            limit(limit).\
            all()
        return top_scores