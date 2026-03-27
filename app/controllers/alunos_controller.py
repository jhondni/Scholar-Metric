# app/controllers/alunos_controller.py - Controller de Alunos

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from app import db
from app.models.aluno import Aluno

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')


# ==================== Formulários ====================

class AlunoForm(FlaskForm):
    """Formulário de aluno."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=100)
    ])
    matricula = StringField('Matrícula', validators=[
        DataRequired(message='Matrícula é obrigatória'),
        Length(max=20)
    ])
    data_nascimento = DateField('Data de Nascimento', validators=[Optional()])
    cpf = StringField('CPF', validators=[Optional(), Length(max=14)])
    email = StringField('E-mail', validators=[Optional(), Email()])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    endereco = TextAreaField('Endereço', validators=[Optional()])
    nome_responsavel = StringField('Nome do Responsável', validators=[Optional(), Length(max=100)])
    telefone_responsavel = StringField('Telefone do Responsável', validators=[Optional(), Length(max=20)])
    email_responsavel = StringField('E-mail do Responsável', validators=[Optional(), Email()])
    ano_letivo = StringField('Ano Letivo', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('transferido', 'Transferido'),
        ('evadido', 'Evadido')
    ])


# ==================== Rotas ====================

@alunos_bp.route('/')
@login_required
def index():
    """Lista de alunos."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    status = request.args.get('status', 'ativo')
    
    query = Aluno.query
    
    if busca:
        query = query.filter(
            Aluno.nome.ilike(f'%{busca}%') |
            Aluno.matricula.ilike(f'%{busca}%')
        )
    
    if status:
        query = query.filter_by(status=status)
    
    alunos = query.order_by(Aluno.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('alunos/index.html', alunos=alunos, busca=busca, status=status)


@alunos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo aluno."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    form = AlunoForm()
    
    if form.validate_on_submit():
        if Aluno.query.filter_by(matricula=form.matricula.data).first():
            flash('Matrícula já cadastrada', 'error')
            return render_template('alunos/form.html', form=form, titulo='Novo Aluno')
        
        aluno = Aluno(
            nome=form.nome.data,
            matricula=form.matricula.data,
            data_nascimento=form.data_nascimento.data,
            cpf=form.cpf.data,
            email=form.email.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data,
            nome_responsavel=form.nome_responsavel.data,
            telefone_responsavel=form.telefone_responsavel.data,
            email_responsavel=form.email_responsavel.data,
            ano_letivo=form.ano_letivo.data,
            status=form.status.data
        )
        
        db.session.add(aluno)
        db.session.commit()
        
        flash('Aluno cadastrado com sucesso', 'success')
        return redirect(url_for('alunos.index'))
    
    return render_template('alunos/form.html', form=form, titulo='Novo Aluno')


@alunos_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do aluno."""
    aluno = Aluno.query.get_or_404(id)
    return render_template('alunos/detalhe.html', aluno=aluno)


@alunos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar aluno."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno = Aluno.query.get_or_404(id)
    form = AlunoForm(obj=aluno)
    
    if form.validate_on_submit():
        aluno.nome = form.nome.data
        aluno.data_nascimento = form.data_nascimento.data
        aluno.cpf = form.cpf.data
        aluno.email = form.email.data
        aluno.telefone = form.telefone.data
        aluno.endereco = form.endereco.data
        aluno.nome_responsavel = form.nome_responsavel.data
        aluno.telefone_responsavel = form.telefone_responsavel.data
        aluno.email_responsavel = form.email_responsavel.data
        aluno.ano_letivo = form.ano_letivo.data
        aluno.status = form.status.data
        
        db.session.commit()
        
        flash('Aluno atualizado com sucesso', 'success')
        return redirect(url_for('alunos.detalhe', id=aluno.id))
    
    return render_template('alunos/form.html', form=form, titulo='Editar Aluno', aluno=aluno)


@alunos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir aluno."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno = Aluno.query.get_or_404(id)
    aluno.status = 'inativo'
    
    db.session.commit()
    
    flash('Aluno desativado com sucesso', 'success')
    return redirect(url_for('alunos.index'))


@alunos_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar alunos."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    alunos = Aluno.query.filter(
        Aluno.status == 'ativo',
        Aluno.nome.ilike(f'%{termo}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'matricula': a.matricula
    } for a in alunos])
