# app/controllers/professores_controller.py - Controller de Professores (Supabase + DTOs)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, time as time_class

from app.repositories import ProfessorRepository, MateriaRepository, UsuarioRepository
from app.dtos.professor_dto import ProfessorDTO

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')

# Instâncias dos repositórios (reutilizadas)
_professor_repo = ProfessorRepository()
_materia_repo = MateriaRepository()
_usuario_repo = UsuarioRepository()

# Dicionário de repositórios para DTOs
_repos = {
    'professor': _professor_repo,
    'materia': _materia_repo,
    'usuario': _usuario_repo
}


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

@professores_bp.route('/')
@login_required
def index():
    """Lista de professores."""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
    professores_raw = _professor_repo.get_all(order_by='registro')
    
    if busca:
        professores_filtered = []
        for p in professores_raw:
            if busca.lower() in p.get('registro', '').lower():
                professores_filtered.append(p)
            else:
                usuario = _usuario_repo.get_by_id(p.get('usuario_id'))
                if usuario and busca.lower() in usuario.get('nome', '').lower():
                    professores_filtered.append(p)
        professores_raw = professores_filtered
    
    professores_list = [ProfessorDTO(p, _repos) for p in professores_raw]
    professores = _paginate(professores_list, page)
    
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
        if _professor_repo.get_by_registro(form.registro.data):
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
        
        _professor_repo.create(data)
        
        flash('Professor cadastrado com sucesso', 'success')
        return redirect(url_for('professores.index'))
    
    return render_template('professores/form.html', form=form, titulo='Novo Professor')


@professores_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhes do professor."""
    professor_data = _professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = ProfessorDTO(professor_data, _repos)
    return render_template('professores/detalhe.html', professor=professor)


@professores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar professor."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão para editar professores', 'error')
        return redirect(url_for('professores.index'))
    
    professor_data = _professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = ProfessorDTO(professor_data, _repos)
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
        
        _professor_repo.update(id, data)
        
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
    
    _professor_repo.update(id, {'ativo': False})
    
    flash('Professor desativado com sucesso', 'success')
    return redirect(url_for('professores.index'))


@professores_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar professores."""
    termo = request.args.get('q', '')
    
    if len(termo) < 2:
        return jsonify([])
    
    professores_raw = _professor_repo.get_active_professors()
    resultado = []
    
    for p in professores_raw:
        usuario = _usuario_repo.get_by_id(p.get('usuario_id'))
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
    """Adiciona disponibilidade ao professor para múltiplos dias."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        flash('Sem permissão', 'error')
        return redirect(url_for('professores.index'))
    
    professor_data = _professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    # Processar múltiplos dias selecionados
    dias_semana = request.form.getlist('dias_semana')
    horario_inicio = request.form.get('horario_inicio')
    horario_fim = request.form.get('horario_fim')
    
    if not dias_semana:
        flash('Selecione pelo menos um dia da semana', 'error')
        return redirect(url_for('professores.detalhe', id=id))
    
    if horario_inicio and horario_fim:
        from app.services.supabase_client import get_supabase_client
        
        try:
            client = get_supabase_client()
            dias_criados = 0
            dias_existentes = 0
            erros = []
            
            # Dias da semana para exibir nomes nos logs
            nomes_dias = {
                '0': 'Segunda-feira',
                '1': 'Terça-feira',
                '2': 'Quarta-feira',
                '3': 'Quinta-feira',
                '4': 'Sexta-feira',
                '5': 'Sábado',
                '6': 'Domingo'
            }
            
            for dia in dias_semana:
                try:
                    # Verificar se já existe para este professor, dia e horário
                    existing = client.table('disponibilidade_professores') \
                        .select('id') \
                        .eq('professor_id', id) \
                        .eq('dia_semana', int(dia)) \
                        .eq('horario_inicio', horario_inicio) \
                        .eq('horario_fim', horario_fim) \
                        .execute()
                    
                    if existing.data:
                        dias_existentes += 1
                        continue
                    
                    client.table('disponibilidade_professores').insert({
                        'professor_id': id,
                        'dia_semana': int(dia),
                        'horario_inicio': horario_inicio,
                        'horario_fim': horario_fim,
                        'ativo': True
                    }).execute()
                    dias_criados += 1
                    
                except Exception as day_error:
                    error_msg = str(day_error)
                    nome_dia = nomes_dias.get(dia, f'Dia {dia}')
                    erros.append(f"{nome_dia}: {error_msg[:50]}")
            
            # Mensagens de resultado
            if dias_criados > 0:
                if dias_criados == 1:
                    flash(f'Disponibilidade adicionada com sucesso', 'success')
                else:
                    flash(f'{dias_criados} disponibilidades adicionadas com sucesso', 'success')
            
            if dias_existentes > 0:
                if dias_existentes == 1:
                    flash('1 disponibilidade já existia e foi ignorada', 'info')
                else:
                    flash(f'{dias_existentes} disponibilidades já existiam e foram ignoradas', 'info')
            
            if erros:
                flash(f'Erros ao adicionar: {"; ".join(erros)}', 'error')
                
        except Exception as e:
            error_msg = str(e)
            
            # Tratamento específico para erro de tabela não encontrada (PGRST205)
            if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
                print(f"[ERRO] adicionar_disponibilidade: Tabela 'disponibilidade_professores' "
                      f"não encontrada no Supabase.")
                flash('Erro: Tabela de disponibilidade não encontrada no banco de dados. '
                      'Execute o script de migração SQL primeiro.', 'error')
            # Tratamento para erro de validação de horário
            elif 'chk_horario_valido' in error_msg:
                flash('Erro: O horário de fim deve ser maior que o horário de início.', 'error')
            # Outros erros
            else:
                print(f"[ERRO] adicionar_disponibilidade: {e}")
                flash(f'Erro ao adicionar disponibilidade: {error_msg[:100]}', 'error')
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
    
    professor_data = _professor_repo.get_by_id(id)
    if not professor_data:
        flash('Professor não encontrado', 'error')
        return redirect(url_for('professores.index'))
    
    professor = ProfessorDTO(professor_data, _repos)
    
    if request.method == 'POST':
        materia_ids = request.form.getlist('materias')
        
        # Limpar matérias atuais via Supabase
        from app.services.supabase_client import get_supabase_client
        client = get_supabase_client()
        client.table('professor_materias').delete().eq('professor_id', id).execute()
        
        # Adicionar novas matérias
        for mid in materia_ids:
            _professor_repo.associate_materia(id, int(mid))
        
        flash('Matérias do professor atualizadas com sucesso', 'success')
        return redirect(url_for('professores.detalhe', id=id))
    
    materias_raw = _materia_repo.get_active_materias()
    return render_template('professores/materias.html', professor=professor, materias=materias_raw)


@professores_bp.route('/<int:id>/materias/adicionar', methods=['POST'])
@login_required
def adicionar_materia(id):
    """Adiciona uma matéria ao professor via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    materia_id = request.json.get('materia_id')
    
    if _professor_repo.associate_materia(id, materia_id):
        return jsonify({'success': True, 'message': 'Matéria adicionada'})
    
    return jsonify({'error': 'Erro ao adicionar matéria'}), 400


@professores_bp.route('/<int:id>/materias/<int:materia_id>', methods=['DELETE'])
@login_required
def remover_materia(id, materia_id):
    """Remove uma matéria do professor via API."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if _professor_repo.dissociate_materia(id, materia_id):
        return jsonify({'success': True, 'message': 'Matéria removida'})
    
    return jsonify({'error': 'Erro ao remover matéria'}), 400
