from flask import Blueprint, request, jsonify, render_template_string, send_file, current_app
from models.models import Student, PEI, PEIHistory
from database.connection import db
import pdfkit
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import csv
from io import StringIO
import openpyxl
from io import BytesIO
from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, Any

pei_bp = Blueprint('pei', __name__)

# Schema Pydantic para validação
class AlunoSchema(BaseModel):
    student_id: Optional[int] = None
    nome: str = Field(..., min_length=1)
    curso: Optional[str] = None
    unidade: Optional[str] = None
    periodo: Optional[str] = None
    data_elaboracao: Optional[datetime] = None
    responsavel: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    idade: Optional[int] = None
    diagnostico_cid: Optional[str] = None
    transtorno_identificado: Optional[str] = None
    laudo_medico: Optional[str] = None
    psicologo: Optional[str] = None
    psiquiatra: Optional[str] = None
    psicopedagogo: Optional[str] = None
    outros_profissionais: Optional[str] = None
    perfil_aluno: Optional[str] = None
    observacoes_gerais: Optional[str] = None
    proxima_avaliacao: Optional[datetime] = None
    responsavel_legal: Optional[str] = None
    orientador_responsavel: Optional[str] = None
    supervisor: Optional[str] = None
    gerente_unidade: Optional[str] = None

    @validator('nome')
    def validar_nome(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Campo 'nome' é obrigatório")
        return v.strip()

    @validator('data_elaboracao', 'data_nascimento', 'proxima_avaliacao', pre=True)
    def parse_data(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"Data inválida: {v}")
        return v

    @validator('idade', pre=True)
    def validar_idade(cls, v):
        if isinstance(v, str) and v.strip() in ['', ' ', None]:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            raise ValueError("Idade deve ser um número válido ou vazio")

# Rota principal: Salvar ou editar aluno + PEI
@pei_bp.route('/api/pei', methods=['POST'])
def criar_pei():
    try:
        # Pegar UPLOAD_FOLDER do contexto do app
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Processar dados recebidos
        if request.is_json:
            data = request.get_json()
            aluno_data = data.get('aluno')
            conteudo_data = data.get('conteudo')
        else:
            aluno_json = request.form.get('aluno')
            conteudo_json = request.form.get('conteudo')
            if not aluno_json or not conteudo_json:
                return jsonify({"error": "Dados ausentes no formulário"}), 400
            try:
                aluno_data = json.loads(aluno_json)
                conteudo_data = json.loads(conteudo_json)
            except json.JSONDecodeError as je:
                return jsonify({"error": "Erro ao decodificar JSON", "detalhe": str(je)}), 400

        if not aluno_data:
            return jsonify({"error": "Dados do aluno ausentes"}), 400

        # Validar com Pydantic
        try:
            aluno_validado = AlunoSchema(**aluno_data)
        except Exception as ve:
            return jsonify({
                "error": "Validação dos dados falhou",
                "detalhes": ve.errors()
            }), 400

        aluno_data = aluno_validado.dict()

        student_id = aluno_data.get('student_id')

        # Se for edição
        if student_id and str(student_id).isdigit():
            aluno = Student.query.get(int(student_id))
            if not aluno:
                return jsonify({"error": "Aluno não encontrado"}), 404

            # Atualiza campos editáveis
            aluno.nome = aluno_data.get('nome')
            aluno.curso = aluno_data.get('curso')
            aluno.unidade = aluno_data.get('unidade')
            aluno.periodo = aluno_data.get('periodo')
            aluno.data_elaboracao = aluno_data.get('data_elaboracao')
            aluno.responsavel = aluno_data.get('responsavel')
            aluno.data_nascimento = aluno_data.get('data_nascimento')
            aluno.idade = aluno_data.get('idade')
            aluno.diagnostico_cid = aluno_data.get('diagnostico_cid')
            aluno.transtorno_identificado = aluno_data.get('transtorno_identificado')
            aluno.laudo_medico = aluno_data.get('laudo_medico')
            aluno.psicologo = aluno_data.get('psicologo')
            aluno.psiquiatra = aluno_data.get('psiquiatra')
            aluno.psicopedagogo = aluno_data.get('psicopedagogo')
            aluno.outros_profissionais = aluno_data.get('outros_profissionais')
            aluno.perfil_aluno = aluno_data.get('perfil_aluno')
            aluno.observacoes_gerais = aluno_data.get('observacoes_gerais')
            aluno.proxima_avaliacao = aluno_data.get('proxima_avaliacao')
            aluno.responsavel_legal = aluno_data.get('responsavel_legal')
            aluno.orientador_responsavel = aluno_data.get('orientador_responsavel')
            aluno.supervisor = aluno_data.get('supervisor')
            aluno.gerente_unidade = aluno_data.get('gerente_unidade')

        # Se for novo cadastro
        else:
            aluno = Student(
                nome=aluno_data.get('nome'),
                curso=aluno_data.get('curso'),
                unidade=aluno_data.get('unidade'),
                periodo=aluno_data.get('periodo'),
                data_elaboracao=aluno_data.get('data_elaboracao'),
                responsavel=aluno_data.get('responsavel'),
                data_nascimento=aluno_data.get('data_nascimento'),
                idade=aluno_data.get('idade'),
                diagnostico_cid=aluno_data.get('diagnostico_cid'),
                transtorno_identificado=aluno_data.get('transtorno_identificado'),
                laudo_medico=aluno_data.get('laudo_medico'),
                psicologo=aluno_data.get('psicologo'),
                psiquiatra=aluno_data.get('psiquiatra'),
                psicopedagogo=aluno_data.get('psicopedagogo'),
                outros_profissionais=aluno_data.get('outros_profissionais'),
                perfil_aluno=aluno_data.get('perfil_aluno'),
                observacoes_gerais=aluno_data.get('observacoes_gerais'),
                proxima_avaliacao=aluno_data.get('proxima_avaliacao'),
                responsavel_legal=aluno_data.get('responsavel_legal'),
                orientador_responsavel=aluno_data.get('orientador_responsavel'),
                supervisor=aluno_data.get('supervisor'),
                gerente_unidade=aluno_data.get('gerente_unidade')
            )
            db.session.add(aluno)
            db.session.flush()

        # Upload do arquivo
        if 'laudo_medico_arquivo' in request.files:
            file = request.files['laudo_medico_arquivo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                aluno.laudo_medico_arquivo = filename

        # Criação do PEI
        pei = PEI(student_id=aluno.id, conteudo=json.dumps(conteudo_data, ensure_ascii=False))
        db.session.add(pei)

        # Registro de histórico
        historico = PEIHistory(
            pei_id=pei.id,
            editado_por=session.get('user_id') or 1,
            student_id=aluno.id,
            conteudo_anterior="{}",
            conteudo_novo=json.dumps(conteudo_data, ensure_ascii=False)
        )
        db.session.add(historico)

        db.session.commit()

        return jsonify({
            "message": "✅ Cadastro salvo com sucesso!",
            "student_id": aluno.id,
            "tipo": "edição" if student_id else "novo"
        }), 201

    except Exception as e:
        db.session.rollback()
        print("❌ Erro interno:", str(e))
        return jsonify({
            "error": "Erro ao salvar o PEI",
            "detalhe": str(e),
            "payload": aluno_data
        }), 500


# Buscar aluno por ID
@pei_bp.route('/api/alunos/<int:student_id>', methods=['GET'])
def buscar_aluno_por_id(student_id):
    aluno = Student.query.get(student_id)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404
    pei = PEI.query.filter_by(student_id=aluno.id).order_by(PEI.data_registro.desc()).first()
    aluno_dict = aluno.to_dict()
    conteudo = {}
    if pei:
        try:
            conteudo = json.loads(pei.conteudo) if isinstance(pei.conteudo, str) else pei.conteudo
        except:
            pass
    aluno_dict.update({
        'meta_curto_prazo': conteudo.get('metas', {}).get('curto_prazo', {}).get('meta', ''),
        'responsavel_curto': conteudo.get('metas', {}).get('curto_prazo', {}).get('responsavel', ''),
        'avaliacao_curto': conteudo.get('metas', {}).get('curto_prazo', {}).get('avaliacao', ''),
        'meta_medio_prazo': conteudo.get('metas', {}).get('medio_prazo', {}).get('meta', ''),
        'responsavel_medio': conteudo.get('metas', {}).get('medio_prazo', {}).get('responsavel', ''),
        'avaliacao_medio': conteudo.get('metas', {}).get('medio_prazo', {}).get('avaliacao', ''),
        'meta_longo_prazo': conteudo.get('metas', {}).get('longo_prazo', {}).get('meta', ''),
        'responsavel_longo': conteudo.get('metas', {}).get('longo_prazo', {}).get('responsavel', ''),
        'avaliacao_longo': conteudo.get('metas', {}).get('longo_prazo', {}).get('avaliacao', ''),
        'objetivos_gerais': conteudo.get('objetivos_gerais', ''),
        'adaptaçoes_pedagogicas': conteudo.get('adaptaçoes_pedagogicas', ''),
        'intervencoes_complementares': conteudo.get('intervencoes_complementares', '')
    })
    return jsonify({'aluno': aluno_dict, 'conteudo': conteudo}), 200


# Buscar alunos por nome
@pei_bp.route('/api/alunos', methods=['GET'])
def buscar_alunos():
    nome = request.args.get('nome')
    if not nome:
        return jsonify([]), 200
    alunos = Student.query.filter(Student.nome.ilike(f'%{nome}%')).all()
    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'curso': a.curso,
        'unidade': a.unidade,
        'periodo': a.periodo,
        'data_elaboracao': a.data_elaboracao.isoformat() if a.data_elaboracao else "",
        'responsavel': a.responsavel,
        'data_nascimento': a.data_nascimento.isoformat() if a.data_nascimento else "",
        'idade': a.idade,
        'diagnostico_cid': a.diagnostico_cid,
        'transtorno_identificado': a.transtorno_identificado,
        'laudo_medico': a.laudo_medico,
        'psicologo': a.psicologo,
        'psiquiatra': a.psiquiatra,
        'psicopedagogo': a.psicopedagogo,
        'outros_profissionais': a.outros_profissionais,
        'perfil_aluno': a.perfil_aluno,
        'observacoes_gerais': a.observacoes_gerais,
        'proxima_avaliacao': a.proxima_avaliacao.isoformat() if a.proxima_avaliacao else "",
        'responsavel_legal': a.responsavel_legal,
        'orientador_responsavel': a.orientador_responsavel,
        'supervisor': a.supervisor,
        'gerente_unidade': a.gerente_unidade
    } for a in alunos]), 200


