# app/controllers/alunos_controller.py - Controller de Alunos (Supabase)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import datetime

from app.repositories import AlunoRepository

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

# Instância do repositório
aluno_repo = AlunoRepository()


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


# ==================== Funções Auxiliares ====================

def _dict_to_aluno_obj(data):
    """Converte dicionário do Supabase em objeto compatível com templates."""
    if not data:
        return None
    
    class AlunoObj:
        def __init__(self, d):
            self.id = d.get('id')
            self.nome = d.get('nome', '')
            self.matricula = d.get('matricula', '')
            self.data_nascimento = d.get('data_nascimento')
            if isinstance(self.data_nascimento, str):
                try:
                    self.data_nascimento = datetime.strptime(self.data_nascimento, '%Y-%m-%d').date()
                except:
                    self.data_nascimento = None
            self.cpf = d.get('cpf', '')
            self.email = d.get('email', '')
            self.telefone = d.get('telefone', '')
            self.endereco = d.get('endereco', '')
            self.nome_responsavel = d.get('nome_responsavel', '')
            self.telefone_responsavel = d.get('telefone_responsavel', '')
            self.email_responsavel = d.get('email_responsavel', '')
            self.ano_letivo = d.get('ano_letivo', '')
            self.status = d.get('status', 'ativo')
            self.criado_em = d.get('criado_em')
            self.atualizado_em = d.get('atualizado_em')
    
    return AlunoObj(data)


# ==================== Rotas ====================

@alunos_bp.route('/')
@login_required
def index():
    """Lista de alunos."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    status = request.args.get('status', 'ativo')
    
    # Buscar alunos do Supabase
    if busca:
        alunos_raw = aluno_repo.search(busca)
        if status:
            alunos_raw = [a for a in alunos_raw if a.get('status') == status]
    elif status:
        alunos_raw = aluno_repo.get_by_field('status', status)
    else:
        alunos_raw = aluno_repo.get_all(order_by='nome')
    
    # Paginação manual
    per_page = 20
    total = len(alunos_raw)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_page = alunos_raw[start:end]
    
    # Converter para objetos
    alunos_obj = [_dict_to_aluno_obj(a) for a in alunos_page]
    
    # Criar objeto de paginação compatível
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
    
    alunos_paginados = PaginateObj(alunos_obj, page, per_page, total)
    
    return render_template('alunos/index.html', alunos=alunos_paginados, busca=busca, status=status)


@alunos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo aluno."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    form = AlunoForm()
    
    if form.validate_on_submit():
        # Verificar se matrícula já existe
        if aluno_repo.get_by_matricula(form.matricula.data):
            flash('Matrícula já cadastrada', 'error')
            return render_template('alunos/form.html', form=form, titulo='Novo Aluno')
        
        data = {
            'nome': form.nome.data,
            'matricula': form.matricula.data,
            'data_nascimento': str(form.data_nascimento.data) if form.data_nascimento.data else None,
            'cpf': form.cpf.data,
            'email': form.email.data,
            'telefone': form.telefone.data,
            'endereco': form.endereco.data,
            'nome_responsavel': form.nome_responsavel.data,
            'telefone_responsavel': form.telefone_responsavel.data,
            'email_responsavel': form.email_responsavel.data,
            'ano_letivo': int(form.ano_letivo.data) if form.ano_letivo.data else None,
            'status': form.status.data
        }
        
        aluno_repo.create(data)
        
        flash('Aluno cadastrado com sucesso', 'success')
        return redirect(url_for('alunos.index'))
    
    return render_template('alunos/form.html', form=form, titulo='Novo Aluno')


@alunos_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do aluno."""
    aluno_data = aluno_repo.get_by_id(id)
    if not aluno_data:
        flash('Aluno não encontrado', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno = _dict_to_aluno_obj(aluno_data)
    return render_template('alunos/detalhe.html', aluno=aluno)


@alunos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar aluno."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno_data = aluno_repo.get_by_id(id)
    if not aluno_data:
        flash('Aluno não encontrado', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno = _dict_to_aluno_obj(aluno_data)
    form = AlunoForm(obj=aluno)
    
    if form.validate_on_submit():
        data = {
            'nome': form.nome.data,
            'data_nascimento': str(form.data_nascimento.data) if form.data_nascimento.data else None,
            'cpf': form.cpf.data,
            'email': form.email.data,
            'telefone': form.telefone.data,
            'endereco': form.endereco.data,
            'nome_responsavel': form.nome_responsavel.data,
            'telefone_responsavel': form.telefone_responsavel.data,
            'email_responsavel': form.email_responsavel.data,
            'ano_letivo': int(form.ano_letivo.data) if form.ano_letivo.data else None,
            'status': form.status.data
        }
        
        aluno_repo.update(id, data)
        
        flash('Aluno atualizado com sucesso', 'success')
        return redirect(url_for('alunos.detalhe', id=id))
    
    return render_template('alunos/form.html', form=form, titulo='Editar Aluno', aluno=aluno)


@alunos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir aluno."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno_repo.update(id, {'status': 'inativo'})
    
    flash('Aluno desativado com sucesso', 'success')
    return redirect(url_for('alunos.index'))


@alunos_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar alunos."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    alunos = aluno_repo.search(termo)
    alunos_ativos = [a for a in alunos if a.get('status') == 'ativo'][:10]
    
    return jsonify([{
        'id': a.get('id'),
        'nome': a.get('nome'),
        'matricula': a.get('matricula')
    } for a in alunos_ativos])
