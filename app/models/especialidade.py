# app/models/especialidade.py - Modelo de Especialidade do Professor

from datetime import datetime
from app import db


class Especialidade(db.Model):
    """
    Modelo de Especialidade.
    
    Representa uma área de especialização que um professor pode ter.
    """
    
    __tablename__ = 'especialidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=True)
    ativa = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Especialidade {self.nome}>'


professor_especialidades = db.Table('professor_especialidades',
    db.Column('professor_id', db.Integer, db.ForeignKey('professores.id'), primary_key=True),
    db.Column('especialidade_id', db.Integer, db.ForeignKey('especialidades.id'), primary_key=True)
)


class DisponibilidadeProfessor(db.Model):
    """
    Modelo de Disponibilidade do Professor.
    
    Armazena os dias e horários disponíveis de cada professor.
    """
    
    __tablename__ = 'disponibilidade_professores'
    
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    
    # Dia da semana (0 = Segunda, 6 = Domingo)
    dia_semana = db.Column(db.Integer, nullable=False)
    
    # Horário de início e fim
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    
    # Status
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento
    professor = db.relationship('Professor', backref=db.backref('disponibilidades', lazy='dynamic'))
    
    @staticmethod
    def get_dia_label(dia_semana):
        """Retorna label do dia da semana."""
        dias = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        return dias.get(dia_semana, '')
    
    def to_dict(self) -> dict:
        """Converte a disponibilidade para dicionário."""
        return {
            'id': self.id,
            'professor_id': self.professor_id,
            'dia_semana': self.dia_semana,
            'horario_inicio': self.horario_inicio.isoformat() if self.horario_inicio else None,
            'horario_fim': self.horario_fim.isoformat() if self.horario_fim else None,
            'ativo': self.ativo
        }
    
    def __repr__(self):
        return f'<Disponibilidade Professor {self.professor_id} - {self.get_dia_label(self.dia_semana)}>'