# Listar todos os alunos
@pei_bp.route('/api/alunos/listar', methods=['GET'])
def listar_todos_alunos():
    alunos = Student.query.all()
    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'curso': a.curso,
        'data_nascimento': a.data_nascimento.isoformat() if a.data_nascimento else "",
        'proxima_avaliacao': a.proxima_avaliacao.isoformat() if a.proxima_avaliacao else ""
    } for a in alunos]), 200


# Exportação PDF
@pei_bp.route('/api/pei/pdf', methods=['POST'])
def gerar_pdf():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Dados inválidos para exportação"}), 400

    logo_url = request.url_root + 'static/assets/senac-logo.png'
    template = """
    <html><head><meta charset="UTF-8"><style>
    body {font-family: 'DejaVu Sans', sans-serif;padding: 40px;color: #333;font-size: 14px;}
    .header {text-align: center;margin-bottom: 30px;}
    .header img {max-width: 160px;margin-bottom: 10px;}
    h1 {color: #003D7C;font-size: 24px;margin-top: 0;text-align: center;}
    h2 {color: #003D7C;font-size: 18px;border-left: 4px solid #F7931E;padding-left: 10px;margin-top: 25px;}
    table {width: 100%;border-collapse: collapse;margin: 20px 0;}
    th, td {border: 1px solid #ccc;padding: 8px;text-align: left;}
    .assinatura {display: flex;justify-content: space-between;margin-top: 40px;}
    </style></head><body>
    <div class="header">
        <img src="{{ logo_url }}" alt="Logo Senac">
        <h1>Plano Educacional Individualizado (PEI)</h1>
    </div>
    <p><strong>Nome:</strong> {{ aluno.nome }}</p>
    <p><strong>Curso:</strong> {{ aluno.curso }}</p>
    <p><strong>Objetivos Gerais:</strong> {{ objetivos_gerais }}</p>
    <h2>Metas Individuais</h2>
    <table>
        <tr><th>Método</th><th>Meta</th><th>Responsável</th><th>Avaliação</th></tr>
        <tr><td>Curto prazo</td><td>{{ meta_curto_prazo }}</td><td>{{ responsavel_curto }}</td><td>{{ avaliacao_curto }}</td></tr>
        <tr><td>Médio prazo</td><td>{{ meta_medio_prazo }}</td><td>{{ responsavel_medio }}</td><td>{{ avaliacao_medio }}</td></tr>
        <tr><td>Longo prazo</td><td>{{ meta_longo_prazo }}</td><td>{{ responsavel_longo }}</td><td>{{ avaliacao_longo }}</td></tr>
    </table>
    <h2>Adaptações Pedagógicas</h2>
    <p>{{ adaptaçoes_pedagogicas }}</p>
    <h2>Intervenções Complementares</h2>
    <p>{{ intervencoes_complementares }}</p>
    <h2>Perfil do Aluno</h2>
    <p>{{ perfil_aluno }}</p>
    <h2>Acompanhamento e Revisão do PEI</h2>
    <p><strong>Observações gerais:</strong> {{ observacoes_gerais }}</p>
    <p><strong>Data da próxima avaliação:</strong> {{ proxima_avaliacao }}</p>
    <div class="assinatura">
        <div>Responsável Legal<br>__________________________<br>{{ responsavel_legal }}</div>
        <div>Orientador Responsável<br>__________________________<br>{{ orientador_responsavel }}</div>
        <div>Supervisor<br>__________________________<br>{{ supervisor }}</div>
        <div>Gerente de Unidade<br>__________________________<br>{{ gerente_unidade }}</div>
    </div>
    </body></html>
    """

    rendered = render_template_string(template, logo_url=logo_url, **dados)
    options = {
        'encoding': 'utf-8',
        'enable-local-file-access': '',
        'no-stop-slow-scripts': ''
    }
    try:
        pdf = pdfkit.from_string(rendered, False, options=options)
        return pdf, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f"attachment; filename=pei_{dados.get('aluno', {}).get('nome', 'aluno')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    except Exception as e:
        return jsonify({
            "error": "Erro ao gerar PDF",
            "detalhe": str(e)
        }), 500


