# app/models/feriado.py - Modelo de Feriado

from datetime import datetime

from app import db


class Feriado(db.Model):
    """
    Modelo de Feriado.
    
    Gerencia feriados nacionais, estaduais e municipais.
    Aulas não podem ser agendadas em feriados.
    """
    
    __tablename__ = 'feriados'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False, unique=True)
    tipo = db.Column(db.String(20), nullable=False, default='nacional')
    # Tipos: 'nacional', 'estadual', 'municipal'
    
    # Descrição
    descricao = db.Column(db.Text, nullable=True)
    
    # Controle
    recorrente = db.Column(db.Boolean, default=False)  # Repete todo ano
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def is_feriado(data):
        """
        Verifica se uma data é feriado.
        
        Args:
            data: Data a verificar
            
        Returns:
            bool: True se for feriado
        """
        return Feriado.query.filter_by(data=data).first() is not None
    
    @staticmethod
    def feriados_no_periodo(data_inicio, data_fim):
        """
        Retorna feriados em um período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            list: Lista de feriados
        """
        return Feriado.query.filter(
            Feriado.data >= data_inicio,
            Feriado.data <= data_fim
        ).all()
    
    def to_dict(self) -> dict:
        """Converte o feriado para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'data': self.data.isoformat() if self.data else None,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'recorrente': self.recorrente,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def __repr__(self):
        return f'<Feriado {self.nome} - {self.data}>'
