from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configurações de upload
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Banco de dados
db_uri = os.getenv('DATABASE_URL', 'sqlite:///pei.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'segredo_senac_2025')

# Inicializa banco
db.init_app(app)

# Registra Blueprints
from routes.auth import auth_bp
from routes.pei import pei_bp
app.register_blueprint(auth_bp)
app.register_blueprint(pei_bp)

# ========== DECORADOR DE AUTENTICAÇÃO ==========
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ========== ROTAS PRINCIPAIS ==========
@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/cadastro')
@login_required
def cadastro_page():
    return render_template('cadastro.html')

@app.route('/search')
@login_required
def search_page():
    return render_template('search.html')

@app.route('/historico')
@login_required
def historico_page():
    return render_template('historico.html')

@app.route('/relatorios')
@login_required
def relatorios_page():
    return render_template('relatorios.html')

@app.route('/preview')
@login_required
def preview_page():
    return render_template('preview.html')

@app.route('/preview_versao')
@login_required
def preview_versao_page():
    return render_template('preview_versao.html')

@app.route('/register')
@login_required
def register_page():
    return render_template('register.html')

@app.route('/change-password')
@login_required
def change_password_page():
    return render_template('change_password.html')
