"""
app/repositories/feriado_repository.py - Repositório de Feriados

Operações de acesso a dados para a tabela de feriados via SQLAlchemy.
"""

from typing import List, Optional, Dict
from datetime import date
from app import db
from app.models.feriado import Feriado
from app.models.dia_nao_letivo import DiaNaoLetivo


class FeriadoRepository:
    """Repositório para operações com feriados via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todos os feriados."""
        query = Feriado.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Feriado, key):
                    query = query.filter(getattr(Feriado, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Feriado, order_by[1:])))
            else:
                query = query.order_by(getattr(Feriado, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [f.to_dict() for f in query.all()]
    
    def get_by_id(self, feriado_id: int) -> Optional[Dict]:
        """Busca feriado por ID."""
        fer = Feriado.query.get(feriado_id)
        return fer.to_dict() if fer else None
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca feriados por tipo."""
        feriados = Feriado.query.filter_by(tipo=tipo).all()
        return [f.to_dict() for f in feriados]
    
    def get_recorrentes(self) -> List[Dict]:
        """Retorna feriados que se repetem todo ano."""
        feriados = Feriado.query.filter_by(recorrente=True).all()
        return [f.to_dict() for f in feriados]
    
    def get_by_date(self, data: date) -> Optional[Dict]:
        """Verifica se uma data é feriado."""
        fer = Feriado.query.filter_by(data=data).first()
        return fer.to_dict() if fer else None
    
    def is_feriado(self, data: date) -> bool:
        """Verifica se uma data é feriado."""
        return Feriado.query.filter_by(data=data).first() is not None
    
    def get_in_period(self, data_inicio: date, data_fim: date) -> List[Dict]:
        """Retorna feriados em um período."""
        feriados = Feriado.query.filter(
            Feriado.data >= data_inicio,
            Feriado.data <= data_fim
        ).order_by(Feriado.data).all()
        return [f.to_dict() for f in feriados]
    
    def get_upcoming(self, limit: int = 5) -> List[Dict]:
        """Retorna próximos feriados."""
        today = date.today()
        feriados = Feriado.query.filter(Feriado.data >= today).order_by(Feriado.data).limit(limit).all()
        return [f.to_dict() for f in feriados]
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria um novo feriado."""
        try:
            fer = Feriado()
            for key, value in data.items():
                if hasattr(fer, key):
                    setattr(fer, key, value)
            
            db.session.add(fer)
            db.session.commit()
            return fer.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, feriado_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um feriado existente."""
        try:
            fer = Feriado.query.get(feriado_id)
            if not fer:
                return None
            
            for key, value in data.items():
                if hasattr(fer, key):
                    setattr(fer, key, value)
            
            db.session.commit()
            return fer.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, feriado_id: int) -> bool:
        """Deleta um feriado."""
        try:
            fer = Feriado.query.get(feriado_id)
            if fer:
                db.session.delete(fer)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """Conta feriados."""
        query = Feriado.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Feriado, key):
                    query = query.filter(getattr(Feriado, key) == value)
        return query.count()


class DiaNaoLetivoRepository:
    """Repositório para operações com dias não letivos via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todos os dias não letivos."""
        query = DiaNaoLetivo.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(DiaNaoLetivo, key):
                    query = query.filter(getattr(DiaNaoLetivo, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(DiaNaoLetivo, order_by[1:])))
            else:
                query = query.order_by(getattr(DiaNaoLetivo, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [d.to_dict() for d in query.all()]
    
    def get_by_id(self, dia_id: int) -> Optional[Dict]:
        """Busca dia não letivo por ID."""
        dia = DiaNaoLetivo.query.get(dia_id)
        return dia.to_dict() if dia else None
    
    def get_by_tipo(self, tipo: str) -> List[Dict]:
        """Busca dias não letivos por tipo."""
        dias = DiaNaoLetivo.query.filter_by(tipo=tipo).all()
        return [d.to_dict() for d in dias]
    
    def is_dia_nao_letivo(self, data: date) -> bool:
        """Verifica se uma data é dia não letivo."""
        dia = DiaNaoLetivo.query.filter(
            DiaNaoLetivo.data_inicio <= data,
            DiaNaoLetivo.data_fim >= data
        ).first()
        return dia is not None
    
    def get_in_period(self, data_inicio: date, data_fim: date) -> List[Dict]:
        """Retorna dias não letivos em um período."""
        dias = DiaNaoLetivo.query.filter(
            DiaNaoLetivo.data_inicio <= data_fim,
            DiaNaoLetivo.data_fim >= data_inicio
        ).order_by(DiaNaoLetivo.data_inicio).all()
        return [d.to_dict() for d in dias]
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria um novo dia não letivo."""
        try:
            dia = DiaNaoLetivo()
            for key, value in data.items():
                if hasattr(dia, key):
                    setattr(dia, key, value)
            
            db.session.add(dia)
            db.session.commit()
            return dia.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, dia_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um dia não letivo existente."""
        try:
            dia = DiaNaoLetivo.query.get(dia_id)
            if not dia:
                return None
            
            for key, value in data.items():
                if hasattr(dia, key):
                    setattr(dia, key, value)
            
            db.session.commit()
            return dia.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, dia_id: int) -> bool:
        """Deleta um dia não letivo."""
        try:
            dia = DiaNaoLetivo.query.get(dia_id)
            if dia:
                db.session.delete(dia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
