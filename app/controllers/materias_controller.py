# app/controllers/materias_controller.py - Controller de Matérias (Supabase)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.repositories import MateriaRepository

materias_bp = Blueprint('materias', __name__, url_prefix='/materias')

# Instância do repositório
materia_repo = MateriaRepository()


# ==================== Formulários ====================

class MateriaForm(FlaskForm):
    """Formulário de matéria."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=100)
    ])
    codigo = StringField('Código', validators=[
        DataRequired(message='Código é obrigatório'),
        Length(max=20)
    ])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    carga_horaria = IntegerField('Carga Horária', validators=[Optional()])


# ==================== Funções Auxiliares ====================

def _dict_to_materia_obj(data):
    """Converte dicionário do Supabase em objeto compatível com templates."""
    if not data:
        return None
    
    class MateriaObj:
        def __init__(self, d):
            self.id = d.get('id')
            self.nome = d.get('nome', '')
            self.codigo = d.get('codigo', '')
            self.descricao = d.get('descricao', '')
            self.carga_horaria = d.get('carga_horaria')
            self.ativa = d.get('ativa', True)
    
    return MateriaObj(data)


# ==================== Rotas ====================

@materias_bp.route('/')
@login_required
def index():
    """Lista de matérias."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    materias_raw = materia_repo.get_all(order_by='nome')
    
    if busca:
        materias_raw = [m for m in materias_raw if busca.lower() in m.get('nome', '').lower() or busca.lower() in m.get('codigo', '').lower()]
    
    # Paginação manual
    per_page = 20
    total = len(materias_raw)
    start = (page - 1) * per_page
    end = start + per_page
    materias_page = materias_raw[start:end]
    
    materias_obj = [_dict_to_materia_obj(m) for m in materias_page]
    
    class PaginateObj:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
        
        def iter_pages(self):
            for i in range(1, self.pages + 1):
                yield i
    
    materias_paginadas = PaginateObj(materias_obj, page, per_page, total)
    
    return render_template('materias/index.html', materias=materias_paginadas, busca=busca)


@materias_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar nova matéria."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar matérias', 'error')
        return redirect(url_for('materias.index'))
    
    form = MateriaForm()
    
    if form.validate_on_submit():
        if materia_repo.get_by_codigo(form.codigo.data):
            flash('Código já cadastrado', 'error')
            return render_template('materias/form.html', form=form, titulo='Nova Matéria')
        
        if materia_repo.get_one_by_field('nome', form.nome.data):
            flash('Nome já cadastrado', 'error')
            return render_template('materias/form.html', form=form, titulo='Nova Matéria')
        
        data = {
            'nome': form.nome.data,
            'codigo': form.codigo.data,
            'descricao': form.descricao.data,
            'carga_horaria': form.carga_horaria.data,
            'ativa': True
        }
        
        materia_repo.create(data)
        
        flash('Matéria cadastrada com sucesso', 'success')
        return redirect(url_for('materias.index'))
    
    return render_template('materias/form.html', form=form, titulo='Nova Matéria')


@materias_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da matéria."""
    from app.models.materia import Materia
    materia = Materia.query.get(id)
    if not materia:
        flash('Matéria não encontrada', 'error')
        return redirect(url_for('materias.index'))
    
    return render_template('materias/detalhe.html', materia=materia)


@materias_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar matéria."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar matérias', 'error')
        return redirect(url_for('materias.index'))
    
    materia_data = materia_repo.get_by_id(id)
    if not materia_data:
        flash('Matéria não encontrada', 'error')
        return redirect(url_for('materias.index'))
    
    materia = _dict_to_materia_obj(materia_data)
    form = MateriaForm(obj=materia)
    
    if form.validate_on_submit():
        data = {
            'nome': form.nome.data,
            'codigo': form.codigo.data,
            'descricao': form.descricao.data,
            'carga_horaria': form.carga_horaria.data
        }
        
        materia_repo.update(id, data)
        
        flash('Matéria atualizada com sucesso', 'success')
        return redirect(url_for('materias.detalhe', id=id))
    
    return render_template('materias/form.html', form=form, titulo='Editar Matéria', materia=materia)


@materias_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir matéria."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir matérias', 'error')
        return redirect(url_for('materias.index'))
    
    materia_repo.update(id, {'ativa': False})
    
    flash('Matéria desativada com sucesso', 'success')
    return redirect(url_for('materias.index'))
