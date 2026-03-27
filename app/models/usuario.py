# app/models/usuario.py - Modelo de Usuário

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager


class Usuario(UserMixin, db.Model):
    """
    Modelo de Usuário do sistema.
    
    Responsável pela autenticação e controle de acesso.
    Herda de UserMixin para integração com Flask-Login.
    """
    
    __tablename__ = 'usuarios'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    
    # Perfil
    tipo = db.Column(db.String(20), nullable=False, default='professor')
    # Tipos: 'diretora', 'coordenacao', 'professor'
    
    avatar = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    
    # Preferências
    tema = db.Column(db.String(10), default='light')
    # Temas: 'light', 'dark'
    
    # Controle
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    professor = db.relationship('Professor', backref='usuario', uselist=False, lazy=True)
    
    def set_senha(self, senha):
        """Define a senha do usuário com hash."""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta."""
        return check_password_hash(self.senha_hash, senha)
    
    def tem_permissao(self, permissoes):
        """
        Verifica se o usuário tem permissão.
        
        Args:
            permissoes: Lista de tipos permitidos
            
        Returns:
            bool: True se tem permissão
        """
        return self.tipo in permissoes
    
    def atualizar_ultimo_acesso(self):
        """Atualiza o timestamp do último acesso."""
        self.ultimo_acesso = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Usuario {self.nome} ({self.tipo})>'


@login_manager.user_loader
def load_user(user_id):
    """Callback para carregar usuário na sessão."""
    return Usuario.query.get(int(user_id))
