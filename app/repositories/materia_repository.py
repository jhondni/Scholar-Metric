"""
app/repositories/materia_repository.py - Repositório de Matérias

Operações de acesso a dados para a tabela de matérias.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class MateriaRepository(BaseRepository):
    """Repositório para operações com matérias."""
    
    def __init__(self):
        super().__init__('materias')
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca matéria por código."""
        return self.get_one_by_field('codigo', codigo)
    
    def get_active_materias(self) -> List[Dict]:
        """Retorna todas as matérias ativas."""
        return self.get_by_field('ativa', True)
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """
        Busca matérias que um professor pode lecionar.
        
        Args:
            professor_id: ID do professor
            
        Returns:
            List[Dict]: Lista de matérias
        """
        try:
            client = self._get_client()
            result = client.table('professor_materias').select('materia_id').eq('professor_id', professor_id).execute()
            if not result.data:
                return []
            
            materia_ids = [r['materia_id'] for r in result.data]
            
            materias = []
            for materia_id in materia_ids:
                materia = self.get_by_id(materia_id)
                if materia:
                    materias.append(materia)
            
            return materias
        except Exception as e:
            print(f"[ERRO] get_by_professor em materias: {e}")
            return []
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """
        Busca matérias de uma turma com configuração de aulas.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de matérias com aulas_por_periodo
        """
        try:
            client = self._get_client()
            result = client.table('turma_materias').select('*, materias(*)').eq('turma_id', turma_id).execute()
            
            materias = []
            for item in (result.data or []):
                if item.get('materias'):
                    materia = item['materias']
                    materia['aulas_por_periodo'] = item.get('aulas_por_periodo', 2)
                    materias.append(materia)
            
            return materias
        except Exception as e:
            print(f"[ERRO] get_by_turma em materias: {e}")
            return []
    
    def get_available_professors(self, materia_id: int) -> List[Dict]:
        """
        Busca professores disponíveis para uma matéria.
        
        Args:
            materia_id: ID da matéria
            
        Returns:
            List[Dict]: Lista de professores
        """
        try:
            client = self._get_client()
            result = client.table('professor_materias').select('professor_id').eq('materia_id', materia_id).execute()
            if not result.data:
                return []
            
            professor_ids = [r['professor_id'] for r in result.data]
            
            professores = []
            for prof_id in professor_ids:
                prof = client.table('professores').select('*').eq('id', prof_id).execute()
                if prof.data:
                    professores.append(prof.data[0])
            
            return professores
        except Exception as e:
            print(f"[ERRO] get_available_professors em materias: {e}")
            return []
    
    def associate_with_professor(self, materia_id: int, professor_id: int) -> bool:
        """Associa uma matéria a um professor."""
        try:
            client = self._get_client()
            client.table('professor_materias').upsert({
                'materia_id': materia_id,
                'professor_id': professor_id
            }, on_conflict='materia_id,professor_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_with_professor: {e}")
            return False
    
    def associate_with_turma(self, materia_id: int, turma_id: int, 
                             aulas_por_periodo: int = 2) -> bool:
        """Associa uma matéria a uma turma com configuração de aulas."""
        try:
            client = self._get_client()
            client.table('turma_materias').upsert({
                'materia_id': materia_id,
                'turma_id': turma_id,
                'aulas_por_periodo': aulas_por_periodo
            }, on_conflict='materia_id,turma_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_with_turma: {e}")
            return False
