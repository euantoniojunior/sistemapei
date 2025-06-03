from database.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Student(db.Model):
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
    laudo_medico = db.Column(db.String(3))  # Sim/Não
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

class PEI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    conteudo = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    aluno = db.relationship('Student', backref='peis')

class PEIHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pei_id = db.Column(db.Integer, db.ForeignKey('pei.id'))
    editado_por = db.Column(db.Integer, db.ForeignKey('user.id'))
    conteudo_anterior = db.Column(db.Text)
    conteudo_novo = db.Column(db.Text)
    data_edicao = db.Column(db.DateTime, default=datetime.utcnow)
    pei = db.relationship('PEI', backref='historicos')
    editor = db.relationship('User', backref='edicoes_pei')
