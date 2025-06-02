from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import User
from database.connection import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Usuário ou senha inválido"}), 401

    session['user_id'] = user.id
    return jsonify({"message": "Login realizado com sucesso!"})


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Nome de usuário já existe."}), 400

    hashed_pw = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário criado com sucesso!"}), 201


@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"error": "Você precisa estar logado."}), 401

    data = request.json
    current_user = User.query.get(session['user_id'])

    if not check_password_hash(current_user.password, data['oldPassword']):
        return jsonify({"error": "Senha antiga incorreta."}), 400

    new_password = data.get('newPassword', '')
    if len(new_password) < 6:
        return jsonify({"error": "Nova senha deve ter pelo menos 6 caracteres."}), 400

    try:
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"message": "✅ Senha alterada com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "❌ Erro ao alterar senha.", "detalhe": str(e)}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
