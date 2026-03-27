# app/controllers/dashboard_controller.py - Controller do Dashboard

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.aula import Aula
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Página principal do dashboard."""
    
    # Estatísticas gerais
    total_turmas = Turma.query.filter_by(ativa=True).count()
    total_alunos = Aluno.query.filter_by(status='ativo').count()
    total_professores = Professor.query.filter_by(ativo=True).count()
    
    # Aulas de hoje
    hoje = datetime.utcnow().date()
    aulas_hoje = Aula.query.filter_by(data=hoje).filter(
        Aula.status != 'cancelada'
    ).count()
    
    # Aulas da semana
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    aulas_semana = Aula.query.filter(
        Aula.data >= inicio_semana,
        Aula.data <= fim_semana,
        Aula.status != 'cancelada'
    ).count()
    
    # Próximas aulas
    proximas_aulas = Aula.query.filter(
        Aula.data >= hoje,
        Aula.status == 'agendada'
    ).order_by(Aula.data, Aula.horario_inicio).limit(5).all()
    
    return render_template('dashboard/index.html',
        total_turmas=total_turmas,
        total_alunos=total_alunos,
        total_professores=total_professores,
        aulas_hoje=aulas_hoje,
        aulas_semana=aulas_semana,
        proximas_aulas=proximas_aulas
    )
