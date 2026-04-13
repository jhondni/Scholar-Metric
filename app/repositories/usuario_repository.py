"""
app/repositories/usuario_repository.py - Repositório de Usuários

Operações de acesso a dados para a tabela de usuários via SQLAlchemy.
"""

from typing import List, Optional, Dict
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.usuario import Usuario


class UsuarioRepository:
    """Repositório para operações com usuários via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todos os usuários."""
        query = Usuario.query
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(Usuario, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Usuario, order_by[1:])))
            else:
                query = query.order_by(getattr(Usuario, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [u.to_dict() for u in query.all()]
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID."""
        user = Usuario.query.get(user_id)
        return user.to_dict() if user else None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email."""
        user = Usuario.query.filter_by(email=email).first()
        return user.to_dict() if user else None
    
    def get_active_users(self) -> List[Dict]:
        """Retorna todos os usuários ativos."""
        users = Usuario.query.filter_by(ativo=True).all()
        return [u.to_dict() for u in users]
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca usuários por tipo."""
        users = Usuario.query.filter_by(tipo=tipo).all()
        return [u.to_dict() for u in users]
    
    def create_user(self, nome: str, email: str, senha: str, tipo: str = 'professor',
                    tema: str = 'light', ativo: bool = True) -> Optional[Dict]:
        """Cria um novo usuário com senha hash."""
        try:
            user = Usuario()
            user.nome = nome
            user.email = email
            user.set_senha(senha)
            user.tipo = tipo
            user.tema = tema
            user.ativo = ativo
            
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create_user: {e}")
            return None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria usuário a partir de dicionário."""
        try:
            user = Usuario()
            for key, value in data.items():
                if hasattr(user, key):
                    if key == 'senha':
                        user.set_senha(value)
                    else:
                        setattr(user, key, value)
            
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um usuário existente."""
        try:
            user = Usuario.query.get(user_id)
            if not user:
                return None
            
            for key, value in data.items():
                if hasattr(user, key):
                    if key == 'senha':
                        user.set_senha(value)
                    else:
                        setattr(user, key, value)
            
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, user_id: int) -> bool:
        """Deleta um usuário."""
        try:
            user = Usuario.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def verify_password(self, user_id: int, senha: str) -> bool:
        """Verifica se a senha está correta."""
        user = Usuario.query.get(user_id)
        if not user:
            return False
        return user.verificar_senha(senha)
    
    def update_password(self, user_id: int, nova_senha: str) -> bool:
        """Atualiza a senha do usuário."""
        try:
            user = Usuario.query.get(user_id)
            if not user:
                return False
            user.set_senha(nova_senha)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update_password: {e}")
            return False
    
    def update_theme(self, user_id: int, tema: str) -> bool:
        """Atualiza o tema do usuário."""
        try:
            user = Usuario.query.get(user_id)
            if not user:
                return False
            user.tema = tema
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update_theme: {e}")
            return False
    
    def deactivate(self, user_id: int) -> bool:
        """Desativa um usuário."""
        return self.update(user_id, {'ativo': False}) is not None
    
    def update_last_access(self, user_id: int) -> bool:
        """Atualiza timestamp do último acesso."""
        try:
            user = Usuario.query.get(user_id)
            if not user:
                return False
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update_last_access: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """Conta usuários."""
        query = Usuario.query
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(Usuario, key) == value)
        return query.count()
    
    def exists(self, user_id: int) -> bool:
        """Verifica se usuário existe."""
        return Usuario.query.get(user_id) is not None
