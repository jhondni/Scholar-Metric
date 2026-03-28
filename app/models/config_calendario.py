# app/models/config_calendario.py - Modelo de Configuração de Geração de Calendário

from datetime import datetime, date
from app import db


class ConfiguracaoCalendario(db.Model):
    """
    Armazena configurações da geração automática de calendário.
    
    Útil para histórico e manutenção de preferências.
    """
    
    __tablename__ = 'config_calendario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    # Período
    periodo = db.Column(db.String(20), nullable=False)
    # Opções: 'trimestral', 'semestral', 'anual'
    
    # Datas
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    
    # Turmas (IDs separados por vírgula)
    turmas_selecionadas = db.Column(db.String(500), nullable=True)
    
    # Resultados
    total_aulas_criadas = db.Column(db.Integer, default=0)
    mensagem_erro = db.Column(db.Text, nullable=True)
    
    # Controle
    gerado_em = db.Column(db.DateTime, default=datetime.utcnow)
    gerado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    @staticmethod
    def get_periodo_label(periodo: str) -> str:
        """Retorna label formatado para o período."""
        labels = {
            'trimestral': 'Trimestre',
            'semestral': 'Semestre',
            'anual': 'Ano'
        }
        return labels.get(periodo, periodo)
    
    def __repr__(self):
        return f'<ConfiguracaoCalendario {self.nome} - {self.periodo}>'