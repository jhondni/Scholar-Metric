# app/controllers/escolas_controller.py - Controller de Escolas

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime, timedelta

from app import db
from app.models.escola import Escola, ConviteEscola
from app.models.usuario import Usuario
from app.models.professor import Professor

escolas_bp = Blueprint('escolas', __name__, url_prefix='/escolas')


class EscolaForm(FlaskForm):
    """Formulário de escola."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=150)
    ])
    cnpj = StringField('CNPJ', validators=[Optional(), Length(max=18)])
    endereco = TextAreaField('Endereço', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Length(max=120)])
    ano_letivo = IntegerField('Ano Letivo Atual', validators=[Optional()])


@escolas_bp.route('/')
@login_required
def index():
    """Lista de escolas (apenas para diretoras)."""
    if current_user.tipo != 'diretora':
        flash('Acesso negado', 'error')
        return redirect(url_for('dashboard.index'))
    
    escolas = Escola.query.order_by(Escola.nome).all()
    return render_template('escolas/index.html', escolas=escolas)


@escolas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def nova():
    """Criar nova escola."""
    if current_user.tipo != 'diretora':
        flash('Acesso negado', 'error')
        return redirect(url_for('dashboard.index'))
    
    form = EscolaForm()
    
    if form.validate_on_submit():
        escola = Escola(
            nome=form.nome.data,
            cnpj=form.cnpj.data,
            endereco=form.endereco.data,
            telefone=form.telefone.data,
            email=form.email.data,
            ano_letivo=form.ano_letivo.data if form.ano_letivo.data else datetime.now().year
        )
        
        # A diretora atual se torna responsável pela escola
        escola.diretoras.append(current_user)
        
        current_user.escola_id = escola.id
        
        db.session.add(escola)
        db.session.commit()
        
        flash('Escola criada com sucesso!', 'success')
        return redirect(url_for('escolas.index'))
    
    return render_template('escolas/form.html', form=form, titulo='Nova Escola')


@escolas_bp.route('/<uuid:uuid_hash>/convidar', methods=['GET', 'POST'])
@login_required
def convidar(uuid_hash):
    """Convidar usuário para escola via hash."""
    escola = Escola.query.filter_by(uuid_hash=str(uuid_hash)).first_or_404()
    
    if current_user.tipo != 'diretora' or current_user.escola_id != escola.id:
        flash('Acesso negado', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        tipo = request.form.get('tipo_usuario')
        
        # Verificar se convite já existe
        convite_existente = ConviteEscola.query.filter_by(
            escola_id=escola.id,
            email_convidado=email,
            status='pendente'
        ).first()
        
        if convite_existente:
            flash('Já existe um convite pendente para este e-mail', 'warning')
            return render_template('escolas/convidar.html', escola=escola)
        
        convite = ConviteEscola(
            escola_id=escola.id,
            convidado_por_id=current_user.id,
            email_convidado=email,
            tipo_usuario=tipo,
            validade_em=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(convite)
        db.session.commit()
        
        flash(f'Convite enviado para {email}', 'success')
        return redirect(url_for('escolas.index'))
    
    return render_template('escolas/convidar.html', escola=escola)


@escolas_bp.route('/convite/<uuid:uuid_hash>', methods=['GET', 'POST'])
@login_required
def responder_convite(uuid_hash):
    """Página para usuário responder convite."""
    convite = ConviteEscola.query.filter_by(uuid_hash=str(uuid_hash)).first_or_404()
    
    # Verificar se o convite é para o usuário atual
    if current_user.email != convite.email_convidado:
        flash('Este convite não é para você', 'error')
        return redirect(url_for('dashboard.index'))
    
    if not convite.esta_valido():
        flash('Convite expirado ou inválido', 'error')
        return redirect(url_for('configuracoes.index'))
    
    if request.method == 'POST':
        acao = request.form.get('acao')
        
        if acao == 'aceitar':
            # Aceitar convite
            convite.status = 'aceito'
            
            # Vincular usuário à escola
            current_user.escola_id = convite.escola_id
            current_user.tipo = convite.tipo_usuario
            current_user.convite_pendente_id = None
            
            # Se for professor, criar registro de professor
            if convite.tipo_usuario == 'professor':
                existing_professor = Professor.query.filter_by(usuario_id=current_user.id).first()
                if not existing_professor:
                    professor = Professor(
                        usuario_id=current_user.id,
                        registro=f'PROF{datetime.now().strftime("%Y%m%d%H%M%S")}'
                    )
                    db.session.add(professor)
            
            flash(f'Bem-vindo à {convite.escola.nome}!', 'success')
            
        elif acao == 'recusar':
            convite.status = 'recusado'
            flash('Convite recusado', 'info')
        
        db.session.commit()
        
        return redirect(url_for('dashboard.index'))
    
    return render_template('escolas/responder_convite.html', convite=convite)


@escolas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar escola."""
    escola = Escola.query.get_or_404(id)
    
    if current_user.tipo != 'diretora' or current_user.escola_id != escola.id:
        flash('Acesso negado', 'error')
        return redirect(url_for('dashboard.index'))
    
    form = EscolaForm(obj=escola)
    
    if form.validate_on_submit():
        escola.nome = form.nome.data
        escola.cnpj = form.cnpj.data
        escola.endereco = form.endereco.data
        escola.telefone = form.telefone.data
        escola.email = form.email.data
        escola.ano_letivo = form.ano_letivo.data
        
        db.session.commit()
        flash('Escola atualizada com sucesso', 'success')
        return redirect(url_for('escolas.index'))
    
    return render_template('escolas/form.html', form=form, titulo='Editar Escola', escola=escola)


@escolas_bp.route('/api/buscar-usuario')
@login_required
def buscar_usuario():
    """API para buscar usuário pelo ID/hash."""
    termo = request.args.get('q', '')
    
    if len(termo) < 3:
        return jsonify([])
    
    # Buscar por UUID ou nome
    usuarios = Usuario.query.filter(
        Usuario.email != current_user.email,
        db.or_(
            Usuario.uuid_hash == termo,
            Usuario.nome.ilike(f'%{termo}%')
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': u.uuid_hash,
        'nome': u.nome,
        'email': u.email,
        'tipo': u.tipo
    } for u in usuarios])