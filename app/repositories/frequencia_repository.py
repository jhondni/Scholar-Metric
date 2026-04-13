"""
app/repositories/frequencia_repository.py - Repositório de Frequências

Operações de acesso a dados para a tabela de frequências via SQLAlchemy.
"""

from typing import List, Optional, Dict
from app import db
from app.models.frequencia import Frequencia


class FrequenciaRepository:
    """Repositório para operações com frequências via SQLAlchemy."""
    
    def __init__(self):
        pass
    
    def get_all(self, filters: Dict = None, order_by: str = None,
                limit: int = None, offset: int = None) -> List[Dict]:
        """Busca todas as frequências."""
        query = Frequencia.query
        
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Frequencia, key):
                    query = query.filter(getattr(Frequencia, key) == value)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(db.desc(getattr(Frequencia, order_by[1:])))
            else:
                query = query.order_by(getattr(Frequencia, order_by))
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return [f.to_dict() for f in query.all()]
    
    def get_by_id(self, frequencia_id: int) -> Optional[Dict]:
        """Busca frequência por ID."""
        freq = Frequencia.query.get(frequencia_id)
        return freq.to_dict() if freq else None
    
    def get_by_aula(self, aula_id: int) -> List[Dict]:
        """Busca frequências de uma aula."""
        frequencias = Frequencia.query.filter_by(aula_id=aula_id).all()
        return [f.to_dict() for f in frequencias]
    
    def get_by_aluno(self, aluno_id: int) -> List[Dict]:
        """Busca frequências de um aluno."""
        frequencias = Frequencia.query.filter_by(aluno_id=aluno_id).all()
        return [f.to_dict() for f in frequencias]
    
    def get_by_field(self, field: str, value) -> List[Dict]:
        """Busca frequências por campo."""
        if hasattr(Frequencia, field):
            frequencias = Frequencia.query.filter(getattr(Frequencia, field) == value).all()
            return [f.to_dict() for f in frequencias]
        return []
    
    def get_one_by_field(self, field: str, value) -> Optional[Dict]:
        """Busca uma frequência por campo."""
        if hasattr(Frequencia, field):
            freq = Frequencia.query.filter(getattr(Frequencia, field) == value).first()
            return freq.to_dict() if freq else None
        return None
    
    def get_by_aluno_and_aula(self, aluno_id: int, aula_id: int) -> Optional[Dict]:
        """Busca frequência específica de um aluno em uma aula."""
        freq = Frequencia.query.filter_by(aluno_id=aluno_id, aula_id=aula_id).first()
        return freq.to_dict() if freq else None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Cria uma nova frequência."""
        try:
            freq = Frequencia()
            for key, value in data.items():
                if hasattr(freq, key):
                    setattr(freq, key, value)
            
            db.session.add(freq)
            db.session.commit()
            return freq.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] create: {e}")
            return None
    
    def update(self, frequencia_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza uma frequência existente."""
        try:
            freq = Frequencia.query.get(frequencia_id)
            if not freq:
                return None
            
            for key, value in data.items():
                if hasattr(freq, key):
                    setattr(freq, key, value)
            
            db.session.commit()
            return freq.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] update: {e}")
            return None
    
    def delete(self, frequencia_id: int) -> bool:
        """Deleta uma frequência."""
        try:
            freq = Frequencia.query.get(frequencia_id)
            if freq:
                db.session.delete(freq)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] delete: {e}")
            return False
    
    def register_presence(self, aluno_id: int, aula_id: int,
                          presente: bool = True, justificativa: str = None) -> Optional[Dict]:
        """Registra presença ou ausência de um aluno."""
        existing = self.get_by_aluno_and_aula(aluno_id, aula_id)
        if existing:
            return self.update(existing['id'], {
                'presente': presente,
                'justificativa': justificativa
            })
        return self.create({
            'aluno_id': aluno_id,
            'aula_id': aula_id,
            'presente': presente,
            'justificativa': justificativa
        })
    
    def register_batch(self, aula_id: int, presencas: List[Dict]) -> int:
        """Registra frequências em lote para uma aula."""
        count = 0
        for presenca in presencas:
            result = self.register_presence(
                aluno_id=presenca['aluno_id'],
                aula_id=aula_id,
                presente=presenca.get('presente', True),
                justificativa=presenca.get('justificativa')
            )
            if result:
                count += 1
        return count
    
    def get_aluno_stats(self, aluno_id: int, turma_id: int = None) -> Dict:
        """Calcula estatísticas de frequência de um aluno."""
        query = Frequencia.query.filter_by(aluno_id=aluno_id)
        
        if turma_id:
            from app.models.aula import Aula
            query = query.join(Aula).filter(Aula.turma_id == turma_id)
        
        registros = query.all()
        total = len(registros)
        presencas = sum(1 for r in registros if r.presente)
        faltas = total - presencas
        percentual = (presencas / total * 100) if total > 0 else 100.0
        
        return {
            'total': total,
            'presencas': presencas,
            'faltas': faltas,
            'percentual': round(percentual, 1)
        }
    
    def count(self, filters: Dict = None) -> int:
        """Conta frequências."""
        query = Frequencia.query
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(Frequencia, key):
                    query = query.filter(getattr(Frequencia, key) == value)
        return query.count()
