# app/models/turma.py - Modelo de Turma

from datetime import datetime

from app import db


class Turma(db.Model):
    """
    Modelo de Turma.
    
    Representa uma turma escolar com alunos e professores associados.
    """
    
    __tablename__ = 'turmas'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Informações acadêmicas
    serie = db.Column(db.String(30), nullable=False)
    ano_letivo = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(20), nullable=False)
    # Turnos: 'manha', 'tarde', 'noite'
    
    # Capacidade
    capacidade_maxima = db.Column(db.Integer, default=40)
    
    # Descrição
    descricao = db.Column(db.Text, nullable=True)
    
    # Controle
    ativa = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    aulas = db.relationship('Aula', backref='turma', lazy='dynamic')
    materias = db.relationship('Materia', secondary='turma_materias',
                               backref=db.backref('turmas', lazy='dynamic'))
    
    def get_aulas_por_periodo(self, materia_id):
        """
        Retorna a quantidade de aulas por período para uma matéria.
        
        Args:
            materia_id: ID da matéria
            
        Returns:
            int: Número de aulas por período
        """
        from app.models.materia import turma_materias
        result = db.session.query(turma_materias.c.aulas_por_periodo).filter(
            turma_materias.c.turma_id == self.id,
            turma_materias.c.materia_id == materia_id
        ).first()
        return result[0] if result else 0
    
    def set_aulas_por_periodo(self, materia_id, aulas):
        """
        Define a quantidade de aulas por período para uma matéria.
        
        Args:
            materia_id: ID da matéria
            aulas: Número de aulas por período
        """
        from app.models.materia import turma_materias
        db.session.execute(
            turma_materias.update().where(
                db.and_(
                    turma_materias.c.turma_id == self.id,
                    turma_materias.c.materia_id == materia_id
                )
            ).values(aulas_por_periodo=aulas)
        )
    
    def total_alunos(self):
        """Retorna o número de alunos na turma."""
        return self.alunos.count()
    
    def total_aulas(self):
        """Retorna o número de aulas da turma."""
        return self.aulas.count()
    
    def media_turma(self):
        """
        Calcula a média geral da turma.
        
        Returns:
            float: Média geral
        """
        from app.models.nota import Nota
        notas = Nota.query.join(Nota.aluno).filter(
            Nota.turma_id == self.id
        ).all()
        if not notas:
            return 0.0
        return sum(n.valor for n in notas) / len(notas)
    
    def percentual_frequencia_media(self):
        """
        Calcula o percentual médio de frequência da turma.
        
        Returns:
            float: Percentual de frequência
        """
        if not self.alunos:
            return 0.0
        total = sum(a.percentual_frequencia(self.id) for a in self.alunos)
        return total / len(self.alunos)
    
    def to_dict(self) -> dict:
        """Converte a turma para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'serie': self.serie,
            'ano_letivo': self.ano_letivo,
            'turno': self.turno,
            'capacidade_maxima': self.capacidade_maxima,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def __repr__(self):
        return f'<Turma {self.nome} ({self.codigo})>'
