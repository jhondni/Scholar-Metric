# app/controllers/aulas_controller.py - Controller de Aulas

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, timedelta

from app import db
from app.models.aula import Aula
from app.models.turma import Turma
from app.models.professor import Professor
from app.models.feriado import Feriado
from app.models.dia_nao_letivo import DiaNaoLetivo

aulas_bp = Blueprint('aulas', __name__, url_prefix='/aulas')


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

def verificar_dia_letivo(data):
    """Verifica se um dia é letivo (não é feriado nem dia não letivo)."""
    if Feriado.is_feriado(data):
        return False
    if DiaNaoLetivo.is_dia_nao_letivo(data):
        return False
    return True


def criar_aulas_recorrentes(aula_pai, datas):
    """Cria aulas filhas para datas recorrentes."""
    aulas_criadas = []
    
    for data in datas:
        # Pular feriados e dias não letivos
        if not verificar_dia_letivo(data):
            continue
        
        # Verificar se já existe aula neste horário para a turma
        conflito = Aula.query.filter(
            Aula.turma_id == aula_pai.turma_id,
            Aula.data == data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= aula_pai.horario_inicio,
                    Aula.horario_fim > aula_pai.horario_inicio
                ),
                db.and_(
                    Aula.horario_inicio < aula_pai.horario_fim,
                    Aula.horario_fim >= aula_pai.horario_fim
                )
            )
        ).first()
        
        if conflito:
            continue
        
        aula_filha = Aula(
            materia=aula_pai.materia,
            descricao=aula_pai.descricao,
            turma_id=aula_pai.turma_id,
            professor_id=aula_pai.professor_id,
            data=data,
            horario_inicio=aula_pai.horario_inicio,
            horario_fim=aula_pai.horario_fim,
            recorrente=False,
            aula_pai_id=aula_pai.id
        )
        
        db.session.add(aula_filha)
        aulas_criadas.append(aula_filha)
    
    return aulas_criadas


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
    
    query = Aula.query
    
    if busca:
        query = query.filter(Aula.materia.ilike(f'%{busca}%'))
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    
    if data_inicio:
        query = query.filter(Aula.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    
    if data_fim:
        query = query.filter(Aula.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    aulas = query.order_by(Aula.data.desc(), Aula.horario_inicio).paginate(
        page=page, per_page=20, error_out=False
    )
    
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    
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
    
    # Popular choices de turmas e professores
    form.turma_id.choices = [(t.id, f'{t.nome} ({t.codigo})') 
                             for t in Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()]
    form.professor_id.choices = [(p.id, p.usuario.nome) 
                                 for p in Professor.query.filter_by(ativo=True).join(Professor.usuario).order_by().all()]
    
    if form.validate_on_submit():
        # Verificar conflito de horário
        conflito = Aula.query.filter(
            Aula.turma_id == form.turma_id.data,
            Aula.data == form.data.data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= form.horario_inicio.data,
                    Aula.horario_fim > form.horario_inicio.data
                ),
                db.and_(
                    Aula.horario_inicio < form.horario_fim.data,
                    Aula.horario_fim >= form.horario_fim.data
                )
            )
        ).first()
        
        if conflito:
            flash('Já existe uma aula agendada neste horário para esta turma', 'error')
            return render_template('aulas/form.html', form=form, titulo='Nova Aula')
        
        # Verificar se é dia letivo
        if not verificar_dia_letivo(form.data.data):
            flash('Não é possível agendar aulas em feriados ou dias não letivos', 'error')
            return render_template('aulas/form.html', form=form, titulo='Nova Aula')
        
        # Criar aula principal
        aula = Aula(
            materia=form.materia.data,
            descricao=form.descricao.data,
            turma_id=form.turma_id.data,
            professor_id=form.professor_id.data,
            data=form.data.data,
            horario_inicio=form.horario_inicio.data,
            horario_fim=form.horario_fim.data,
            recorrente=form.recorrente.data,
            tipo_recorrencia=form.tipo_recorrencia.data if form.recorrente.data else None,
            data_fim_recorrencia=form.data_fim_recorrencia.data if form.recorrente.data else None,
            dia_semana=form.data.data.weekday() if form.recorrente.data else None
        )
        
        db.session.add(aula)
        db.session.flush()  # Para obter o ID
        
        # Se for recorrente, criar aulas filhas
        if form.recorrente.data and form.data_fim_recorrencia.data:
            datas = Aula.gerar_datas_recorrencia(
                form.data.data,
                form.tipo_recorrencia.data,
                form.data_fim_recorrencia.data
            )
            criar_aulas_recorrentes(aula, datas[1:])  # Pular a primeira data (já criada)
        
        db.session.commit()
        
        flash('Aula criada com sucesso', 'success')
        return redirect(url_for('aulas.index'))
    
    return render_template('aulas/form.html', form=form, titulo='Nova Aula')


