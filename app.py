from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from database.connection import db
from models.models import User
from routes.auth import auth_bp
from routes.pei import pei_bp
import os
from werkzeug.security import generate_password_hash

# ========== CONFIGURAÇÃO DA APLICAÇÃO ==========
app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)
#PASTA UPLOAD DE LAUDOS
UPLOAD_FOLDER = 'static/laudos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurações gerais
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'segredo_senac_2025')

# Banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pei.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco
db.init_app(app)

# Registra os Blueprints
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

@app.route('/register')
def register_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/historico')
@login_required
def historico_page():
    return render_template('historico.html')

@app.route('/relatorios')
@login_required
def relatorios_page():
    return render_template('relatorios.html')

@app.route('/change-password')
@login_required
def change_password_page():
    return render_template('change_password.html')

@app.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('login_page'))

# ========== FUNÇÃO DE CRIAÇÃO DE USUÁRIOS PADRÃO ==========
def criar_usuarios_padrao():
    with app.app_context():
        try:
            # Garante que a sessão esteja ativa
            admin = User.query.filter_by(username='admin').first()
            mediador = User.query.filter_by(username='mediador').first()

            if not admin:
                hashed_pw = generate_password_hash('123456')
                admin = User(username='admin', password=hashed_pw)
                db.session.add(admin)

            if not mediador:
                hashed_pw = generate_password_hash('123456')
                mediador = User(username='mediador', password=hashed_pw)
                db.session.add(mediador)

            db.session.commit()
            print("[INFO] Usuários padrão criados ou já existem.")
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] Ao criar usuários: {e}")
        finally:
            db.session.remove()

# ========== INICIALIZAÇÃO DO BANCO E USUÁRIOS ==========
@app.before_request
def inicializar_usuarios_uma_vez():
    if 'usuarios_inicializados' not in app.config:
        criar_usuarios_padrao()
        app.config['usuarios_inicializados'] = True

# ========== RODAR LOCALMENTE (opcional) ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        criar_usuarios_padrao()  # Executa localmente também

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
