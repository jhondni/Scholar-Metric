# config.py - Configurações do Analitcs School
#
# Este arquivo gerencia todas as configurações da aplicação,
# incluindo detecção automática de ambiente (local, produção, serverless).

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def is_serverless():
    """
    Detecta se a aplicação está rodando em ambiente serverless (Vercel, AWS Lambda, etc).
    
    Returns:
        bool: True se estiver em ambiente serverless
    """
    return (
        os.environ.get('VERCEL') == '1' or
        os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or
        os.environ.get('VERCEL_ENV') is not None or
        '/var/task' in os.path.abspath(__file__)  # Vercel/lambda path
    )


def is_production():
    """
    Detecta se a aplicação está em produção.
    
    Returns:
        bool: True se estiver em produção
    """
    return os.environ.get('FLASK_ENV') == 'production' or is_serverless()


def get_database_uri():
    """
    Retorna a URI do banco de dados de forma segura.
    
    Em ambiente serverless (Vercel):
    - Usa PostgreSQL das variáveis de ambiente
    - NÃO tenta testar a conexão (causa timeout)
    - NÃO usa SQLite (filesystem read-only)
    
    Em ambiente local:
    - Tenta PostgreSQL
    - Faz fallback para SQLite se PostgreSQL não disponível
    
    Returns:
        str: URI de conexão do banco de dados
    """
    # Detectar ambiente
    serverless = is_serverless()
    production = is_production()
    
    # Obter URI do banco das variáveis de ambiente
    db_uri = os.environ.get('DATABASE_URL')
    
    if serverless or production:
        # Em produção/serverless: usar variável de ambiente diretamente
        if db_uri:
            # Corrigir formato da URL se necessário (Render/Railway usam postgres://)
            if db_uri.startswith('postgres://'):
                db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
            return db_uri
        
        # Se não houver DATABASE_URL em produção, usar SQLite em /tmp
        # /tmp é o único diretório gravável em serverless
        if serverless:
            sqlite_path = '/tmp/analitcs_school.db'
            return f'sqlite:///{sqlite_path}'
        
        # Fallback para SQLite local em produção sem DATABASE_URL
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'analitcs_school.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return f'sqlite:///{sqlite_path}'
    
    # Ambiente de desenvolvimento local
    if not db_uri:
        db_uri = 'postgresql://postgres:postgres@localhost:5432/analitcs_school'
    
    # Testar conexão PostgreSQL apenas em desenvolvimento
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        result = urlparse(db_uri)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port or 5432,
            user=result.username,
            password=result.password,
            dbname=result.path[1:],
            connect_timeout=3
        )
        conn.close()
        print("[OK] Conectado ao PostgreSQL")
        return db_uri
    except Exception as e:
        print(f"[AVISO] PostgreSQL não disponível: {e}")
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'analitcs_school.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        print(f"[OK] Usando SQLite como fallback: {sqlite_path}")
        return f'sqlite:///{sqlite_path}'


class Config:
    """Configuração base do aplicativo."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Banco de Dados (obtido dinamicamente)
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    
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
    """Configuração para produção (inclui serverless)."""
    DEBUG = False
    TESTING = False
    
    # Em produção, sessão deve usar cookies assinados (não filesystem)
    SESSION_TYPE = None


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
