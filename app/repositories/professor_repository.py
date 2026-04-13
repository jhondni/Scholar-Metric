"""
app/repositories/professor_repository.py - Repositório de Professores

Operações de acesso a dados para a tabela de professores via SQLAlchemy.
"""

from typing import List, Optional, Dict
from app import db
from app.models.professor import Professor


class ProfessorRepository:
    """Repositório para operações com professores via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todos os professores."""
        query = Professor.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Professor, key):
                    query = query.filter(getattr(Professor, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Professor, order_by[1:])))
            else:
                query = query.order_by(getattr(Professor, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [p.to_dict() for p in query.all()]
    
    def get_by_id(self, professor_id: int) -> Optional[Dict]:
        """Busca professor por ID."""
        professor = Professor.query.get(professor_id)
        return professor.to_dict() if professor else None
    
    def get_by_registro(self, registro: str) -> Optional[Dict]:
        """Busca professor por registro profissional."""
        professor = Professor.query.filter_by(registro=registro).first()
        return professor.to_dict() if professor else None
    
    def get_by_usuario_id(self, usuario_id: int) -> Optional[Dict]:
        """Busca professor pelo ID do usuário."""
        professor = Professor.query.filter_by(usuario_id=usuario_id).first()
        return professor.to_dict() if professor else None
    
    def get_by_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca professor por CPF."""
        professor = Professor.query.filter_by(cpf=cpf).first()
        return professor.to_dict() if professor else None
    
    def get_active_professors(self) -> List[Dict]:
        """Retorna todos os professores ativos."""
        professores = Professor.query.filter_by(ativo=True).all()
        return [p.to_dict() for p in professores]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca professores por campo."""
        if hasattr(Professor, field):
            professores = Professor.query.filter(getattr(Professor, field) == value).all()
            return [p.to_dict() for p in professores]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca um professor por campo."""
        if hasattr(Professor, field):
            professor = Professor.query.filter(getattr(Professor, field) == value).first()
            return professor.to_dict() if professor else None
        return None
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca professores de uma turma específica."""
        from app.models.turma import Turma
        turma = Turma.query.get(turma_id)
        if turma:
            return [p.to_dict() for p in turma.professores]
        return []
    
    def get_by_materia(self, materia_id: int) -> List[Dict]:
        """Busca professores que podem lecionar uma matéria."""
        from app.models.materia import Materia
        materia = Materia.query.get(materia_id)
        if materia:
            return [p.to_dict() for p in materia.professores]
        return []
    
    def get_materias(self, professor_id: int) -> List[Dict]:
        """Retorna as matérias que um professor pode lecionar."""
        professor = Professor.query.get(professor_id)
        if professor:
            return [m.to_dict() for m in professor.materias]
        return []
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria um novo professor."""
        try:
            professor = Professor()
            for key, value in data.items():
                if hasattr(professor, key):
                    setattr(professor, key, value)
            
            db.session.add(professor)
            db.session.commit()
            return professor.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, professor_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um professor existente."""
        try:
            professor = Professor.query.get(professor_id)
            if not professor:
                return None
            
            for key, value in data.items():
                if hasattr(professor, key):
                    setattr(professor, key, value)
            
            db.session.commit()
            return professor.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, professor_id: int) -> bool:
        """Deleta um professor."""
        try:
            professor = Professor.query.get(professor_id)
            if professor:
                db.session.delete(professor)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def associate_materia(self, professor_id: int, materia_id: int) -> bool:
        """Associa um professor a uma matéria."""
        try:
            from app.models.materia import Materia
            professor = Professor.query.get(professor_id)
            materia = Materia.query.get(materia_id)
            if professor and materia and materia not in professor.materias:
                professor.materias.append(materia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_materia: {e}")
            return False
    
    def dissociate_materia(self, professor_id: int, materia_id: int) -> bool:
        """Remove associação de professor com matéria."""
        try:
            from app.models.materia import Materia
            professor = Professor.query.get(professor_id)
            materia = Materia.query.get(materia_id)
            if professor and materia and materia in professor.materias:
                professor.materias.remove(materia)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_materia: {e}")
            return False
    
    def associate_turma(self, professor_id: int, turma_id: int) -> bool:
        """Associa um professor a uma turma."""
        try:
            from app.models.turma import Turma
            professor = Professor.query.get(professor_id)
            turma = Turma.query.get(turma_id)
            if professor and turma and turma not in professor.turmas:
                professor.turmas.append(turma)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_turma: {e}")
            return False
    
    def dissociate_turma(self, professor_id: int, turma_id: int) -> bool:
        """Remove associação de professor com turma."""
        try:
            from app.models.turma import Turma
            professor = Professor.query.get(professor_id)
            turma = Turma.query.get(turma_id)
            if professor and turma and turma in professor.turmas:
                professor.turmas.remove(turma)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_turma: {e}")
            return False
    
    def count(self, filters: Dict = None) -> int:
        """Conta professores."""
        query = Professor.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Professor, key):
                    query = query.filter(getattr(Professor, key) == value)
        return query.count()
    
    def exists(self, professor_id: int) -> bool:
        """Verifica se professor existe."""
        return Professor.query.get(professor_id) is not None
