# app/controllers/aulas_controller.py - Controller de Aulas (Supabase + DTOs)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, timedelta, time as time_class

from app.repositories import AulaRepository, TurmaRepository, ProfessorRepository, FrequenciaRepository, FeriadoRepository, UsuarioRepository
from app.dtos.aula_dto import AulaDTO

aulas_bp = Blueprint('aulas', __name__, url_prefix='/aulas')

# Instâncias dos repositórios (reutilizadas)
_aula_repo = AulaRepository()
_turma_repo = TurmaRepository()
_professor_repo = ProfessorRepository()
_frequencia_repo = FrequenciaRepository()
_feriado_repo = FeriadoRepository()
_usuario_repo = UsuarioRepository()

# Dicionário de repositórios para DTOs
_repos = {
    'aula': _aula_repo,
    'turma': _turma_repo,
    'professor': _professor_repo,
    'frequencia': _frequencia_repo,
    'feriado': _feriado_repo,
    'usuario': _usuario_repo
}


# ==================== Formulários ====================

class AulaForm(FlaskForm):
    """Formulário de aula."""
    materia = StringField('Matéria', validators=[
        DataRequired(message='Matéria é obrigatória'),
        Length(max=100)
    ])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    turma_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    professor_id = SelectField('Professor', coerce=int, validators=[DataRequired()])
    data = DateField('Data', validators=[DataRequired()])
    horario_inicio = TimeField('Horário Início', validators=[DataRequired()])
    horario_fim = TimeField('Horário Fim', validators=[DataRequired()])
    
    recorrente = BooleanField('Aula Recorrente')
    tipo_recorrencia = SelectField('Tipo de Recorrência', choices=[
        ('', 'Selecione'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual')
    ])
    data_fim_recorrencia = DateField('Data Fim Recorrência', validators=[Optional()])


# ==================== Funções Auxiliares ====================

def _paginate(items: list, page: int, per_page: int = 20):
    """Cria objeto de paginação compatível com Flask-SQLAlchemy."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    
    class PaginateObj:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = max(1, (total + per_page - 1) // per_page)
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
        
        def iter_pages(self):
            for i in range(1, self.pages + 1):
                yield i
    
    return PaginateObj(page_items, page, per_page, total)


def verificar_dia_letivo(data):
    """Verifica se um dia é letivo (não é feriado nem dia não letivo)."""
    from app.repositories.feriado_repository import DiaNaoLetivoRepository
    dia_repo = DiaNaoLetivoRepository()
    
    if _feriado_repo.is_feriado(data):
        return False
    if dia_repo.is_dia_nao_letivo(data):
        return False
    return True


# ==================== Rotas ====================

@aulas_bp.route('/')
@login_required
def index():
    """Lista de aulas."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    turma_id = request.args.get('turma_id', type=int)
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Buscar aulas
    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        aulas_raw = _aula_repo.get_by_date_range(inicio, fim, turma_id)
    elif turma_id:
        aulas_raw = _aula_repo.get_by_turma(turma_id)
    else:
        aulas_raw = _aula_repo.get_all(order_by='-data')
    
    if busca:
        aulas_raw = [a for a in aulas_raw if busca.lower() in a.get('materia', '').lower()]
    
    aulas_list = [AulaDTO(a, _repos) for a in aulas_raw]
    aulas = _paginate(aulas_list, page)
    
    turmas_raw = _turma_repo.get_active_turmas()
    turmas = [type('Turma', (), {'id': t.get('id'), 'nome': t.get('nome'), 'codigo': t.get('codigo')})() for t in turmas_raw]
    
    return render_template('aulas/index.html', 
        aulas=aulas, 
        busca=busca, 
        turmas=turmas,
        turma_id=turma_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@aulas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar nova aula."""
    form = AulaForm()
    
    # Popular choices
    turmas_raw = _turma_repo.get_active_turmas()
    form.turma_id.choices = [(t.get('id'), f'{t.get("nome")} ({t.get("codigo")})') for t in turmas_raw]
    
    professores_raw = _professor_repo.get_active_professores()
    professor_choices = []
    for p in professores_raw:
        usuario = _usuario_repo.get_by_id(p.get('usuario_id'))
        nome = usuario.get('nome', 'N/A') if usuario else 'N/A'
        professor_choices.append((p.get('id'), nome))
    form.professor_id.choices = professor_choices
    
    if form.validate_on_submit():
        # Verificar conflito de horário
        if _aula_repo.check_conflict(form.turma_id.data, form.data.data, 
                                    str(form.horario_inicio.data), str(form.horario_fim.data)):
            flash('Já existe uma aula agendada neste horário para esta turma', 'error')
            return render_template('aulas/form.html', form=form, titulo='Nova Aula')
        
        # Verificar se é dia letivo
        if not verificar_dia_letivo(form.data.data):
            flash('Não é possível agendar aulas em feriados ou dias não letivos', 'error')
            return render_template('aulas/form.html', form=form, titulo='Nova Aula')
        
        # Criar aula
        data = {
            'materia': form.materia.data,
            'descricao': form.descricao.data,
            'turma_id': form.turma_id.data,
            'professor_id': form.professor_id.data,
            'data': str(form.data.data),
            'horario_inicio': str(form.horario_inicio.data),
            'horario_fim': str(form.horario_fim.data),
            'recorrente': form.recorrente.data,
            'tipo_recorrencia': form.tipo_recorrencia.data if form.recorrente.data else None,
            'data_fim_recorrencia': str(form.data_fim_recorrencia.data) if form.recorrente.data and form.data_fim_recorrencia.data else None,
            'dia_semana': form.data.data.weekday() if form.recorrente.data else None,
            'status': 'agendada'
        }
        
        _aula_repo.create(data)
        
        flash('Aula criada com sucesso', 'success')
        return redirect(url_for('aulas.index'))
    
    return render_template('aulas/form.html', form=form, titulo='Nova Aula')


@aulas_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da aula."""
    aula_data = _aula_repo.get_by_id(id)
    if not aula_data:
        flash('Aula não encontrada', 'error')
        return redirect(url_for('aulas.index'))
    
    aula = AulaDTO(aula_data, _repos)
    return render_template('aulas/detalhe.html', aula=aula)


@aulas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar aula."""
    aula_data = _aula_repo.get_by_id(id)
    if not aula_data:
        flash('Aula não encontrada', 'error')
        return redirect(url_for('aulas.index'))
    
    # Verificar permissão
    if current_user.tipo == 'professor':
        professor_data = _professor_repo.get_by_usuario_id(current_user.id)
        if professor_data and aula_data.get('professor_id') != professor_data.get('id'):
            flash('Sem permissão para editar esta aula', 'error')
            return redirect(url_for('aulas.index'))
    
    aula = AulaDTO(aula_data, _repos)
    form = AulaForm(obj=aula)
    
    # Popular choices
    turmas_raw = _turma_repo.get_active_turmas()
    form.turma_id.choices = [(t.get('id'), f'{t.get("nome")} ({t.get("codigo")})') for t in turmas_raw]
    
    professores_raw = _professor_repo.get_active_professores()
    professor_choices = []
    for p in professores_raw:
        usuario = _usuario_repo.get_by_id(p.get('usuario_id'))
        nome = usuario.get('nome', 'N/A') if usuario else 'N/A'
        professor_choices.append((p.get('id'), nome))
    form.professor_id.choices = professor_choices
    
    if form.validate_on_submit():
        data = {
            'materia': form.materia.data,
            'descricao': form.descricao.data,
            'turma_id': form.turma_id.data,
            'professor_id': form.professor_id.data,
            'data': str(form.data.data),
            'horario_inicio': str(form.horario_inicio.data),
            'horario_fim': str(form.horario_fim.data)
        }
        
        _aula_repo.update(id, data)
        
        flash('Aula atualizada com sucesso', 'success')
        return redirect(url_for('aulas.detalhe', id=id))
    
    return render_template('aulas/form.html', form=form, titulo='Editar Aula', aula=aula)


@aulas_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar aula."""
    aula_data = _aula_repo.get_by_id(id)
    if not aula_data:
        flash('Aula não encontrada', 'error')
        return redirect(url_for('aulas.index'))
    
    # Verificar permissão
    if current_user.tipo == 'professor':
        professor_data = _professor_repo.get_by_usuario_id(current_user.id)
        if professor_data and aula_data.get('professor_id') != professor_data.get('id'):
            flash('Sem permissão para cancelar esta aula', 'error')
            return redirect(url_for('aulas.index'))
    
    _aula_repo.cancel_aula(id)
    
    flash('Aula cancelada com sucesso', 'success')
    return redirect(url_for('aulas.index'))


@aulas_bp.route('/<int:id>/realizar', methods=['POST'])
@login_required
def realizar(id):
    """Marcar aula como realizada."""
    aula_data = _aula_repo.get_by_id(id)
    if not aula_data:
        flash('Aula não encontrada', 'error')
        return redirect(url_for('aulas.index'))
    
    # Verificar permissão
    if current_user.tipo == 'professor':
        professor_data = _professor_repo.get_by_usuario_id(current_user.id)
        if professor_data and aula_data.get('professor_id') != professor_data.get('id'):
            flash('Sem permissão', 'error')
            return redirect(url_for('aulas.index'))
    
    _aula_repo.realize_aula(id)
    
    flash('Aula marcada como realizada', 'success')
    return redirect(url_for('aulas.detalhe', id=id))


@aulas_bp.route('/<int:id>/frequencia', methods=['GET', 'POST'])
@login_required
def frequencia(id):
    """Gerenciar frequência da aula."""
    aula_data = _aula_repo.get_by_id(id)
    if not aula_data:
        flash('Aula não encontrada', 'error')
        return redirect(url_for('aulas.index'))
    
    aula = AulaDTO(aula_data, _repos)
    
    if request.method == 'POST':
        alunos = _turma_repo.get_alunos(aula_data.get('turma_id'))
        
        presencas = []
        for aluno in alunos:
            presente = request.form.get(f'aluno_{aluno.get("id")}') == 'on'
            justificativa = request.form.get(f'justificativa_{aluno.get("id")}', '')
            
            presencas.append({
                'aluno_id': aluno.get('id'),
                'presente': presente,
                'justificativa': justificativa
            })
        
        _frequencia_repo.register_batch(id, presencas)
        
        flash('Frequência registrada com sucesso', 'success')
        return redirect(url_for('aulas.detalhe', id=id))
    
    return render_template('aulas/frequencia.html', aula=aula)
