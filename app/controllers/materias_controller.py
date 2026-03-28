# app/controllers/materias_controller.py - Controller de Matérias

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models.materia import Materia

materias_bp = Blueprint('materias', __name__, url_prefix='/materias')


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


# ==================== Rotas ====================

@materias_bp.route('/')
@login_required
def index():
    """Lista de matérias."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    query = Materia.query
    
    if busca:
        query = query.filter(
            Materia.nome.ilike(f'%{busca}%') |
            Materia.codigo.ilike(f'%{busca}%')
        )
    
    materias = query.order_by(Materia.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('materias/index.html', materias=materias, busca=busca)


@materias_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar nova matéria."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar matérias', 'error')
        return redirect(url_for('materias.index'))
    
    form = MateriaForm()
    
    if form.validate_on_submit():
        if Materia.query.filter_by(codigo=form.codigo.data).first():
            flash('Código já cadastrado', 'error')
            return render_template('materias/form.html', form=form, titulo='Nova Matéria')
        
        if Materia.query.filter_by(nome=form.nome.data).first():
            flash('Nome já cadastrado', 'error')
            return render_template('materias/form.html', form=form, titulo='Nova Matéria')
        
        materia = Materia(
            nome=form.nome.data,
            codigo=form.codigo.data,
            descricao=form.descricao.data,
            carga_horaria=form.carga_horaria.data
        )
        
        db.session.add(materia)
        db.session.commit()
        
        flash('Matéria cadastrada com sucesso', 'success')
        return redirect(url_for('materias.index'))
    
    return render_template('materias/form.html', form=form, titulo='Nova Matéria')


@materias_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da matéria."""
    materia = Materia.query.get_or_404(id)
    return render_template('materias/detalhe.html', materia=materia)


@materias_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar matéria."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar matérias', 'error')
        return redirect(url_for('materias.index'))
    
    materia = Materia.query.get_or_404(id)
    form = MateriaForm(obj=materia)
    
    if form.validate_on_submit():
        materia.nome = form.nome.data
        materia.codigo = form.codigo.data
        materia.descricao = form.descricao.data
        materia.carga_horaria = form.carga_horaria.data
        
        db.session.commit()
        
        flash('Matéria atualizada com sucesso', 'success')
        return redirect(url_for('materias.detalhe', id=materia.id))
    
    return render_template('materias/form.html', form=form, titulo='Editar Matéria', materia=materia)


@materias_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir matéria."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir matérias', 'error')
        return redirect(url_for('materias.index'))
    
    materia = Materia.query.get_or_404(id)
    materia.ativa = False
    
    db.session.commit()
    
    flash('Matéria desativada com sucesso', 'success')
    return redirect(url_for('materias.index'))