# app/models/dia_nao_letivo.py - Modelo de Dia Não Letivo

from datetime import datetime

from app import db


class DiaNaoLetivo(db.Model):
    """
    Modelo de Dia Não Letivo.
    
    Gerencia dias sem atividades escolares (recesso, eventos, etc).
    Aulas não podem ser agendadas nesses dias.
    """
    
    __tablename__ = 'dias_nao_letivos'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default='recesso')
    # Tipos: 'recesso', 'evento', 'greve', 'emergencia', 'planejamento'
    
    # Descrição
    descricao = db.Column(db.Text, nullable=True)
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def is_dia_nao_letivo(data):
        """
        Verifica se uma data é dia não letivo.
        
        Args:
            data: Data a verificar
            
        Returns:
            bool: True se for dia não letivo
        """
        return DiaNaoLetivo.query.filter(
            DiaNaoLetivo.data_inicio <= data,
            DiaNaoLetivo.data_fim >= data
        ).first() is not None
    
    @staticmethod
    def dias_nao_letivos_no_periodo(data_inicio, data_fim):
        """
        Retorna dias não letivos em um período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            list: Lista de dias não letivos
        """
        return DiaNaoLetivo.query.filter(
            DiaNaoLetivo.data_inicio <= data_fim,
            DiaNaoLetivo.data_fim >= data_inicio
        ).all()
    
    def to_dict(self) -> dict:
        """Converte o dia não letivo para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def __repr__(self):
        return f'<DiaNaoLetivo {self.nome} - {self.data_inicio} a {self.data_fim}>'
