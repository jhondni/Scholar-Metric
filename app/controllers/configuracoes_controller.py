# app/controllers/configuracoes_controller.py - Controller de Configurações

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.repositories import UsuarioRepository

configuracoes_bp = Blueprint('configuracoes', __name__, url_prefix='/configuracoes')

usuario_repo = UsuarioRepository()


@configuracoes_bp.route('/')
@login_required
def index():
    """Página de configurações."""
    return render_template('configuracoes/index.html')


@configuracoes_bp.route('/tema', methods=['POST'])
@login_required
def tema():
    """Salvar preferência de tema."""
    tema = request.json.get('tema')
    
    if tema not in ['light', 'dark']:
        return jsonify({'error': 'Tema inválido'}), 400
    
    usuario_repo.update(current_user.id, {'tema': tema})
    current_user.tema = tema
    
    return jsonify({'success': True, 'tema': tema})


@configuracoes_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Editar perfil do usuário."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        
        data = {}
        if nome:
            data['nome'] = nome
        if telefone:
            data['telefone'] = telefone
        
        if data:
            usuario_repo.update(current_user.id, data)
            if nome:
                current_user.nome = nome
            if telefone:
                current_user.telefone = telefone
        
        return jsonify({'success': True, 'message': 'Perfil atualizado'})
    
    return render_template('configuracoes/perfil.html')


@configuracoes_bp.route('/senha', methods=['POST'])
@login_required
def senha():
    """Alterar senha."""
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if not current_user.verificar_senha(senha_atual):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    
    if nova_senha != confirmar_senha:
        return jsonify({'error': 'Senhas não coincidem'}), 400
    
    if len(nova_senha) < 6:
        return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
    
    usuario_repo.update_password(current_user.id, nova_senha)
    
    return jsonify({'success': True, 'message': 'Senha alterada com sucesso'})


@configuracoes_bp.route('/verificar-banco', methods=['GET'])
@login_required
def verificar_banco():
    """Verifica se todas as tabelas necessárias existem no banco."""
    if not current_user.tem_permissao(['diretora', 'coordenacao']):
        return jsonify({'error': 'Sem permissão'}), 403
    
    required_tables = [
        'usuarios', 'alunos', 'professores', 'turmas', 'aulas',
        'frequencias', 'notas', 'feriados', 'dias_nao_letivos',
        'materias', 'disponibilidade_professores'
    ]
    
    inspector = db.inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    missing_tables = [t for t in required_tables if t not in existing_tables]
    
    if missing_tables:
        return jsonify({
            'success': False,
            'missing_tables': missing_tables,
            'message': f'Tabelas não encontradas: {", ".join(missing_tables)}'
        })
    
    return jsonify({
        'success': True,
        'missing_tables': [],
        'message': 'Todas as tabelas necessárias estão presentes.'
    })
