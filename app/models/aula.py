# app/models/aula.py - Modelo de Aula

from datetime import datetime, timedelta

from app import db


class Aula(db.Model):
    """
    Modelo de Aula.
    
    Representa uma aula agendada no sistema.
    Suporta aulas únicas e recorrentes.
    """
    
    __tablename__ = 'aulas'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    
    # Data e horário
    data = db.Column(db.Date, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    
    # Recorrência
    recorrente = db.Column(db.Boolean, default=False)
    tipo_recorrencia = db.Column(db.String(20), nullable=True)
    # Tipos: 'semanal', 'mensal', 'bimestral', 'trimestral', 'semestral', 'anual'
    dia_semana = db.Column(db.Integer, nullable=True)  # 0=Segunda, 6=Domingo
    data_fim_recorrencia = db.Column(db.Date, nullable=True)
    aula_pai_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='agendada')
    # Status: 'agendada', 'realizada', 'cancelada'
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    frequencias = db.relationship('Frequencia', backref='aula', lazy='dynamic')
    arquivos = db.relationship('Arquivo', backref='aula', lazy='dynamic')
    aulas_filhas = db.relationship('Aula', backref=db.backref('aula_pai', remote_side=[id]), lazy='dynamic')
    
    @staticmethod
    def gerar_datas_recorrencia(data_inicio, tipo_recorrencia, data_fim):
        """
        Gera datas para aulas recorrentes.
        
        Args:
            data_inicio: Data inicial
            tipo_recorrencia: Tipo de recorrência
            data_fim: Data final
            
        Returns:
            list: Lista de datas
        """
        datas = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            datas.append(data_atual)
            
            if tipo_recorrencia == 'semanal':
                data_atual += timedelta(weeks=1)
            elif tipo_recorrencia == 'mensal':
                data_atual += timedelta(days=30)
            elif tipo_recorrencia == 'bimestral':
                data_atual += timedelta(days=60)
            elif tipo_recorrencia == 'trimestral':
                data_atual += timedelta(days=90)
            elif tipo_recorrencia == 'semestral':
                data_atual += timedelta(days=180)
            elif tipo_recorrencia == 'anual':
                data_atual += timedelta(days=365)
            else:
                break
        
        return datas
    
    def verificar_conflito(self):
        """
        Verifica se existe conflito de horário.
        
        Returns:
            bool: True se existe conflito
        """
        conflito = Aula.query.filter(
            Aula.id != self.id,
            Aula.turma_id == self.turma_id,
            Aula.data == self.data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= self.horario_inicio,
                    Aula.horario_fim > self.horario_inicio
                ),
                db.and_(
                    Aula.horario_inicio < self.horario_fim,
                    Aula.horario_fim >= self.horario_fim
                )
            )
        ).first()
        return conflito is not None
    
    def __repr__(self):
        return f'<Aula {self.materia} - {self.data}>'
