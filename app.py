# funcster\backend\app.py
import json
import os
from flask import Flask, abort, jsonify, request

from app_config import app
from models import db, Mentor, Coder, Snippet, User
from auth import AuthError, get_token_auth_header, has_scope, requires_auth


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

        # First, check to see if username is already being used in local bd, and abort with 409 (conflict) if so
        if Mentor.exists(username) or Coder.exists(username):
            abort(409)

       # Then, try to add new user to auth0 database:
        url = f'https://{AUTH0_DOMAIN}/dbconnections/signup'

        post_object = {
            "client_id" : AUTH0_CLIENT_ID,
            "email": email,
            "password": password,
            "connection": AUTH0_CONNECTION,
            "username": username,
            "user_metadata": {
                "role": usertype.title()
            }
        }

        auth0_response = requests.post(url, json = post_object)
        
        # If there was a problmem with auth0 process, abort:
        if hasattr(auth0_response, 'error'):
            abort(401)

        # Finally, if auth0 signup orcess successful,
        # insert user into local database:

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

# method used to get information for a user after they're looged in
# used by the front end's handleAuthentication() process to provide
# customization depending on usertype
@app.route('/userinfo/<username>')
@requires_auth
def get_user_info(username):
    
    # First, check to see if user is a Coder
    # If so, return relevant information for profile on front end
    coder = Coder.get_by_name(username)
    if coder:
        if coder.mentor:
            mentor = coder.mentor.username
        else:
            mentor = None
        
        if coder.snippets:
            snippets = [snippet.to_dict() for snippet in coder.snippets]
        else:
            snippets = []

        return jsonify({
            "success": True,
            "user_id": coder.id,
            "usertype": "Coder",
            "mentor": mentor,
            "snippets": snippets
        })
    
    # If not a coder, then check to see if user is a Mentor
    # If so, return relevant information for profile on front end
    mentor = Mentor.get_by_name(username)
    if mentor:
        coders = []
        if mentor.coders:
            coder_objs = mentor.coders 
            for coder in coder_objs:
                coders.append({ 
                    "username": coder.username, 
                    "id": coder.id,
                    "snippets": [snippet.to_dict() for snippet in coder.snippets if snippet.needs_review] 
                    })

        else:
            coders = []

        return jsonify({
            "success": True,
            "user_id": mentor.id,
            "usertype": "Mentor",
            "coders": coders
        })
    
    # If neither a coder nor a mentor is found, return 404 error
    abort(404)


# return all current coders
@app.route('/coders')
@requires_auth
def get_all_coders():
    
    try:
        coders = [coder.to_dict() for coder in Coder.query.all()]
        return jsonify ({
            "success": True,
            "coders": coders
        })
    except:
        abort(500)

@app.route('/coders/available')
@requires_auth
def get_available_coders():

    try:
        available_coders = [coder.to_dict() for coder in Coder.need_mentor()]

        return jsonify({
            "success": True,
            "coders": available_coders
        })
    except:
        abort(500)


# Route to add/update the mentor selected for a specific coder:
@app.route('/coder/<coder_id>/mentor', methods=['PATCH'])
@requires_auth
def select_mentor(coder_id):
    body = request.get_json()
    mentor_id = body.get('mentorId', None)
    if not mentor_id:
        abort(400)
    
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        abort(404)

    coder = Coder.query.get(coder_id)
    if not coder:
        abort(404)
    
    try:
        if coder.mentor_id:
            if (coder.mentor_id == mentor_id):
                return jsonify({
                    "success": True,
                    "message": "This mentor was already the mentor for this coder."
                })
            else:
                current_mentor = Mentor.query.get(coder.mentor_id)
                current_mentor.coders.remove(coder)
                current_mentor.update()
        
        mentor.coders.append(coder)
        mentor.update()
        return jsonify({
            "success": True,
            "message": "A new mentor has been selected for this coder."
        })
    except:
        abort(500)


