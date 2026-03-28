# app/controllers/calendario_controller.py - Controller do Calendário (Supabase)

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
import calendar

from app.repositories import AulaRepository, FeriadoRepository, TurmaRepository, ProfessorRepository, UsuarioRepository
from app.repositories.feriado_repository import DiaNaoLetivoRepository

calendario_bp = Blueprint('calendario', __name__, url_prefix='/calendario')

# Instâncias dos repositórios
aula_repo = AulaRepository()
feriado_repo = FeriadoRepository()
dia_nao_letivo_repo = DiaNaoLetivoRepository()
turma_repo = TurmaRepository()
professor_repo = ProfessorRepository()
usuario_repo = UsuarioRepository()


@calendario_bp.route('/')
@login_required
def index():
    """Página do calendário."""
    return render_template('calendario/index.html')


@calendario_bp.route('/api/eventos')
@login_required
def api_eventos():
    """API para obter eventos do calendário."""
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    
    if not inicio or not fim:
        hoje = datetime.utcnow().date()
        inicio = hoje.replace(day=1)
        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
        fim = hoje.replace(day=ultimo_dia)
    else:
        inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(fim, '%Y-%m-%d').date()
    
    eventos = []
    
    # Aulas
    aulas = aula_repo.get_by_date_range(inicio, fim)
    
    for aula in aulas:
        if aula.get('status') == 'cancelada':
            continue
        
        turma = turma_repo.get_by_id(aula.get('turma_id'))
        professor = professor_repo.get_by_id(aula.get('professor_id'))
        usuario = usuario_repo.get_by_id(professor.get('usuario_id')) if professor else None
        
        data_aula = aula.get('data')
        horario_inicio = aula.get('horario_inicio', '00:00:00')
        horario_fim = aula.get('horario_fim', '00:00:00')
        
        if isinstance(horario_inicio, str) and len(horario_inicio) > 5:
            horario_inicio = horario_inicio[:5]
        if isinstance(horario_fim, str) and len(horario_fim) > 5:
            horario_fim = horario_fim[:5]
        
        eventos.append({
            'id': f'aula_{aula.get("id")}',
            'title': f'{aula.get("materia")} - {turma.get("nome", "N/A") if turma else "N/A"}',
            'start': f'{data_aula}T{horario_inicio}',
            'end': f'{data_aula}T{horario_fim}',
            'type': 'aula',
            'color': '#4f46e5',
            'turma': turma.get('nome', 'N/A') if turma else 'N/A',
            'professor': usuario.get('nome', 'N/A') if usuario else 'N/A'
        })
    
    # Feriados
    feriados = feriado_repo.get_in_period(inicio, fim)
    
    for feriado in feriados:
        eventos.append({
            'id': f'feriado_{feriado.get("id")}',
            'title': feriado.get('nome', ''),
            'start': feriado.get('data'),
            'end': feriado.get('data'),
            'type': 'feriado',
            'color': '#ef4444',
            'allDay': True
        })
    
    # Dias não letivos
    dias = dia_nao_letivo_repo.get_in_period(inicio, fim)
    
    for dia in dias:
        eventos.append({
            'id': f'nao_letivo_{dia.get("id")}',
            'title': dia.get('nome', ''),
            'start': dia.get('data_inicio'),
            'end': dia.get('data_fim'),
            'type': 'nao_letivo',
            'color': '#f59e0b',
            'allDay': True
        })
    
    return jsonify(eventos)


@calendario_bp.route('/feriados', methods=['GET', 'POST'])
@login_required
def feriados():
    """Gerenciar feriados."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
        tipo = request.form.get('tipo', 'nacional')
        descricao = request.form.get('descricao', '')
        
        if feriado_repo.get_by_date(data):
            return jsonify({'error': 'Já existe um feriado nesta data'}), 400
        
        feriado_repo.create({
            'nome': nome,
            'data': str(data),
            'tipo': tipo,
            'descricao': descricao,
            'recorrente': False
        })
        
        return jsonify({'success': True, 'message': 'Feriado cadastrado'})
    
    feriados_raw = feriado_repo.get_all(order_by='data')
    
    # Converter para objetos
    feriados_lista = [type('Feriado', (), {
        'id': f.get('id'),
        'nome': f.get('nome', ''),
        'data': datetime.strptime(f.get('data'), '%Y-%m-%d').date() if isinstance(f.get('data'), str) else f.get('data'),
        'tipo': f.get('tipo', ''),
        'descricao': f.get('descricao', '')
    })() for f in feriados_raw]
    
    return render_template('calendario/feriados.html', feriados=feriados_lista)


@calendario_bp.route('/feriados/<int:id>/excluir', methods=['DELETE'])
@login_required
def excluir_feriado(id):
    """Excluir feriado."""
    feriado_repo.delete(id)
    return jsonify({'success': True, 'message': 'Feriado excluído'})


@calendario_bp.route('/dias-nao-letivos', methods=['GET', 'POST'])
@login_required
def dias_nao_letivos():
    """Gerenciar dias não letivos."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_inicio = datetime.strptime(request.form.get('data_inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.form.get('data_fim'), '%Y-%m-%d').date()
        tipo = request.form.get('tipo', 'recesso')
        descricao = request.form.get('descricao', '')
        
        dia_nao_letivo_repo.create({
            'nome': nome,
            'data_inicio': str(data_inicio),
            'data_fim': str(data_fim),
            'tipo': tipo,
            'descricao': descricao
        })
        
        return jsonify({'success': True, 'message': 'Dia não letivo cadastrado'})
    
    dias_raw = dia_nao_letivo_repo.get_all(order_by='-data_inicio')
    
    # Converter para objetos
    dias = [type('DiaNaoLetivo', (), {
        'id': d.get('id'),
        'nome': d.get('nome', ''),
        'data_inicio': datetime.strptime(d.get('data_inicio'), '%Y-%m-%d').date() if isinstance(d.get('data_inicio'), str) else d.get('data_inicio'),
        'data_fim': datetime.strptime(d.get('data_fim'), '%Y-%m-%d').date() if isinstance(d.get('data_fim'), str) else d.get('data_fim'),
        'tipo': d.get('tipo', ''),
        'descricao': d.get('descricao', '')
    })() for d in dias_raw]
    
    return render_template('calendario/dias_nao_letivos.html', dias=dias)


@calendario_bp.route('/dias-nao-letivos/<int:id>/excluir', methods=['DELETE'])
@login_required
def excluir_dia_nao_letivo(id):
    """Excluir dia não letivo."""
    dia_nao_letivo_repo.delete(id)
    return jsonify({'success': True, 'message': 'Dia não letivo excluído'})
