"""
app/repositories/disponibilidade_repository.py - Repositório de Disponibilidade de Professores

Operações de acesso a dados para a tabela de disponibilidade_professores via SQLAlchemy.
"""

from typing import List, Optional, Dict
from datetime import time
from app import db
from app.models.especialidade import DisponibilidadeProfessor


class DisponibilidadeRepository:
    """Repositório para operações com disponibilidade de professores via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as disponibilidades."""
        query = DisponibilidadeProfessor.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(DisponibilidadeProfessor, key):
                    query = query.filter(getattr(DisponibilidadeProfessor, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(DisponibilidadeProfessor, order_by[1:])))
            else:
                query = query.order_by(getattr(DisponibilidadeProfessor, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [d.to_dict() for d in query.all()]
    
    def get_by_id(self, disp_id: int) -> Optional[Dict]:
        """Busca disponibilidade por ID."""
        disp = DisponibilidadeProfessor.query.get(disp_id)
        return disp.to_dict() if disp else None
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """Busca disponibilidades de um professor."""
        disps = DisponibilidadeProfessor.query.filter_by(
            professor_id=professor_id, ativo=True
        ).order_by(DisponibilidadeProfessor.dia_semana).all()
        return [d.to_dict() for d in disps]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca disponibilidades por campo."""
        if hasattr(DisponibilidadeProfessor, field):
            disps = DisponibilidadeProfessor.query.filter(
                getattr(DisponibilidadeProfessor, field) == value
            ).all()
            return [d.to_dict() for d in disps]
        return []
    
    def exists_by_dia_horario(self, professor_id: int, dia_semana: int,
                              horario_inicio, horario_fim) -> bool:
        """Verifica se já existe disponibilidade para este professor, dia e horário."""
        if isinstance(horario_inicio, str):
            parts = horario_inicio.split(':')
            horario_inicio = time(int(parts[0]), int(parts[1]))
        if isinstance(horario_fim, str):
            parts = horario_fim.split(':')
            horario_fim = time(int(parts[0]), int(parts[1]))
        
        existing = DisponibilidadeProfessor.query.filter_by(
            professor_id=professor_id,
            dia_semana=dia_semana,
            horario_inicio=horario_inicio,
            horario_fim=horario_fim,
            ativo=True
        ).first()
        
        return existing is not None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova disponibilidade."""
        try:
            disp = DisponibilidadeProfessor()
            for key, value in data.items():
                if hasattr(disp, key):
                    if key in ('horario_inicio', 'horario_fim') and isinstance(value, str):
                        parts = value.split(':')
                        value = time(int(parts[0]), int(parts[1]))
                    setattr(disp, key, value)
            
            db.session.add(disp)
            db.session.commit()
            return disp.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create disponibilidade: {e}")
            return None
    
    def delete(self, disp_id: int) -> bool:
        """Deleta uma disponibilidade (soft delete - desativa)."""
        try:
            disp = DisponibilidadeProfessor.query.get(disp_id)
            if disp:
                disp.ativo = False
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete disponibilidade: {e}")
            return False
    
    def hard_delete(self, disp_id: int) -> bool:
        """Deleta uma disponibilidade permanentemente."""
        try:
            disp = DisponibilidadeProfessor.query.get(disp_id)
            if disp:
                db.session.delete(disp)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] hard_delete disponibilidade: {e}")
            return False
    
    def delete_by_professor(self, professor_id: int) -> int:
        """Remove todas as disponibilidades de um professor (soft delete)."""
        try:
            disps = DisponibilidadeProfessor.query.filter_by(
                professor_id=professor_id
            ).all()
            count = 0
            for disp in disps:
                disp.ativo = False
                count += 1
            db.session.commit()
            return count
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete_by_professor: {e}")
            return 0
