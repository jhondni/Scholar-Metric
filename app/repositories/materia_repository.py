"""
app/repositories/materia_repository.py - Repositório de Matérias

Operações de acesso a dados para a tabela de matérias via SQLAlchemy.
"""

from typing import List, Optional, Dict
from app import db
from app.models.materia import Materia


class MateriaRepository:
    """Repositório para operações com matérias via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as matérias."""
        query = Materia.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Materia, key):
                    query = query.filter(getattr(Materia, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Materia, order_by[1:])))
            else:
                query = query.order_by(getattr(Materia, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [m.to_dict() for m in query.all()]
    
    def get_by_id(self, materia_id: int) -> Optional[Dict]:
        """Busca matéria por ID."""
        materia = Materia.query.get(materia_id)
        return materia.to_dict() if materia else None
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca matéria por código."""
        materia = Materia.query.filter_by(codigo=codigo).first()
        return materia.to_dict() if materia else None
    
    def get_active_materias(self) -> List[Dict]:
        """Retorna todas as matérias ativas."""
        materias = Materia.query.filter_by(ativa=True).all()
        return [m.to_dict() for m in materias]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca matérias por campo."""
        if hasattr(Materia, field):
            materias = Materia.query.filter(getattr(Materia, field) == value).all()
            return [m.to_dict() for m in materias]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca uma matéria por campo."""
        if hasattr(Materia, field):
            materia = Materia.query.filter(getattr(Materia, field) == value).first()
            return materia.to_dict() if materia else None
        return None
    
    def get_by_professor(self, professor_id: int) -> List[Dict]:
        """Busca matérias que um professor pode lecionar."""
        from app.models.professor import Professor
        professor = Professor.query.get(professor_id)
        if professor:
            return [m.to_dict() for m in professor.materias]
        return []
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca matérias de uma turma com configuração de aulas."""
        from app.models.turma import Turma
        from app.models.materia import turma_materias
        
        turma = Turma.query.get(turma_id)
        if not turma:
            return []
        
        result = []
        for materia in turma.materias:
            m_dict = materia.to_dict()
            m_dict['aulas_por_periodo'] = turma.get_aulas_por_periodo(materia.id)
            result.append(m_dict)
        return result
    
    def get_available_professors(self, materia_id: int) -> List[Dict]:
        """Busca professores disponíveis para uma matéria."""
        materia = Materia.query.get(materia_id)
        if materia:
            return [p.to_dict() for p in materia.professores]
        return []
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova matéria."""
        try:
            materia = Materia()
            for key, value in data.items():
                if hasattr(materia, key):
                    setattr(materia, key, value)
            
            db.session.add(materia)
            db.session.commit()
            return materia.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, materia_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma matéria existente."""
        try:
            materia = Materia.query.get(materia_id)
            if not materia:
                return None
            
            for key, value in data.items():
                if hasattr(materia, key):
                    setattr(materia, key, value)
            
            db.session.commit()
            return materia.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, materia_id: int) -> bool:
        """Deleta uma matéria."""
        try:
            materia = Materia.query.get(materia_id)
            if materia:
                db.session.delete(materia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def associate_with_professor(self, materia_id: int, professor_id: int) -> bool:
        """Associa uma matéria a um professor."""
        try:
            from app.models.professor import Professor
            materia = Materia.query.get(materia_id)
            professor = Professor.query.get(professor_id)
            if materia and professor and materia not in professor.materias:
                professor.materias.append(materia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_with_professor: {e}")
            return False
    
    def dissociate_professor(self, materia_id: int, professor_id: int) -> bool:
        """Remove associação de matéria com professor."""
        try:
            from app.models.professor import Professor
            materia = Materia.query.get(materia_id)
            professor = Professor.query.get(professor_id)
            if materia and professor and materia in professor.materias:
                professor.materias.remove(materia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_professor: {e}")
            return False
    
    def associate_with_turma(self, materia_id: int, turma_id: int,
                             aulas_por_periodo: int = 2) -> bool:
        """Associa uma matéria a uma turma com configuração de aulas."""
        try:
            from app.models.turma import Turma
            from app.models.materia import turma_materias
            materia = Materia.query.get(materia_id)
            turma = Turma.query.get(turma_id)
            if materia and turma:
                if materia not in turma.materias:
                    turma.materias.append(materia)
                
                db.session.execute(
                    turma_materias.insert().values(
                        turma_id=turma_id,
                        materia_id=materia_id,
                        aulas_por_periodo=aulas_por_periodo
                    ).on_conflict_do_update(
                        index_elements=['turma_id', 'materia_id'],
                        set_={'aulas_por_periodo': aulas_por_periodo}
                    )
                )
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_with_turma: {e}")
            return False
    
    def dissociate_turma(self, materia_id: int, turma_id: int) -> bool:
        """Remove associação de matéria com turma."""
        try:
            from app.models.turma import Turma
            from app.models.materia import turma_materias
            materia = Materia.query.get(materia_id)
            turma = Turma.query.get(turma_id)
            if materia and turma and materia in turma.materias:
                turma.materias.remove(materia)
                db.session.execute(
                    turma_materias.delete().where(
                        db.and_(
                            turma_materias.c.turma_id == turma_id,
                            turma_materias.c.materia_id == materia_id
                        )
                    )
                )
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_turma: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """Conta matérias."""
        query = Materia.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Materia, key):
                    query = query.filter(getattr(Materia, key) == value)
        return query.count()
    
    def exists(self, materia_id: int) -> bool:
        """Verifica se matéria existe."""
        return Materia.query.get(materia_id) is not None
