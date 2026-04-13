# app/controllers/alunos_controller.py - Controller de Alunos (Supabase + DTOs)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import datetime

from app.repositories import AlunoRepository
from app.dtos.aluno_dto import AlunoDTO

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

# Instâncias dos repositórios (reutilizadas)
_aluno_repo = AlunoRepository()

# Dicionário de repositórios para DTOs
_repos = {
    'aluno': _aluno_repo
}


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

def _paginate(items: list, page: int, per_page: int = 20):
    """Cria objeto de paginação compatível com Flask-SQLAlchemy."""
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

@alunos_bp.route('/')
@login_required
def index():
    """Lista de alunos."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    status = request.args.get('status', 'ativo')
    
    # Buscar alunos do Supabase
    if busca:
        alunos_raw = _aluno_repo.search(busca)
        if status:
            alunos_raw = [a for a in alunos_raw if a.get('status') == status]
    elif status:
        alunos_raw = _aluno_repo.get_by_field('status', status)
    else:
        alunos_raw = _aluno_repo.get_all(order_by='nome')
    
    alunos_list = [AlunoDTO(a, _repos) for a in alunos_raw]
    alunos = _paginate(alunos_list, page)
    
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
        # Verificar se matrícula já existe
        if _aluno_repo.get_by_matricula(form.matricula.data):
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
        
        _aluno_repo.create(data)
        
        flash('Aluno cadastrado com sucesso', 'success')
        return redirect(url_for('alunos.index'))
    
    return render_template('alunos/form.html', form=form, titulo='Novo Aluno')


@alunos_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do aluno."""
    from datetime import date
    from app.repositories import NotaRepository, MateriaRepository
    
    aluno_data = _aluno_repo.get_by_id(id)
    if not aluno_data:
        flash('Aluno não encontrado', 'error')
        return redirect(url_for('alunos.index'))
    
    # Buscar notas por ano
    nota_repo = NotaRepository()
    materia_repo = MateriaRepository()
    
    notas = nota_repo.get_by_aluno(id)
    
    # DEBUG: print raw notes
    print(f"[DEBUG] Total notas: {len(notas)}")
    for n in notas[:3]:
        print(f"[DEBUG] Nota: aluno={n.get('aluno_id')}, ano={n.get('ano_letivo')}, materia_id={n.get('materia_id')}, valor={n.get('valor')}")
    
    # Organizar por ano e matéria
    notas_por_ano = {}
    atividade_repo = None
    
    for nota in notas:
        ano = nota.get('ano_letivo', date.today().year)
        materia_id = nota.get('materia_id')
        
        # Fallback: get materia_id from atividade if not set on nota
        if not materia_id and nota.get('atividade_id'):
            if not atividade_repo:
                from app.repositories import AtividadeRepository
                atividade_repo = AtividadeRepository()
            atividade = atividade_repo.get_by_id(nota['atividade_id'])
            if atividade:
                materia_id = atividade.get('materia_id')
        
        print(f"[DEBUG] Processing: ano={ano}, materia_id={materia_id}")
        
        if ano not in notas_por_ano:
            notas_por_ano[ano] = {}
        
        if materia_id:
            if materia_id not in notas_por_ano[ano]:
                materia = materia_repo.get_by_id(materia_id)
                materia_nome = materia.get('nome', 'Matéria') if materia else 'Matéria'
                print(f"[DEBUG] Created materia entry: {materia_nome}")
                notas_por_ano[ano][materia_id] = {
                    'materia_nome': materia_nome,
                    'atividades': [],
                    'soma_notas': 0,
                    'count': 0
                }
            
            # Buscar atividade se houver
            atividade_info = None
            if nota.get('atividade_id'):
                from app.repositories import AtividadeRepository
                at_repo = AtividadeRepository()
                atividade = at_repo.get_by_id(nota['atividade_id'])
                if atividade:
                    atividade_info = {
                        'nome': atividade.get('nome', ''),
                        'data': str(atividade.get('data', '')),
                        'tipo': atividade.get('tipo', ''),
                        'nota': nota.get('valor', 0)
                    }
            
            notas_por_ano[ano][materia_id]['atividades'].append(atividade_info or {
                'nome': nota.get('descricao', 'Avaliação'),
                'data': '-',
                'tipo': nota.get('tipo_avaliacao', ''),
                'nota': nota.get('valor', 0)
            })
            
            notas_por_ano[ano][materia_id]['soma_notas'] += nota.get('valor', 0)
            notas_por_ano[ano][materia_id]['count'] += 1
    
    # Calcular médias
    for ano in notas_por_ano:
        for materia_id in notas_por_ano[ano]:
            dados = notas_por_ano[ano][materia_id]
            if dados['count'] > 0:
                dados['media'] = dados['soma_notas'] / dados['count']
            else:
                dados['media'] = 0
    
    # Buscar turmas e matérias do aluno (para aba Turmas)
    from app.repositories import ProfessorRepository, TurmaRepository, NotaRepository
    professor_repo = ProfessorRepository()
    turma_repo = TurmaRepository()
    nota_repo = NotaRepository()
    
    # Criar DTO do aluno antes de usar
    aluno = AlunoDTO(aluno_data, _repos)
    
    # Buscar turmas do aluno
    aluno_turmas = _aluno_repo.get_turmas(id)
    materias_do_aluno = []
    ano_atual = date.today().year
    
    for tur in aluno_turmas:
        turma_id = tur.get('id')
        turmas_materias = turma_repo.get_materias(turma_id)
        
        for mat in turmas_materias:
            materia_id = mat.get('id')
            materia_codigo = mat.get('codigo', '')
            
            # Buscar notas do aluno nesta matéria
            notas_materia = nota_repo.get_by_aluno_materia(id, materia_id, ano_atual)
            
            # Calcular média
            if notas_materia:
                valores = [n.get('valor', 0) for n in notas_materia]
                media = sum(valores) / len(valores)
            else:
                media = None
            
            # Frequência (geral do aluno)
            frequencia = aluno.percentual_frequencia()
            
            materias_do_aluno.append({
                'codigo': materia_codigo,
                'media': media,
                'frequencia': frequencia
            })
    
    return render_template('alunos/detalhe.html', aluno=aluno, notas_por_ano=notas_por_ano, materias_do_aluno=materias_do_aluno)


@alunos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar aluno."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar alunos', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno_data = _aluno_repo.get_by_id(id)
    if not aluno_data:
        flash('Aluno não encontrado', 'error')
        return redirect(url_for('alunos.index'))
    
    aluno = AlunoDTO(aluno_data, _repos)
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
        
        _aluno_repo.update(id, data)
        
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
    
    _aluno_repo.update(id, {'status': 'inativo'})
    
    flash('Aluno desativado com sucesso', 'success')
    return redirect(url_for('alunos.index'))


@alunos_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar alunos."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    alunos = _aluno_repo.search(termo)
    alunos_ativos = [a for a in alunos if a.get('status') == 'ativo'][:10]
    
    return jsonify([{
        'id': a.get('id'),
        'nome': a.get('nome'),
        'matricula': a.get('matricula')
    } for a in alunos_ativos])
