import json
import os

from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

from app_config import app

db = SQLAlchemy(app)

'''
User - generic User base class (can be further modelled into Mentor or Coder)
'''
class User(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True)

'''
Mentor - User who reviews code of Coders
         Each Mentor can have many Coders
'''
class Mentor(User):
    __tablename__ = 'mentors'
    coders = db.relationship('Coder', backref='mentor', lazy=True)


'''
Coder - User who writes and stores functions & classes
        Each coder has one Mentor
        Each coder can have many Snippets
'''
class Coder(User):
    __tablename__ = 'coders'
    snippets = db.relationship('Snippet', backref='coder', lazy=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))


'''
Snippet - Code function or class written and stored by Coder and Reviewed by Mentor
'''
class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snippet_name = db.Column(db.String(24))
    coder_id = db.Column(db.Integer, db.ForeignKey('coders.id'))


db.create_all()
