# app/controllers/professores_controller.py - Controller de Professores

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models.professor import Professor
from app.models.usuario import Usuario

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')


# ==================== Formulários ====================

class ProfessorForm(FlaskForm):
    """Formulário de professor."""
    registro = StringField('Registro', validators=[
        DataRequired(message='Registro é obrigatório'),
        Length(max=20)
    ])
    especialidade = StringField('Especialidade', validators=[Optional(), Length(max=100)])
    formacao = TextAreaField('Formação', validators=[Optional()])
    cpf = StringField('CPF', validators=[Optional(), Length(max=14)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    endereco = TextAreaField('Endereço', validators=[Optional()])
    ativo = SelectField('Status', choices=[
        ('1', 'Ativo'),
        ('0', 'Inativo')
    ])


# ==================== Rotas ====================

@professores_bp.route('/')
@login_required
def index():
    """Lista de professores."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    query = Professor.query
    
    if busca:
        query = query.join(Professor.usuario).filter(
            Usuario.nome.ilike(f'%{busca}%') |
            Professor.registro.ilike(f'%{busca}%')
        )
    
    professores = query.order_by(Professor.registro).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('professores/index.html', professores=professores, busca=busca)


@professores_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar professores', 'error')
        return redirect(url_for('professores.index'))
    
    form = ProfessorForm()
    
    if form.validate_on_submit():
        if Professor.query.filter_by(registro=form.registro.data).first():
            flash('Registro já cadastrado', 'error')
            return render_template('professores/form.html', form=form, titulo='Novo Professor')
        
        professor = Professor(
            usuario_id=current_user.id,
            registro=form.registro.data,
            especialidade=form.especialidade.data,
            formacao=form.formacao.data,
            cpf=form.cpf.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data,
            ativo=form.ativo.data == '1'
        )
        
        db.session.add(professor)
        db.session.commit()
        
        flash('Professor cadastrado com sucesso', 'success')
        return redirect(url_for('professores.index'))
    
    return render_template('professores/form.html', form=form, titulo='Novo Professor')


@professores_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do professor."""
    professor = Professor.query.get_or_404(id)
    return render_template('professores/detalhe.html', professor=professor)


@professores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor = Professor.query.get_or_404(id)
    form = ProfessorForm(obj=professor)
    
    if form.validate_on_submit():
        professor.especialidade = form.especialidade.data
        professor.formacao = form.formacao.data
        professor.cpf = form.cpf.data
        professor.telefone = form.telefone.data
        professor.endereco = form.endereco.data
        professor.ativo = form.ativo.data == '1'
        
        db.session.commit()
        
        flash('Professor atualizado com sucesso', 'success')
        return redirect(url_for('professores.detalhe', id=professor.id))
    
    return render_template('professores/form.html', form=form, titulo='Editar Professor', professor=professor)


@professores_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir professor."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor = Professor.query.get_or_404(id)
    professor.ativo = False
    
    db.session.commit()
    
    flash('Professor desativado com sucesso', 'success')
    return redirect(url_for('professores.index'))


@professores_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar professores."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    professores = Professor.query.join(Professor.usuario).filter(
        Professor.ativo == True,
        Usuario.nome.ilike(f'%{termo}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'nome': p.usuario.nome,
        'registro': p.registro
    } for p in professores])
