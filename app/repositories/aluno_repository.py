"""
app/repositories/aluno_repository.py - Repositório de Alunos

Operações de acesso a dados para a tabela de alunos via SQLAlchemy.
"""

from typing import List, Optional, Dict
from app import db
from app.models.aluno import Aluno
from app.models.turma import Turma


class AlunoRepository:
    """Repositório para operações com alunos via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todos os alunos."""
        query = Aluno.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Aluno, key):
                    query = query.filter(getattr(Aluno, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Aluno, order_by[1:])))
            else:
                query = query.order_by(getattr(Aluno, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [a.to_dict() for a in query.all()]
    
    def get_by_id(self, aluno_id: int) -> Optional[Dict]:
        """Busca aluno por ID."""
        aluno = Aluno.query.get(aluno_id)
        return aluno.to_dict() if aluno else None
    
    def get_by_matricula(self, matricula: str) -> Optional[Dict]:
        """Busca aluno por matrícula."""
        aluno = Aluno.query.filter_by(matricula=matricula).first()
        return aluno.to_dict() if aluno else None
    
    def get_by_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca aluno por CPF."""
        aluno = Aluno.query.filter_by(cpf=cpf).first()
        return aluno.to_dict() if aluno else None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Busca aluno por e-mail."""
        aluno = Aluno.query.filter_by(email=email).first()
        return aluno.to_dict() if aluno else None
    
    def get_active_students(self) -> List[Dict]:
        """Retorna todos os alunos ativos."""
        alunos = Aluno.query.filter_by(status='ativo').all()
        return [a.to_dict() for a in alunos]
    
    def get_by_ano_letivo(self, ano: int) -> List[Dict]:
        """Busca alunos por ano letivo."""
        alunos = Aluno.query.filter_by(ano_letivo=ano).all()
        return [a.to_dict() for a in alunos]
    
    def get_by_turma(self, turma_id: int) -> List[Dict]:
        """Busca alunos de uma turma específica."""
        turma = Turma.query.get(turma_id)
        if turma:
            return [a.to_dict() for a in turma.alunos]
        return []
    
    def get_turmas(self, aluno_id: int) -> List[Dict]:
        """Busca turmas de um aluno específico."""
        aluno = Aluno.query.get(aluno_id)
        if aluno:
            return [t.to_dict() for t in aluno.turmas]
        return []
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca alunos por campo."""
        if hasattr(Aluno, field):
            alunos = Aluno.query.filter(getattr(Aluno, field) == value).all()
            return [a.to_dict() for a in alunos]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca um aluno por campo."""
        if hasattr(Aluno, field):
            aluno = Aluno.query.filter(getattr(Aluno, field) == value).first()
            return aluno.to_dict() if aluno else None
        return None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria um novo aluno."""
        try:
            aluno = Aluno()
            for key, value in data.items():
                if hasattr(aluno, key):
                    setattr(aluno, key, value)
            
            db.session.add(aluno)
            db.session.commit()
            return aluno.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, aluno_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um aluno existente."""
        try:
            aluno = Aluno.query.get(aluno_id)
            if not aluno:
                return None
            
            for key, value in data.items():
                if hasattr(aluno, key):
                    setattr(aluno, key, value)
            
            db.session.commit()
            return aluno.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, aluno_id: int) -> bool:
        """Deleta um aluno."""
        try:
            aluno = Aluno.query.get(aluno_id)
            if aluno:
                db.session.delete(aluno)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def associate_with_turma(self, aluno_id: int, turma_id: int) -> bool:
        """Associa um aluno a uma turma."""
        try:
            from app.models.turma import Turma
            aluno = Aluno.query.get(aluno_id)
            turma = Turma.query.get(turma_id)
            if aluno and turma:
                turma.alunos.append(aluno)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] associate_with_turma: {e}")
            return False
    
    def dissociate_from_turma(self, aluno_id: int, turma_id: int) -> bool:
        """Remove a associação de um aluno com uma turma."""
        try:
            from app.models.turma import Turma
            aluno = Aluno.query.get(aluno_id)
            turma = Turma.query.get(turma_id)
            if aluno and turma and aluno in turma.alunos:
                turma.alunos.remove(aluno)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] dissociate_from_turma: {e}")
            return False
    
    def search(self, query: str) -> List[Dict]:
        """Busca alunos por nome ou matrícula."""
        alunos = Aluno.query.filter(
            db.or_(
                Aluno.nome.ilike(f'%{query}%'),
                Aluno.matricula.ilike(f'%{query}%')
            )
        ).all()
        return [a.to_dict() for a in alunos]
    
    def count(self, filters: Dict = None) -> int:
        """Conta alunos."""
        query = Aluno.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Aluno, key):
                    query = query.filter(getattr(Aluno, key) == value)
        return query.count()
    
    def exists(self, aluno_id: int) -> bool:
        """Verifica se aluno existe."""
        return Aluno.query.get(aluno_id) is not None
