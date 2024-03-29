#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import relationship
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
import hashlib
from flask import request
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    first_name = db.Column(db.String(64))
    other_names = db.Column(db.String(64))
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    gender=db.Column(db.Enum('male', 'female', 'other'))
    is_verified = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def l_seen(self):
        return datetime.strftime(self.last_seen, '%d-%b-%Y')
    def m_since(self):
        return datetime.strftime(self.member_since, '%d-%b-%Y')
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
    def can(self, permissions):
        return self.role is not None and \
        (       self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url, hash=hash, size=size, default=default, rating=rating)
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

    def generate_confirmation_token(self, user_id, expiration='3600'):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': user_id})
    
    @staticmethod
    def confirm(token):
        s=Serializer(current_app.config['SECRET_KEY'], '3600')
        try:
            data = s.loads(token)
            user_id = data.get('confirm')
            user = User.query.get(user_id)
        except:
            return False
        if user:
            user.is_verified = True
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f"{self.first_name}"

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
    

class BaseQuestion(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option_A = db.Column(db.String(64), nullable=False)
    option_B = db.Column(db.String(64), nullable=False)
    option_C = db.Column(db.String(64), nullable=False)
    option_D = db.Column(db.String(64), nullable=False)
    answer = db.Column(db.String(64), nullable=False)

    
    
    def get_chosen_answer(self, option):
        if option == 'A':
            return self.option_A
        elif option == 'B':
            return self.option_B
        elif option == 'C':
            return self.option_C
        elif option == 'D':
            return self.option_D
        else:
            return None
        
    def get_answer_text(self):
        if self.answer == 'A':
            return self.option_A
        elif self.answer == 'B':
            return self.option_B
        elif self.answer == 'C':
            return self.option_C
        elif self.answer == 'D':
            return self.option_D
        else:
            return None
        

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
            Permission.COMMENT |
            Permission.WRITE_ARTICLES, True),
        'Moderator': (Permission.FOLLOW |
            Permission.COMMENT |
            Permission.WRITE_ARTICLES |
            Permission.MODERATE_COMMENTS, False),
        'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

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

class PathologyQuestion(BaseQuestion):
    __tablename__ = 'pathology_questions'


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
    
class TokenUsed(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),\
                           nullable=False)
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(255))
    headline = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def blog_timestamp(self):
        return datetime.strftime(self.timestamp, '%d-%b-%Y')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def blog_timestamp(self):
        return datetime.strftime(self.timestamp, '%d-%b-%Y')
