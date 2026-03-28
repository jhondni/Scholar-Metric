"""
app/repositories/professor_repository.py - Repositório de Professores

Operações de acesso a dados para a tabela de professores.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class ProfessorRepository(BaseRepository):
    """Repositório para operações com professores."""
    
    def __init__(self):
        super().__init__('professores')
    
    def get_by_registro(self, registro: str) -> Optional[Dict]:
        """Busca professor por registro profissional."""
        return self.get_one_by_field('registro', registro)
    
    def get_by_usuario_id(self, usuario_id: int) -> Optional[Dict]:
        """Busca professor pelo ID do usuário."""
        return self.get_one_by_field('usuario_id', usuario_id)
    
    def get_active_professors(self) -> List[Dict]:
        """Retorna todos os professores ativos."""
        return self.get_by_field('ativo', True)
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """
        Busca professores de uma turma específica.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de professores da turma
        """
        try:
            client = self._get_client()
            result = client.table('professores_turmas').select('professor_id').eq('turma_id', turma_id).execute()
            if not result.data:
                return []
            
            professor_ids = [r['professor_id'] for r in result.data]
            
            professores = []
            for prof_id in professor_ids:
                prof = self.get_by_id(prof_id)
                if prof:
                    professores.append(prof)
            
            return professores
        except Exception as e:
            print(f"[ERRO] get_by_turma em professores: {e}")
            return []
    
    def get_by_materia(self, materia_id: int) -> List[Dict]:
        """
        Busca professores que podem lecionar uma matéria.
        
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
                prof = self.get_by_id(prof_id)
                if prof:
                    professores.append(prof)
            
            return professores
        except Exception as e:
            print(f"[ERRO] get_by_materia em professores: {e}")
            return []
    
    def get_materias(self, professor_id: int) -> List[Dict]:
        """
        Retorna as matérias que um professor pode lecionar.
        
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
                materia = client.table('materias').select('*').eq('id', materia_id).execute()
                if materia.data:
                    materias.append(materia.data[0])
            
            return materias
        except Exception as e:
            print(f"[ERRO] get_materias em professores: {e}")
            return []
    
    def associate_materia(self, professor_id: int, materia_id: int) -> bool:
        """Associa um professor a uma matéria."""
        try:
            client = self._get_client()
            client.table('professor_materias').upsert({
                'professor_id': professor_id,
                'materia_id': materia_id
            }, on_conflict='professor_id,materia_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_materia: {e}")
            return False
    
    def dissociate_materia(self, professor_id: int, materia_id: int) -> bool:
        """Remove associação de professor com matéria."""
        try:
            client = self._get_client()
            client.table('professor_materias').delete().eq('professor_id', professor_id).eq('materia_id', materia_id).execute()
            return True
        except Exception as e:
            print(f"[ERRO] dissociate_materia: {e}")
            return False
    
    def associate_turma(self, professor_id: int, turma_id: int) -> bool:
        """Associa um professor a uma turma."""
        try:
            client = self._get_client()
            client.table('professores_turmas').upsert({
                'professor_id': professor_id,
                'turma_id': turma_id
            }, on_conflict='professor_id,turma_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_turma: {e}")
            return False
