"""
app/repositories/turma_repository.py - Repositório de Turmas

Operações de acesso a dados para a tabela de turmas.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class TurmaRepository(BaseRepository):
    """Repositório para operações com turmas."""
    
    def __init__(self):
        super().__init__('turmas')
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca turma por código."""
        return self.get_one_by_field('codigo', codigo)
    
    def get_active_turmas(self) -> List[Dict]:
        """Retorna todas as turmas ativas."""
        return self.get_by_field('ativa', True)
    
    def get_by_turno(self, turno: str) -> List[Dict]:
        """Busca turmas por turno."""
        return self.get_by_field('turno', turno)
    
    def get_by_ano_letivo(self, ano: int) -> List[Dict]:
        """Busca turmas por ano letivo."""
        return self.get_by_field('ano_letivo', ano)
    
    def get_alunos(self, turma_id: int) -> List[Dict]:
        """
        Retorna os alunos de uma turma.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de alunos
        """
        try:
            client = self._get_client()
            result = client.table('alunos_turmas').select('aluno_id').eq('turma_id', turma_id).execute()
            if not result.data:
                return []
            
            aluno_ids = [r['aluno_id'] for r in result.data]
            
            alunos = []
            for aluno_id in aluno_ids:
                aluno = client.table('alunos').select('*').eq('id', aluno_id).execute()
                if aluno.data:
                    alunos.append(aluno.data[0])
            
            return alunos
        except Exception as e:
            print(f"[ERRO] get_alunos em turmas: {e}")
            return []
    
    def get_materias(self, turma_id: int) -> List[Dict]:
        """
        Retorna as matérias de uma turma com aulas_por_periodo.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de matérias com configuração
        """
        try:
            client = self._get_client()
            result = client.table('turma_materias').select('*, materias(*)').eq('turma_id', turma_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] get_materias em turmas: {e}")
            return []
    
    def get_professores(self, turma_id: int) -> List[Dict]:
        """
        Retorna os professores de uma turma.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de professores
        """
        try:
            client = self._get_client()
            result = client.table('professores_turmas').select('professor_id').eq('turma_id', turma_id).execute()
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
            print(f"[ERRO] get_professores em turmas: {e}")
            return []
    
    def associate_aluno(self, turma_id: int, aluno_id: int) -> bool:
        """Associa um aluno à turma."""
        try:
            client = self._get_client()
            client.table('alunos_turmas').upsert({
                'turma_id': turma_id,
                'aluno_id': aluno_id
            }, on_conflict='turma_id,aluno_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_aluno: {e}")
            return False
    
    def set_materia(self, turma_id: int, materia_id: int, aulas_por_periodo: int = 2) -> bool:
        """Configura uma matéria para a turma com aulas por período."""
        try:
            client = self._get_client()
            client.table('turma_materias').upsert({
                'turma_id': turma_id,
                'materia_id': materia_id,
                'aulas_por_periodo': aulas_por_periodo
            }, on_conflict='turma_id,materia_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] set_materia: {e}")
            return False
    
    def remove_materia(self, turma_id: int, materia_id: int) -> bool:
        """Remove uma matéria da turma."""
        try:
            client = self._get_client()
            client.table('turma_materias').delete().eq('turma_id', turma_id).eq('materia_id', materia_id).execute()
            return True
        except Exception as e:
            print(f"[ERRO] remove_materia: {e}")
            return False
    
    def count_alunos(self, turma_id: int) -> int:
        """Conta o número de alunos na turma."""
        try:
            client = self._get_client()
            result = client.table('alunos_turmas').select('aluno_id', count='exact').eq('turma_id', turma_id).execute()
            return result.count if result.count else 0
        except Exception as e:
            print(f"[ERRO] count_alunos: {e}")
            return 0
