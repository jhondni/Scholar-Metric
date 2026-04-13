"""
app/repositories/atividade_repository.py - Repositório de Atividades

Operações de acesso a dados para a tabela de atividades via SQLAlchemy.
"""

from typing import List, Optional, Dict
from datetime import date
from app import db
from app.models.atividade import Atividade


class AtividadeRepository:
    """Repositório para operações com atividades via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as atividades."""
        query = Atividade.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Atividade, key):
                    query = query.filter(getattr(Atividade, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Atividade, order_by[1:])))
            else:
                query = query.order_by(getattr(Atividade, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [a.to_dict() for a in query.all()]
    
    def get_by_id(self, atividade_id: int) -> Optional[Dict]:
        """Busca atividade por ID."""
        atividade = Atividade.query.get(atividade_id)
        return atividade.to_dict() if atividade else None
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca atividades de uma turma."""
        atividades = Atividade.query.filter_by(turma_id=turma_id, ativo=True).order_by(Atividade.data.desc()).all()
        return [a.to_dict() for a in atividades]
    
    def get_by_turma_materia(self, turma_id: int, materia_id: int) -> List[Dict]:
        """Busca atividades de uma turma e matéria."""
        atividades = Atividade.query.filter_by(
            turma_id=turma_id, 
            materia_id=materia_id, 
            ativo=True
        ).order_by(Atividade.data.desc()).all()
        return [a.to_dict() for a in atividades]
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """Busca atividades de um professor."""
        atividades = Atividade.query.filter_by(professor_id=professor_id, ativo=True).order_by(Atividade.data.desc()).all()
        return [a.to_dict() for a in atividades]
    
    def get_by_date_range(self, data_inicio: date, data_fim: date, turma_id: int = None) -> List[Dict]:
        """Busca atividades em um intervalo de datas."""
        query = Atividade.query.filter(
            Atividade.data >= data_inicio,
            Atividade.data <= data_fim,
            Atividade.ativo == True
        )
        
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        return [a.to_dict() for a in query.order_by(Atividade.data).all()]
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova atividade."""
        try:
            atividade = Atividade()
            for key, value in data.items():
                if hasattr(atividade, key):
                    if key == 'data' and isinstance(value, str):
                        from datetime import datetime
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    setattr(atividade, key, value)
            
            db.session.add(atividade)
            db.session.commit()
            return atividade.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, atividade_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma atividade existente."""
        try:
            atividade = Atividade.query.get(atividade_id)
            if not atividade:
                return None
            
            for key, value in data.items():
                if hasattr(atividade, key):
                    if key == 'data' and isinstance(value, str):
                        from datetime import datetime
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    setattr(atividade, key, value)
            
            db.session.commit()
            return atividade.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, atividade_id: int) -> bool:
        """Deleta (desativa) uma atividade."""
        try:
            atividade = Atividade.query.get(atividade_id)
            if atividade:
                atividade.ativo = False
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """Conta atividades."""
        query = Atividade.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Atividade, key):
                    query = query.filter(getattr(Atividade, key) == value)
        return query.count()