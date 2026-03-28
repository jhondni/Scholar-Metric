"""
app/repositories/frequencia_repository.py - Repositório de Frequências

Operações de acesso a dados para a tabela de frequências.
"""

from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository


class FrequenciaRepository(BaseRepository):
    """Repositório para operações com frequências."""
    
    def __init__(self):
        super().__init__('frequencias')
    
    def get_by_aula(self, aula_id: int) -> List[Dict]:
        """Busca frequências de uma aula."""
        return self.get_by_field('aula_id', aula_id)
    
    def get_by_aluno(self, aluno_id: int) -> List[Dict]:
        """Busca frequências de um aluno."""
        return self.get_by_field('aluno_id', aluno_id)
    
    def get_by_aluno_and_aula(self, aluno_id: int, aula_id: int) -> Optional[Dict]:
        """
        Busca frequência específica de um aluno em uma aula.
        
        Args:
            aluno_id: ID do aluno
            aula_id: ID da aula
            
        Returns:
            Optional[Dict]: Frequência encontrada ou None
        """
        try:
            client = self._get_client()
            result = client.table(self.table_name).select('*')
            result = result.eq('aluno_id', aluno_id).eq('aula_id', aula_id)
            result = result.limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[ERRO] get_by_aluno_and_aula: {e}")
            return None
    
    def register_presence(self, aluno_id: int, aula_id: int, 
                          presente: bool = True, justificativa: str = None) -> Optional[Dict]:
        """
        Registra presença ou ausência de um aluno.
        
        Args:
            aluno_id: ID do aluno
            aula_id: ID da aula
            presente: Se o aluno está presente
            justificativa: Justificativa para ausência
            
        Returns:
            Optional[Dict]: Registro criado/atualizado
        """
        data = {
            'aluno_id': aluno_id,
            'aula_id': aula_id,
            'presente': presente,
            'justificativa': justificativa
        }
        
        # Tenta atualizar se já existe
        existing = self.get_by_aluno_and_aula(aluno_id, aula_id)
        if existing:
            return self.update(existing['id'], {
                'presente': presente,
                'justificativa': justificativa
            })
        
        return self.create(data)
    
    def register_batch(self, aula_id: int, presencas: List[Dict]) -> int:
        """
        Registra frequências em lote para uma aula.
        
        Args:
            aula_id: ID da aula
            presencas: Lista de {aluno_id: int, presente: bool, justificativa: str}
            
        Returns:
            int: Número de registros criados/atualizados
        """
        count = 0
        for presenca in presencas:
            result = self.register_presence(
                aluno_id=presenca['aluno_id'],
                aula_id=aula_id,
                presente=presenca.get('presente', True),
                justificativa=presenca.get('justificativa')
            )
            if result:
                count += 1
        return count
    
    def get_aluno_stats(self, aluno_id: int, turma_id: int = None) -> Dict:
        """
        Calcula estatísticas de frequência de um aluno.
        
        Args:
            aluno_id: ID do aluno
            turma_id: Filtrar por turma (opcional)
            
        Returns:
            Dict: {total: int, presencas: int, faltas: int, percentual: float}
        """
        try:
            client = self._get_client()
            query = client.table(self.table_name).select('*').eq('aluno_id', aluno_id)
            
            if turma_id:
                # Busca aulas da turma
                aulas = client.table('aulas').select('id').eq('turma_id', turma_id).execute()
                if aulas.data:
                    aula_ids = [a['id'] for a in aulas.data]
                    query = query.in_('aula_id', aula_ids)
            
            result = query.execute()
            registros = result.data if result.data else []
            
            total = len(registros)
            presencas = sum(1 for r in registros if r.get('presente'))
            faltas = total - presencas
            percentual = (presencas / total * 100) if total > 0 else 100.0
            
            return {
                'total': total,
                'presencas': presencas,
                'faltas': faltas,
                'percentual': round(percentual, 1)
            }
        except Exception as e:
            print(f"[ERRO] get_aluno_stats: {e}")
            return {'total': 0, 'presencas': 0, 'faltas': 0, 'percentual': 100.0}
