# app/controllers/analise_controller.py - Controller de Análise

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.professor import Professor
from app.models.aula import Aula
from app.models.nota import Nota
from app.models.frequencia import Frequencia

analise_bp = Blueprint('analise', __name__, url_prefix='/analise')


@analise_bp.route('/')
@login_required
def index():
    """Página principal de análise."""
    return render_template('analise/index.html')


@analise_bp.route('/api/geral')
@login_required
def api_geral():
    """API com estatísticas gerais."""
    # Distribuição de alunos por turma
    turmas = Turma.query.filter_by(ativa=True).all()
    dist_turmas = [{
        'nome': t.nome,
        'total': t.total_alunos(),
        'capacidade': t.capacidade_maxima
    } for t in turmas]
    
    # Aulas por mês (últimos 6 meses)
    hoje = datetime.utcnow().date()
    aulas_por_mes = []
    for i in range(5, -1, -1):
        mes = hoje.month - i
        ano = hoje.year
        if mes <= 0:
            mes += 12
            ano -= 1
        
        total = Aula.query.filter(
            func.extract('month', Aula.data) == mes,
            func.extract('year', Aula.data) == ano,
            Aula.status != 'cancelada'
        ).count()
        
        aulas_por_mes.append({
            'mes': f'{mes:02d}/{ano}',
            'total': total
        })
    
    return jsonify({
        'dist_turmas': dist_turmas,
        'aulas_por_mes': aulas_por_mes,
        'total_alunos': Aluno.query.filter_by(status='ativo').count(),
        'total_turmas': Turma.query.filter_by(ativa=True).count(),
        'total_professores': Professor.query.filter_by(ativo=True).count()
    })


@analise_bp.route('/api/alunos/risco')
@login_required
def api_alunos_risco():
    """API com alunos em risco de evasão."""
    alunos = Aluno.query.filter_by(status='ativo').all()
    
    alunos_risco = []
    for aluno in alunos:
        freq = aluno.percentual_frequencia()
        media = aluno.media_notas()
        
        # Calcular risco
        risco = 'baixo'
        if freq < 75 or media < 5:
            risco = 'alto'
        elif freq < 85 or media < 7:
            risco = 'medio'
        
        if risco != 'baixo':
            alunos_risco.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'matricula': aluno.matricula,
                'frequencia': round(freq, 1),
                'media': round(media, 1),
                'risco': risco
            })
    
    # Ordenar por risco (alto primeiro)
    alunos_risco.sort(key=lambda x: 0 if x['risco'] == 'alto' else 1)
    
    return jsonify(alunos_risco)


@analise_bp.route('/api/turmas/desempenho')
@login_required
def api_turmas_desempenho():
    """API com desempenho das turmas."""
    turmas = Turma.query.filter_by(ativa=True).all()
    
    desempenho = []
    for turma in turmas:
        media = turma.media_turma()
        freq = turma.percentual_frequencia_media()
        
        desempenho.append({
            'id': turma.id,
            'nome': turma.nome,
            'media': round(media, 1),
            'frequencia': round(freq, 1),
            'total_alunos': turma.total_alunos()
        })
    
    return jsonify(desempenho)


@analise_bp.route('/api/disciplinas')
@login_required
def api_disciplinas():
    """API com desempenho por disciplina."""
    # Média de notas por matéria
    notas_por_materia = db.session.query(
        Aula.materia,
        func.avg(Nota.valor).label('media'),
        func.count(Nota.id).label('total')
    ).join(Nota, Nota.aula_id == Aula.id).group_by(Aula.materia).all()
    
    disciplinas = [{
        'materia': materia,
        'media': round(float(media or 0), 1),
        'total': total
    } for materia, media, total in notas_por_materia]
    
    return jsonify(disciplinas)
