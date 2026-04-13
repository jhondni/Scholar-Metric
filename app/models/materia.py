# app/models/materia.py - Modelo de Matéria

from app import db


class Materia(db.Model):
    """
    Modelo de Matéria.
    
    Representa uma disciplina/matéria lecionada na escola.
    """
    
    __tablename__ = 'materias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=True)
    carga_horaria = db.Column(db.Integer, nullable=True)
    ativa = db.Column(db.Boolean, default=True)
    
    def to_dict(self) -> dict:
        """Converte a matéria para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'carga_horaria': self.carga_horaria,
            'ativa': self.ativa
        }
    
    def __repr__(self):
        return f'<Materia {self.nome}>'


professor_materias = db.Table('professor_materias',
    db.Column('professor_id', db.Integer, db.ForeignKey('professores.id'), primary_key=True),
    db.Column('materia_id', db.Integer, db.ForeignKey('materias.id'), primary_key=True)
)

turma_materias = db.Table('turma_materias',
    db.Column('turma_id', db.Integer, db.ForeignKey('turmas.id'), primary_key=True),
    db.Column('materia_id', db.Integer, db.ForeignKey('materias.id'), primary_key=True),
    db.Column('aulas_por_periodo', db.Integer, default=2)
)