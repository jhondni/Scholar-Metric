# app/models/aluno.py - Modelo de Aluno

from datetime import datetime

from app import db
from app.models.nota import Nota


class Aluno(db.Model):
    """
    Modelo de Aluno.
    
    Representa um estudante matriculado no sistema.
    Pode estar associado a múltiplas turmas.
    """
    
    __tablename__ = 'alunos'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Informações pessoais
    data_nascimento = db.Column(db.Date, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    
    # Informações do responsável
    nome_responsavel = db.Column(db.String(100), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)
    email_responsavel = db.Column(db.String(120), nullable=True)
    
    # Informações acadêmicas
    ano_letivo = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='ativo')
    # Status: 'ativo', 'inativo', 'transferido', 'evadido'
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    turmas = db.relationship('Turma', secondary='alunos_turmas', backref=db.backref('alunos', lazy='dynamic'))
    frequencias = db.relationship('Frequencia', backref='aluno', lazy='dynamic')
    notas = db.relationship('Nota', backref='aluno', lazy='dynamic')
    
    def media_notas(self, turma_id=None):
        """
        Calcula a média de notas do aluno.
        
        Args:
            turma_id: Filtrar por turma específica (opcional)
            
        Returns:
            float: Média das notas
        """
        query = Nota.query.filter_by(aluno_id=self.id)
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        notas = query.all()
        if not notas:
            return 0.0
        return sum(n.valor for n in notas) / len(notas)
    
    def percentual_frequencia(self, turma_id=None):
        """
        Calcula o percentual de frequência do aluno.
        
        Args:
            turma_id: Filtrar por turma específica (opcional)
            
        Returns:
            float: Percentual de presença (0-100)
        """
        from app.models.aula import Aula
        from app.models.frequencia import Frequencia
        
        query_aula = Aula.query
        if turma_id:
            query_aula = Aula.query.filter_by(turma_id=turma_id)
        
        total_aulas = query_aula.filter(Aula.data <= datetime.utcnow().date()).count()
        if total_aulas == 0:
            return 100.0
        
        query_freq = Frequencia.query.filter_by(aluno_id=self.id, presente=True)
        if turma_id:
            query_freq = query_freq.join(Aula).filter(Aula.turma_id == turma_id)
        
        presencas = query_freq.count()
        return (presencas / total_aulas) * 100
    
    def __repr__(self):
        return f'<Aluno {self.nome} ({self.matricula})>'


# Tabela de associação para relacionamento N:N entre alunos e turmas
alunos_turmas = db.Table('alunos_turmas',
    db.Column('aluno_id', db.Integer, db.ForeignKey('alunos.id'), primary_key=True),
    db.Column('turma_id', db.Integer, db.ForeignKey('turmas.id'), primary_key=True),
    db.Column('data_matricula', db.DateTime, default=datetime.utcnow)
)
