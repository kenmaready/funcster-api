# funcster\backend\app.py
import json
import os
from functools import wraps
import requests
from flask import Flask, abort, jsonify, request, _request_ctx_stack
from six.moves.urllib.request import urlopen
from jose import jwt

from app_config import app
from models import db, Mentor, Coder, Snippet, User

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CONNECTION = os.environ['AUTH0_CONNECTION']
API_IDENTIFIER = os.environ['API_IDENTIFIER']
ALGORITHMS = ["RS256"]


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex): 
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    print(request.headers)
    auth = request.headers.get("Authorization", None)
    print('auth: ', auth)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)

    if unverified_claims.get("permissions"):
        token_scopes = unverified_claims.get("permissions")
        for token_scope in token_scopes:
            print(token_scopes)
            if token_scope == required_scope:
                return True
    return False


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        print('requires_auth() called...')
        token = get_token_auth_header()
        print("get_token_auth_header() returned token: ", token)
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


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
        print("url:", url)

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
        print("post_object:", post_object)

        auth0_response = requests.post(url, json = post_object)
        print(auth0_response.text)
        
        # If there was a problmem with auth0 process, abort:
        if hasattr(auth0_response, 'error'):
            print(auth0_response.error)
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

# return all current coders
@app.route('/coders', methods=['GET'])
@requires_auth
def get_coders():
    
    try:
        coders = [coder.to_dict() for coder in Coder.query.all()]
        return jsonify ({
            "success": True,
            "coders": coders
        })
    except:
        abort(500)

@app.route('/coders/<username>')
@requires_auth
def get_coder(coder_username):

    pass

# return all current mentors
@app.route('/mentors', methods=['GET'])
@requires_auth
def get_mentors():
    print("get_mentors() endpoint has been called...")
    if requires_scope("get:mentors"):
        print("you're in!!!!")
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

# method used to get information for a user after they're looged in
# used by the front end's handleAuthentication() process to provide
# customization depending on usertype
@app.route('/userinfo/<username>')
@requires_auth
def get_user_info(username):
    
    check_coders = Coder.get_by_name(username)
    if check_coders:
        if check_coders.mentor:
            mentor = check_coders.mentor.username
        else:
            mentor = None
        
        if check_coders.snippets:
            snippets = [snippet.to_dict() for snippet in check_coders.snippets]
        else:
            snippets = []
        print(snippets)

        return jsonify({
            "success": True,
            "user_id": check_coders.id,
            "usertype": "Coder",
            "mentor": mentor,
            "snippets": snippets
        })
    
    check_mentors = Mentor.get_by_name(username)
    if check_mentors:
        return jsonify({
            "success": True,
            "user_id": check_mentors.id,
            "usertype": "Mentor"
        })
        
    abort(404)

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
@app.route('/snippet/new', methods=['POST'])
@requires_auth
def post_new_snippet():
    print('post_new_snippet() called...')
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
            print(snippet.to_dict())
            # insert snippet by appending as a child to its coder and 
            # updating coder
            print(coder.to_dict())
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

@app.route('/snippet/<snippet_id>', methods=['POST'])
@requires_auth
def post_revised_snippet(snippet_id):
    print('post_revised_snippet() called...')
    body = request.get_json()
    print(body)

    snippet = Snippet.query.get(snippet_id)
    if not snippet:
        abort(404)
    
    if not body.get('name') or  not body.get('code'):
        abort(400)

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(port=5000)