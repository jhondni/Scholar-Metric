# app/models/professor.py - Modelo de Professor

from datetime import datetime

from app import db


class Professor(db.Model):
    """
    Modelo de Professor.
    
    Representa um docente do sistema.
    Pode estar associado a múltiplas turmas e aulas.
    """
    
    __tablename__ = 'professores'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    # Informações profissionais
    registro = db.Column(db.String(20), unique=True, nullable=False, index=True)
    especialidade = db.Column(db.String(100), nullable=True)
    formacao = db.Column(db.Text, nullable=True)
    
    # Informações pessoais
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    
    # Controle
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    turmas = db.relationship('Turma', secondary='professores_turmas', backref=db.backref('professores', lazy='dynamic'))
    aulas = db.relationship('Aula', backref='professor', lazy='dynamic')
    
    def total_aulas(self, periodo=None):
        """
        Retorna o total de aulas do professor.
        
        Args:
            periodo: Filtrar por período (opcional)
            
        Returns:
            int: Número de aulas
        """
        from app.models.aula import Aula
        query = Aula.query.filter_by(professor_id=self.id)
        if periodo:
            query = query.filter(Aula.data >= periodo[0], Aula.data <= periodo[1])
        return query.count()
    
    def turmas_ativas(self):
        """Retorna as turmas ativas do professor."""
        from app.models.turma import Turma
        return Turma.query.join(Turma.professores).filter(
            Professor.id == self.id,
            Turma.ativa == True
        ).all()
    
    def __repr__(self):
        return f'<Professor {self.registro}>'


# Tabela de associação para relacionamento N:N entre professores e turmas
professores_turmas = db.Table('professores_turmas',
    db.Column('professor_id', db.Integer, db.ForeignKey('professores.id'), primary_key=True),
    db.Column('turma_id', db.Integer, db.ForeignKey('turmas.id'), primary_key=True),
    db.Column('data_associacao', db.DateTime, default=datetime.utcnow)
)