@aulas_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes da aula."""
    aula = Aula.query.get_or_404(id)
    return render_template('aulas/detalhe.html', aula=aula)


@aulas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar aula."""
    aula = Aula.query.get_or_404(id)
    
    # Verificar permissão
    if current_user.tipo == 'professor' and aula.professor_id != current_user.professor.id:
        flash('Sem permissão para editar esta aula', 'error')
        return redirect(url_for('aulas.index'))
    
    form = AulaForm(obj=aula)
    form.turma_id.choices = [(t.id, f'{t.nome} ({t.codigo})') 
                             for t in Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()]
    form.professor_id.choices = [(p.id, p.usuario.nome) 
                                 for p in Professor.query.filter_by(ativo=True).join(Professor.usuario).all()]
    
    if form.validate_on_submit():
        aula.materia = form.materia.data
        aula.descricao = form.descricao.data
        aula.turma_id = form.turma_id.data
        aula.professor_id = form.professor_id.data
        aula.data = form.data.data
        aula.horario_inicio = form.horario_inicio.data
        aula.horario_fim = form.horario_fim.data
        
        db.session.commit()
        
        flash('Aula atualizada com sucesso', 'success')
        return redirect(url_for('aulas.detalhe', id=aula.id))
    
    return render_template('aulas/form.html', form=form, titulo='Editar Aula', aula=aula)


@aulas_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar aula."""
    aula = Aula.query.get_or_404(id)
    
    if current_user.tipo == 'professor' and aula.professor_id != current_user.professor.id:
        flash('Sem permissão para cancelar esta aula', 'error')
        return redirect(url_for('aulas.index'))
    
    aula.status = 'cancelada'
    db.session.commit()
    
    flash('Aula cancelada com sucesso', 'success')
    return redirect(url_for('aulas.index'))


@aulas_bp.route('/<int:id>/realizar', methods=['POST'])
@login_required
def realizar(id):
    """Marcar aula como realizada."""
    aula = Aula.query.get_or_404(id)
    
    if current_user.tipo == 'professor' and aula.professor_id != current_user.professor.id:
        flash('Sem permissão', 'error')
        return redirect(url_for('aulas.index'))
    
    aula.status = 'realizada'
    db.session.commit()
    
    flash('Aula marcada como realizada', 'success')
    return redirect(url_for('aulas.detalhe', id=aula.id))


@aulas_bp.route('/<int:id>/frequencia', methods=['GET', 'POST'])
@login_required
def frequencia(id):
    """Gerenciar frequência da aula."""
    aula = Aula.query.get_or_404(id)
    
    if request.method == 'POST':
        from app.models.frequencia import Frequencia
        
        for aluno in aula.turma.alunos:
            presente = request.form.get(f'aluno_{aluno.id}') == 'on'
            justificativa = request.form.get(f'justificativa_{aluno.id}', '')
            
            freq = Frequencia.query.filter_by(aluno_id=aluno.id, aula_id=aula.id).first()
            
            if freq:
                freq.presente = presente
                freq.justificativa = justificativa
            else:
                freq = Frequencia(
                    aluno_id=aluno.id,
                    aula_id=aula.id,
                    presente=presente,
                    justificativa=justificativa
                )
                db.session.add(freq)
        
        db.session.commit()
        flash('Frequência registrada com sucesso', 'success')
        return redirect(url_for('aulas.detalhe', id=aula.id))
    
    return render_template('aulas/frequencia.html', aula=aula)