# Histórico de alterações
@pei_bp.route('/api/pei/historico/<int:student_id>', methods=['GET'])
def get_historico_pei(student_id):
    aluno = Student.query.get(student_id)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404
    historico = PEIHistory.query.filter_by(student_id=student_id).all()
    resultado = []
    for h in historico:
        try:
            conteudo = json.loads(h.conteudo_novo) if isinstance(h.conteudo_novo, str) else h.conteudo_novo
        except:
            conteudo = {}
        resultado.append({
            'historico_id': h.id,
            'pei_id': h.pei_id,
            'student_id': h.student_id,
            'editado_por': h.editado_por,
            'data_edicao': h.data_edicao.isoformat(),
            'conteudo': conteudo
        })
    return jsonify(resultado), 200


# Carregar versão específica do histórico
@pei_bp.route('/api/pei/historico/versao/<int:history_id>', methods=['GET'])
def get_versao_historico(history_id):
    historia = PEIHistory.query.get(history_id)
    if not historia:
        return jsonify({"error": "Versão do histórico não encontrada"}), 404
    try:
        conteudo = json.loads(historia.conteudo_novo) if isinstance(historia.conteudo_novo, str) else historia.conteudo_novo
        aluno = Student.query.get(conteudo.get('student_id', historia.student_id))
        return jsonify({
            'aluno': aluno.to_dict(),
            'conteudo': conteudo,
            'historico_id': historia.id,
            'pei_id': historia.pei_id,
            'student_id': aluno.id,
            'data_edicao': historia.data_edicao.isoformat(),
            'usuario': f"Usuário {historia.editado_por}"
        })
    except Exception as e:
        return jsonify({"error": "Erro ao carregar versão", "detalhe": str(e)}), 500


