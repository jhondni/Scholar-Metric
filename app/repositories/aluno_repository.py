"""
app/repositories/aluno_repository.py - Repositório de Alunos

Operações de acesso a dados para a tabela de alunos.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class AlunoRepository(BaseRepository):
    """Repositório para operações com alunos."""
    
    def __init__(self):
        super().__init__('alunos')
    
    def get_by_matricula(self, matricula: str) -> Optional[Dict]:
        """Busca aluno por matrícula."""
        return self.get_one_by_field('matricula', matricula)
    
    def get_by_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca aluno por CPF."""
        return self.get_one_by_field('cpf', cpf)
    
    def get_active_students(self) -> List[Dict]:
        """Retorna todos os alunos ativos."""
        return self.get_by_field('status', 'ativo')
    
    def get_by_ano_letivo(self, ano: int) -> List[Dict]:
        """Busca alunos por ano letivo."""
        return self.get_by_field('ano_letivo', ano)
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """
        Busca alunos de uma turma específica.
        
        Args:
            turma_id: ID da turma
            
        Returns:
            List[Dict]: Lista de alunos da turma
        """
        try:
            client = self._get_client()
            # Busca IDs dos alunos na tabela de associação
            result = client.table('alunos_turmas').select('aluno_id').eq('turma_id', turma_id).execute()
            if not result.data:
                return []
            
            aluno_ids = [r['aluno_id'] for r in result.data]
            
            # Busca os alunos
            alunos = []
            for aluno_id in aluno_ids:
                aluno = self.get_by_id(aluno_id)
                if aluno:
                    alunos.append(aluno)
            
            return alunos
        except Exception as e:
            print(f"[ERRO] get_by_turma em alunos: {e}")
            return []
    
    def associate_with_turma(self, aluno_id: int, turma_id: int) -> bool:
        """
        Associa um aluno a uma turma.
        
        Args:
            aluno_id: ID do aluno
            turma_id: ID da turma
            
        Returns:
            bool: True se associado com sucesso
        """
        try:
            client = self._get_client()
            client.table('alunos_turmas').upsert({
                'aluno_id': aluno_id,
                'turma_id': turma_id
            }, on_conflict='aluno_id,turma_id').execute()
            return True
        except Exception as e:
            print(f"[ERRO] associate_with_turma: {e}")
            return False
    
    def dissociate_from_turma(self, aluno_id: int, turma_id: int) -> bool:
        """
        Remove a associação de um aluno com uma turma.
        
        Args:
            aluno_id: ID do aluno
            turma_id: ID da turma
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            client = self._get_client()
            client.table('alunos_turmas').delete().eq('aluno_id', aluno_id).eq('turma_id', turma_id).execute()
            return True
        except Exception as e:
            print(f"[ERRO] dissociate_from_turma: {e}")
            return False
    
    def search(self, query: str) -> List[Dict]:
        """
        Busca alunos por nome ou matrícula.
        
        Args:
            query: Termo de busca
            
        Returns:
            List[Dict]: Lista de alunos encontrados
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*').ilike('nome', f'%{query}%').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[ERRO] search em alunos: {e}")
            return []
