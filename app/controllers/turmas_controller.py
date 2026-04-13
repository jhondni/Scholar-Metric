# app/controllers/turmas_controller.py - Controller de Turmas (Supabase + DTOs)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime

from app.repositories import TurmaRepository, AlunoRepository, MateriaRepository
from app.dtos.turma_dto import TurmaDTO

turmas_bp = Blueprint('turmas', __name__, url_prefix='/turmas')

# Instâncias dos repositórios (reutilizadas)
_turma_repo = TurmaRepository()
_aluno_repo = AlunoRepository()
_materia_repo = MateriaRepository()

# Dicionário de repositórios para DTOs
_repos = {
    'turma': _turma_repo,
    'aluno': _aluno_repo,
    'materia': _materia_repo
}


# ==================== Formulários ====================

class TurmaForm(FlaskForm):
    """Formulário de turma."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=50)
    ])
    codigo = StringField('Código', validators=[
        DataRequired(message='Código é obrigatório'),
        Length(max=20)
    ])
    serie = StringField('Série', validators=[
        DataRequired(message='Série é obrigatória'),
        Length(max=30)
    ])
    ano_letivo = IntegerField('Ano Letivo', validators=[
        DataRequired(message='Ano letivo é obrigatório'),
        NumberRange(min=2020, max=2030)
    ])
    turno = SelectField('Turno', choices=[
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite')
    ], validators=[DataRequired()])
    capacidade_maxima = IntegerField('Capacidade', validators=[
        NumberRange(min=1, max=100)
    ], default=40)
    descricao = TextAreaField('Descrição')


# ==================== Funções Auxiliares ====================

def _paginate(items: list, page: int, per_page: int = 20):
    """
    Cria objeto de paginação compatível com Flask-SQLAlchemy.
    
    Args:
        items: Lista de itens
        page: Página atual
        per_page: Itens por página
        
    Returns:
        Objeto de paginação
    """
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


# ==================== Rotas ====================

@turmas_bp.route('/')
@login_required
def index():
    """Lista de turmas."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    turmas_raw = _turma_repo.get_all(order_by='nome')
    
    if busca:
        turmas_raw = [t for t in turmas_raw 
                      if busca.lower() in t.get('nome', '').lower() 
                      or busca.lower() in t.get('codigo', '').lower()]
    
    turmas_list = [TurmaDTO(t, _repos) for t in turmas_raw]
    turmas = _paginate(turmas_list, page)
    
    return render_template('turmas/index.html', turmas=turmas, busca=busca)


@turmas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar nova turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para criar turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    form = TurmaForm()
    
    if form.validate_on_submit():
        if _turma_repo.get_by_codigo(form.codigo.data):
            flash('Código de turma já existe', 'error')
            return render_template('turmas/form.html', form=form, titulo='Nova Turma')
        
        data = {
            'nome': form.nome.data,
            'codigo': form.codigo.data,
            'serie': form.serie.data,
            'ano_letivo': form.ano_letivo.data,
            'turno': form.turno.data,
            'capacidade_maxima': form.capacidade_maxima.data or 40,
            'descricao': form.descricao.data,
            'ativa': True
        }
        
        _turma_repo.create(data)
        
        flash('Turma criada com sucesso', 'success')
        return redirect(url_for('turmas.index'))
    
    return render_template('turmas/form.html', form=form, titulo='Nova Turma')


@turmas_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da turma."""
    turma_data = _turma_repo.get_by_id(id)
    if not turma_data:
        flash('Turma não encontrada', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = TurmaDTO(turma_data, _repos)
    return render_template('turmas/detalhe.html', turma=turma)


@turmas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    turma_data = _turma_repo.get_by_id(id)
    if not turma_data:
        flash('Turma não encontrada', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = TurmaDTO(turma_data, _repos)
    form = TurmaForm(obj=turma)
    
    if form.validate_on_submit():
        data = {
            'nome': form.nome.data,
            'serie': form.serie.data,
            'ano_letivo': form.ano_letivo.data,
            'turno': form.turno.data,
            'capacidade_maxima': form.capacidade_maxima.data or 40,
            'descricao': form.descricao.data
        }
        
        _turma_repo.update(id, data)
        
        flash('Turma atualizada com sucesso', 'success')
        return redirect(url_for('turmas.detalhe', id=id))
    
    return render_template('turmas/form.html', form=form, titulo='Editar Turma', turma=turma)


@turmas_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir turma."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    _turma_repo.update(id, {'ativa': False})
    
    flash('Turma desativada com sucesso', 'success')
    return redirect(url_for('turmas.index'))


@turmas_bp.route('/<int:id>/alunos', methods=['POST'])
@login_required
def adicionar_aluno(id):
    """Adicionar aluno à turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    aluno_id = request.json.get('aluno_id')
    
    turma_data = _turma_repo.get_by_id(id)
    if not turma_data:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    if _turma_repo.count_alunos(id) >= turma_data.get('capacidade_maxima', 40):
        return jsonify({'error': 'Turma atingiu capacidade máxima'}), 400
    
    if _turma_repo.associate_aluno(id, aluno_id):
        return jsonify({'success': True, 'message': 'Aluno adicionado'})
    
    return jsonify({'error': 'Erro ao adicionar aluno'}), 400


