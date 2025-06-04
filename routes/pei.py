from flask import Blueprint, request, jsonify, render_template_string, session
from models.models import Student, PEI, PEIHistory
from database.connection import db
import pdfkit
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app import app

pei_bp = Blueprint('pei', __name__)

def parse_date(date_str):
    """Converte string de data para objeto date"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


# ✅ Rota: Salvar ou editar aluno + PEI
@pei_bp.route('/api/pei', methods=['POST'])
def criar_pei():
    try:
        data = request.get_json()
        aluno_data = data.get('aluno')
        conteudo_data = data.get('conteudo')

        # Campos obrigatórios
        campos_obrigatorios = ['nome', 'curso', 'unidade', 'periodo', 'data_elaboracao', 'responsavel']
        faltando = [campo for campo in campos_obrigatorios if not aluno_data.get(campo)]
        if faltando:
            return jsonify({
                "error": "Campos obrigatórios ausentes",
                "campos": faltando
            }), 400

        # Se vier ID, é uma edição
        student_id = aluno_data.get('id')
        aluno = None
        eh_edicao = False

        if student_id:
            aluno = Student.query.get(student_id)
            if not aluno:
                return jsonify({"error": "Aluno não encontrado"}), 404
            eh_edicao = True
        else:
            aluno = Student(**{
                'nome': aluno_data.get('nome'),
                'curso': aluno_data.get('curso'),
                'unidade': aluno_data.get('unidade'),
                'periodo': aluno_data.get('periodo'),
                'data_elaboracao': parse_date(aluno_data.get('data_elaboracao')),
                'responsavel': aluno_data.get('responsavel'),
                'data_nascimento': parse_date(aluno_data.get('data_nascimento')),
                'idade': aluno_data.get('idade'),
                'diagnostico_cid': aluno_data.get('diagnostico_cid'),
                'transtorno_identificado': aluno_data.get('transtorno_identificado'),
                'laudo_medico': aluno_data.get('laudo_medico'),
                'psicologo': aluno_data.get('psicologo'),
                'psiquiatra': aluno_data.get('psiquiatra'),
                'psicopedagogo': aluno_data.get('psicopedagogo'),
                'outros_profissionais': aluno_data.get('outros_profissionais'),
                'perfil_aluno': aluno_data.get('perfil_aluno'),
                'observacoes_gerais': aluno_data.get('observacoes_gerais'),
                'proxima_avaliacao': parse_date(aluno_data.get('proxima_avaliacao')),
                'responsavel_legal': aluno_data.get('responsavel_legal'),
                'orientador_responsavel': aluno_data.get('orientador_responsavel'),
                'supervisor': aluno_data.get('supervisor'),
                'gerente_unidade': aluno_data.get('gerente_unidade')
            })
            db.session.add(aluno)
        else:
            # Atualiza campos existentes
            aluno.nome = aluno_data.get('nome')
            aluno.curso = aluno_data.get('curso')
            aluno.unidade = aluno_data.get('unidade')
            aluno.periodo = aluno_data.get('periodo')
            aluno.data_elaboracao = parse_date(aluno_data.get('data_elaboracao'))
            aluno.responsavel = aluno_data.get('responsavel')
            aluno.data_nascimento = parse_date(aluno_data.get('data_nascimento'))
            aluno.idade = aluno_data.get('idade')
            aluno.diagnostico_cid = aluno_data.get('diagnostico_cid')
            aluno.transtorno_identificado = aluno_data.get('transtorno_identificado')
            aluno.laudo_medico = aluno_data.get('laudo_medico')
            aluno.psicologo = aluno_data.get('psicologo')
            aluno.psicopedagogo = aluno_data.get('psicopedagogo')
            aluno.outros_profissionais = aluno_data.get('outros_profissionais')
            aluno.perfil_aluno = aluno_data.get('perfil_aluno')
            aluno.observacoes_gerais = aluno_data.get('observacoes_gerais')
            aluno.proxima_avaliacao = parse_date(aluno_data.get('proxima_avaliacao'))
            aluno.responsavel_legal = aluno_data.get('responsavel_legal')
            aluno.orientador_responsavel = aluno_data.get('orientador_responsavel')
            aluno.supervisor = aluno_data.get('supervisor')
            aluno.gerente_unidade = aluno_data.get('gerente_unidade')

        # Upload do laudo médico (se houver)
        if 'laudo_medico_arquivo' in request.files:
            file = request.files['laudo_medico_arquivo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                aluno.laudo_medico_arquivo = filename

        db.session.flush()

        # Salva conteúdo do PEI como JSON
        pei = PEI.query.filter_by(student_id=aluno.id).first()
        if not pei:
            pei = PEI(student_id=aluno.id)
            db.session.add(pei)

        # Salva conteúdo do PEI
        pei.conteudo = json.dumps(conteudo_data, ensure_ascii=False)

        # Se for edição, salva no histórico
        if eh_edicao:
            historico = PEIHistory(
                pei_id=pei.id,
                editado_por=session.get('user_id'),
                conteudo_anterior=json.dumps(aluno.to_dict()),
                conteudo_novo=json.dumps({
                    **aluno.to_dict(),
                    'peis': pei.conteudo
                })
            )
            db.session.add(historico)

        db.session.commit()
        return jsonify({"message": "✅ Cadastro atualizado com sucesso!", "student_id": aluno.id}), 200

    except Exception as e:
        db.session.rollback()
        print("❌ Erro interno:", str(e))
        return jsonify({
            "error": "Erro ao salvar o PEI",
            "detalhe": str(e)
        }), 500


# ✅ Nova rota: Buscar aluno por ID
@pei_bp.route('/api/alunos', methods=['GET'])
def buscar_aluno_por_id():
    student_id = request.args.get('id')
    if not student_id or not student_id.isdigit():
        return jsonify({"error": "ID do aluno inválido"}), 400

    aluno = Student.query.get(int(student_id))
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    return jsonify(aluno.to_dict()), 200


# ✅ Nova rota: Listar histórico de alterações
@pei_bp.route('/api/historico/<int:pei_id>', methods=['GET'])
def get_historico(pei_id):
    historico = PEIHistory.query.filter_by(pei_id=pei_id).all()
    if not historico:
        return jsonify([]), 200

    return jsonify([{
        'id': h.id,
        'pei_id': h.pei_id,
        'editado_por': h.editado_por,
        'data_edicao': h.data_edicao.isoformat(),
        'conteudo_anterior': h.conteudo_anterior,
        'conteudo_novo': h.conteudo_novo
    } for h in historico]), 200


# ✅ Rota: Gerenciamento de Registros no Banco de dados #

@pei_bp.route('/api/alunos/all', methods=['GET'])
def listar_todos_alunos():
    alunos = Student.query.all()
    return jsonify([{ 
        'id': a.id,
        'nome': a.nome,
        'curso': a.curso,
        'unidade': a.unidade,
        'data_elaboracao': a.data_elaboracao.isoformat() if a.data_elaboracao else None
    } for a in alunos])

@pei_bp.route('/api/alunos/<int:id>', methods=['DELETE'])
def deletar_aluno(id):
    aluno = Student.query.get(id)
    if not aluno:
        return jsonify({'error': 'Aluno não encontrado'}), 404
    db.session.delete(aluno)
    db.session.commit()
    return jsonify({'message': f'✅ Aluno {id} excluído com sucesso.'})

@pei_bp.route('/api/alunos', methods=['DELETE'])
def deletar_todos_alunos():
    Student.query.delete()
    db.session.commit()
    return jsonify({'message': '✅ Todos os alunos foram excluídos.'})

# ✅ Rota: Gerar PDF do PEI
@pei_bp.route('/api/pei/pdf', methods=['POST'])
def gerar_pdf():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Dados inválidos para exportação"}), 400

    logo_url = request.url_root + 'static/assets/senac-logo.png'
    template = """
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {
            font-family: 'DejaVu Sans', 'Roboto', sans-serif;
            padding: 40px;
            color: #333;
            font-size: 14px;
          }
          .header {
            text-align: center;
            margin-bottom: 30px;
          }
          .header img {
            max-width: 160px;
            margin-bottom: 10px;
          }
          h1 {
            color: #003D7C;
            font-size: 24px;
            margin-top: 0;
            text-align: center;
          }
          h2 {
            color: #003D7C;
            font-size: 18px;
            margin-top: 25px;
            border-left: 4px solid #F7931E;
            padding-left: 10px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
          }
          th, td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
          }
          .assinatura {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
          }
          .assinatura div {
            width: 45%;
            text-align: center;
            margin: 10px 0;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <img src="{{ logo_url }}" alt="SENAC Logo">
          <h1>Plano Educacional Individualizado (PEI)</h1>
        </div>
        <p><strong>Nome do Aluno:</strong> {{ nome }}</p>
        <div style="display:flex; gap: 20px;">
          <p><strong>Curso Técnico:</strong> {{ curso }}</p>
          <p><strong>Unidade SENAC:</strong> {{ unidade }}</p>
          <p><strong>Período Letivo:</strong> {{ periodo }}</p>
        </div>
        <div style="display:flex; gap: 20px;">
          <p><strong>Data de Elaboração:</strong> {{ data_elaboracao }}</p>
          <p><strong>Responsável pela Elaboração:</strong> {{ responsavel }}</p>
        </div>
        <h2>1. Identificação do Aluno</h2>
        <div style="display:flex; gap: 20px;">
          <p><strong>Data de Nascimento:</strong> {{ data_nascimento }}</p>
          <p><strong>Idade:</strong> {{ idade }} anos</p>
          <p><strong>Diagnóstico (CID):</strong> {{ diagnostico_cid }}</p>
        </div>
        <div style="display:flex; gap: 20px;">
          <p><strong>Transtorno identificado:</strong> {{ transtorno_identificado }}</p>
          <p><strong>Laudo Médico / Profissional de Saúde:</strong> {{ laudo_medico }}</p>
        </div>
        <p><strong>Psicólogo:</strong> {{ psicologo }}</p>
        <p><strong>Psiquiatra:</strong> {{ psiquiatra }}</p>
        <p><strong>Psicopedagogo:</strong> {{ psicopedagogo }}</p>
        <p><strong>Outros Profissionais:</strong> {{ outros_profissionais }}</p>
        <h2>2. Perfil do Aluno</h2>
        <p>{{ perfil_aluno or 'N/A' }}</p>
        <h2>3. Objetivos Gerais do PEI</h2>
        <p>{{ objetivos_gerais or 'N/A' }}</p>
        <h2>4. Adaptações e Estratégias Pedagógicas</h2>
        <p>{{ adaptaçoes_pedagogicas or 'N/A' }}</p>
        <h2>5. Intervenções Complementares</h2>
        <p>{{ intervencoes_complementares or 'N/A' }}</p>
        <h2>6. Metas Individuais</h2>
        <table>
          <tr><th>Período</th><th>Meta</th><th>Responsável</th><th>Avaliação</th></tr>
          <tr><td>Curto prazo</td><td>{{ meta_curto_prazo }}</td><td>{{ responsavel_curto }}</td><td>{{ avaliacao_curto }}</td></tr>
          <tr><td>Médio prazo</td><td>{{ meta_medio_prazo }}</td><td>{{ responsavel_medio }}</td><td>{{ avaliacao_medio }}</td></tr>
          <tr><td>Longo prazo</td><td>{{ meta_longo_prazo }}</td><td>{{ responsavel_longo }}</td><td>{{ avaliacao_longo }}</td></tr>
        </table>
        <h2>7. Acompanhamento e Revisão do PEI</h2>
        <p><strong>Observações gerais:</strong> {{ observacoes_gerais or 'N/A' }}</p>
        <p><strong>Data da próxima avaliação:</strong> {{ proxima_avaliacao or 'N/A' }}</p>
        <div class="assinatura">
          <div>
            Responsável legal<br>
            __________________________<br>
            {{ responsavel_legal }}
          </div>
          <div>
            Orientador responsável<br>
            __________________________<br>
            {{ orientador_responsavel }}
          </div>
          <div>
            Supervisor<br>
            __________________________<br>
            {{ supervisor }}
          </div>
          <div>
            Gerente de Unidade<br>
            __________________________<br>
            {{ gerente_unidade }}
          </div>
        </div>
      </body>
    </html>
    """

    rendered = render_template_string(template, logo_url=logo_url, **dados)
    options = {
        'encoding': 'utf-8',
        'enable-local-file-access': '',
        'no-stop-slow-scripts': None
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
