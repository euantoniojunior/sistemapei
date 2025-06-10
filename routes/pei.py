from flask import Blueprint, request, jsonify, session, render_template_string
from models.models import Student, PEI, PEIHistory
from database.connection import db
import pdfkit
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os

pei_bp = Blueprint('pei', __name__)

UPLOAD_FOLDER = 'static/laudos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# ✅ Rota principal: Salvar ou editar um PEI
@pei_bp.route('/api/pei', methods=['POST'])
def criar_pei():
    try:
        if request.is_json:
            data = request.get_json()
            aluno_data = data.get('aluno')
            conteudo_data = data.get('conteudo')
        else:
            aluno_json = request.form.get('aluno')
            conteudo_json = request.form.get('conteudo')

            if not aluno_json or not conteudo_json:
                return jsonify({"error": "Dados ausentes no formulário"}), 400

            aluno_data = json.loads(aluno_json)
            conteudo_data = json.loads(conteudo_json)

        student_id = aluno_data.get('student_id')  # ← Usando o campo certo!

        if student_id and str(student_id).isdigit():
            aluno = Student.query.get(int(student_id))
            if not aluno:
                return jsonify({"error": "Aluno não encontrado"}), 404
            # Atualiza campos editáveis...
        else:
            # Cria novo aluno
            aluno = Student(
                nome=aluno_data.get('nome'),
                curso=aluno_data.get('curso'),
                unidade=aluno_data.get('unidade'),
                periodo=aluno_data.get('periodo'),
                data_elaboracao=parse_date(aluno_data.get('data_elaboracao')),
                responsavel=aluno_data.get('responsavel'),
                data_nascimento=parse_date(aluno_data.get('data_nascimento')),
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
                proxima_avaliacao=parse_date(aluno_data.get('proxima_avaliacao')),
                responsavel_legal=aluno_data.get('responsavel_legal'),
                orientador_responsavel=aluno_data.get('orientador_responsavel'),
                supervisor=aluno_data.get('supervisor'),
                gerente_unidade=aluno_data.get('gerente_unidade')
            )
            db.session.add(aluno)
            db.session.flush()  # Garante ID antes de salvar PEI

        # Salva conteúdo do PEI como JSON
        pei = PEI(student_id=aluno.id, conteudo=json.dumps(conteudo_data, ensure_ascii=False))
        db.session.add(pei)

        # Registra histórico da edição
        historico = PEIHistory(
            pei_id=pei.id,
            editado_por=session.get('user_id') or 1,
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
            "detalhe": str(e)
        }), 500


# ✅ Nova rota: Buscar aluno por ID (para edição)
@pei_bp.route('/api/alunos/<int:student_id>', methods=['GET'])
def buscar_aluno_por_id(student_id):
    aluno = Student.query.get(student_id)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    pei = PEI.query.filter_by(student_id=aluno.id).order_by(PEI.data_registro.desc()).first()
    aluno_dict = aluno.to_dict()

    if pei:
        try:
            conteudo = pei.get_conteudo()
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
        except Exception as e:
            print("Erro ao processar conteúdo do PEI:", e)

    return jsonify(aluno_dict), 200


# ✅ Nova rota: Gerar PDF do PEI
@pei_bp.route('/api/pei/pdf', methods=['POST'])
def gerar_pdf():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Dados inválidos para exportação"}), 400

    logo_url = request.url_root + 'static/assets/senac-logo.png'

    template = """
    <html><head><meta charset="UTF-8"><style>
    body {font-family: 'DejaVu Sans', 'Roboto', sans-serif;padding: 40px;color: #333;font-size: 14px;}
    .header {text-align: center;margin-bottom: 30px;}
    .header img {max-width: 160px;margin-bottom: 10px;}
    h1 {color: #003D7C;font-size: 24px;margin-top: 0;text-align: center;}
    h2 {color: #003D7C;font-size: 18px;}
    table {width: 100%;border-collapse: collapse;margin: 20px 0;}
    th, td {border: 1px solid #ccc;padding: 10px;text-align: left;}
    .assinatura {display: flex;justify-content: space-between;margin-top: 40px;}
    </style></head><body>
    <div class="header">
        <img src="{{ logo_url }}" alt="Logo Senac">
        <h1>Plano Educacional Individualizado (PEI)</h1>
    </div>
    <p><strong>Nome:</strong> {{ nome }}</p>
    <p><strong>Curso:</strong> {{ curso }}</p>
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
    <div class="assinatura">
        <div>Responsável Legal<br>__________________________</div>
        <div>Orientador Responsável<br>__________________________</div>
        <div>Supervisor<br>__________________________</div>
        <div>Gerente de Unidade<br>__________________________</div>
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
            'Content-Disposition': f"attachment; filename=pei_{dados.get('nome', 'aluno')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    except Exception as e:
        return jsonify({
            "error": "Erro ao gerar PDF",
            "detalhe": str(e)
        }), 500
