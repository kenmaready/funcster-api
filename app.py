# funcster\backend\app.py
import os
from flask import Flask, jsonify

from app_config import app
from models import db, Mentor, Coder, Snippet


@app.route('/')
def index():
    return jsonify({
    "success": True,
    "message": "welcome to funcster."
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