# Baixar CSV
@pei_bp.route('/api/alunos/csv', methods=['GET'])
def baixar_csv():
    alunos = Student.query.all()
    if not alunos:
        return jsonify({"error": "Nenhum aluno cadastrado"}), 404
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Nome", "Curso", "Unidade", "Período", "Data Elaboração",
        "Responsável", "Data Nascimento", "Idade", "Diagnóstico CID",
        "Transtorno", "Laudo Médico", "Psicólogo", "Psiquiatra",
        "Psicopedagogo", "Outros Profissionais", "Perfil Aluno", "Observações Gerais",
        "Próxima Avaliação", "Responsável Legal", "Orientador", "Supervisor", "Gerente Unidade"
    ])
    for aluno in alunos:
        writer.writerow([
            aluno.id, aluno.nome, aluno.curso, aluno.unidade, aluno.periodo,
            aluno.data_elaboracao.isoformat() if aluno.data_elaboracao else "",
            aluno.responsavel,
            aluno.data_nascimento.isoformat() if aluno.data_nascimento else "",
            aluno.idade, aluno.diagnostico_cid, aluno.transtorno_identificado,
            aluno.laudo_medico, aluno.psicologo, aluno.psiquiatra,
            aluno.psicopedagogo, aluno.outros_profissionais, aluno.perfil_aluno,
            aluno.observacoes_gerais,
            aluno.proxima_avaliacao.isoformat() if aluno.proxima_avaliacao else "",
            aluno.responsavel_legal, aluno.orientador_responsavel, aluno.supervisor,
            aluno.gerente_unidade
        ])
    output.seek(0)
    return output.getvalue(), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=alunos.csv"
    }


