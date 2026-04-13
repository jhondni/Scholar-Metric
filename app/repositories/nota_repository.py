"""
app/repositories/nota_repository.py - Repositório de Notas

Operações de acesso a dados para a tabela de notas via SQLAlchemy.
"""

from typing import List, Optional, Dict
from app import db
from app.models.nota import Nota


class NotaRepository:
    """Repositório para operações com notas via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as notas."""
        query = Nota.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Nota, key):
                    query = query.filter(getattr(Nota, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Nota, order_by[1:])))
            else:
                query = query.order_by(getattr(Nota, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [n.to_dict() for n in query.all()]
    
    def get_by_id(self, nota_id: int) -> Optional[Dict]:
        """Busca nota por ID."""
        nota = Nota.query.get(nota_id)
        return nota.to_dict() if nota else None
    
    def get_by_aluno(self, aluno_id: int) -> List[Dict]:
        """Busca notas de um aluno."""
        notas = Nota.query.filter_by(aluno_id=aluno_id).order_by(Nota.bimestre).all()
        return [n.to_dict() for n in notas]
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca notas de uma turma."""
        notas = Nota.query.filter_by(turma_id=turma_id).all()
        return [n.to_dict() for n in notas]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca notas por campo."""
        if hasattr(Nota, field):
            notas = Nota.query.filter(getattr(Nota, field) == value).all()
            return [n.to_dict() for n in notas]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca uma nota por campo."""
        if hasattr(Nota, field):
            nota = Nota.query.filter(getattr(Nota, field) == value).first()
            return nota.to_dict() if nota else None
        return None
    
    def get_by_aluno_and_turma(self, aluno_id: int, turma_id: int) -> List[Dict]:
        """Busca notas de um aluno em uma turma."""
        notas = Nota.query.filter_by(aluno_id=aluno_id, turma_id=turma_id).order_by(Nota.bimestre).all()
        return [n.to_dict() for n in notas]
    
    def get_by_bimestre(self, turma_id: int, bimestre: int) -> List[Dict]:
        """Busca notas por bimestre."""
        notas = Nota.query.filter_by(turma_id=turma_id, bimestre=bimestre).all()
        return [n.to_dict() for n in notas]
    
    def get_by_atividade(self, atividade_id: int) -> List[Dict]:
        """Busca notas de uma atividade."""
        notas = Nota.query.filter_by(atividade_id=atividade_id).order_by(Nota.aluno_id).all()
        return [n.to_dict() for n in notas]
    
    def get_by_aluno_atividade(self, aluno_id: int, atividade_id: int) -> Optional[Dict]:
        """Busca nota de um aluno em uma atividade específica."""
        nota = Nota.query.filter_by(aluno_id=aluno_id, atividade_id=atividade_id).first()
        return nota.to_dict() if nota else None
    
    def get_by_aluno_ano(self, aluno_id: int, ano_letivo: int) -> List[Dict]:
        """Busca notas de um aluno em um ano letivo."""
        notas = Nota.query.filter_by(aluno_id=aluno_id, ano_letivo=ano_letivo).all()
        return [n.to_dict() for n in notas]
    
    def get_by_aluno_materia(self, aluno_id: int, materia_id: int, ano_letivo: int = None) -> List[Dict]:
        """Busca notas de um aluno em uma matéria."""
        query = Nota.query.filter_by(aluno_id=aluno_id, materia_id=materia_id)
        if ano_letivo:
            query = query.filter_by(ano_letivo=ano_letivo)
        notas = query.all()
        return [n.to_dict() for n in notas]
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova nota."""
        try:
            nota = Nota()
            for key, value in data.items():
                if hasattr(nota, key):
                    setattr(nota, key, value)
            
            db.session.add(nota)
            db.session.commit()
            return nota.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, nota_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma nota existente."""
        try:
            nota = Nota.query.get(nota_id)
            if not nota:
                return None
            
            for key, value in data.items():
                if hasattr(nota, key):
                    setattr(nota, key, value)
            
            db.session.commit()
            return nota.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, nota_id: int) -> bool:
        """Deleta uma nota."""
        try:
            nota = Nota.query.get(nota_id)
            if nota:
                db.session.delete(nota)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def get_aluno_average(self, aluno_id: int, turma_id: int = None) -> float:
        """Calcula a média de notas de um aluno."""
        query = Nota.query.filter_by(aluno_id=aluno_id)
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        notas = query.all()
        if not notas:
            return 0.0
        
        total = sum(n.valor for n in notas)
        return round(total / len(notas), 2)
    
    def get_turma_average(self, turma_id: int) -> float:
        """Calcula a média geral de uma turma."""
        notas = Nota.query.filter_by(turma_id=turma_id).all()
        if not notas:
            return 0.0
        
        total = sum(n.valor for n in notas)
        return round(total / len(notas), 2)
    
    def get_aluno_stats(self, aluno_id: int, turma_id: int = None) -> Dict:
        """Calcula estatísticas completas de notas de um aluno."""
        query = Nota.query.filter_by(aluno_id=aluno_id)
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        notas = query.all()
        if not notas:
            return {'media': 0.0, 'maior': 0.0, 'menor': 0.0, 'total': 0}
        
        valores = [n.valor for n in notas]
        return {
            'media': round(sum(valores) / len(valores), 2),
            'maior': max(valores),
            'menor': min(valores),
            'total': len(valores)
        }
    
    def count(self, filters: Dict = None) -> int:
        """Conta notas."""
        query = Nota.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Nota, key):
                    query = query.filter(getattr(Nota, key) == value)
        return query.count()
    
    def exists(self, nota_id: int) -> bool:
        """Verifica se nota existe."""
        return Nota.query.get(nota_id) is not None
