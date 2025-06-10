from flask import Blueprint, request, jsonify, session
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    session['user_id'] = user.id
    return jsonify({"message": "Login bem-sucedido!"}), 200

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Nome ou senha não fornecidos"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Usuário já existe"}), 400

    hashed_pw = generate_password_hash(password)
    user = User(username=username, password=hashed_pw)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário criado com sucesso!"}), 201

@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Você precisa estar logado"}), 401

    user = User.query.get(user_id)

    if not check_password_hash(user.password, old_password):
        return jsonify({"error": "Senha antiga incorreta"}), 401

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Senha alterada com sucesso!"}), 200
