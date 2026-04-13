"""
app/repositories/base_repository.py - Repositório Base

Classe base para todos os repositórios do sistema.
Fornece operações CRUD genéricas via SQLAlchemy ORM.
"""

from typing import List, Optional, Any
from sqlalchemy import desc
from app import db


class BaseRepository:
    """
    Repositório base com operações CRUD genéricas.
    
    Todos os repositórios específicos herdam desta classe.
    """
    
    model_class = None
    
    def __init__(self, table_name: str = None, model_class=None):
        """
        Inicializa o repositório.
        
        Args:
            table_name: Nome da tabela (para compatibilidade, não usado)
            model_class: Classe do modelo SQLAlchemy
        """
        if model_class is not None:
            self.model_class = model_class
    
    def _to_dict(self, obj) -> Optional[dict]:
        """Converte objeto SQLAlchemy para dicionário."""
        if obj is None:
            return None
        if hasattr(obj, '__dict__'):
            result = {}
            for key in obj.__table__.columns.keys():
                value = getattr(obj, key, None)
                if hasattr(value, 'isoformat'):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
            return result
        return None
    
    def get_all(self, filters: dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[dict]:
        """
        Busca todos os registros com filtros opcionais.
        
        Args:
            filters: Dicionário de filtros {campo: valor}
            order_by: Campo para ordenação (ex: 'nome', '-nome' para DESC)
            limit: Limite de registros
            offset: Offset para paginação
            
        Returns:
            List[dict]: Lista de registros
        """
        try:
            query = self.model_class.query
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        if hasattr(self.model_class, key):
                            query = query.filter(getattr(self.model_class, key) == value)
            
            if order_by:
                if order_by.startswith('-'):
                    column = getattr(self.model_class, order_by[1:], None)
                    if column:
                        query = query.order_by(desc(column))
                else:
                    column = getattr(self.model_class, order_by, None)
                    if column:
                        query = query.order_by(column)
            
            if limit:
                query = query.limit(limit)
            
            if offset:
                query = query.offset(offset)
            
            results = query.all()
            return [self._to_dict(r) for r in results]
        except Exception as e:
            print(f"[ERRO] get_all em {self.model_class.__name__}: {e}")
            return []
    
    def get_by_id(self, record_id: int) -> Optional[dict]:
        """
        Busca um registro pelo ID.
        
        Args:
            record_id: ID do registro
            
        Returns:
            Optional[dict]: Registro encontrado ou None
        """
        try:
            result = self.model_class.query.get(record_id)
            return self._to_dict(result)
        except Exception as e:
            print(f"[ERRO] get_by_id em {self.model_class.__name__}: {e}")
            return None
    
    def get_by_field(self, field: str, value: Any) -> List[dict]:
        """
        Busca registros por um campo específico.
        
        Args:
            field: Nome do campo
            value: Valor a buscar
            
        Returns:
            List[dict]: Lista de registros encontrados
        """
        try:
            column = getattr(self.model_class, field, None)
            if column:
                results = self.model_class.query.filter(column == value).all()
                return [self._to_dict(r) for r in results]
            return []
        except Exception as e:
            print(f"[ERRO] get_by_field em {self.model_class.__name__}: {e}")
            return []
    
    def get_one_by_field(self, field: str, value: Any) -> Optional[dict]:
        """
        Busca um único registro por um campo específico.
        
        Args:
            field: Nome do campo
            value: Valor a buscar
            
        Returns:
            Optional[dict]: Registro encontrado ou None
        """
        try:
            column = getattr(self.model_class, field, None)
            if column:
                result = self.model_class.query.filter(column == value).first()
                return self._to_dict(result)
            return None
        except Exception as e:
            print(f"[ERRO] get_one_by_field em {self.model_class.__name__}: {e}")
            return None
    
    def create(self, data: dict) -> Optional[dict]:
        """
        Cria um novo registro.
        
        Args:
            data: Dicionário com os dados do registro
            
        Returns:
            Optional[dict]: Registro criado ou None em caso de erro
        """
        try:
            instance = self.model_class()
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.add(instance)
            db.session.commit()
            return self._to_dict(instance)
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create em {self.model_class.__name__}: {e}")
            return None
    
    def update(self, record_id: int, data: dict) -> Optional[dict]:
        """
        Atualiza um registro existente.
        
        Args:
            record_id: ID do registro
            data: Dicionário com os dados a atualizar
            
        Returns:
            Optional[dict]: Registro atualizado ou None em caso de erro
        """
        try:
            instance = self.model_class.query.get(record_id)
            if not instance:
                return None
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
            return self._to_dict(instance)
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update em {self.model_class.__name__}: {e}")
            return None
    
    def delete(self, record_id: int) -> bool:
        """
        Deleta um registro.
        
        Args:
            record_id: ID do registro
            
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            instance = self.model_class.query.get(record_id)
            if instance:
                db.session.delete(instance)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete em {self.model_class.__name__}: {e}")
            return False
    
    def count(self, filters: dict = None) -> int:
        """
        Conta registros com filtros opcionais.
        
        Args:
            filters: Dicionário de filtros {campo: valor}
            
        Returns:
            int: Número de registros
        """
        try:
            query = self.model_class.query
            
            if filters:
                for key, value in filters.items():
                    if value is not None and hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
            
            return query.count()
        except Exception as e:
            print(f"[ERRO] count em {self.model_class.__name__}: {e}")
            return 0
    
    def exists(self, record_id: int) -> bool:
        """
        Verifica se um registro existe.
        
        Args:
            record_id: ID do registro
            
        Returns:
            bool: True se existe
        """
        try:
            return self.model_class.query.get(record_id) is not None
        except Exception as e:
            print(f"[ERRO] exists em {self.model_class.__name__}: {e}")
            return False
    
    def upsert(self, data: dict, on_conflict: str = 'id') -> Optional[dict]:
        """
        Insere ou atualiza um registro (UPSERT).
        
        Args:
            data: Dicionário com os dados
            on_conflict: Campo para detectar conflito
            
        Returns:
            Optional[dict]: Registro criado/atualizado ou None
        """
        try:
            conflict_id = data.get(on_conflict)
            if conflict_id:
                instance = self.model_class.query.get(conflict_id)
                if instance:
                    for key, value in data.items():
                        if hasattr(instance, key):
                            setattr(instance, key, value)
                    db.session.commit()
                    return self._to_dict(instance)
            
            instance = self.model_class()
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.add(instance)
            db.session.commit()
            return self._to_dict(instance)
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] upsert em {self.model_class.__name__}: {e}")
            return None
