"""
app/repositories/aula_repository.py - Repositório de Aulas

Operações de acesso a dados para a tabela de aulas.
"""

from typing import List, Dict, Optional
from datetime import date, datetime
from app.repositories.base_repository import BaseRepository


class AulaRepository(BaseRepository):
    """Repositório para operações com aulas."""
    
    def __init__(self):
        super().__init__('aulas')
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca aulas de uma turma."""
        return self.get_by_field('turma_id', turma_id)
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """Busca aulas de um professor."""
        return self.get_by_field('professor_id', professor_id)
    
    def get_by_date_range(self, data_inicio: date, data_fim: date, 
                          turma_id: int = None) -> List[Dict]:
        """
        Busca aulas em um intervalo de datas.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            turma_id: Filtrar por turma (opcional)
            
        Returns:
            List[Dict]: Lista de aulas
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('*')
            query = query.gte('data', str(data_inicio))
            query = query.lte('data', str(data_fim))
            
            if turma_id:
                query = query.eq('turma_id', turma_id)
            
            result = query.order('data').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_by_date_range em aulas: {e}")
            return []
    
    def get_by_date(self, data: date, turma_id: int = None) -> List[Dict]:
        """
        Busca aulas de uma data específica.
        
        Args:
            data: Data da aula
            turma_id: Filtrar por turma (opcional)
            
        Returns:
            List[Dict]: Lista de aulas
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('*').eq('data', str(data))
            
            if turma_id:
                query = query.eq('turma_id', turma_id)
            
            result = query.order('horario_inicio').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_by_date em aulas: {e}")
            return []
    
    def get_upcoming(self, turma_id: int = None, limit: int = 10) -> List[Dict]:
        """
        Busca próximas aulas.
        
        Args:
            turma_id: Filtrar por turma (opcional)
            limit: Limite de resultados
            
        Returns:
            List[Dict]: Lista de próximas aulas
        """
        try:
            client = self._get_client()
            today = str(date.today())
            query = client.table(self.table_name).select('*').gte('data', today)
            
            if turma_id:
                query = query.eq('turma_id', turma_id)
            
            result = query.order('data').limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_upcoming em aulas: {e}")
            return []
    
    def check_conflict(self, turma_id: int, data: date, 
                       horario_inicio: str, horario_fim: str,
                       exclude_id: int = None) -> bool:
        """
        Verifica se existe conflito de horário.
        
        Args:
            turma_id: ID da turma
            data: Data da aula
            horario_inicio: Hora de início
            horario_fim: Hora de término
            exclude_id: ID da aula a excluir da verificação
            
        Returns:
            bool: True se existe conflito
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('id')
            query = query.eq('turma_id', turma_id)
            query = query.eq('data', str(data))
            query = query.neq('status', 'cancelada')
            
            if exclude_id:
                query = query.neq('id', exclude_id)
            
            # Verifica sobreposição de horários
            query = query.or_(
                f'horario_inicio.lte.{horario_fim},horario_fim.gte.{horario_inicio}'
            )
            
            result = query.execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"[ERRO] check_conflict em aulas: {e}")
            return False
    
    def cancel_aula(self, aula_id: int) -> bool:
        """Cancela uma aula."""
        result = self.update(aula_id, {'status': 'cancelada'})
        return result is not None
    
    def realize_aula(self, aula_id: int) -> bool:
        """Marca uma aula como realizada."""
        result = self.update(aula_id, {'status': 'realizada'})
        return result is not None