# return all current mentors
@app.route('/mentors', methods=['GET'])
@requires_auth
def get_mentors():
    if has_scope("get:mentors"):
        try:
            mentors = [mentor.to_dict() for mentor in Mentor.query.all()]
            return jsonify ({
                "success": True,
                "mentors": mentors
            })
        except:
            abort(500)
    
    else:
        abort(403)

@app.route('/mentor/<mentor_id>/coder', methods=['PATCH'])
@requires_auth
def select_coder(mentor_id):

    body = request.get_json()
    coder_id = body.get('coderId', None)
    if not coder_id:
        abort(400)
    
    coder = Coder.query.get(coder_id)
    if not coder:
        abort(404)
    
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        abort(404)
    
    try:
        mentor.coders.append(coder)
        mentor.update()
        return jsonify({
            "success": True,
            "message": "A new coder has been added to your list of coders."
        })
    except:
        abort(500)


# endpoint to obtain information about a specific snippet:
@app.route('/snippet/<snippet_id>')
@requires_auth
def get_snippet(snippet_id):
    snippet = Snippet.query.get(snippet_id)
    if not snippet:
        abort(404)
    
    snippet = snippet.to_dict()
    snippet['success'] = True
    
    return jsonify(snippet)


# route to post new snippet to database
@app.route('/snippet', methods=['POST'])
@requires_auth
def post_new_snippet():
    
    if has_scope("post:snippet"):
        body = request.get_json()

        coderId = body.get('coderId', None)
        coder = Coder.query.get(coderId)
        
        if not coder:
            abort(404)
        
        attrs = {}
        attrs['snippet_name'] = body.get('name', None)
        attrs['code'] = body.get('code', None)
        attrs['needs_review'] = body.get('needsReview', False)
        attrs['comments'] = body.get('comments', '')

        if attrs['snippet_name'] and attrs['code']:
            try:
                snippet = Snippet(**attrs)
                # insert snippet by appending as a child to its coder and 
                # updating coder
                coder.snippets.append(snippet)
                coder.update()
                return jsonify({
                    "success": True,
                    "message": "Snippet has been successfully saved to database"
                })
            except:
                abort(500)
        
        else:
            abort(400)

    else:
        abort(403)


@app.route('/snippet/<snippet_id>', methods=['PATCH'])
@requires_auth
def post_revise_snippet(snippet_id):
    
    body = request.get_json()

    # check to be sure required fields (body and code) are in snippet,
    # if not, return a 400 error
    if not body.get('name') or  not body.get('code'):
        abort(400)

    # get basic information for next authorization tests
    coder_id = body.get('coderId', None)
    usertype = body.get('usertype', None)
    user_id = body.get('userId', None)

    # authorization checks - check specific id of user:
    # - if posted by a coder, make sure it is the snippet's owner and verify
    #   permissions from auth token:
    if usertype == 'Coder':
        if user_id != coder_id or not has_scope('edit:own:snippet'):
            abort(403)

    # - if posted by a mentor, make sure it is the mentor of the 
    #   snippet's owner and verify permissions from wuth token
    elif usertype == 'Mentor':
        coder = Coder.query.get(coder_id)
        if not coder:
            abort(400)
        if (coder.mentor_id != user_id) or not has_scope('edit:others:snippet'):
            abort(403)
    
    # - if usertype something other than Coder or Mentor, abort with 400 error
    else:
        abort(400)

    # Get the snippet (if not found, return 404 error)
    snippet = Snippet.query.get(snippet_id)
    if not snippet:
        abort(404)
    
    try:
        snippet.snippet_name = body.get('name')
        snippet.code = body.get('code')
        snippet.needs_review = body.get('needsReview', False)
        snippet.comments = body.get('comments', '')

        snippet.update()
        return jsonify({
            "success": True,
            "message": "Snippet has been successfully updated in database"
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

@app.errorhandler(403)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 403,
      "message": "You can't go there."
    }), 403

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


@app.errorhandler(AuthError)
def handle_auth_error(ex): 
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(port=5000)