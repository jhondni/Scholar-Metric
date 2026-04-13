# app/controllers/atividades_controller.py - Controller de Atividades

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, date

from app.repositories import AtividadeRepository, NotaRepository, MateriaRepository, TurmaRepository, ProfessorRepository

atividades_bp = Blueprint('atividades', __name__, url_prefix='/atividades')

# Instâncias dos repositórios
atividade_repo = AtividadeRepository()
nota_repo = NotaRepository()
materia_repo = MateriaRepository()
turma_repo = TurmaRepository()
professor_repo = ProfessorRepository()


# ==================== Formulários ====================

class AtividadeForm(FlaskForm):
    """Formulário de atividade."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=100)
    ])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    data = DateField('Data', validators=[DataRequired(message='Data é obrigatória')])
    materia_id = SelectField('Matéria', coerce=int, validators=[DataRequired(message='Matéria é obrigatória')])
    turma_id = SelectField('Turma', coerce=int, validators=[DataRequired(message='Turma é obrigatória')])
    tipo = SelectField('Tipo', choices=[
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('exercicio', 'Exercício'),
        ('participacao', 'Participação'),
        ('projeto', 'Projeto'),
        ('avaliacao', 'Avaliação')
    ], validators=[DataRequired()])
    peso = FloatField('Peso', validators=[Optional()], default=1.0)
    valor_maximo = FloatField('Valor Máximo', validators=[Optional()], default=10.0)


class NotaForm(FlaskForm):
    """Formulário de nota."""
    valor = FloatField('Nota', validators=[
        DataRequired(message='Nota é obrigatória')
    ])
    descricao = StringField('Descrição', validators=[Optional(), Length(max=200)])


# ==================== Funções Auxiliares ====================

def _get_professor_id():
    """Retorna o ID do professor logado ou None."""
    if hasattr(current_user, 'professor') and current_user.professor:
        return current_user.professor.id
    return None


def _pode_criar_atividade(materia_id, turma_id):
    """Verifica se o usuário pode criar atividade."""
    if current_user.tem_permissao(['diretora', 'coordenacao']):
        return True
    
    professor_id = _get_professor_id()
    if not professor_id:
        return False
    
    # Verificar se professor leciona essa matéria na turma
    turmas_prof = professor_repo.get_by_materia(materia_id)
    return any(t.get('id') == turma_id for t in turmas_prof)


# ==================== Rotas ====================

@atividades_bp.route('/turma/<int:turma_id>')
@login_required
def listar(turma_id):
    """Lista atividades de uma turma."""
    atividades = atividade_repo.get_by_turma(turma_id)
    turma = turma_repo.get_by_id(turma_id)
    
    return render_template('atividades/index.html', 
                         atividades=atividades, 
                         turma=turma)


@atividades_bp.route('/turma/<int:turma_id>/materia/<int:materia_id>')
@login_required
def listar_por_materia(turma_id, materia_id):
    """Lista atividades de uma turma e matéria."""
    atividades = atividade_repo.get_by_turma_materia(turma_id, materia_id)
    turma = turma_repo.get_by_id(turma_id)
    materia = materia_repo.get_by_id(materia_id)
    
    return render_template('atividades/index.html',
                         atividades=atividades,
                         turma=turma,
                         materia=materia)


@atividades_bp.route('/turma/<int:turma_id>/novo', methods=['GET', 'POST'])
@login_required
def novo(turma_id):
    """Criar nova atividade."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para criar atividades', 'error')
        return redirect(url_for('turmas.detalhe', id=turma_id))
    
    form = AtividadeForm()
    
    # Popular selects - usando filters para turmas ativas
    turmas = turma_repo.get_all(filters={'ativa': True})
    form.turma_id.choices = [(0, 'Selecione')] + [(t['id'], t['nome']) for t in turmas]
    
    # Se tem professor logado, filtrar matérias
    professor_id = _get_professor_id()
    if professor_id:
        materias = professor_repo.get_materias(professor_id)
        form.materia_id.choices = [(0, 'Selecione')] + [(m['id'], m['nome']) for m in materias]
    else:
        materias = materia_repo.get_active_materias()
        form.materia_id.choices = [(0, 'Selecione')] + [(m['id'], m['nome']) for m in materias]
    
    if form.validate_on_submit():
        professor_id = _get_professor_id()
        if not professor_id:
            # Se for coordenação/diretora, buscar primeiro professor ativo
            professors = professor_repo.get_active_professors()
            if professors:
                professor_id = professors[0]['id']
        
        if not professor_id:
            flash('Nenhum professor encontrado', 'error')
            return render_template('atividades/form.html', form=form, titulo='Nova Atividade', turma_id=turma_id)
        
        data = {
            'nome': form.nome.data,
            'descricao': form.descricao.data,
            'data': form.data.data,
            'materia_id': form.materia_id.data,
            'turma_id': form.turma_id.data,
            'professor_id': professor_id,
            'tipo': form.tipo.data,
            'peso': form.peso.data or 1.0,
            'valor_maximo': form.valor_maximo.data or 10.0,
            'ativo': True
        }
        
        atividade = atividade_repo.create(data)
        if atividade:
            flash('Atividade criada com sucesso', 'success')
            return redirect(url_for('turmas.detalhe', id=turma_id))
        
        flash('Erro ao criar atividade', 'error')
    
    # Pre-selecionar turma se informada
    if not form.turma_id.data and turma_id:
        form.turma_id.data = turma_id
    
    return render_template('atividades/form.html', form=form, titulo='Nova Atividade', turma_id=turma_id)


