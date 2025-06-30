from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from database.connection import db
from models.models import Student, User
from routes.auth import auth_bp
from routes.pei import pei_bp
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect


app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Configurações de Upload
UPLOAD_FOLDER = 'static/laudos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configurações gerais
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'segredo_senac_2025')

# Banco de dados
db_uri = os.getenv('DATABASE_URL', 'sqlite:///pei.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa banco
db.init_app(app)

# Registra blueprints
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
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    usuario = User.query.get(user_id)
    if not usuario:
        session.clear()
        return redirect(url_for('login_page'))

    return render_template('dashboard.html',
                           username=usuario.username,
                           role=usuario.role)


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


@app.route('/registros')
@login_required
def registros_page():
    return render_template('registro.html')


@app.route('/change-password')
@login_required
def change_password_page():
    return render_template('change_password.html')


@app.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('login_page'))


# ========== FUNÇÕES AUXILIARES PARA INICIALIZAÇÃO ==========
def verificar_e_criar_colunas(engine):
    """Verifica se todas as colunas necessárias existem e cria-as se necessário"""
    inspector = inspect(engine)

    if 'student' not in inspector.get_table_names():
        print("⚠️ Tabela 'student' não existe")
        return

    columns = [col['name'] for col in inspector.get_columns('student')]

    colunas_necessarias = {
        'laudo_medico_arquivo': 'VARCHAR(255)',
        'responsavel_legal': 'VARCHAR(150)',
        'orientador_responsavel': 'VARCHAR(150)',
        'supervisor': 'VARCHAR(150)',
        'gerente_unidade': 'VARCHAR(150)'
    }

    missing_cols = [f"ADD COLUMN {col} {ctype}" for col, ctype in colunas_necessarias.items() if col not in columns]

    if missing_cols:
        with engine.connect() as conn:
            for cmd in missing_cols:
                try:
                    conn.execute(f"ALTER TABLE student {cmd};")
                    print(f"[INFO] Coluna '{cmd}' criada na tabela 'student'")
                except Exception as e:
                    print(f"[ERRO] Falha ao criar coluna '{cmd}': {e}")
            conn.commit()


def criar_tabelas_se_necessario():
    """Garante que todas as tabelas sejam criadas"""
    with app.app_context():
        engine = db.engine
        db.create_all()
        verificar_e_criar_colunas(engine)


def criar_usuarios_padrao():
    """Cria usuários padrão se não existirem"""
    with app.app_context():
        try:
            admin = User.query.filter_by(username='admin').first()
            mediador = User.query.filter_by(username='mediador').first()

            if not admin:
                hashed_pw = generate_password_hash('123456')
                admin = User(username='admin', password=hashed_pw, role='admin')
                db.session.add(admin)

            if not mediador:
                hashed_pw = generate_password_hash('123456')
                mediador = User(username='mediador', password=hashed_pw, role='mediador')
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
def inicializar_aplicacao():
    if not getattr(app, 'inicializado', False):
        criar_tabelas_se_necessario()
        criar_usuarios_padrao()
        app.inicializado = True


# ========== RODAR LOCALMENTE (opcional) ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
