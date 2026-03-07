# Version: 2026-03-03-v171 | Date: 2026-03-03 | Description: Main entry point. Connects API and Web routes.
# Functions: add_movie_api()

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import add_movie_logic
from web_routes import init_routes

app = Flask(__name__)
CORS(app)

# 웹 검색 관련 라우트 초기화
init_routes(app)

# API (Greasemonkey 전용) 라우트
@app.route('/api/add_movie', methods=['POST'])
def add_movie_api():
    success, result = add_movie_logic(request.get_json())
    return jsonify({"status": "success" if success else "error", "message": result}), (200 if success else 400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
