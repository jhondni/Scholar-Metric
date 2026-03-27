# app/models/arquivo.py - Modelo de Arquivo

from datetime import datetime

from app import db


class Arquivo(db.Model):
    """
    Modelo de Arquivo.
    
    Gerencia uploads de materiais didáticos.
    Estrutura: Turma → Aula → Arquivos
    """
    
    __tablename__ = 'arquivos'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome_original = db.Column(db.String(255), nullable=False)
    nome_armazenado = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    tamanho = db.Column(db.Integer, nullable=False)  # em bytes
    
    # Relacionamentos
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    
    # Descrição
    descricao = db.Column(db.Text, nullable=True)
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def tamanho_formatado(self):
        """Retorna o tamanho formatado em KB ou MB."""
        if self.tamanho < 1024:
            return f'{self.tamanho} B'
        elif self.tamanho < 1024 * 1024:
            return f'{self.tamanho / 1024:.1f} KB'
        else:
            return f'{self.tamanho / (1024 * 1024):.1f} MB'
    
    def extensao(self):
        """Retorna a extensão do arquivo."""
        return self.nome_original.rsplit('.', 1)[-1].lower()
    
    def __repr__(self):
        return f'<Arquivo {self.nome_original}>'
