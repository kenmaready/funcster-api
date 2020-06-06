# </> funcster-api

![funcster logo](logo.png)

## Introduction

Funcster-api is the back end of a capstone project for the Udacity Full-Stack Developer Nanodegree. The repository for the front end of the project is [here](https://github.com/kenmaready/funcster).

funcster is a simple app allowing 'Coders' to post, store and edit snippets of python code in their own snippet library, and their 'Mentors' to view, revise and comment on that code.

The project utilizes auth0 for authentication and some authorization, and postgresql as a database for the back end. The back end is built in python, using the flask framework with flask-sqlalchemy as an ORM to manage and connect with the database.

The project is currently deployed on heroku:

-   front end: [funcster.herokuapp.com](https://funcster.herokuapp.com/)
-   back end/api: [funcster-api.herokuapp.com](https://funcster-api.herokuapp.com/)

## Overview

The application has two types of users: 'Mentors' and 'Coders'. Coders can write and save code snippets (python functions and classes), select a mentor and ask their mentor to review their code. Mentors can select coders and review code posted by their coders who have asked for review. When reviewing, Mentors can edit the code and can also leave notes for their coders.

Each Coder can only have one Mentor, but each Mentor can have many Coders. Each Coder can have many Snippets, but each Snippet belongs to one Coder.

### Udacity Reviewer Testing

For ease of reviewing, on the deployed app at heroku, I've created three Coder users (coder1, coder2 and coder3) and three Mentor users (mentor1, mentor2 and mentor3) which are already registered on auth0, each having the simple password '123456'. I've also left a console.log() of their access tokens within the deployed application, so if the tokens I provide you have expired or don't work when you try to review my app, you can go to the deployed front end at [funcster.herokuapp.com](https://funcster.herokuapp.com/), log in with a user and use chrome development tools to view the console and get a newly-generated valid access token. For example, you could log in with coder1 to get a "Coder" access token, and mentor1 to get a "Mentor" access token. Access tokens should remain valid for 24 hours.

Also, for purposes of this review, I've published the .env file in the repository, so you will not need to set all the environment variables described below, they will be set for you if you have dotenv installed on your machine. There is a valid 'Coder' access token and a valid 'Mentor' access token in the .env file which you can use for testing.

### Getting Started

After downloading/cloning the projects, you should run `pip install -r requirements.txt` to be sure that you have the required dependencies available in your environment.

You will also need to set some environment variables in order to get the app to work. You can do so manually in your CLI using 'export' (or 'set' on Windows machines) for each of the variables, or you can create a file named '.env' in the root folder for this project and define the variables in that file. If you use the second menthod, in order to have flask automatically pick up the variables in your .env file, you will need to have `dotenv` installed locally to use the .env file, so if you do not have it, run `pip install python-dotenv` from your command line to install it. After installing dotenv, Flask will automatically run the .env file each time you use `flask run`.

The environment variables you will need to set are:

```
FLASK_APP=app.py
FLASK_DEBUG=True
FLASK_ENV=development
DATABASE_URL={path to your local postgres database for this app, including any needed password}
TEST_DATABASE_URL={ path to your local postgres testing database, which should be separate from your regular database (only needed for test_app.py)}

AUTH0_DOMAIN=funcster.auth0.com
API_AUDIENCE=funcster-auth0-api

AUTH0_CLIENT_ID={the auth0 client ID for your funcster application on auth0}
AUTH0_CONNECTION={the name of the auth0 database you will use to store user information. If you go with the default provided by auth0, it will be 'Username-Password-Authentication'}
API_IDENTIFIER={the auth0 identifier for the auth0 API you'll be using to get user info}

AUTH0_CODER_TOKEN={a valid JWT access token provided for a Coder registered on the application (only needed for test_app.py)}
AUTH0_MENTOR_TOKEN={ valid JWT access token provided for a Mentor registered on the application (only needed for test_app.py)}
```

Once requirements have been installed and environment variables defined, run the app by running `run flask` in the root folder. If run locally, the api will be served on [http://localhost:5000](http://localhost:5000). The endpoints are all defined and described in the app.py file. Many of the endpoints are restricted and require authentification with a working jwt access token from auth0. In some cases, the endpoints require certain permissions which are provided in the token.

### Technologies

Funcster-api is built using:

-   **SQLAlchemy ORM** as our ORM layer
-   **PostgreSQL** as our database
-   **Python3** and **Flask** as our server language and server framework
-   **Flask-Migrate** for creating and running schema migrations

### Using the API: Endpoints

The endpoints in the API are:

-   '/' (GET)

_just returns a success message to let you know you are communicating with the
funcster-api._

-   '/signup' (POST)

_runs through the signup process to register a new user with auth0 and with the
postgresql database. Expects data in the body of the request with the following
information:_\
_'usertype' {either 'coder' or 'mentor'}_\
_'username'_\
_'password'_\
_'email'_

_will check to see if there is already a conflicting username (in which case it will
return a 409 error), and then attempt to register the user with auth0 and if that
succeeds, will register the user in the api's postgresql database as either a mentor
or a coder, as applicable. If successful, returns a JSON object with "success": True
and a "message" indicating that the signup was successful._

-   '/userinfo/<username>' (GET)

_returns profile information for a user based upon the username passed in the URL.
Does not expect any information in the body of the request, but does require an Authorization
header with a Bearer token (which is a valid jwt Auth0 access token) having the appropriate
permission (either a Coder or Mentor access token will carry the needed permission). Searches
the Mentor & Coder database tables to see if the username exists and if not will return a 404
error. If successful, returns a JSON object with information about the user. The exact information
depends on whether the user is a Mentor or a Coder, and will include:_

_for a Coder:_

-   _"success": True_
-   _"user_id": {the Coder's ID from the Coder table in the postgresql database}_
-   _"usertype": "Coder"_
-   _"mentor": {the username (string) of the coder's mentor - if the coder does not have a
    mentor, this will be null}_
-   _"snippets": {a list of snippets, with each snippet in JSON form - if the coder does not
    yet have any snippets, will be an empty list}_

_for a Mentor:_

-   _"success": True_
-   _"user_id": {the Mentor's ID from the Mentor table in the postgresql database}_
-   _"usertype": "Mentor"_
-   _"coders": {a list of coders (if any) belonging to this Mentor. Each coder in the list is
    provided as a JSON object with the coder's username, ID and a list of any snippets}_

-   '/coders' (GET)

_returns a list of all coders in the database. Does not expect any information in the body of the request, but does require an Authorization header with a Bearer token (which is a valid jwt Auth0 access token) having the proper permission (only a Mentor token has the proper permission for this endpoint). Returns a JSON object with a "success" key having a value of true, and a list of coders, each of which is a JSON object containing the information about each coder stored in the postgresql database (id, username, mentor_id, snippets)_

-   '/coders/available' (GET)

_similar to '/coders' (see above), but provides list of only those coders who do not currently have a Mentor associated with them. Same Authorization header and permissions required as for the '/coders' endpoint._

-   '/coder/<coder_id>/mentor' (PATCH)

_this endpoint allows a Coder to select a Mentor. It requires an Authorization header with a valid Auth0 jwt 'Coder' access token. The coder's id is to be included in
the URL of the request, and this expects a body with
a 'mentorId' consisting of the selected mentor's ID from the
Mentor table of the postgresql database. If successfule,
returns a JSON object with 'success' equal to true, and a message verifying that the mentor was successfully added._

-   '/mentors' (GET)

_this endpoint returns a list of mentors, with each mentor represented as a JSON object containing the mentor's information from the Mentor table of the postgresql database (id, username, coders (which is a list of coder JSONs)). This endpoint requires an Authorization header consisting of a valid 'Mentor' jwt Auth0 access token._

-   '/mentor/<mentor_id>/coder' (PATCH)

_this endpoint allows a Mentor to add a specified Coder to
the Mentor's list of Coders. The Mentor's id is included in the URL of the request, and the body should include a 'coderId' which is the selected Coder's id from the Coder table of the postgresql database. This endpoint requires an Authorization header with a Bearer token consisting of a valid 'Mentor' jwt Auth0 access token._

-   '/snippet/<snippet_id>' (GET)

_this endpoint returns a requested code snippet from the database based on the snippet's id in the postgresql database which is provided in the URL. This request requires an Authorization header with a Bearer token consisting of a valid Auth0 jwt access token (may be either a Coder or a Mentor token)._

-   '/snippet' (POST)

_this endpoint is used to post a new code Snippet to the database. It requires an Authorization header with a Bearer token consisting of a valid 'Coder' Auth0 jwt access token. The Snippet information should be provided in the body of the post request, and should include:_\

-   _'name': {name for the snippet}_\
-   _'code': {the actual code of the snippet as a string}_\
-   _'needsReview': {a boolean indicating whether the code need to be reviewed by the applicable Mentor}_\
-   _'comments': {optional, probably a blank string for initial post (comments are intended to be added later by a Mentor)}_

*   '/snippet/<snippet_id>' (PATCH)

_this endpoint is used to update an existing snippet (after being edited or reviewed by the Coder or by a Mentor). The Snippet's id is provided in the URL and the request must include an Authorization header consisting of a Bearer token which may be either a 'Coder' or 'Mentor' Auth0 jwt access token. The body of the request can include the same parameters as the POST method for a new snippet (see above). **NOTE that if a parameter is not provided, this will change the attribute to a blank string, null or False in the database (basically erasing the existing value), so please provide the original value for each attribute if not intending to change the existing value.**_

-   '/snippet/<snippet_id>' (DELETE)

_this endpoint allows a coder to delete an existing Snippet (identified by the Snippet's id provided in the URL). This request must include an Authorization header consisting of a Bearer token which is a valid 'Coder' Auth0 jwt access token. This enpoint expects a 'coderId' to be provided in the body of the request, which id must match the id of the Coder associated with the Snippet in the postgresql database._

### Main Files: Project Structure

```sh
├── app.py *** the main driver of the app. Includes your routes (controllers).
                  "flask run" to run after installing dependences and setting environment
                  variables
├── auth.py *** helper functions relating to authenticating auth0 access tokens, and
                checking permissions from request headers
├── funcsterdb_test.psql *** a psql 'dump' from a test database with mock data; can be used
                             to set up a database with users and code for testing purposes
├── manage.py *** sets up flask-migrate to run database migrations
├── models.py *** the models to be used to set up tables/schema in the database, along with some
                  helpful methods to interact with those tables from the application
├── Profile *** utility file needed for deployment to heroku
├── README.md
├── requirements.txt *** The dependencies we need to install with "pip install -r requirements.txt"
├── test_app.py *** a suite of test functions utilizing python unit_test; this also utilizes dotenv
                    to load environment variables necessary for testing. A postgresql testing database
                    will need to be created to provide a database for testing that will not interfere
                    with any actual data in your app (testing will empty and recreate the database each
                    time it is run)
```
