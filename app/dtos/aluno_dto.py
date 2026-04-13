"""
app/dtos/aluno_dto.py - DTO de Aluno

Encapsula dados do aluno do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Aluno.
"""

from datetime import datetime
from app.dtos.base_dto import BaseDTO


class AlunoDTO(BaseDTO):
    """
    Data Transfer Object para Aluno.
    
    Fornece todos os atributos e métodos esperados pelos templates,
    incluindo cálculos de frequência e média de notas.
    """
    
    def __init__(self, data: dict, repos: dict = None):
        """
        Inicializa o DTO a partir de dados do Supabase.
        
        Args:
            data: Dicionário com dados do Supabase
            repos: Dicionário com repositórios para consultas
        """
        self.id = data.get('id')
        self.nome = data.get('nome', '')
        self.matricula = data.get('matricula', '')
        self.data_nascimento = self.parse_date(data.get('data_nascimento'))
        self.cpf = data.get('cpf', '')
        self.email = data.get('email', '')
        self.telefone = data.get('telefone', '')
        self.endereco = data.get('endereco', '')
        self.nome_responsavel = data.get('nome_responsavel', '')
        self.telefone_responsavel = data.get('telefone_responsavel', '')
        self.email_responsavel = data.get('email_responsavel', '')
        self.ano_letivo = data.get('ano_letivo')
        self.status = data.get('status', 'ativo')
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._turmas = None
        self._frequencias_cache = {}
        self._notas_cache = {}
    
    def percentual_frequencia(self, turma_id: int = None) -> float:
        """
        Calcula o percentual de frequência do aluno.
        
        Args:
            turma_id: Filtrar por turma específica (opcional)
            
        Returns:
            float: Percentual de presença (0-100)
        """
        from app.repositories import FrequenciaRepository, AulaRepository
        
        freq_repo = self._repos.get('frequencia') or FrequenciaRepository()
        aula_repo = self._repos.get('aula') or AulaRepository()
        
        cache_key = f'freq_{turma_id}'
        if cache_key in self._frequencias_cache:
            return self._frequencias_cache[cache_key]
        
        # Buscar frequências do aluno
        if turma_id:
            # Buscar aulas da turma
            aulas = aula_repo.get_by_turma(turma_id)
            aula_ids = [a.get('id') for a in aulas if a.get('status') != 'cancelada']
            
            if not aula_ids:
                self._frequencias_cache[cache_key] = 100.0
                return 100.0
            
            # Contar presenças
            total = len(aula_ids)
            presencas = 0
            
            for aula_id in aula_ids:
                freq = freq_repo.get_by_aluno_and_aula(self.id, aula_id)
                if freq and freq.get('presente', False):
                    presencas += 1
        else:
            # Buscar todas as frequências do aluno
            freqs = freq_repo.get_by_aluno(self.id)
            # Filtrar apenas aulas realizadas (não canceladas)
            total = 0
            presencas = 0
            
            for freq in freqs:
                aula = aula_repo.get_by_id(freq.get('aula_id'))
                if aula and aula.get('status') != 'cancelada':
                    total += 1
                    if freq.get('presente', False):
                        presencas += 1
        
        if total == 0:
            result = 100.0
        else:
            result = (presencas / total) * 100
        
        self._frequencias_cache[cache_key] = result
        return result
    
    def media_notas(self, turma_id: int = None) -> float:
        """
        Calcula a média de notas do aluno.
        
        Args:
            turma_id: Filtrar por turma específica (opcional)
            
        Returns:
            float: Média das notas
        """
        from app.repositories import NotaRepository
        
        nota_repo = self._repos.get('nota') or NotaRepository()
        
        cache_key = f'nota_{turma_id}'
        if cache_key in self._notas_cache:
            return self._notas_cache[cache_key]
        
        if turma_id:
            notas = nota_repo.get_by_aluno_and_turma(self.id, turma_id)
        else:
            notas = nota_repo.get_by_aluno(self.id)
        
        if not notas:
            result = 0.0
        else:
            total = sum(n.get('valor', 0) for n in notas)
            result = total / len(notas)
        
        self._notas_cache[cache_key] = result
        return result
    
    @property
    def turmas(self) -> list:
        """
        Retorna as turmas do aluno.
        
        Returns:
            list: Lista de TurmaDTO
        """
        if self._turmas is not None:
            return self._turmas
        
        from app.repositories import AlunoRepository, TurmaRepository
        from app.dtos.turma_dto import TurmaDTO
        
        aluno_repo = self._repos.get('aluno') or AlunoRepository()
        turma_repo = self._repos.get('turma') or TurmaRepository()
        
        self._turmas = []
        turmas_raw = aluno_repo.get_by_turma(self.id)
        
        for item in turmas_raw:
            self._turmas.append(TurmaDTO(item, self._repos))
        
        return self._turmas
    
    def __repr__(self):
        return f'<AlunoDTO {self.nome} ({self.matricula})>'
