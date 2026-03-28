"""
app/repositories/usuario_repository.py - Repositório de Usuários

Operações de acesso a dados para a tabela de usuários.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository
from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioRepository(BaseRepository):
    """Repositório para operações com usuários."""
    
    def __init__(self):
        super().__init__('usuarios')
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email."""
        return self.get_one_by_field('email', email)
    
    def get_active_users(self) -> List[Dict]:
        """Retorna todos os usuários ativos."""
        return self.get_by_field('ativo', True)
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca usuários por tipo (diretora, coordenacao, professor)."""
        return self.get_by_field('tipo', tipo)
    
    def create_user(self, nome: str, email: str, senha: str, tipo: str = 'professor',
                    tema: str = 'light', ativo: bool = True) -> Optional[Dict]:
        """
        Cria um novo usuário com senha hash.
        
        Args:
            nome: Nome completo
            email: Email único
            senha: Senha em texto plano (será hasheada)
            tipo: Tipo de usuário
            tema: Tema preferido
            ativo: Status ativo
            
        Returns:
            Optional[Dict]: Usuário criado ou None
        """
        data = {
            'nome': nome,
            'email': email,
            'senha_hash': generate_password_hash(senha),
            'tipo': tipo,
            'tema': tema,
            'ativo': ativo
        }
        return self.create(data)
    
    def verify_password(self, user_id: int, senha: str) -> bool:
        """
        Verifica se a senha está correta.
        
        Args:
            user_id: ID do usuário
            senha: Senha em texto plano
            
        Returns:
            bool: True se a senha estiver correta
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
        return check_password_hash(user.get('senha_hash', ''), senha)
    
    def update_password(self, user_id: int, nova_senha: str) -> bool:
        """
        Atualiza a senha do usuário.
        
        Args:
            user_id: ID do usuário
            nova_senha: Nova senha em texto plano
            
        Returns:
            bool: True se atualizado com sucesso
        """
        result = self.update(user_id, {
            'senha_hash': generate_password_hash(nova_senha)
        })
        return result is not None
    
    def update_theme(self, user_id: int, tema: str) -> bool:
        """
        Atualiza o tema do usuário.
        
        Args:
            user_id: ID do usuário
            tema: Tema ('light' ou 'dark')
            
        Returns:
            bool: True se atualizado com sucesso
        """
        result = self.update(user_id, {'tema': tema})
        return result is not None
    
    def deactivate(self, user_id: int) -> bool:
        """Desativa um usuário."""
        result = self.update(user_id, {'ativo': False})
        return result is not None