# Baixar Excel
@pei_bp.route('/api/alunos/excel', methods=['GET'])
def baixar_excel():
    alunos = Student.query.all()
    if not alunos:
        return jsonify({"error": "Nenhum aluno cadastrado"}), 404
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Alunos Cadastrados"
    ws.append([
        "ID", "Nome", "Curso", "Unidade", "Período", "Data Elaboração",
        "Responsável", "Data Nascimento", "Idade", "Diagnóstico CID",
        "Transtorno Identificado", "Laudo Médico", "Psicólogo", "Psiquiatra",
        "Psicopedagogo", "Outros Profissionais", "Perfil Aluno", "Observações Gerais",
        "Próxima Avaliação", "Responsável Legal", "Orientador", "Supervisor", "Gerente Unidade"
    ])
    for aluno in alunos:
        ws.append([
            aluno.id, aluno.nome, aluno.curso, aluno.unidade, aluno.periodo,
            aluno.data_elaboracao.isoformat() if aluno.data_elaboracao else "",
            aluno.responsavel,
            aluno.data_nascimento.isoformat() if aluno.data_nascimento else "",
            aluno.idade, aluno.diagnostico_cid, aluno.transtorno_identificado,
            aluno.laudo_medico, aluno.psicologo, aluno.psiquiatra,
            aluno.psicopedagogo, aluno.outros_profissionais, aluno.perfil_aluno,
            aluno.observacoes_gerais,
            aluno.proxima_avaliacao.isoformat() if aluno.proxima_avaliacao else "",
            aluno.responsavel_legal, aluno.orientador_responsavel, aluno.supervisor,
            aluno.gerente_unidade
        ])
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='alunos_pei.xlsx'
    )


# Excluir aluno
@pei_bp.route('/api/alunos/excluir/<int:id>', methods=['DELETE'])
def excluir_registro(id):
    aluno = Student.query.get(id)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado."}), 404
    try:
        db.session.delete(aluno)
        db.session.commit()
        return jsonify({"message": f"✅ Aluno {id} excluído com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "❌ Erro ao excluir aluno.", "detalhe": str(e)}), 500
