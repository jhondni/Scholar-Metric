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
from app.models.materia import Materia, turma_materias

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


# ==================== Matérias da Turma ====================

@turmas_bp.route('/<int:id>/materias', methods=['GET', 'POST'])
@login_required
def materias(id):
    """Gerenciar matérias da turma com quantidade de aulas por período."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerenciar matérias de turmas', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = Turma.query.get_or_404(id)
    
    if request.method == 'POST':
        materia_ids = request.form.getlist('materias')
        aulas_por_periodo = {}
        
        for mid in materia_ids:
            aulas = request.form.get(f'aulas_{mid}', 2, type=int)
            aulas_por_periodo[int(mid)] = aulas
        
        # Remover todas as matérias atuais
        db.session.execute(
            turma_materias.delete().where(turma_materias.c.turma_id == turma.id)
        )
        
        # Adicionar novas matérias com aulas_por_periodo
        for mid in materia_ids:
            mid_int = int(mid)
            aulas = aulas_por_periodo.get(mid_int, 2)
            db.session.execute(
                turma_materias.insert().values(
                    turma_id=turma.id,
                    materia_id=mid_int,
                    aulas_por_periodo=aulas
                )
            )
        
        db.session.commit()
        flash('Matérias da turma atualizadas com sucesso', 'success')
        return redirect(url_for('turmas.detalhe', id=turma.id))
    
    materias = Materia.query.filter_by(ativa=True).order_by(Materia.nome).all()
    return render_template('turmas/materias.html', turma=turma, materias=materias)


@turmas_bp.route('/<int:id>/materias/adicionar', methods=['POST'])
@login_required
def adicionar_materia(id):
    """Adiciona uma matéria à turma via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.get_or_404(id)
    materia_id = request.json.get('materia_id')
    aulas_por_periodo = request.json.get('aulas_por_periodo', 2)
    
    materia = Materia.query.get_or_404(materia_id)
    
    # Verificar se já existe
    existing = db.session.query(turma_materias).filter_by(
        turma_id=turma.id, materia_id=materia.id
    ).first()
    
    if existing:
        return jsonify({'error': 'Matéria já está na turma'}), 400
    
    db.session.execute(
        turma_materias.insert().values(
            turma_id=turma.id,
            materia_id=materia.id,
            aulas_por_periodo=aulas_por_periodo
        )
    )
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Matéria adicionada'})


@turmas_bp.route('/<int:id>/materias/<int:materia_id>', methods=['DELETE'])
@login_required
def remover_materia(id, materia_id):
    """Remove uma matéria da turma via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.get_or_404(id)
    
    db.session.execute(
        turma_materias.delete().where(
            db.and_(
                turma_materias.c.turma_id == turma.id,
                turma_materias.c.materia_id == materia_id
            )
        )
    )
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Matéria removida'})


# ==================== Geração de Calendário ====================

@turmas_bp.route('/<int:id>/gerar-calendario', methods=['POST'])
@login_required
def gerar_calendario(id):
    """Gera calendário automático para a turma."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerar calendário', 'error')
        return redirect(url_for('turmas.index'))
    
    turma = Turma.query.get_or_404(id)
    
    if not turma.materias:
        flash('A turma não possui matérias cadastradas. Adicione matérias antes de gerar o calendário.', 'error')
        return redirect(url_for('turmas.detalhe', id=turma.id))
    
    # Verificar se há professores disponíveis para as matérias
    materias_sem_professor = []
    for materia in turma.materias:
        if not materia.professores.filter_by(ativo=True).first():
            materias_sem_professor.append(materia.nome)
    
    if materias_sem_professor:
        flash(f'Não há professores disponíveis para: {", ".join(materias_sem_professor)}. Associe professores às matérias antes de gerar o calendário.', 'error')
        return redirect(url_for('turmas.detalhe', id=turma.id))
    
    periodo = request.form.get('periodo', 'semestral')
    
    from app.services.gerador_calendario import gerar_calendario_avancado
    
    resultado = gerar_calendario_avancado(
        turma_id=turma.id,
        periodo=periodo
    )
    
    if resultado['success']:
        flash(f'Calendário gerado com sucesso! {resultado["total_aulas"]} aulas criadas.', 'success')
    else:
        flash(f'Erro ao gerar calendário: {resultado.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('turmas.detalhe', id=turma.id))


@turmas_bp.route('/gerar-calendario-todas', methods=['POST'])
@login_required
def gerar_calendario_todas():
    """Gera calendário automático para todas as turmas ativas."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerar calendário', 'error')
        return redirect(url_for('turmas.index'))
    
    periodo = request.form.get('periodo', 'semestral')
    
    from app.services.gerador_calendario import gerar_calendario_avancado
    
    resultado = gerar_calendario_avancado(periodo=periodo)
    
    if resultado['success']:
        detalhes = '<br>'.join(resultado['detalhes'])
        flash(f'Calendário gerado! Total: {resultado["total_aulas"]} aulas.<br>{detalhes}', 'success')
    else:
        flash(f'Erro ao gerar calendário: {resultado.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('turmas.index'))
