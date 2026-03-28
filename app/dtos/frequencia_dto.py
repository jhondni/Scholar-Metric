"""
app/dtos/frequencia_dto.py - DTO de Frequência

Encapsula dados de frequência do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Frequência.
"""

from app.dtos.base_dto import BaseDTO


class FrequenciaDTO(BaseDTO):
    """
    Data Transfer Object para Frequência.
    
    Fornece todos os atributos esperados pelos templates.
    """
    
    def __init__(self, data: dict, repos: dict = None):
        """
        Inicializa o DTO a partir de dados do Supabase.
        
        Args:
            data: Dicionário com dados do Supabase
            repos: Dicionário com repositórios para consultas
        """
        self.id = data.get('id')
        self.aluno_id = data.get('aluno_id')
        self.aula_id = data.get('aula_id')
        self.presente = self.parse_bool(data.get('presente', True))
        self.justificativa = data.get('justificativa', '')
        self.registrado_em = self.parse_datetime(data.get('registrado_em'))
        
        # Dados do aluno (pode vir enriquecido)
        self._aluno_data = data.get('aluno')
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._aluno = None
    
    @property
    def aluno(self):
        """
        Retorna o objeto AlunoDTO associado.
        
        Returns:
            AlunoDTO ou objeto simples
        """
        if self._aluno is not None:
            return self._aluno
        
        if self._aluno_data:
            from app.dtos.aluno_dto import AlunoDTO
            if isinstance(self._aluno_data, dict):
                self._aluno = AlunoDTO(self._aluno_data, self._repos)
            else:
                self._aluno = self._aluno_data
        else:
            from app.repositories import AlunoRepository
            aluno_repo = self._repos.get('aluno') or AlunoRepository()
            aluno_data = aluno_repo.get_by_id(self.aluno_id)
            
            if aluno_data:
                from app.dtos.aluno_dto import AlunoDTO
                self._aluno = AlunoDTO(aluno_data, self._repos)
            else:
                self._aluno = type('Aluno', (), {'id': self.aluno_id, 'nome': 'N/A'})()
        
        return self._aluno
    
    def __repr__(self):
        status = 'Presente' if self.presente else 'Ausente'
        return f'<FrequenciaDTO Aluno:{self.aluno_id} - {status}>'
