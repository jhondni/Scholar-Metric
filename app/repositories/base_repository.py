"""
app/repositories/base_repository.py - Repositório Base

Classe base para todos os repositórios do sistema.
Fornece operações CRUD genéricas via Supabase REST API.
"""

from typing import List, Dict, Optional, Any
from app.services.supabase_client import get_supabase_client


class BaseRepository:
    """
    Repositório base com operações CRUD genéricas.
    
    Todos os repositórios específicos herdam desta classe.
    """
    
    def __init__(self, table_name: str, model_class=None):
        """
        Inicializa o repositório.
        
        Args:
            table_name: Nome da tabela no Supabase
            model_class: Classe do modelo SQLAlchemy (opcional, para conversão)
        """
        self.table_name = table_name
        self.model_class = model_class
    
    def _get_client(self):
        """Retorna o cliente Supabase."""
        return get_supabase_client()
    
    def get_all(self, filters: Dict = None, order_by: str = None, 
                limit: int = None, offset: int = None) -> List[Dict]:
        """
        Busca todos os registros com filtros opcionais.
        
        Args:
            filters: Dicionário de filtros {campo: valor}
            order_by: Campo para ordenação (ex: 'nome', '-nome' para DESC)
            limit: Limite de registros
            offset: Offset para paginação
            
        Returns:
            List[Dict]: Lista de registros
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('*')
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            if order_by:
                if order_by.startswith('-'):
                    query = query.order(order_by[1:], desc=True)
                else:
                    query = query.order(order_by)
            
            if limit:
                query = query.limit(limit)
            
            if offset:
                query = query.offset(offset)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_all em {self.table_name}: {e}")
            return []
    
    def get_by_id(self, record_id: int) -> Optional[Dict]:
        """
        Busca um registro pelo ID.
        
        Args:
            record_id: ID do registro
            
        Returns:
            Optional[Dict]: Registro encontrado ou None
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*').eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] get_by_id em {self.table_name}: {e}")
            return None
    
    def get_by_field(self, field: str, value: Any) -> List[Dict]:
        """
        Busca registros por um campo específico.
        
        Args:
            field: Nome do campo
            value: Valor a buscar
            
        Returns:
            List[Dict]: Lista de registros encontrados
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*').eq(field, value).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_by_field em {self.table_name}: {e}")
            return []
    
    def get_one_by_field(self, field: str, value: Any) -> Optional[Dict]:
        """
        Busca um único registro por um campo específico.
        
        Args:
            field: Nome do campo
            value: Valor a buscar
            
        Returns:
            Optional[Dict]: Registro encontrado ou None
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*').eq(field, value).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] get_one_by_field em {self.table_name}: {e}")
            return None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """
        Cria um novo registro.
        
        Args:
            data: Dicionário com os dados do registro
            
        Returns:
            Optional[Dict]: Registro criado ou None em caso de erro
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] create em {self.table_name}: {e}")
            return None
    
    def update(self, record_id: int, data: Dict) -> Optional[Dict]:
        """
        Atualiza um registro existente.
        
        Args:
            record_id: ID do registro
            data: Dicionário com os dados a atualizar
            
        Returns:
            Optional[Dict]: Registro atualizado ou None em caso de erro
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).update(data).eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] update em {self.table_name}: {e}")
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
            client = self._get_client()
            client.table(self.table_name).delete().eq('id', record_id).execute()
            return True
        except Exception as e:
            print(f"[ERRO] delete em {self.table_name}: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """
        Conta registros com filtros opcionais.
        
        Args:
            filters: Dicionário de filtros {campo: valor}
            
        Returns:
            int: Número de registros
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('id', count='exact')
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            result = query.execute()
            return result.count if result.count is not None else 0
        except Exception as e:
            print(f"[ERRO] count em {self.table_name}: {e}")
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
            client = self._get_client()
            result = client.table(self.table_name).select('id').eq('id', record_id).limit(1).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"[ERRO] exists em {self.table_name}: {e}")
            return False
    
    def upsert(self, data: Dict, on_conflict: str = 'id') -> Optional[Dict]:
        """
        Insere ou atualiza um registro (UPSERT).
        
        Args:
            data: Dicionário com os dados
            on_conflict: Campo para detectar conflito
            
        Returns:
            Optional[Dict]: Registro criado/atualizado ou None
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).upsert(data, on_conflict=on_conflict).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] upsert em {self.table_name}: {e}")
            return None
