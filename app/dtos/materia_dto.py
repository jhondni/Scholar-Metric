"""
app/dtos/materia_dto.py - DTO de Matéria

Encapsula dados da matéria do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Materia.
"""

from app.dtos.base_dto import BaseDTO


class MateriaDTO(BaseDTO):
    """
    Data Transfer Object para Matéria.
    
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
        self.descricao = data.get('descricao', '')
        self.carga_horaria = data.get('carga_horaria')
        self.ativa = self.parse_bool(data.get('ativa', True))
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._professores = None
    
    @property
    def professores(self):
        """
        Retorna os professores que podem lecionar esta matéria.
        
        Returns:
            MateriaProfessoresProxy: Proxy que simula comportamento SQLAlchemy
        """
        return MateriaProfessoresProxy(self.id, self._repos)
    
    def __repr__(self):
        return f'<MateriaDTO {self.nome}>'


class MateriaProfessoresProxy:
    """
    Proxy que simula o comportamento de relationship do SQLAlchemy
    para acessar professores de uma matéria.
    
    Permite usar: materia.professores.filter_by(ativo=True).all()
    """
    
    def __init__(self, materia_id: int, repos: dict = None):
        self.materia_id = materia_id
        self._repos = repos or {}
        self._professores = None
    
    def _load_professores(self):
        """Carrega os professores da matéria."""
        if self._professores is not None:
            return
        
        from app.repositories import MateriaRepository
        from app.dtos.professor_dto import ProfessorDTO
        
        materia_repo = self._repos.get('materia') or MateriaRepository()
        
        professores_raw = materia_repo.get_available_professors(self.materia_id)
        self._professores = [ProfessorDTO(p, self._repos) for p in professores_raw]
    
    def all(self) -> list:
        """
        Retorna todos os professores.
        
        Returns:
            list: Lista de ProfessorDTO
        """
        self._load_professores()
        return self._professores
    
    def filter_by(self, **kwargs) -> 'MateriaProfessoresProxy':
        """
        Filtra professores por atributos.
        
        Args:
            **kwargs: Filtros (ex: ativo=True)
            
        Returns:
            MateriaProfessoresProxy: Self para encadeamento
        """
        self._load_professores()
        
        if 'ativo' in kwargs:
            ativo = kwargs['ativo']
            self._professores = [p for p in self._professores if p.ativo == ativo]
        
        return self
    
    def first(self):
        """
        Retorna o primeiro professor.
        
        Returns:
            ProfessorDTO ou None
        """
        self._load_professores()
        return self._professores[0] if self._professores else None
    
    def __iter__(self):
        self._load_professores()
        return iter(self._professores)
    
    def __len__(self):
        self._load_professores()
        return len(self._professores)
    
    def __bool__(self):
        self._load_professores()
        return len(self._professores) > 0
