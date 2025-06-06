from flask import Blueprint, request, jsonify, render_template_string
from models.models import Student, PEI
from database.connection import db
import pdfkit
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os

pei_bp = Blueprint('pei', __name__)


def parse_date(date_str):
    """Converte string de data para objeto date"""
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
        if request.content_type.startswith('application/json'):
            data = request.get_json()
            aluno_data = data.get('aluno')
            conteudo_data = data.get('conteudo')
        else:
            aluno_data = json.loads(request.form.get('aluno'))
            conteudo_data = json.loads(request.form.get('conteudo'))

        student_id = aluno_data.get('id')

        # Se for edição, busca o aluno existente
        if student_id and str(student_id).isdigit():
            aluno = Student.query.get(int(student_id))
            if not aluno:
                return jsonify({"error": "Aluno não encontrado"}), 404

            # Atualiza campos editáveis
            aluno.data_nascimento = parse_date(aluno_data.get('data_nascimento'))
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
            aluno.proxima_avaliacao = parse_date(aluno_data.get('proxima_avaliacao'))
            aluno.responsavel_legal = aluno_data.get('responsavel_legal')
            aluno.orientador_responsavel = aluno_data.get('orientador_responsavel')
            aluno.supervisor = aluno_data.get('supervisor')
            aluno.gerente_unidade = aluno_data.get('gerente_unidade')

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
            db.session.flush()

            # Upload do laudo médico (opcional)
            if 'laudo_medico_arquivo' in request.files:
                file = request.files['laudo_medico_arquivo']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    aluno.laudo_medico_arquivo = filename

        # Salva o conteúdo do PEI como JSON
        pei = PEI(
            student_id=aluno.id,
            conteudo=json.dumps(conteudo_data, ensure_ascii=False)
        )
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


# ✅ Nova rota: Busca alunos por nome (usada na search.html)
@pei_bp.route('/api/alunos', methods=['GET'])
def buscar_alunos():
    nome = request.args.get('nome')
    if not nome:
        return jsonify({"error": "Nome é obrigatório"}), 400

    alunos = Student.query.filter(Student.nome.ilike(f'%{nome}%')).all()
    if not alunos:
        return jsonify([])

    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'curso': a.curso,
        'unidade': a.unidade,
        'periodo': a.periodo,
        'data_elaboracao': a.data_elaboracao.isoformat() if a.data_elaboracao else None,
        'responsavel': a.responsavel,
        'data_nascimento': a.data_nascimento.isoformat() if a.data_nascimento else None,
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
        'proxima_avaliacao': a.proxima_avaliacao.isoformat() if a.proxima_avaliacao else None,
        'responsavel_legal': a.responsavel_legal,
        'orientador_responsavel': a.orientador_responsavel,
        'supervisor': a.supervisor,
        'gerente_unidade': a.gerente_unidade
    } for a in alunos])


# ✅ Nova rota: Buscar versão específica do PEI
@pei_bp.route('/api/pei/<int:pei_id>', methods=['GET'])
def get_pei_by_id(pei_id):
    pei = PEI.query.get(pei_id)
    if not pei:
        return jsonify({"error": "Versão do PEI não encontrada"}), 404

    aluno = Student.query.get(pei.student_id)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    try:
        conteudo = json.loads(pei.conteudo) if isinstance(pei.conteudo, str) else pei.conteudo
    except:
        conteudo = {}

    return jsonify({
        "aluno": aluno.to_dict(),
        "conteudo": conteudo,
        "pei_id": pei.id,
        "data_registro": pei.data_registro.isoformat()
    }), 200


# ✅ Nova rota: Exportar como PDF
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
        <p><strong>Transtorno identificado:</strong> {{ transtorno_identificado }}</p>
        <p><strong>Laudo Médico:</strong> {{ laudo_medico }}</p>
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
