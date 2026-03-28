"""
app/repositories/feriado_repository.py - Repositório de Feriados

Operações de acesso a dados para a tabela de feriados.
"""

from typing import List, Dict, Optional
from datetime import date
from app.repositories.base_repository import BaseRepository


class FeriadoRepository(BaseRepository):
    """Repositório para operações com feriados."""
    
    def __init__(self):
        super().__init__('feriados')
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca feriados por tipo (nacional, estadual, municipal)."""
        return self.get_by_field('tipo', tipo)
    
    def get_recorrentes(self) -> List[Dict]:
        """Retorna feriados que se repetem todo ano."""
        return self.get_by_field('recorrente', True)
    
    def get_by_date(self, data: date) -> Optional[Dict]:
        """
        Verifica se uma data é feriado.
        
        Args:
            data: Data a verificar
            
        Returns:
            Optional[Dict]: Feriado encontrado ou None
        """
        return self.get_one_by_field('data', str(data))
    
    def is_feriado(self, data: date) -> bool:
        """
        Verifica se uma data é feriado.
        
        Args:
            data: Data a verificar
            
        Returns:
            bool: True se for feriado
        """
        return self.get_by_date(data) is not None
    
    def get_in_period(self, data_inicio: date, data_fim: date) -> List[Dict]:
        """
        Retorna feriados em um período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            List[Dict]: Lista de feriados no período
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*')
            result = result.gte('data', str(data_inicio))
            result = result.lte('data', str(data_fim))
            result = result.order('data').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_in_period em feriados: {e}")
            return []
    
    def get_upcoming(self, limit: int = 5) -> List[Dict]:
        """
        Retorna próximos feriados.
        
        Args:
            limit: Número máximo de feriados
            
        Returns:
            List[Dict]: Lista de próximos feriados
        """
        try:
            client = self._get_client()
            today = str(date.today())
            result = client.table(self.table_name).select('*').gte('data', today)
            result = result.order('data').limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_upcoming em feriados: {e}")
            return []


class DiaNaoLetivoRepository(BaseRepository):
    """Repositório para operações com dias não letivos."""
    
    def __init__(self):
        super().__init__('dias_nao_letivos')
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca dias não letivos por tipo."""
        return self.get_by_field('tipo', tipo)
    
    def is_dia_nao_letivo(self, data: date) -> bool:
        """
        Verifica se uma data é dia não letivo.
        
        Args:
            data: Data a verificar
            
        Returns:
            bool: True se for dia não letivo
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('id')
            result = result.lte('data_inicio', str(data))
            result = result.gte('data_fim', str(data))
            result = result.limit(1).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"[ERRO] is_dia_nao_letivo: {e}")
            return False
    
    def get_in_period(self, data_inicio: date, data_fim: date) -> List[Dict]:
        """
        Retorna dias não letivos em um período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            List[Dict]: Lista de dias não letivos
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*')
            result = result.lte('data_inicio', str(data_fim))
            result = result.gte('data_fim', str(data_inicio))
            result = result.order('data_inicio').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_in_period em dias_nao_letivos: {e}")
            return []
