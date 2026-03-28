# app/controllers/professores_controller.py - Controller de Professores (Supabase)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, time as time_class

from app.repositories import ProfessorRepository, MateriaRepository, UsuarioRepository

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')

# Instâncias dos repositórios
professor_repo = ProfessorRepository()
materia_repo = MateriaRepository()
usuario_repo = UsuarioRepository()


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


# ==================== Funções Auxiliares ====================

def _dict_to_professor_obj(data):
    """Converte dicionário do Supabase em objeto compatível com templates."""
    if not data:
        return None
    
    # Buscar dados do usuário
    usuario_data = usuario_repo.get_by_id(data.get('usuario_id'))
    
    class UsuarioObj:
        def __init__(self, d):
            self.id = d.get('id')
            self.nome = d.get('nome', '')
            self.email = d.get('email', '')
            self.telefone = d.get('telefone', '')
    
    class ProfessorObj:
        def __init__(self, d, usuario):
            self.id = d.get('id')
            self.usuario_id = d.get('usuario_id')
            self.registro = d.get('registro', '')
            self.especialidade = d.get('especialidade', '')
            self.formacao = d.get('formacao', '')
            self.cpf = d.get('cpf', '')
            self.telefone = d.get('telefone', '')
            self.endereco = d.get('endereco', '')
            self.ativo = d.get('ativo', True)
            self.criado_em = d.get('criado_em')
            self.atualizado_em = d.get('atualizado_em')
            self.usuario = usuario
            self.materias = []  # Será preenchido quando necessário
    
    usuario = UsuarioObj(usuario_data) if usuario_data else UsuarioObj({})
    return ProfessorObj(data, usuario)


# ==================== Rotas ====================

@professores_bp.route('/')
@login_required
def index():
    """Lista de professores."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    professores_raw = professor_repo.get_all(order_by='registro')
    
    if busca:
        professores_raw = [p for p in professores_raw if busca.lower() in p.get('registro', '').lower()]
        # Também buscar por nome do usuário
        for p in professor_repo.get_all():
            usuario = usuario_repo.get_by_id(p.get('usuario_id'))
            if usuario and busca.lower() in usuario.get('nome', '').lower():
                if p not in professores_raw:
                    professores_raw.append(p)
    
    # Paginação manual
    per_page = 20
    total = len(professores_raw)
    start = (page - 1) * per_page
    end = start + per_page
    professores_page = professores_raw[start:end]
    
    professores_obj = [_dict_to_professor_obj(p) for p in professores_page]
    
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
    
    professores_paginados = PaginateObj(professores_obj, page, per_page, total)
    
    return render_template('professores/index.html', professores=professores_paginados, busca=busca)


@professores_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para cadastrar professores', 'error')
        return redirect(url_for('professores.index'))
    
    form = ProfessorForm()
    
    if form.validate_on_submit():
        if professor_repo.get_by_registro(form.registro.data):
            flash('Registro já cadastrado', 'error')
            return render_template('professores/form.html', form=form, titulo='Novo Professor')
        
        data = {
            'usuario_id': current_user.id,
            'registro': form.registro.data,
            'especialidade': form.especialidade.data,
            'formacao': form.formacao.data,
            'cpf': form.cpf.data,
            'telefone': form.telefone.data,
            'endereco': form.endereco.data,
            'ativo': form.ativo.data == '1'
        }
        
        professor_repo.create(data)
        
        flash('Professor cadastrado com sucesso', 'success')
        return redirect(url_for('professores.index'))
    
    return render_template('professores/form.html', form=form, titulo='Novo Professor')


@professores_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do professor."""
    professor_data = professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = _dict_to_professor_obj(professor_data)
    
    # Buscar matérias do professor
    professor.materias = professor_repo.get_materias(id)
    
    return render_template('professores/detalhe.html', professor=professor)


