import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "API is running",
        "port": "8000",
        "environment_check": {
            "openai_key_exists": bool(os.environ.get("OPENAI_API_KEY")),
            "openai_org_exists": bool(os.environ.get("OPENAI_ORGANIZATION"))
        }
    })

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    return jsonify({
        "message": "Test endpoint working",
        "method": request.method,
        "headers": dict(request.headers)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
