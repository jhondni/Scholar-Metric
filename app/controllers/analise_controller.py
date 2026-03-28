# app/controllers/analise_controller.py - Controller de Análise (Supabase)

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta

from app.repositories import AlunoRepository, TurmaRepository, ProfessorRepository, AulaRepository, NotaRepository, FrequenciaRepository

analise_bp = Blueprint('analise', __name__, url_prefix='/analise')

# Instâncias dos repositórios
aluno_repo = AlunoRepository()
turma_repo = TurmaRepository()
professor_repo = ProfessorRepository()
aula_repo = AulaRepository()
nota_repo = NotaRepository()
frequencia_repo = FrequenciaRepository()


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
    turmas_raw = turma_repo.get_active_turmas()
    dist_turmas = [{
        'nome': t.get('nome', ''),
        'total': turma_repo.count_alunos(t.get('id')),
        'capacidade': t.get('capacidade_maxima', 40)
    } for t in turmas_raw]
    
    # Aulas por mês (últimos 6 meses)
    hoje = datetime.utcnow().date()
    aulas_por_mes = []
    
    for i in range(5, -1, -1):
        mes = hoje.month - i
        ano = hoje.year
        if mes <= 0:
            mes += 12
            ano -= 1
        
        # Buscar aulas do mês
        inicio_mes = datetime(ano, mes, 1).date()
        if mes == 12:
            fim_mes = datetime(ano + 1, 1, 1).date() - timedelta(days=1)
        else:
            fim_mes = datetime(ano, mes + 1, 1).date() - timedelta(days=1)
        
        aulas_mes = aula_repo.get_by_date_range(inicio_mes, fim_mes)
        total = len([a for a in aulas_mes if a.get('status') != 'cancelada'])
        
        aulas_por_mes.append({
            'mes': f'{mes:02d}/{ano}',
            'total': total
        })
    
    return jsonify({
        'dist_turmas': dist_turmas,
        'aulas_por_mes': aulas_por_mes,
        'total_alunos': aluno_repo.count({'status': 'ativo'}),
        'total_turmas': turma_repo.count({'ativa': True}),
        'total_professores': professor_repo.count({'ativo': True})
    })


@analise_bp.route('/api/alunos/risco')
@login_required
def api_alunos_risco():
    """API com alunos em risco de evasão."""
    alunos_raw = aluno_repo.get_active_students()
    
    alunos_risco = []
    for aluno in alunos_raw:
        aluno_id = aluno.get('id')
        
        # Calcular frequência
        freq_stats = frequencia_repo.get_aluno_stats(aluno_id)
        freq = freq_stats.get('percentual', 100.0)
        
        # Calcular média
        nota_stats = nota_repo.get_aluno_stats(aluno_id)
        media = nota_stats.get('media', 0.0)
        
        # Calcular risco
        risco = 'baixo'
        if freq < 75 or media < 5:
            risco = 'alto'
        elif freq < 85 or media < 7:
            risco = 'medio'
        
        if risco != 'baixo':
            alunos_risco.append({
                'id': aluno_id,
                'nome': aluno.get('nome', ''),
                'matricula': aluno.get('matricula', ''),
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
    turmas_raw = turma_repo.get_active_turmas()
    
    desempenho = []
    for turma in turmas_raw:
        turma_id = turma.get('id')
        
        # Calcular média da turma
        media = nota_repo.get_turma_average(turma_id)
        
        # Calcular frequência média
        alunos = turma_repo.get_alunos(turma_id)
        total_freq = 0
        count_alunos = len(alunos)
        
        for aluno in alunos:
            freq_stats = frequencia_repo.get_aluno_stats(aluno.get('id'), turma_id)
            total_freq += freq_stats.get('percentual', 100.0)
        
        freq_media = total_freq / count_alunos if count_alunos > 0 else 100.0
        
        desempenho.append({
            'id': turma_id,
            'nome': turma.get('nome', ''),
            'media': round(media, 1),
            'frequencia': round(freq_media, 1),
            'total_alunos': count_alunos
        })
    
    return jsonify(desempenho)


@analise_bp.route('/api/disciplinas')
@login_required
def api_disciplinas():
    """API com desempenho por disciplina."""
    # Buscar todas as aulas e notas
    aulas_raw = aula_repo.get_all()
    
    # Agrupar notas por matéria
    materias_stats = {}
    
    for aula in aulas_raw:
        materia = aula.get('materia', 'N/A')
        aula_id = aula.get('id')
        
        # Buscar notas desta aula
        notas = nota_repo.get_by_field('aula_id', aula_id)
        
        if materia not in materias_stats:
            materias_stats[materia] = {'soma': 0, 'total': 0}
        
        for nota in notas:
            materias_stats[materia]['soma'] += nota.get('valor', 0)
            materias_stats[materia]['total'] += 1
    
    disciplinas = [{
        'materia': materia,
        'media': round(stats['soma'] / stats['total'], 1) if stats['total'] > 0 else 0,
        'total': stats['total']
    } for materia, stats in materias_stats.items()]
    
    return jsonify(disciplinas)