@turmas_bp.route('/<int:id>/alunos/<int:aluno_id>', methods=['DELETE'])
@login_required
def remover_aluno(id, aluno_id):
    """Remover aluno da turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if _aluno_repo.dissociate_from_turma(aluno_id, id):
        return jsonify({'success': True, 'message': 'Aluno removido'})
    
    return jsonify({'error': 'Erro ao remover aluno'}), 400


# ==================== Matérias da Turma ====================

@turmas_bp.route('/<int:id>/materias', methods=['GET', 'POST'])
@login_required
def materias(id):
    """Gerenciar matérias da turma com quantidade de aulas por período."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerenciar matérias de turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    turma_data = _turma_repo.get_by_id(id)
    if not turma_data:
        flash('Turma não encontrada', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = TurmaDTO(turma_data, _repos)
    
    if request.method == 'POST':
        materia_ids = request.form.getlist('materias')
        
        from app.models.materia import turma_materias
        from app import db
        
        db.session.execute(
            turma_materias.delete().where(turma_materias.c.turma_id == id)
        )
        
        for mid in materia_ids:
            aulas = request.form.get(f'aulas_{mid}', 2, type=int)
            _turma_repo.set_materia(id, int(mid), aulas)
        
        flash('Matérias da turma atualizadas com sucesso', 'success')
        return redirect(url_for('turmas.detalhe', id=id))
    
    from app.dtos.materia_dto import MateriaDTO
    
    materias_raw = _materia_repo.get_active_materias()
    materias = [MateriaDTO(m, _repos) for m in materias_raw]
    
    return render_template('turmas/materias.html', turma=turma, materias=materias)


@turmas_bp.route('/<int:id>/materias/adicionar', methods=['POST'])
@login_required
def adicionar_materia(id):
    """Adiciona uma matéria à turma via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    materia_id = request.json.get('materia_id')
    aulas_por_periodo = request.json.get('aulas_por_periodo', 2)
    
    if _turma_repo.set_materia(id, materia_id, aulas_por_periodo):
        return jsonify({'success': True, 'message': 'Matéria adicionada'})
    
    return jsonify({'error': 'Erro ao adicionar matéria'}), 400


@turmas_bp.route('/<int:id>/materias/<int:materia_id>', methods=['DELETE'])
@login_required
def remover_materia(id, materia_id):
    """Remove uma matéria da turma via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if _turma_repo.remove_materia(id, materia_id):
        return jsonify({'success': True, 'message': 'Matéria removida'})
    
    return jsonify({'error': 'Erro ao remover matéria'}), 400


# ==================== Geração de Calendário ====================

@turmas_bp.route('/<int:id>/gerar-calendario', methods=['POST'])
@login_required
def gerar_calendario(id):
    """Gera calendário automático para a turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerar calendário', 'error')
        return redirect(url_for('turmas.index'))
    
    turma_data = _turma_repo.get_by_id(id)
    if not turma_data:
        flash('Turma não encontrada', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = TurmaDTO(turma_data, _repos)
    
    if not turma.materias:
        flash('A turma não possui matérias cadastradas. Adicione matérias antes de gerar o calendário.', 'error')
        return redirect(url_for('turmas.detalhe', id=id))
    
    periodo = request.form.get('periodo', 'semestral')
    
    try:
        from app.services.gerador_calendario import gerar_calendario_avancado
        
        resultado = gerar_calendario_avancado(
            turma_id=id,
            periodo=periodo
        )
        
        if resultado['success']:
            flash(f'Calendário gerado com sucesso! {resultado["total_aulas"]} aulas criadas.', 'success')
        else:
            flash(f'Erro ao gerar calendário: {resultado.get("error", "Erro desconhecido")}', 'error')
    except Exception as e:
        flash(f'Erro ao gerar calendário: {str(e)}', 'error')
    
    return redirect(url_for('turmas.detalhe', id=id))


@turmas_bp.route('/gerar-calendario-todas', methods=['POST'])
@login_required
def gerar_calendario_todas():
    """Gera calendário automático para todas as turmas ativas."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerar calendário', 'error')
        return redirect(url_for('turmas.index'))
    
    periodo = request.form.get('periodo', 'semestral')
    
    try:
        from app.services.gerador_calendario import gerar_calendario_avancado
        
        resultado = gerar_calendario_avancado(periodo=periodo)
        
        if resultado['success']:
            flash(f'Calendário gerado! Total: {resultado["total_aulas"]} aulas.', 'success')
        else:
            flash(f'Erro ao gerar calendário: {resultado.get("error", "Erro desconhecido")}', 'error')
    except Exception as e:
        flash(f'Erro ao gerar calendário: {str(e)}', 'error')
    
    return redirect(url_for('turmas.index'))
