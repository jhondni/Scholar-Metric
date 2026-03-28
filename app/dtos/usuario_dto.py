"""
app/dtos/usuario_dto.py - DTO de Usuário

Encapsula dados do usuário do Supabase.
"""

from app.dtos.base_dto import BaseDTO


class UsuarioDTO(BaseDTO):
    """
    Data Transfer Object para Usuário.
    
    Fornece todos os atributos esperados pelos templates.
    """
    
    def __init__(self, data: dict):
        """
        Inicializa o DTO a partir de dados do Supabase.
        
        Args:
            data: Dicionário com dados do Supabase
        """
        self.id = data.get('id')
        self.nome = data.get('nome', '')
        self.email = data.get('email', '')
        self.tipo = data.get('tipo', 'professor')
        self.avatar = data.get('avatar')
        self.telefone = data.get('telefone')
        self.tema = data.get('tema', 'light')
        self.ativo = self.parse_bool(data.get('ativo', True))
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        self.ultimo_acesso = self.parse_datetime(data.get('ultimo_acesso'))
    
    def __repr__(self):
        return f'<UsuarioDTO {self.nome} ({self.tipo})>'
