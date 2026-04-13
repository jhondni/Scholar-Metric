"""
app/repositories/turma_repository.py - Repositório de Turmas

Operações de acesso a dados para a tabela de turmas via SQLAlchemy.
"""

from typing import List, Optional, Dict
from sqlalchemy import func
from app import db
from app.models.turma import Turma


class TurmaRepository:
    """Repositório para operações com turmas via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as turmas."""
        query = Turma.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Turma, key):
                    query = query.filter(getattr(Turma, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Turma, order_by[1:])))
            else:
                query = query.order_by(getattr(Turma, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [t.to_dict() for t in query.all()]
    
    def get_by_id(self, turma_id: int) -> Optional[Dict]:
        """Busca turma por ID."""
        turma = Turma.query.get(turma_id)
        return turma.to_dict() if turma else None
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca turma por código."""
        turma = Turma.query.filter_by(codigo=codigo).first()
        return turma.to_dict() if turma else None
    
    def get_active_turmas(self) -> List[Dict]:
        """Retorna todas as turmas ativas."""
        turmas = Turma.query.filter_by(ativa=True).all()
        return [t.to_dict() for t in turmas]
    
    def get_by_turno(self, turno: str) -> List[Dict]:
        """Busca turmas por turno."""
        turmas = Turma.query.filter_by(turno=turno).all()
        return [t.to_dict() for t in turmas]
    
    def get_by_ano_letivo(self, ano: int) -> List[Dict]:
        """Busca turmas por ano letivo."""
        turmas = Turma.query.filter_by(ano_letivo=ano).all()
        return [t.to_dict() for t in turmas]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca turmas por campo."""
        if hasattr(Turma, field):
            turmas = Turma.query.filter(getattr(Turma, field) == value).all()
            return [t.to_dict() for t in turmas]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca uma turma por campo."""
        if hasattr(Turma, field):
            turma = Turma.query.filter(getattr(Turma, field) == value).first()
            return turma.to_dict() if turma else None
        return None
    
    def get_alunos(self, turma_id: int) -> List[Dict]:
        """Retorna os alunos de uma turma."""
        turma = Turma.query.get(turma_id)
        if turma:
            return [a.to_dict() for a in turma.alunos]
        return []
    
    def get_materias(self, turma_id: int) -> List[Dict]:
        """Retorna as matérias de uma turma com aulas_por_periodo."""
        turma = Turma.query.get(turma_id)
        if turma:
            result = []
            for materia in turma.materias:
                m_dict = materia.to_dict()
                m_dict['aulas_por_periodo'] = turma.get_aulas_por_periodo(materia.id)
                result.append(m_dict)
            return result
        return []
    
    def get_professores(self, turma_id: int) -> List[Dict]:
        """Retorna os professores de uma turma."""
        turma = Turma.query.get(turma_id)
        if turma:
            return [p.to_dict() for p in turma.professores]
        return []
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova turma."""
        try:
            turma = Turma()
            for key, value in data.items():
                if hasattr(turma, key):
                    setattr(turma, key, value)
            
            db.session.add(turma)
            db.session.commit()
            return turma.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, turma_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma turma existente."""
        try:
            turma = Turma.query.get(turma_id)
            if not turma:
                return None
            
            for key, value in data.items():
                if hasattr(turma, key):
                    setattr(turma, key, value)
            
            db.session.commit()
            return turma.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, turma_id: int) -> bool:
        """Deleta uma turma."""
        try:
            turma = Turma.query.get(turma_id)
            if turma:
                db.session.delete(turma)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def associate_aluno(self, turma_id: int, aluno_id: int) -> bool:
        """Associa um aluno à turma."""
        try:
            from app.models.aluno import Aluno
            turma = Turma.query.get(turma_id)
            aluno = Aluno.query.get(aluno_id)
            if turma and aluno and aluno not in turma.alunos:
                turma.alunos.append(aluno)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_aluno: {e}")
            return False
    
    def dissociate_aluno(self, turma_id: int, aluno_id: int) -> bool:
        """Remove associação de aluno com turma."""
        try:
            from app.models.aluno import Aluno
            turma = Turma.query.get(turma_id)
            aluno = Aluno.query.get(aluno_id)
            if turma and aluno and aluno in turma.alunos:
                turma.alunos.remove(aluno)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_aluno: {e}")
            return False
    
    def set_materia(self, turma_id: int, materia_id: int, aulas_por_periodo: int = 2) -> bool:
        """Configura uma matéria para a turma com aulas por período."""
        try:
            from app.models.materia import Materia, turma_materias
            turma = Turma.query.get(turma_id)
            materia = Materia.query.get(materia_id)
            if turma and materia:
                if materia not in turma.materias:
                    turma.materias.append(materia)
                db.session.execute(
                    turma_materias.update().where(
                        db.and_(
                            turma_materias.c.turma_id == turma_id,
                            turma_materias.c.materia_id == materia_id
                        )
                    ).values(aulas_por_periodo=aulas_por_periodo)
                )
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] set_materia: {e}")
            return False
    
    def remove_materia(self, turma_id: int, materia_id: int) -> bool:
        """Remove uma matéria da turma."""
        try:
            from app.models.materia import Materia, turma_materias
            turma = Turma.query.get(turma_id)
            materia = Materia.query.get(materia_id)
            if turma and materia and materia in turma.materias:
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
            print(f"[ERRO] remove_materia: {e}")
            return False
    
    def count_alunos(self, turma_id: int) -> int:
        """Conta o número de alunos na turma."""
        turma = Turma.query.get(turma_id)
        if turma:
            return turma.alunos.count()
        return 0
    
    def count(self, filters: Dict = None) -> int:
        """Conta turmas."""
        query = Turma.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Turma, key):
                    query = query.filter(getattr(Turma, key) == value)
        return query.count()
    
    def exists(self, turma_id: int) -> bool:
        """Verifica se turma existe."""
        return Turma.query.get(turma_id) is not None
