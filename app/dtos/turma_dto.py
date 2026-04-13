"""
app/dtos/turma_dto.py - DTO de Turma

Encapsula dados da turma do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Turma.
"""

from datetime import datetime
from app.dtos.base_dto import BaseDTO


class TurmaDTO(BaseDTO):
    """
    Data Transfer Object para Turma.
    
    Fornece todos os atributos e métodos esperados pelos templates.
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
        self.codigo = data.get('codigo', '')
        self.serie = data.get('serie', '')
        self.ano_letivo = data.get('ano_letivo')
        self.turno = data.get('turno', '')
        self.capacidade_maxima = data.get('capacidade_maxima', 40)
        self.descricao = data.get('descricao', '')
        self.ativa = self.parse_bool(data.get('ativa', True))
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._alunos = None
        self._materias = None
        self._professores = None
        self._aulas_por_periodo_cache = {}
    
    def total_alunos(self) -> int:
        """
        Retorna o número de alunos na turma.
        
        Returns:
            int: Número de alunos
        """
        from app.repositories import TurmaRepository
        turma_repo = self._repos.get('turma') or TurmaRepository()
        return turma_repo.count_alunos(self.id)
    
    def total_aulas(self) -> int:
        """
        Retorna o número de aulas da turma.
        
        Returns:
            int: Número de aulas
        """
        from app.repositories import AulaRepository
        aula_repo = self._repos.get('aula') or AulaRepository()
        aulas = aula_repo.get_by_turma(self.id)
        return len(aulas)
    
    def media_turma(self) -> float:
        """
        Calcula a média geral da turma.
        
        Returns:
            float: Média geral
        """
        from app.repositories import NotaRepository
        nota_repo = self._repos.get('nota') or NotaRepository()
        return nota_repo.get_turma_average(self.id)
    
    def percentual_frequencia_media(self) -> float:
        """
        Calcula o percentual médio de frequência da turma.
        
        Returns:
            float: Percentual de frequência
        """
        alunos = self.alunos
        if not alunos:
            return 0.0
        
        total = sum(a.percentual_frequencia(self.id) for a in alunos)
        return total / len(alunos)
    
    def get_aulas_por_periodo(self, materia_id: int) -> int:
        """
        Retorna a quantidade de aulas por período para uma matéria.
        
        Args:
            materia_id: ID da matéria
            
        Returns:
            int: Número de aulas por período
        """
        if materia_id in self._aulas_por_periodo_cache:
            return self._aulas_por_periodo_cache[materia_id]
        
        from app.models.turma import Turma
        from app.models.materia import turma_materias
        from app import db
        
        try:
            result = db.session.query(turma_materias.c.aulas_por_periodo).filter(
                turma_materias.c.turma_id == self.id,
                turma_materias.c.materia_id == materia_id
            ).first()
            
            value = result[0] if result else 0
            self._aulas_por_periodo_cache[materia_id] = value
            return value
        except Exception as e:
            print(f"[ERRO] TurmaDTO.get_aulas_por_periodo: {e}")
            return 0
    
    @property
    def alunos(self) -> list:
        """
        Retorna os alunos da turma.
        
        Returns:
            list: Lista de AlunoDTO
        """
        if self._alunos is not None:
            return self._alunos
        
        from app.repositories import AlunoRepository
        from app.dtos.aluno_dto import AlunoDTO
        
        aluno_repo = self._repos.get('aluno') or AlunoRepository()
        
        alunos_raw = aluno_repo.get_by_turma(self.id)
        self._alunos = [AlunoDTO(a, self._repos) for a in alunos_raw]
        
        return self._alunos
    
    @property
    def materias(self) -> list:
        """
        Retorna as matérias da turma.
        
        Returns:
            list: Lista de MateriaDTO
        """
        if self._materias is not None:
            return self._materias
        
        from app.repositories import TurmaRepository, MateriaRepository
        from app.dtos.materia_dto import MateriaDTO
        
        turma_repo = self._repos.get('turma') or TurmaRepository()
        
        materias_raw = turma_repo.get_materias(self.id)
        self._materias = []
        
        for item in materias_raw:
            # O formato pode variar: {'materias': {...}, 'aulas_por_periodo': N} ou direto
            if isinstance(item, dict):
                if 'materias' in item and isinstance(item['materias'], dict):
                    materia_data = item['materias']
                elif 'id' in item:
                    materia_data = item
                else:
                    continue
            else:
                continue
            
            if materia_data.get('id'):
                self._materias.append(MateriaDTO(materia_data, self._repos))
        
        return self._materias
    
    @property
    def professores(self) -> list:
        """
        Retorna os professores da turma.
        
        Returns:
            list: Lista de ProfessorDTO
        """
        if self._professores is not None:
            return self._professores
        
        from app.repositories import TurmaRepository, ProfessorRepository
        from app.dtos.professor_dto import ProfessorDTO
        
        turma_repo = self._repos.get('turma') or TurmaRepository()
        
        professores_raw = turma_repo.get_professores(self.id)
        self._professores = [ProfessorDTO(p, self._repos) for p in professores_raw]
        
        return self._professores
    
    def __repr__(self):
        return f'<TurmaDTO {self.nome} ({self.codigo})>'
