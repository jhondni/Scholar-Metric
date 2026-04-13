"""
app/repositories/aula_repository.py - Repositório de Aulas

Operações de acesso a dados para a tabela de aulas via SQLAlchemy.
"""

from typing import List, Optional, Dict
from datetime import date, datetime, time
from app import db
from app.models.aula import Aula


class AulaRepository:
    """Repositório para operações com aulas via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as aulas."""
        query = Aula.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Aula, key):
                    query = query.filter(getattr(Aula, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Aula, order_by[1:])))
            else:
                query = query.order_by(getattr(Aula, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [a.to_dict() for a in query.all()]
    
    def get_by_id(self, aula_id: int) -> Optional[Dict]:
        """Busca aula por ID."""
        aula = Aula.query.get(aula_id)
        return aula.to_dict() if aula else None
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca aulas de uma turma."""
        aulas = Aula.query.filter_by(turma_id=turma_id).all()
        return [a.to_dict() for a in aulas]
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """Busca aulas de um professor."""
        aulas = Aula.query.filter_by(professor_id=professor_id).all()
        return [a.to_dict() for a in aulas]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca aulas por campo."""
        if hasattr(Aula, field):
            aulas = Aula.query.filter(getattr(Aula, field) == value).all()
            return [a.to_dict() for a in aulas]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca uma aula por campo."""
        if hasattr(Aula, field):
            aula = Aula.query.filter(getattr(Aula, field) == value).first()
            return aula.to_dict() if aula else None
        return None
    
    def get_by_date_range(self, data_inicio: date, data_fim: date,
                          turma_id: int = None) -> List[Dict]:
        """Busca aulas em um intervalo de datas."""
        query = Aula.query.filter(
            Aula.data >= data_inicio,
            Aula.data <= data_fim
        )
        
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        aulas = query.order_by(Aula.data).all()
        return [a.to_dict() for a in aulas]
    
    def get_by_date(self, data: date, turma_id: int = None) -> List[Dict]:
        """Busca aulas de uma data específica."""
        query = Aula.query.filter_by(data=data)
        
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        aulas = query.order_by(Aula.horario_inicio).all()
        return [a.to_dict() for a in aulas]
    
    def get_upcoming(self, turma_id: int = None, limit: int = 10) -> List[Dict]:
        """Busca próximas aulas."""
        today = date.today()
        query = Aula.query.filter(Aula.data >= today)
        
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        
        aulas = query.order_by(Aula.data).limit(limit).all()
        return [a.to_dict() for a in aulas]
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova aula."""
        try:
            aula = Aula()
            for key, value in data.items():
                if hasattr(aula, key):
                    if key in ('horario_inicio', 'horario_fim') and isinstance(value, str):
                        parts = value.split(':')
                        value = time(int(parts[0]), int(parts[1]))
                    elif key == 'data' and isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    setattr(aula, key, value)
            
            db.session.add(aula)
            db.session.commit()
            return aula.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, aula_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma aula existente."""
        try:
            aula = Aula.query.get(aula_id)
            if not aula:
                return None
            
            for key, value in data.items():
                if hasattr(aula, key):
                    if key in ('horario_inicio', 'horario_fim') and isinstance(value, str):
                        parts = value.split(':')
                        value = time(int(parts[0]), int(parts[1]))
                    elif key == 'data' and isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    setattr(aula, key, value)
            
            db.session.commit()
            return aula.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, aula_id: int) -> bool:
        """Deleta uma aula."""
        try:
            aula = Aula.query.get(aula_id)
            if aula:
                db.session.delete(aula)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def check_conflict(self, turma_id: int, data: date,
                       horario_inicio: str, horario_fim: str,
                       exclude_id: int = None) -> bool:
        """Verifica se existe conflito de horário."""
        if isinstance(horario_inicio, str):
            parts = horario_inicio.split(':')
            horario_inicio = time(int(parts[0]), int(parts[1]))
        if isinstance(horario_fim, str):
            parts = horario_fim.split(':')
            horario_fim = time(int(parts[0]), int(parts[1]))
        
        query = Aula.query.filter(
            Aula.turma_id == turma_id,
            Aula.data == data,
            Aula.status != 'cancelada'
        )
        
        if exclude_id:
            query = query.filter(Aula.id != exclude_id)
        
        conflito = query.filter(
            db.or_(
                db.and_(
                    Aula.horario_inicio <= horario_inicio,
                    Aula.horario_fim > horario_inicio
                ),
                db.and_(
                    Aula.horario_inicio < horario_fim,
                    Aula.horario_fim >= horario_fim
                )
            )
        ).first()
        
        return conflito is not None
    
    def cancel_aula(self, aula_id: int) -> bool:
        """Cancela uma aula."""
        return self.update(aula_id, {'status': 'cancelada'}) is not None
    
    def realize_aula(self, aula_id: int) -> bool:
        """Marca uma aula como realizada."""
        return self.update(aula_id, {'status': 'realizada'}) is not None
    
    def count(self, filters: Dict = None) -> int:
        """Conta aulas."""
        query = Aula.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Aula, key):
                    query = query.filter(getattr(Aula, key) == value)
        return query.count()
    
    def exists(self, aula_id: int) -> bool:
        """Verifica se aula existe."""
        return Aula.query.get(aula_id) is not None
