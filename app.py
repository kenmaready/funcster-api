# funcster\backend\app.py
import os
from flask import Flask, abort, jsonify, request

from app_config import app
from models import db, Mentor, Coder, Snippet, User


@app.route('/')
def index():
    return jsonify({
    "success": True,
    "message": "welcome to funcster."
    })

# route for new user signup. requires a username, email address and a status of mentor/coder
@app.route('/signup', methods=['POST'])
def signup_user():

    # get body of request; if nothing included, abort with 400
    body = request.get_json()
    if not body:
        abort(400)

    # set attributes for new User based on body input
    username = body.get('username', None)
    usertype = body.get('usertype', None)

    # proceed only if both required fields are provided
    if username and usertype:

        # first check to see if username is already being used, and abort with 409 (conflict) if so
        if Mentor.exists(username) or Coder.exists(username):
            abort(409)

        # instantiate a new object for the new user
        if usertype == 'mentor':
            user = Mentor(username = username)
        if usertype == 'coder':
            user = Coder(username = username)
        
        # try to add the new user to the applicable table in the database
        try:
            user.insert()
        except:
            abort(500)
    
    # if required fields weren't provided in the request, abort with 400
    else:
        abort(400)
    
    return jsonify({
        "success": "True",
        "user_id": user.id
    })


@app.route('/code', methods=['POST'])
def add_new_snippet():
    body = request.get_json()
    snippet = body.get('snippet', None)
    snippet_type = body.get('snippet_type', None)


# route to quell 404 errors from favicon requests when serving api separately
@app.route('/favicon.ico')
def favicon():
    return send_static_file('favicon.ico')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(port=5000)