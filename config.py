# config.py - Configurações do Analitcs School

import os
from dotenv import load_dotenv

load_dotenv()


def check_database_connection(db_uri):
    """
    Verifica se a conexão com o banco de dados é possível.
    
    Args:
        db_uri: URI de conexão do banco
        
    Returns:
        bool: True se a conexão for bem-sucedida
    """
    if db_uri.startswith('sqlite:///'):
        return True
        
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        result = urlparse(db_uri)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port or 5432,
            user=result.username,
            password=result.password,
            dbname=result.path[1:]
        )
        conn.close()
        return True
    except Exception as e:
        print(f"[AVISO] PostgreSQL não disponível: {e}")
        return False


def get_database_uri():
    """
    Retorna a URI do banco de dados.
    Se PostgreSQL não estiver disponível, usa SQLite como fallback.
    
    Returns:
        str: URI de conexão
    """
    pg_uri = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/analitcs_school'
    
    if check_database_connection(pg_uri):
        print("[OK] Conectado ao PostgreSQL")
        return pg_uri
    else:
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'analitcs_school.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        print(f"[OK] Usando SQLite como fallback: {sqlite_path}")
        return f'sqlite:///{sqlite_path}'


class Config:
    """Configuração base do aplicativo."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Banco de Dados
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de Arquivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'}
    
    # Sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Paginação
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuração para testes."""
    DEBUG = True
    TESTING = True
    
    def __init__(self):
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'test.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{sqlite_path}'


class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
