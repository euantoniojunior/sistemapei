from database.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='usuario')  # admin, mediador, usuario

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    curso = db.Column(db.String(100))
    unidade = db.Column(db.String(100))
    periodo = db.Column(db.String(50))
    data_elaboracao = db.Column(db.Date)
    responsavel = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    idade = db.Column(db.Integer)
    diagnostico_cid = db.Column(db.String(100))
    transtorno_identificado = db.Column(db.String(100))
    laudo_medico = db.Column(db.String(3))  # Sim / Não
    laudo_medico_arquivo = db.Column(db.String(255))  # Nome do arquivo salvo em /static/laudos/
    psicologo = db.Column(db.String(150))
    psiquiatra = db.Column(db.String(150))
    psicopedagogo = db.Column(db.String(150))
    outros_profissionais = db.Column(db.Text)
    perfil_aluno = db.Column(db.Text)
    observacoes_gerais = db.Column(db.Text)
    proxima_avaliacao = db.Column(db.Date)
    responsavel_legal = db.Column(db.String(150))
    orientador_responsavel = db.Column(db.String(150))
    supervisor = db.Column(db.String(150))
    gerente_unidade = db.Column(db.String(150))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'curso': self.curso,
            'unidade': self.unidade,
            'periodo': self.periodo,
            'data_elaboracao': self.data_elaboracao.isoformat() if self.data_elaboracao else None,
            'responsavel': self.responsavel,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'idade': self.idade,
            'diagnostico_cid': self.diagnostico_cid,
            'transtorno_identificado': self.transtorno_identificado,
            'laudo_medico': self.laudo_medico,
            'psicologo': self.psicologo,
            'psiquiatra': self.psiquiatra,
            'psicopedagogo': self.psicopedagogo,
            'outros_profissionais': self.outros_profissionais,
            'perfil_aluno': self.perfil_aluno,
            'observacoes_gerais': self.observacoes_gerais,
            'proxima_avaliacao': self.proxima_avaliacao.isoformat() if self.proxima_avaliacao else None,
            'responsavel_legal': self.responsavel_legal,
            'orientador_responsavel': self.orientador_responsavel,
            'supervisor': self.supervisor,
            'gerente_unidade': self.gerente_unidade
        }

    def __repr__(self):
        return f'<Student {self.nome}>'

class PEI(db.Model):
    __tablename__ = 'pei'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    conteudo = db.Column(db.Text)  # JSON com todo conteúdo do PEI
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    aluno = db.relationship('Student', backref='peis')

    def get_conteudo(self):
        try:
            return json.loads(self.conteudo) if isinstance(self.conteudo, str) else self.conteudo
        except Exception as e:
            print(f"[ERRO] Falha ao carregar conteúdo do PEI ID {self.id}: {e}")
            return {}

    def __repr__(self):
        return f'<PEI ID={self.id}, Aluno ID={self.student_id}>'

class PEIHistory(db.Model):
    __tablename__ = 'pei_history'
    id = db.Column(db.Integer, primary_key=True)
    pei_id = db.Column(db.Integer, db.ForeignKey('pei.id'))
    editado_por = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))  # Novo campo
    conteudo_anterior = db.Column(db.Text)  # JSON antes da edição
    conteudo_novo = db.Column(db.Text)      # JSON após a edição
    data_edicao = db.Column(db.DateTime, default=datetime.utcnow)

    pei = db.relationship('PEI', backref='historicos')
    editor = db.relationship('User', backref='edicoes_pei')
    aluno = db.relationship('Student', backref='historico_pei')

    def to_dict(self):
        try:
            anterior = json.loads(self.conteudo_anterior) if self.conteudo_anterior else {}
        except:
            anterior = {}
        try:
            novo = json.loads(self.conteudo_novo) if self.conteudo_novo else {}
        except:
            novo = {}
        return {
            'historico_id': self.id,
            'pei_id': self.pei_id,
            'student_id': self.student_id,
            'editado_por': self.editado_por,
            'usuario': self.editor.username if self.editor else "Desconhecido",
            'data_edicao': self.data_edicao.isoformat(),
            'conteudo_anterior': anterior,
            'conteudo_novo': novo
        }

    def __repr__(self):
        return f'<PEIHistory PEI={self.pei_id}, Editor={self.editado_por}, Data={self.data_edicao}>'
