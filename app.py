# funcster\backend\app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS

from models import setup_db

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

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

    return app

app = create_app()

if __name__ == '__main__':
  app.run(port=5000)