@professores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor_data = professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = _dict_to_professor_obj(professor_data)
    form = ProfessorForm(obj=professor)
    
    if form.validate_on_submit():
        data = {
            'especialidade': form.especialidade.data,
            'formacao': form.formacao.data,
            'cpf': form.cpf.data,
            'telefone': form.telefone.data,
            'endereco': form.endereco.data,
            'ativo': form.ativo.data == '1'
        }
        
        professor_repo.update(id, data)
        
        flash('Professor atualizado com sucesso', 'success')
        return redirect(url_for('professores.detalhe', id=id))
    
    return render_template('professores/form.html', form=form, titulo='Editar Professor', professor=professor)


@professores_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir professor."""
    if not current_user.tem_permissao(['diretora']):
        flash('Sem permissão para excluir professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor_repo.update(id, {'ativo': False})
    
    flash('Professor desativado com sucesso', 'success')
    return redirect(url_for('professores.index'))


@professores_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar professores."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    professores_raw = professor_repo.get_active_professors()
    resultado = []
    
    for p in professores_raw:
        usuario = usuario_repo.get_by_id(p.get('usuario_id'))
        if usuario and termo.lower() in usuario.get('nome', '').lower():
            resultado.append({
                'id': p.get('id'),
                'nome': usuario.get('nome'),
                'registro': p.get('registro')
            })
        if len(resultado) >= 10:
            break
    
    return jsonify(resultado)


# ==================== Disponibilidade do Professor ====================

@professores_bp.route('/<int:id>/adicionar-disponibilidade', methods=['POST'])
@login_required
def adicionar_disponibilidade(id):
    """Adiciona disponibilidade ao professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão', 'error')
        return redirect(url_for('professores.index'))
    
    professor_data = professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    dia_semana = request.form.get('dia_semana', type=int)
    horario_inicio = request.form.get('horario_inicio')
    horario_fim = request.form.get('horario_fim')
    
    if horario_inicio and horario_fim:
        from app.services.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        client.table('disponibilidade_professores').insert({
            'professor_id': id,
            'dia_semana': dia_semana,
            'horario_inicio': horario_inicio,
            'horario_fim': horario_fim,
            'ativo': True
        }).execute()
        
        flash('Disponibilidade adicionada com sucesso', 'success')
    else:
        flash('Preencha os horários', 'error')
    
    return redirect(url_for('professores.detalhe', id=id))


# ==================== Matérias do Professor ====================

@professores_bp.route('/<int:id>/materias', methods=['GET', 'POST'])
@login_required
def materias(id):
    """Gerenciar matérias que o professor pode lecionar."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para gerenciar matérias de professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor_data = professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = _dict_to_professor_obj(professor_data)
    
    if request.method == 'POST':
        materia_ids = request.form.getlist('materias')
        
        # Limpar matérias atuais via Supabase
        from app.services.supabase_client import get_supabase_client
        client = get_supabase_client()
        client.table('professor_materias').delete().eq('professor_id', id).execute()
        
        # Adicionar novas matérias
        for mid in materia_ids:
            professor_repo.associate_materia(id, int(mid))
        
        flash('Matérias do professor atualizadas com sucesso', 'success')
        return redirect(url_for('professores.detalhe', id=id))
    
    materias_raw = materia_repo.get_active_materias()
    professor.materias = professor_repo.get_materias(id)
    
    return render_template('professores/materias.html', professor=professor, materias=materias_raw)


@professores_bp.route('/<int:id>/materias/adicionar', methods=['POST'])
@login_required
def adicionar_materia(id):
    """Adiciona uma matéria ao professor via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    materia_id = request.json.get('materia_id')
    
    if professor_repo.associate_materia(id, materia_id):
        return jsonify({'success': True, 'message': 'Matéria adicionada'})
    
    return jsonify({'error': 'Erro ao adicionar matéria'}), 400


@professores_bp.route('/<int:id>/materias/<int:materia_id>', methods=['DELETE'])
@login_required
def remover_materia(id, materia_id):
    """Remove uma matéria do professor via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if professor_repo.dissociate_materia(id, materia_id):
        return jsonify({'success': True, 'message': 'Matéria removida'})
    
    return jsonify({'error': 'Erro ao remover matéria'}), 400
