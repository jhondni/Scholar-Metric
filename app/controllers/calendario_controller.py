# app/controllers/calendario_controller.py - Controller do Calendário

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
import calendar

from app.models.aula import Aula
from app.models.feriado import Feriado
from app.models.dia_nao_letivo import DiaNaoLetivo

calendario_bp = Blueprint('calendario', __name__, url_prefix='/calendario')


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
        # Padrão: mês atual
        hoje = datetime.utcnow().date()
        inicio = hoje.replace(day=1)
        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
        fim = hoje.replace(day=ultimo_dia)
    else:
        inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(fim, '%Y-%m-%d').date()
    
    eventos = []
    
    # Aulas
    aulas = Aula.query.filter(
        Aula.data >= inicio,
        Aula.data <= fim,
        Aula.status != 'cancelada'
    ).all()
    
    for aula in aulas:
        eventos.append({
            'id': f'aula_{aula.id}',
            'title': f'{aula.materia} - {aula.turma.nome}',
            'start': f'{aula.data.isoformat()}T{aula.horario_inicio.strftime("%H:%M")}',
            'end': f'{aula.data.isoformat()}T{aula.horario_fim.strftime("%H:%M")}',
            'type': 'aula',
            'color': '#4f46e5',
            'turma': aula.turma.nome,
            'professor': aula.professor.usuario.nome
        })
    
    # Feriados
    feriados = Feriado.query.filter(
        Feriado.data >= inicio,
        Feriado.data <= fim
    ).all()
    
    for feriado in feriados:
        eventos.append({
            'id': f'feriado_{feriado.id}',
            'title': feriado.nome,
            'start': feriado.data.isoformat(),
            'end': feriado.data.isoformat(),
            'type': 'feriado',
            'color': '#ef4444',
            'allDay': True
        })
    
    # Dias não letivos
    dias_nao_letivos = DiaNaoLetivo.query.filter(
        DiaNaoLetivo.data_inicio <= fim,
        DiaNaoLetivo.data_fim >= inicio
    ).all()
    
    for dia in dias_nao_letivos:
        eventos.append({
            'id': f'nao_letivo_{dia.id}',
            'title': dia.nome,
            'start': dia.data_inicio.isoformat(),
            'end': dia.data_fim.isoformat(),
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
        from app import db
        
        nome = request.form.get('nome')
        data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
        tipo = request.form.get('tipo', 'nacional')
        descricao = request.form.get('descricao', '')
        
        if Feriado.query.filter_by(data=data).first():
            return jsonify({'error': 'Já existe um feriado nesta data'}), 400
        
        feriado = Feriado(
            nome=nome,
            data=data,
            tipo=tipo,
            descricao=descricao
        )
        
        db.session.add(feriado)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feriado cadastrado'})
    
    feriados_lista = Feriado.query.order_by(Feriado.data).all()
    return render_template('calendario/feriados.html', feriados=feriados_lista)


@calendario_bp.route('/feriados/<int:id>/excluir', methods=['DELETE'])
@login_required
def excluir_feriado(id):
    """Excluir feriado."""
    from app import db
    
    feriado = Feriado.query.get_or_404(id)
    db.session.delete(feriado)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Feriado excluído'})


@calendario_bp.route('/dias-nao-letivos', methods=['GET', 'POST'])
@login_required
def dias_nao_letivos():
    """Gerenciar dias não letivos."""
    if request.method == 'POST':
        from app import db
        
        nome = request.form.get('nome')
        data_inicio = datetime.strptime(request.form.get('data_inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.form.get('data_fim'), '%Y-%m-%d').date()
        tipo = request.form.get('tipo', 'recesso')
        descricao = request.form.get('descricao', '')
        
        dia = DiaNaoLetivo(
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo,
            descricao=descricao
        )
        
        db.session.add(dia)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Dia não letivo cadastrado'})
    
    dias = DiaNaoLetivo.query.order_by(DiaNaoLetivo.data_inicio.desc()).all()
    return render_template('calendario/dias_nao_letivos.html', dias=dias)


@calendario_bp.route('/dias-nao-letivos/<int:id>/excluir', methods=['DELETE'])
@login_required
def excluir_dia_nao_letivo(id):
    """Excluir dia não letivo."""
    from app import db
    
    dia = DiaNaoLetivo.query.get_or_404(id)
    db.session.delete(dia)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Dia não letivo excluído'})
