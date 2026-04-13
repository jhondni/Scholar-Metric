# app/models/atividade.py - Modelo de Atividade

from datetime import datetime

from app import db


class Atividade(db.Model):
    """
    Modelo de Atividade.
    
    Representa uma atividade/avaliação escolares (prova, trabalho, exercício, etc).
    """
    
    __tablename__ = 'atividades'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data = db.Column(db.Date, nullable=False)
    
    # Relacionamentos
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    
    # Características
    tipo = db.Column(db.String(30), nullable=False, default='prova')
    # Tipos: 'prova', 'trabalho', 'exercicio', 'participacao', 'projeto', 'avaliacao'
    
    peso = db.Column(db.Float, default=1.0)
    valor_maximo = db.Column(db.Float, default=10.0)
    
    # Controle
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    notas = db.relationship('Nota', backref='atividade', lazy='dynamic')
    
    def media_notas(self):
        """Calcula a média das notas desta atividade."""
        notas = self.notas.all()
        if not notas:
            return 0.0
        return sum(n.valor for n in notas) / len(notas)
    
    def total_notas(self):
        """Retorna o total de notas lançadas."""
        return self.notas.count()
    
    def to_dict(self) -> dict:
        """Converte a atividade para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'data': self.data.isoformat() if self.data else None,
            'materia_id': self.materia_id,
            'turma_id': self.turma_id,
            'professor_id': self.professor_id,
            'tipo': self.tipo,
            'peso': self.peso,
            'valor_maximo': self.valor_maximo,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def __repr__(self):
        return f'<Atividade {self.nome}>'