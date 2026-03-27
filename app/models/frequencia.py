# app/models/frequencia.py - Modelo de Frequência

from datetime import datetime

from app import db


class Frequencia(db.Model):
    """
    Modelo de Frequência.
    
    Registra a presença ou ausência de alunos em aulas.
    """
    
    __tablename__ = 'frequencias'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=False)
    
    # Presença
    presente = db.Column(db.Boolean, default=True)
    justificativa = db.Column(db.Text, nullable=True)
    
    # Controle
    registrado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint única
    __table_args__ = (
        db.UniqueConstraint('aluno_id', 'aula_id', name='uq_frequencia_aluno_aula'),
    )
    
    def __repr__(self):
        status = 'Presente' if self.presente else 'Ausente'
        return f'<Frequencia Aluno:{self.aluno_id} Aula:{self.aula_id} - {status}>'
