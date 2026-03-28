# app/models/escola.py - Modelo de Escola

import uuid
from datetime import datetime
from app import db


class Escola(db.Model):
    """
    Modelo de Escola.
    
    Representa uma instituição de ensinono sistema multi-escola.
    """
    
    __tablename__ = 'escolas'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid_hash = db.Column(db.String(36), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    
    # Período letivo
    ano_letivo_atual = db.Column(db.Integer, nullable=True)
    
    # Controle
    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    diretoras = db.relationship('Usuario', backref='escola', lazy='dynamic',
                               foreign_keys='Usuario.escola_id')
    
    def __init__(self, **kwargs):
        if 'uuid_hash' not in kwargs:
            kwargs['uuid_hash'] = str(uuid.uuid4())
        super(Escola, self).__init__(**kwargs)
    
    def get_link_convite(self):
        """Retorna link de convite para a escola."""
        return f'/escolas/convite/{self.uuid_hash}'
    
    def __repr__(self):
        return f'<Escola {self.nome}>'


class ConviteEscola(db.Model):
    """
    Modelo de Convite para Escola.
    
    Gerencia convites pendentes para professores e coordenadores.
    """
    
    __tablename__ = 'convites_escola'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid_hash = db.Column(db.String(36), unique=True, nullable=False, index=True)
    
    # Quem enviou o convite
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    convidado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Dados do convidado
    email_convidado = db.Column(db.String(120), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)
    # Tipos: 'professor', 'coordenacao'
    
    # Status
    status = db.Column(db.String(20), default='pendente')
    # Status: 'pendente', 'aceito', 'recusado', 'expirado'
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    validade_em = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    escola = db.relationship('Escola', backref=db.backref('convites', lazy='dynamic'))
    convidado_por = db.relationship('Usuario', foreign_keys=[convidado_por_id])
    
    def __init__(self, **kwargs):
        if 'uuid_hash' not in kwargs:
            kwargs['uuid_hash'] = str(uuid.uuid4())
        super(ConviteEscola, self).__init__(**kwargs)
    
    def esta_valido(self):
        """Verifica se o convite ainda é válido."""
        from datetime import timedelta
        if self.status != 'pendente':
            return False
        if self.validade_em and self.validade_em < datetime.utcnow():
            return False
        return True
    
    def aceitar(self):
        """Aceita o convite."""
        self.status = 'aceito'
    
    def recusar(self):
        """Recusa o convite."""
        self.status = 'recusado'
    
    def __repr__(self):
        return f'<Convite {self.email_convidado} - {self.escola.nome}>'