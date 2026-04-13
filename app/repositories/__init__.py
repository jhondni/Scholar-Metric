"""
app/repositories/__init__.py - Repositórios do Analitcs School

Camada de abstração para acesso a dados via SQLAlchemy ORM.
"""

from app.repositories.base_repository import BaseRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.turma_repository import TurmaRepository
from app.repositories.aula_repository import AulaRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.frequencia_repository import FrequenciaRepository
from app.repositories.nota_repository import NotaRepository
from app.repositories.feriado_repository import FeriadoRepository, DiaNaoLetivoRepository
from app.repositories.escola_repository import EscolaRepository
from app.repositories.disponibilidade_repository import DisponibilidadeRepository

__all__ = [
    'BaseRepository',
    'UsuarioRepository',
    'AlunoRepository',
    'ProfessorRepository',
    'TurmaRepository',
    'AulaRepository',
    'MateriaRepository',
    'FrequenciaRepository',
    'NotaRepository',
    'FeriadoRepository',
    'DiaNaoLetivoRepository',
    'EscolaRepository',
    'DisponibilidadeRepository',
]
