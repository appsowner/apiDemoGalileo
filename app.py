from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas

@app.route('/')
def home():
    return jsonify({
        "message": "¡API Flask funcionando correctamente!",
        "status": "success",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "API está funcionando"
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    # Ejemplo de datos de usuarios
    users = [
        {"id": 1, "name": "Juan Pérez", "email": "juan@example.com"},
        {"id": 2, "name": "María García", "email": "maria@example.com"},
        {"id": 3, "name": "Carlos López", "email": "carlos@example.com"}
    ]
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    # Simular creación de usuario
    new_user = {
        "id": 4,  # En una app real, esto sería generado automáticamente
        "name": data['name'],
        "email": data['email']
    }
    
    return jsonify({
        "message": "Usuario creado exitosamente",
        "user": new_user
    }), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Simular búsqueda de usuario
    if user_id == 1:
        user = {"id": 1, "name": "Juan Pérez", "email": "juan@example.com"}
        return jsonify(user)
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    # EasyPanel puede asignar cualquier puerto via variable de entorno
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
