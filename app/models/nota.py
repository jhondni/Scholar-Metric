# app/models/nota.py - Modelo de Nota

from datetime import datetime

from app import db


class Nota(db.Model):
    """
    Modelo de Nota.
    
    Registra notas e avaliações dos alunos.
    """
    
    __tablename__ = 'notas'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=True)
    
    # Avaliação
    tipo_avaliacao = db.Column(db.String(30), nullable=False)
    # Tipos: 'prova', 'trabalho', 'exercicio', 'participacao', 'projeto'
    descricao = db.Column(db.String(200), nullable=True)
    valor = db.Column(db.Float, nullable=False)
    valor_maximo = db.Column(db.Float, default=10.0)
    peso = db.Column(db.Float, default=1.0)
    
    # Bimestre/Período
    bimestre = db.Column(db.Integer, nullable=True)
    
    # Controle
    registrado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def percentual(self):
        """Retorna o percentual de acerto."""
        return (self.valor / self.valor_maximo) * 100
    
    def __repr__(self):
        return f'<Nota Aluno:{self.aluno_id} - {self.valor}/{self.valor_maximo}>'
