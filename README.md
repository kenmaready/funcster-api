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
DATABASE_URL= {path to your local postgres database for this app, including any needed password}
TEST_DATABASE_URL={this is only needed to run test_app.py; it is the path to your local postgres testing database, which should be separate from your regular database}

AUTH0_DOMAIN=funcster.auth0.com
API_AUDIENCE=funcster-auth0-api

AUTH0_CLIENT_ID={the auth0 client ID for your funcster application on auth0}
AUTH0_CONNECTION={the name of the auth0 database you will use to store user information. If you go with the default provided by auth0, it will be 'Username-Password-Authentication'}
API_IDENTIFIER={the auth0 identifier for the auth0 API you'll be using to get user info}

AUTH0_CODER_TOKEN={a valid JWT access token provided for a Coder registered on the application}
AUTH0_MENTOR_TOKEN={ valid JWT access token provided for a Mentor registered on the application}
```

Once requirements have been installed and environment variables defined, run the app by running `run flask` in the root folder. If run locally, the api will be served on [http://localhost:5000](http://localhost:5000). The endpoints are all defined and described in the app.py file. Many of the endpoints are restricted and require authentification with a working jwt access token from auth0. In some cases, the endpoints require certain permissions which are provided in the token.

### Technologies

Funcster-api is built using:

-   **SQLAlchemy ORM** as our ORM layer
-   **PostgreSQL** as our database
-   **Python3** and **Flask** as our server language and server framework
-   **Flask-Migrate** for creating and running schema migrations

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
