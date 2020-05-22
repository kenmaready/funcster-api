import json
import os

from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

from app_config import app

db = SQLAlchemy(app)

'''
User - generic User base class (can be further modelled into Mentor or Coder)
     - used to avoid duplication of methods, as well as to require unique username at user level
'''
class User(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True)

    '''
    insert()
        inserts a new user into a database
        user must have a unique username
        user must have a unique id or null id
        EXAMPLE
            mentor = Mentor(username = 'codeninja1')
            mentor.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a user from a database
        user must exist in the database
        EXAMPLE
            coder = Coder.query.get(13)
            coder.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a user in a database
        the user must exist in the database
        EXAMPLE
            mentor = Mentor.query.get(7)
            mentor.username = 'codedevil23'
            mentor.update()
    '''
    def update(self):
        db.session.commit()

    '''
    exists(username)
        checks to see whether a particular username already exists in the table
        EXAMPLE
            mentor.exists('codedevil23')
    '''
    @classmethod
    def exists(cls, username):
        return cls.query.filter_by(username=username).scalar() is not None


'''
Mentor - User who reviews code of Coders
         Each Mentor can have many Coders
'''
class Mentor(User):
    __tablename__ = 'mentors'
    coders = db.relationship('Coder', backref='mentor', lazy=True)

    '''
    to_dict(): Method for returning dictionarified version of a Mentor
    '''
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "coders": self.coders
        }


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
    to_dict(): Method for returning dictionarified version of a Coder
    '''
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            #"snippets": self.snippets,
            "mentor_id": self.mentor_id
        }


'''
Snippet - Code function or class written and stored by Coder and Reviewed by Mentor
'''
class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snippet_name = db.Column(db.String(24))
    code = db.Column(db.String())
    code_type = db.Column(db.String())
    coder_id = db.Column(db.Integer, db.ForeignKey('coders.id'))

    '''
    insert()
        inserts a new code snippet into a database
        snippet must have a unique id or null id
        snippet must have code and be associated with a coder
        EXAMPLE
            code = Code(snippet_name = 'addition', code='def add(x,y):\\n\\treturn (x+y)', code_type='function', coder_id=17)
            code.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a code snippet from a database
        snippet must exist in the database
        EXAMPLE
            snippet = Snippet.query.get(37)
            snippet.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a code snippet in a database
        the snippet must exist in the database
        EXAMPLE
            snippet = Snippet.query.get(21)
            snippet.code = 'def add(x,y,z):\\n\\treturn (x+y+z)'
            snippet.update()
    '''
    def update(self):
        db.session.commit()



db.create_all()
