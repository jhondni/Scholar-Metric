"""
app/dtos/professor_dto.py - DTO de Professor

Encapsula dados do professor e fornece a mesma interface
que o modelo SQLAlchemy Professor.
"""

from datetime import datetime, time as time_class
from app.dtos.base_dto import BaseDTO


class ProfessorDTO(BaseDTO):
    """
    Data Transfer Object para Professor.
    
    Fornece todos os atributos e métodos esperados pelos templates.
    """
    
    def __init__(self, data: dict, repos: dict = None):
        """
        Inicializa o DTO a partir de dados.
        
        Args:
            data: Dicionário com dados
            repos: Dicionário com repositórios para consultas
        """
        self.id = data.get('id')
        self.usuario_id = data.get('usuario_id')
        self.registro = data.get('registro', '')
        self.especialidade = data.get('especialidade', '')
        self.formacao = data.get('formacao', '')
        self.cpf = data.get('cpf', '')
        self.telefone = data.get('telefone', '')
        self.endereco = data.get('endereco', '')
        self.ativo = self.parse_bool(data.get('ativo', True))
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        
        self._repos = repos or {}
        self._usuario = None
        self._turmas = None
        self._materias = None
        self._aulas_count = None
        self._disponibilidades = None
    
    @property
    def usuario(self):
        """Retorna o objeto UsuarioDTO associado."""
        if self._usuario is not None:
            return self._usuario
        
        from app.repositories import UsuarioRepository
        from app.dtos.usuario_dto import UsuarioDTO
        
        usuario_repo = self._repos.get('usuario') or UsuarioRepository()
        usuario_data = usuario_repo.get_by_id(self.usuario_id)
        
        if usuario_data:
            self._usuario = UsuarioDTO(usuario_data)
        else:
            self._usuario = UsuarioDTO({'nome': 'N/A', 'email': 'N/A'})
        
        return self._usuario
    
    def total_aulas(self, periodo: tuple = None) -> int:
        """Retorna o total de aulas do professor."""
        from app.repositories import AulaRepository
        
        aula_repo = self._repos.get('aula') or AulaRepository()
        
        if periodo:
            aulas = aula_repo.get_by_date_range(periodo[0], periodo[1])
            aulas = [a for a in aulas if a.get('professor_id') == self.id]
        else:
            aulas = aula_repo.get_by_professor(self.id)
        
        return len(aulas)
    
    @property
    def turmas(self) -> list:
        """Retorna as turmas do professor."""
        if self._turmas is not None:
            return self._turmas
        
        from app.repositories import ProfessorRepository, TurmaRepository
        from app.dtos.turma_dto import TurmaDTO
        
        professor_repo = self._repos.get('professor') or ProfessorRepository()
        
        turmas_raw = professor_repo.get_turmas(self.id)
        self._turmas = [TurmaDTO(t, self._repos) for t in turmas_raw]
        
        return self._turmas
    
    @property
    def materias(self) -> list:
        """Retorna as matérias que o professor pode lecionar."""
        if self._materias is not None:
            return self._materias
        
        from app.repositories import ProfessorRepository
        from app.dtos.materia_dto import MateriaDTO
        
        professor_repo = self._repos.get('professor') or ProfessorRepository()
        
        materias_raw = professor_repo.get_materias(self.id)
        self._materias = [MateriaDTO(m, self._repos) for m in materias_raw]
        
        return self._materias
    
    @property
    def disponibilidades(self) -> list:
        """Retorna as disponibilidades do professor."""
        if self._disponibilidades is not None:
            return self._disponibilidades
        
        from app.repositories import DisponibilidadeRepository
        
        disp_repo = self._repos.get('disponibilidade') or DisponibilidadeRepository()
        
        disps_raw = disp_repo.get_by_professor(self.id)
        
        class DisponibilidadeObj:
            def __init__(self, data):
                self.id = data.get('id')
                self.professor_id = data.get('professor_id')
                self.dia_semana = data.get('dia_semana')
                self.horario_inicio = self._parse_time(data.get('horario_inicio'))
                self.horario_fim = self._parse_time(data.get('horario_fim'))
                self.ativo = data.get('ativo', True)
            
            @staticmethod
            def _parse_time(value):
                """Parse time from string or return None."""
                if value is None:
                    return None
                if hasattr(value, 'strftime'):
                    return value
                from datetime import time
                if isinstance(value, str):
                    parts = value.split(':')
                    return time(int(parts[0]), int(parts[1]))
                return value
            
            @staticmethod
            def get_dia_label(dia):
                dias = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
                        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
                return dias.get(dia, '')
        
        self._disponibilidades = [DisponibilidadeObj(d) for d in disps_raw]
        
        return self._disponibilidades
    
    @staticmethod
    def _get_dia_label(dia_semana: int) -> str:
        """Retorna label do dia da semana."""
        dias = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
                3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
        return dias.get(dia_semana, '')
    
    def __repr__(self):
        return f'<ProfessorDTO {self.registro}>'
