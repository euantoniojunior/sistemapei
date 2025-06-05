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

        campos_obrigatorios = ['nome', 'curso', 'unidade', 'periodo', 'data_elaboracao', 'responsavel']
        faltando = [campo for campo in campos_obrigatorios if not aluno_data.get(campo)]
        if faltando:
            return jsonify({"error": "Campos obrigatórios ausentes", "campos": faltando}), 400

        data_elaboracao = parse_date(aluno_data.get('data_elaboracao'))
        data_nascimento = parse_date(aluno_data.get('data_nascimento'))
        proxima_avaliacao = parse_date(aluno_data.get('proxima_avaliacao'))

        aluno = Student(
            nome=aluno_data.get('nome'),
            curso=aluno_data.get('curso'),
            unidade=aluno_data.get('unidade'),
            periodo=aluno_data.get('periodo'),
            data_elaboracao=data_elaboracao,
            responsavel=aluno_data.get('responsavel'),
            data_nascimento=data_nascimento,
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
            proxima_avaliacao=proxima_avaliacao,
            responsavel_legal=aluno_data.get('responsavel_legal'),
            orientador_responsavel=aluno_data.get('orientador_responsavel'),
            supervisor=aluno_data.get('supervisor'),
            gerente_unidade=aluno_data.get('gerente_unidade')
        )

        db.session.add(aluno)
        db.session.flush()

        if 'laudo_medico_arquivo' in request.files:
            file = request.files['laudo_medico_arquivo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                aluno.laudo_medico_arquivo = filename

        pei = PEI(
            student_id=aluno.id,
            conteudo=json.dumps(conteudo_data, ensure_ascii=False)
        )
        db.session.add(pei)
        db.session.commit()
        return jsonify({"message": "✅ PEI criado com sucesso!", "student_id": aluno.id}), 201

    except Exception as e:
        db.session.rollback()
        print("❌ Erro interno:", str(e))
        return jsonify({
            "error": "Erro ao salvar o PEI",
            "detalhe": str(e)
        }), 500

# ✅ Nova rota: Buscar aluno por ID (para edição)
@pei_bp.route('/api/alunos', methods=['GET'])
def buscar_aluno_por_id():
    student_id = request.args.get('id')
    if not student_id or not student_id.isdigit():
        return jsonify({"error": "ID do aluno inválido"}), 400

    aluno = Student.query.get(int(student_id))
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
