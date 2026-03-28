"""
app/repositories/escola_repository.py - Repositório de Escolas

Operações de acesso a dados para a tabela de escolas.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository
import uuid


class EscolaRepository(BaseRepository):
    """Repositório para operações com escolas."""
    
    def __init__(self):
        super().__init__('escolas')
    
    def get_by_uuid(self, uuid_hash: str) -> Optional[Dict]:
        """Busca escola por UUID."""
        return self.get_one_by_field('uuid_hash', uuid_hash)
    
    def get_by_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Busca escola por CNPJ."""
        return self.get_one_by_field('cnpj', cnpj)
    
    def get_active_schools(self) -> List[Dict]:
        """Retorna todas as escolas ativas."""
        return self.get_by_field('ativa', True)
    
    def create_school(self, nome: str, cnpj: str = None, endereco: str = None,
                      telefone: str = None, email: str = None) -> Optional[Dict]:
        """
        Cria uma nova escola.
        
        Args:
            nome: Nome da escola
            cnpj: CNPJ (opcional)
            endereco: Endereço (opcional)
            telefone: Telefone (opcional)
            email: Email (opcional)
            
        Returns:
            Optional[Dict]: Escola criada ou None
        """
        data = {
            'uuid_hash': str(uuid.uuid4()),
            'nome': nome,
            'cnpj': cnpj,
            'endereco': endereco,
            'telefone': telefone,
            'email': email,
            'ativa': True
        }
        return self.create(data)
    
    def get_convites(self, escola_id: int) -> List[Dict]:
        """
        Retorna convites pendentes de uma escola.
        
        Args:
            escola_id: ID da escola
            
        Returns:
            List[Dict]: Lista de convites
        """
        try:
            client = self._get_client()
            result = client.table('convites_escola').select('*').eq('escola_id', escola_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_convites em escolas: {e}")
            return []
    
    def create_convite(self, escola_id: int, convidado_por_id: int,
                       email_convidado: str, tipo_usuario: str) -> Optional[Dict]:
        """
        Cria um convite para a escola.
        
        Args:
            escola_id: ID da escola
            convidado_por_id: ID de quem convidou
            email_convidado: Email do convidado
            tipo_usuario: Tipo de usuário ('professor', 'coordenacao')
            
        Returns:
            Optional[Dict]: Convite criado ou None
        """
        from datetime import datetime, timedelta
        
        data = {
            'uuid_hash': str(uuid.uuid4()),
            'escola_id': escola_id,
            'convidado_por_id': convidado_por_id,
            'email_convidado': email_convidado,
            'tipo_usuario': tipo_usuario,
            'status': 'pendente',
            'validade_em': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        try:
            client = self._get_client()
            result = client.table('convites_escola').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] create_convite: {e}")
            return None
