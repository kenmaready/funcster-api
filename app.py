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
    email = body.get('email', None)
    password = body.get('password', None)

    # proceed only if both required fields are provided
    if username and usertype:

        # first check to see if username is already being used, and abort with 409 (conflict) if so
        if Mentor.exists(username) or Coder.exists(username):
            abort(409)

        # TODO: SEND TO AUTH0 TO REGISTER AS NEW USER, WITH MENTOR OR CODER ROLE ASSIGNED

        # On Success at auth), add to our dtabase:

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

# route to post new snippet to database
@app.route('/coders/<int:coder_id>/snippets', methods=['POST'])
def post_snippet(coder_id):
    body = request.get_json()

    attrs = {}
    attrs['snippet_name'] = body.get('snippetName', None)
    attrs['code'] = body.get('code', None)
    attrs['needs_review'] = body.get('needsReview', False)

    if attrs['snippet_name'] and attrs['code']:
        try:
            snippet = Snippet(**attrs)
            snippet.insert()
            return jsonify({
                "success": True,
                "message": "Snippet has been successfully saved to database"
            })
        except:
            abort(500)
    
    else:
        abort(400)

# return all current coders
@app.route('/coders', methods=['GET'])
def get_coders():
    
    try:
        coders = [coder.to_dict() for coder in Coder.query.all()]
        return jsonify ({
            "success": True,
            "coders": coders
        })
    except:
        abort(500)

# return all current mentors
@app.route('/mentors', methods=['GET'])
def get_mentors():
    
    try:
        mentors = [mentor.to_dict() for mentor in Mentor.query.all()]
        return jsonify ({
            "success": True,
            "mentors": mentors
        })
    except:
        abort(500)


# route to quell 404 errors from favicon requests when serving api separately
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


#----------------------------------------------------------------------------#
# Error Handler Routes
#----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "You may have to come to terms with the very real possibility that the resource you are seeking does not exist."
    }), 404


@app.errorhandler(409)
def conflict(error):
    return jsonify({
      "success": False,
      "error": 409,
      "message": "I feel conflicted. There is already a user by that name in my database, and so I must regretfully decline to honor your request."
    }), 409


@app.errorhandler(500)
def internal_server(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "I have to tell you something. I've screwed up somehow. I was unable to process your request.  It's not you ... it's me."
    }), 500


@app.errorhandler(AuthError)
def not_authorized(AuthError):
  return jsonify({
    "success": False,
    "error": AuthError.status_code,
    "message": AuthError.error['description']

  }), AuthError.status_code

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(port=5000)