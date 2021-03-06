import json
import os

from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def setup_db(app, database_path=os.environ.get('DATABASE_URL')):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    db.app = app
    db.init_app(app)
    db.create_all()

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
    get_by_name(username)
        searches for a user by user name and returns the user if found
    '''
    @classmethod
    def get_by_name(cls, username):
        return cls.query.filter_by(username=username).first()


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
            "coders": [coder.to_dict() for coder in self.coders]
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
            "snippets": [snippet.to_dict() for snippet in self.snippets],
            "mentor_id": self.mentor_id
        }
    
    '''
    need_mentors(): Class Method for returning all coders who don't have a Mentor
    '''
    @classmethod
    def need_mentor(cls):
        return cls.query.filter_by(mentor_id=None)


'''
Snippet - Code function or class written and stored by Coder and Reviewed by Mentor
'''
class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snippet_name = db.Column(db.String(200))
    code = db.Column(db.String())
    needs_review = db.Column(db.Boolean, default=False)
    comments = db.Column(db.String())
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

    ''' to_dict() 
        returns dictionarified version of a snippet
    '''
        
    def to_dict(self):
        return {
            "id": self.id,
            "snippet_name": self.snippet_name,
            "code": self.code,
            "needs_review": self.needs_review,
            "comments": self.comments,
            "coder_id": self.coder_id
        }

