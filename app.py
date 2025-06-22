# app.py
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Flask App en Coolify</h1>
    <p>¡Tu aplicación está funcionando correctamente!</p>
    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/api/info">API Info</a></li>
    </ul>
    '''

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "message": "Application is running",
        "port": os.environ.get('PORT', 5000)
    })

@app.route('/api/info')
def api_info():
    return jsonify({
        "app": "Flask Demo",
        "version": "1.0.0",
        "python_version": "3.x",
        "deployed_on": "Coolify"
    })

if __name__ == '__main__':
    # Importante: usar PORT del entorno y host 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
