# funcster\backend\app.py

import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

#from models import db_drop_and_create_all, setup_db, Drink
#from auth import AuthError, requires_auth

app = Flask(__name__)
#setup_db(app)
CORS(app)

@app.route('/')
def index():
  return jsonify({
    "success": True,
    "message": "welcome to funcster."
  })


if __name__ == '__main__':
  app.run(port=5000)