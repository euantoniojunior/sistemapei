from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import User
from database.connection import db

auth_bp = Blueprint('auth', __name__)


# ✅ Rota: Login de usuário
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Nome de usuário e senha são obrigatórios."}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Usuário ou senha inválido"}), 401

    session['user_id'] = user.id
    return jsonify({
        "message": "Login realizado com sucesso!",
        "username": user.username,
        "role": user.role
    }), 200


# ✅ Nova rota: Obter dados do usuário logado
@auth_bp.route('/api/user/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    user = User.query.get(session['user_id'])

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    }), 200


# ✅ Rota: Registro de novo usuário (para admin)
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Nome de usuário e senha são obrigatórios."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Nome de usuário já existe."}), 400

    if len(password) < 6:
        return jsonify({"error": "Senha deve ter pelo menos 6 caracteres."}), 400

    hashed_pw = generate_password_hash(password)
    user = User(username=username, password=hashed_pw)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao criar usuário.", "detalhe": str(e)}), 500


# ✅ Rota: Alterar senha do usuário logado
@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"error": "Você precisa estar logado."}), 401

    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not old_password or not new_password:
        return jsonify({"error": "Ambas as senhas são obrigatórias."}), 400

    current_user = User.query.get(session['user_id'])

    if not check_password_hash(current_user.password, old_password):
        return jsonify({"error": "Senha antiga incorreta."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Nova senha deve ter pelo menos 6 caracteres."}), 400

    try:
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"message": "✅ Senha alterada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "❌ Erro ao alterar senha.", "detalhe": str(e)}), 500


# ✅ Rota: Logout do usuário
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
