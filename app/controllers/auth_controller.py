# app/controllers/auth_controller.py - Controller de Autenticação

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ==================== Formulários ====================

class LoginForm(FlaskForm):
    """Formulário de login."""
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail é obrigatório'),
        Email(message='E-mail inválido')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória')
    ])
    lembrar = BooleanField('Lembrar-me')


class RegistroForm(FlaskForm):
    """Formulário de registro."""
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=3, max=100, message='Nome deve ter entre 3 e 100 caracteres')
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail é obrigatório'),
        Email(message='E-mail inválido')
    ])
    tipo = SelectField('Tipo', choices=[
        ('professor', 'Professor'),
        ('coordenacao', 'Coordenação'),
        ('diretora', 'Diretora')
    ], validators=[DataRequired(message='Tipo é obrigatório')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Confirmação é obrigatória'),
        EqualTo('senha', message='Senhas não coincidem')
    ])
    
    def validate_email(self, field):
        """Valida se o e-mail já está em uso."""
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError('E-mail já cadastrado')


class RecuperarSenhaForm(FlaskForm):
    """Formulário de recuperação de senha."""
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail é obrigatório'),
        Email(message='E-mail inválido')
    ])


# ==================== Rotas ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and usuario.verificar_senha(form.senha.data):
            if not usuario.ativo:
                flash('Conta desativada. Contate o administrador.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(usuario, remember=form.lembrar.data)
            usuario.atualizar_ultimo_acesso()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        
        flash('E-mail ou senha incorretos', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Rota de registro."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            tipo=form.tipo.data
        )
        usuario.set_senha(form.senha.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html', form=form)


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Rota de recuperação de senha."""
    form = RecuperarSenhaForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario:
            # TODO: Implementar envio de e-mail com link de recuperação
            flash('Instruções enviadas para seu e-mail', 'success')
        else:
            # Por segurança, não informar se o e-mail existe
            flash('Instruções enviadas para seu e-mail', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_senha.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de logout."""
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))