@atividades_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar atividade."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar atividades', 'error')
        return redirect(url_for('dashboard.index'))
    
    atividade = atividade_repo.get_by_id(id)
    if not atividade:
        flash('Atividade não encontrada', 'error')
        return redirect(url_for('dashboard.index'))
    
    form = AtividadeForm(data=atividade)
    
    turmas = turma_repo.get_all(filters={'ativa': True})
    form.turma_id.choices = [(t['id'], t['nome']) for t in turmas]
    
    materias = materia_repo.get_active_materias()
    form.materia_id.choices = [(m['id'], m['nome']) for m in materias]
    
    if form.validate_on_submit():
        data = {
            'nome': form.nome.data,
            'descricao': form.descricao.data,
            'data': form.data.data,
            'materia_id': form.materia_id.data,
            'turma_id': form.turma_id.data,
            'tipo': form.tipo.data,
            'peso': form.peso.data,
            'valor_maximo': form.valor_maximo.data
        }
        
        resultado = atividade_repo.update(id, data)
        if resultado:
            flash('Atividade atualizada com sucesso', 'success')
            return redirect(url_for('atividades.listar', turma_id=atividade['turma_id']))
        
        flash('Erro ao atualizar atividade', 'error')
    
    return render_template('atividades/form.html', form=form, titulo='Editar Atividade', atividade=atividade)


@atividades_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir (desativar) atividade."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    atividade = atividade_repo.get_by_id(id)
    if not atividade:
        return jsonify({'success': False, 'message': 'Atividade não encontrada'}), 404
    
    if atividade_repo.delete(id):
        return jsonify({'success': True, 'message': 'Atividade excluída'})
    
    return jsonify({'success': False, 'message': 'Erro ao excluir'}), 500


# ==================== Rotas de Notas ====================

@atividades_bp.route('/<int:atividade_id>/notas')
@login_required
def ver_notas(atividade_id):
    """Ver notas de uma atividade."""
    atividade = atividade_repo.get_by_id(atividade_id)
    if not atividade:
        flash('Atividade não encontrada', 'error')
        return redirect(url_for('dashboard.index'))
    
    notas = nota_repo.get_by_atividade(atividade_id)
    turma = turma_repo.get_by_id(atividade['turma_id'])
    materia = materia_repo.get_by_id(atividade['materia_id'])
    
    return render_template('atividades/notas.html',
                         atividade=atividade,
                         notas=notas,
                         turma=turma,
                         materia=materia)


@atividades_bp.route('/<int:atividade_id>/lancar-notas', methods=['GET', 'POST'])
@login_required
def lancar_notas(atividade_id):
    """Lançar notas para uma atividade."""
    atividade = atividade_repo.get_by_id(atividade_id)
    if not atividade:
        flash('Atividade não encontrada', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Verificar permissão
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        professor_id = _get_professor_id()
        if professor_id and atividade['professor_id'] != professor_id:
            flash('Você não pode lançar notas desta atividade', 'error')
            return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        data = request.json
        aluno_id = data.get('aluno_id')
        valor = data.get('valor')
        
        if not aluno_id or valor is None:
            return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
        
        # Verificar se já existe nota
        nota_existente = nota_repo.get_by_aluno_atividade(aluno_id, atividade_id)
        
        if nota_existente:
            # Atualizar
            resultado = nota_repo.update(nota_existente['id'], {
                'valor': valor,
                'descricao': data.get('descricao', '')
            })
        else:
            # Criar
            resultado = nota_repo.create({
                'aluno_id': aluno_id,
                'turma_id': atividade['turma_id'],
                'atividade_id': atividade_id,
                'materia_id': atividade['materia_id'],
                'ano_letivo': date.today().year,
                'tipo_avaliacao': atividade['tipo'],
                'valor': valor,
                'valor_maximo': atividade['valor_maximo'],
                'peso': atividade['peso']
            })
        
        if resultado:
            return jsonify({'success': True, 'message': 'Nota salva'})
        
        return jsonify({'success': False, 'message': 'Erro ao salvar nota'}), 500
    
    # GET - mostrar formulário
    turma = turma_repo.get_by_id(atividade['turma_id'])
    alunos = turma_repo.get_alunos(atividade['turma_id'])
    notas_existentes = nota_repo.get_by_atividade(atividade_id)
    
    # Mapear notas por aluno
    notas_map = {n['aluno_id']: n for n in notas_existentes}
    
    return render_template('atividades/lancar_notas.html',
                         atividade=atividade,
                         turma=turma,
                         alunos=alunos,
                         notas=notas_map)


@atividades_bp.route('/api/turma/<int:turma_id>/atividades')
@login_required
def api_atividades_turma(turma_id):
    """API para buscar atividades de uma turma."""
    materia_id = request.args.get('materia_id', type=int)
    
    if materia_id:
        atividades = atividade_repo.get_by_turma_materia(turma_id, materia_id)
    else:
        atividades = atividade_repo.get_by_turma(turma_id)
    
    return jsonify(atividades)