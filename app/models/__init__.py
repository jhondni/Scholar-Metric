# app/models/__init__.py - Modelos do banco de dados

from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.aula import Aula
from app.models.frequencia import Frequencia
from app.models.nota import Nota
from app.models.arquivo import Arquivo
from app.models.feriado import Feriado
from app.models.dia_nao_letivo import DiaNaoLetivo
from app.models.materia import Materia
from app.models.especialidade import DisponibilidadeProfessor

__all__ = [
    'Usuario',
    'Aluno',
    'Professor',
    'Turma',
    'Aula',
    'Frequencia',
    'Nota',
    'Arquivo',
    'Feriado',
    'DiaNaoLetivo',
    'Materia',
    'DisponibilidadeProfessor'
]
