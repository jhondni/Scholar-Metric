# app/controllers/turmas_controller.py - Controller de Turmas

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

from app import db
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.professor import Professor

turmas_bp = Blueprint('turmas', __name__, url_prefix='/turmas')


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


# ==================== Rotas ====================

@turmas_bp.route('/')
@login_required
def index():
    """Lista de turmas."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    query = Turma.query
    
    if busca:
        query = query.filter(
            Turma.nome.ilike(f'%{busca}%') |
            Turma.codigo.ilike(f'%{busca}%')
        )
    
    turmas = query.order_by(Turma.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
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
        if Turma.query.filter_by(codigo=form.codigo.data).first():
            flash('Código de turma já existe', 'error')
            return render_template('turmas/form.html', form=form, titulo='Nova Turma')
        
        turma = Turma(
            nome=form.nome.data,
            codigo=form.codigo.data,
            serie=form.serie.data,
            ano_letivo=form.ano_letivo.data,
            turno=form.turno.data,
            capacidade_maxima=form.capacidade_maxima.data,
            descricao=form.descricao.data
        )
        
        db.session.add(turma)
        db.session.commit()
        
        flash('Turma criada com sucesso', 'success')
        return redirect(url_for('turmas.index'))
    
    return render_template('turmas/form.html', form=form, titulo='Nova Turma')


@turmas_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da turma."""
    turma = Turma.query.get_or_404(id)
    return render_template('turmas/detalhe.html', turma=turma)


@turmas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = Turma.query.get_or_404(id)
    form = TurmaForm(obj=turma)
    
    if form.validate_on_submit():
        turma.nome = form.nome.data
        turma.serie = form.serie.data
        turma.ano_letivo = form.ano_letivo.data
        turma.turno = form.turno.data
        turma.capacidade_maxima = form.capacidade_maxima.data
        turma.descricao = form.descricao.data
        
        db.session.commit()
        
        flash('Turma atualizada com sucesso', 'success')
        return redirect(url_for('turmas.detalhe', id=turma.id))
    
    return render_template('turmas/form.html', form=form, titulo='Editar Turma', turma=turma)


@turmas_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir turma."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = Turma.query.get_or_404(id)
    turma.ativa = False
    
    db.session.commit()
    
    flash('Turma desativada com sucesso', 'success')
    return redirect(url_for('turmas.index'))


@turmas_bp.route('/<int:id>/alunos', methods=['POST'])
@login_required
def adicionar_aluno(id):
    """Adicionar aluno à turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.get_or_404(id)
    aluno_id = request.json.get('aluno_id')
    
    aluno = Aluno.query.get_or_404(aluno_id)
    
    if aluno in turma.alunos:
        return jsonify({'error': 'Aluno já está na turma'}), 400
    
    if turma.total_alunos() >= turma.capacidade_maxima:
        return jsonify({'error': 'Turma atingiu capacidade máxima'}), 400
    
    turma.alunos.append(aluno)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Aluno adicionado'})


@turmas_bp.route('/<int:id>/alunos/<int:aluno_id>', methods=['DELETE'])
@login_required
def remover_aluno(id, aluno_id):
    """Remover aluno da turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.get_or_404(id)
    aluno = Aluno.query.get_or_404(aluno_id)
    
    if aluno not in turma.alunos:
        return jsonify({'error': 'Aluno não está na turma'}), 400
    
    turma.alunos.remove(aluno)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Aluno removido'})
