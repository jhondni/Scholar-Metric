"""
app/repositories/nota_repository.py - Repositório de Notas

Operações de acesso a dados para a tabela de notas.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class NotaRepository(BaseRepository):
    """Repositório para operações com notas."""
    
    def __init__(self):
        super().__init__('notas')
    
    def get_by_aluno(self, aluno_id: int) -> List[Dict]:
        """Busca notas de um aluno."""
        return self.get_by_field('aluno_id', aluno_id)
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca notas de uma turma."""
        return self.get_by_field('turma_id', turma_id)
    
    def get_by_aluno_and_turma(self, aluno_id: int, turma_id: int) -> List[Dict]:
        """
        Busca notas de um aluno em uma turma.
        
        Args:
            aluno_id: ID do aluno
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de notas
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*')
            result = result.eq('aluno_id', aluno_id).eq('turma_id', turma_id)
            result = result.order('bimestre').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_by_aluno_and_turma: {e}")
            return []
    
    def get_by_bimestre(self, turma_id: int, bimestre: int) -> List[Dict]:
        """
        Busca notas por bimestre.
        
        Args:
            turma_id: ID da turma
            bimestre: Número do bimestre
            
        Returns:
            List[Dict]: Lista de notas
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*')
            result = result.eq('turma_id', turma_id).eq('bimestre', bimestre)
            result = result.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_by_bimestre: {e}")
            return []
    
    def get_aluno_average(self, aluno_id: int, turma_id: int = None) -> float:
        """
        Calcula a média de notas de um aluno.
        
        Args:
            aluno_id: ID do aluno
            turma_id: Filtrar por turma (opcional)
            
        Returns:
            float: Média das notas
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('valor').eq('aluno_id', aluno_id)
            
            if turma_id:
                query = query.eq('turma_id', turma_id)
            
            result = query.execute()
            notas = result.data if result.data else []
            
            if not notas:
                return 0.0
            
            total = sum(n.get('valor', 0) for n in notas)
            return round(total / len(notas), 2)
        except Exception as e:
            print(f"[ERRO] get_aluno_average: {e}")
            return 0.0
    
    def get_turma_average(self, turma_id: int) -> float:
        """
        Calcula a média geral de uma turma.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            float: Média geral da turma
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('valor').eq('turma_id', turma_id).execute()
            notas = result.data if result.data else []
            
            if not notas:
                return 0.0
            
            total = sum(n.get('valor', 0) for n in notas)
            return round(total / len(notas), 2)
        except Exception as e:
            print(f"[ERRO] get_turma_average: {e}")
            return 0.0
    
    def get_aluno_stats(self, aluno_id: int, turma_id: int = None) -> Dict:
        """
        Calcula estatísticas completas de notas de um aluno.
        
        Args:
            aluno_id: ID do aluno
            turma_id: Filtrar por turma (opcional)
            
        Returns:
            Dict: {media: float, maior: float, menor: float, total: int}
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('valor').eq('aluno_id', aluno_id)
            
            if turma_id:
                query = query.eq('turma_id', turma_id)
            
            result = query.execute()
            notas = result.data if result.data else []
            
            if not notas:
                return {'media': 0.0, 'maior': 0.0, 'menor': 0.0, 'total': 0}
            
            valores = [n.get('valor', 0) for n in notas]
            
            return {
                'media': round(sum(valores) / len(valores), 2),
                'maior': max(valores),
                'menor': min(valores),
                'total': len(valores)
            }
        except Exception as e:
            print(f"[ERRO] get_aluno_stats em notas: {e}")
            return {'media': 0.0, 'maior': 0.0, 'menor': 0.0, 'total': 0}
