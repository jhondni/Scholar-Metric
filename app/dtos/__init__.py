"""
app/dtos/__init__.py - Data Transfer Objects do Analitcs School

DTOs que encapsulam dados do Supabase e fornecem a mesma interface
que os modelos SQLAlchemy, garantindo compatibilidade com templates.
"""

from app.dtos.usuario_dto import UsuarioDTO
from app.dtos.aluno_dto import AlunoDTO
from app.dtos.professor_dto import ProfessorDTO
from app.dtos.turma_dto import TurmaDTO
from app.dtos.aula_dto import AulaDTO
from app.dtos.materia_dto import MateriaDTO
from app.dtos.frequencia_dto import FrequenciaDTO

__all__ = [
    'UsuarioDTO',
    'AlunoDTO',
    'ProfessorDTO',
    'TurmaDTO',
    'AulaDTO',
    'MateriaDTO',
    'FrequenciaDTO',
]
