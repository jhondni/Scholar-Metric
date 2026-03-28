"""
app/services/supabase_auth.py - Autenticação Supabase para Flask-Login

Wrapper que permite usar dados do Supabase com Flask-Login.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


def _parse_datetime(value):
    """
    Converte string para datetime de forma segura.
    
    Args:
        value: Valor a converter (str, datetime ou None)
        
    Returns:
        datetime ou None
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


class SupabaseUser(UserMixin):
    """
    Wrapper de usuário Supabase compatível com Flask-Login.
    
    Converte dados do Supabase (dicionário) em objeto compatível
    com o sistema de autenticação do Flask-Login.
    """
    
    def __init__(self, data: dict):
        """
        Inicializa o usuário a partir de dados do Supabase.
        
        Args:
            data: Dicionário com dados do usuário do Supabase
        """
        self.id = data.get('id')
        self.nome = data.get('nome', '')
        self.email = data.get('email', '')
        self.senha_hash = data.get('senha_hash', '')
        self.tipo = data.get('tipo', 'professor')
        self.avatar = data.get('avatar')
        self.telefone = data.get('telefone')
        self.tema = data.get('tema', 'light')
        self.ativo = data.get('ativo', True)
        
        # Converter datas de string para datetime
        self.criado_em = _parse_datetime(data.get('criado_em'))
        self.atualizado_em = _parse_datetime(data.get('atualizado_em'))
        self.ultimo_acesso = _parse_datetime(data.get('ultimo_acesso'))
        
        self._data = data
    
    def get_id(self):
        """Retorna o ID do usuário para Flask-Login."""
        return str(self.id)
    
    @property
    def is_active(self):
        """Retorna se o usuário está ativo."""
        return self.ativo
    
    @property
    def is_authenticated(self):
        """Retorna se o usuário está autenticado."""
        return True
    
    @property
    def is_anonymous(self):
        """Retorna se o usuário é anônimo."""
        return False
    
    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha está correta.
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            bool: True se a senha estiver correta
        """
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, senha)
    
    def set_senha(self, senha: str):
        """
        Define a senha do usuário com hash.
        
        Args:
            senha: Senha em texto plano
        """
        self.senha_hash = generate_password_hash(senha)
    
    def tem_permissao(self, permissoes: list) -> bool:
        """
        Verifica se o usuário tem permissão.
        
        Args:
            permissoes: Lista de tipos permitidos
            
        Returns:
            bool: True se tem permissão
        """
        return self.tipo in permissoes
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'senha_hash': self.senha_hash,
            'tipo': self.tipo,
            'avatar': self.avatar,
            'telefone': self.telefone,
            'tema': self.tema,
            'ativo': self.ativo,
            'criado_em': self.criado_em,
            'atualizado_em': self.atualizado_em,
            'ultimo_acesso': self.ultimo_acesso
        }
    
    def __repr__(self):
        return f'<SupabaseUser {self.nome} ({self.tipo})>'
