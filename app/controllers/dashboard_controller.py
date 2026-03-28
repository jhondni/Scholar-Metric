# app/controllers/dashboard_controller.py - Controller do Dashboard (Supabase)

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app.repositories import TurmaRepository, AlunoRepository, ProfessorRepository, AulaRepository

dashboard_bp = Blueprint('dashboard', __name__)

# Instâncias dos repositórios
turma_repo = TurmaRepository()
aluno_repo = AlunoRepository()
professor_repo = ProfessorRepository()
aula_repo = AulaRepository()


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Página principal do dashboard."""
    
    # Estatísticas gerais
    total_turmas = turma_repo.count({'ativa': True})
    total_alunos = aluno_repo.count({'status': 'ativo'})
    total_professores = professor_repo.count({'ativo': True})
    
    # Aulas de hoje
    hoje = datetime.utcnow().date()
    aulas_hoje_data = aula_repo.get_by_date(hoje)
    aulas_hoje = len([a for a in aulas_hoje_data if a.get('status') != 'cancelada'])
    
    # Aulas da semana
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    aulas_semana_data = aula_repo.get_by_date_range(inicio_semana, fim_semana)
    aulas_semana = len([a for a in aulas_semana_data if a.get('status') != 'cancelada'])
    
    # Próximas aulas (com dados de turma e professor)
    proximas_aulas_raw = aula_repo.get_upcoming(limit=5)
    proximas_aulas = []
    for aula in proximas_aulas_raw:
        turma = turma_repo.get_by_id(aula.get('turma_id'))
        professor = professor_repo.get_by_id(aula.get('professor_id'))
        
        # Criar objeto compatível com o template
        aula_obj = type('Aula', (), {
            'id': aula.get('id'),
            'materia': aula.get('materia'),
            'data': datetime.strptime(aula.get('data'), '%Y-%m-%d').date() if isinstance(aula.get('data'), str) else aula.get('data'),
            'horario_inicio': datetime.strptime(aula.get('horario_inicio'), '%H:%M:%S').time() if isinstance(aula.get('horario_inicio'), str) else aula.get('horario_inicio'),
            'horario_fim': datetime.strptime(aula.get('horario_fim'), '%H:%M:%S').time() if isinstance(aula.get('horario_fim'), str) else aula.get('horario_fim'),
            'turma': type('Turma', (), {'nome': turma.get('nome', 'N/A') if turma else 'N/A'})(),
            'professor': type('Professor', (), {'usuario': type('Usuario', (), {'nome': 'N/A'})()})()
        })()
        
        # Buscar nome do professor via join com usuarios
        if professor:
            from app.repositories import UsuarioRepository
            usuario_repo = UsuarioRepository()
            usuario = usuario_repo.get_by_id(professor.get('usuario_id'))
            if usuario:
                aula_obj.professor = type('Professor', (), {
                    'usuario': type('Usuario', (), {'nome': usuario.get('nome', 'N/A')})()
                })()
        
        proximas_aulas.append(aula_obj)
    
    return render_template('dashboard/index.html',
        total_turmas=total_turmas,
        total_alunos=total_alunos,
        total_professores=total_professores,
        aulas_hoje=aulas_hoje,
        aulas_semana=aulas_semana,
        proximas_aulas=proximas_aulas
    )
