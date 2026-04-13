# app/__init__.py - Factory da aplicação Analitcs School

import os
import sys
import traceback
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

from config import config, is_serverless

# Instâncias das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()
csrf = CSRFProtect()


def _log(message: str, level: str = "INFO"):
    """Log estruturado para debugging."""
    serverless = is_serverless()
    prefix = f"[{level}][Serverless]" if serverless else f"[{level}]"
    print(f"{prefix} {message}")


def create_app(config_name='default'):
    """
    Factory function para criar a aplicação Flask.
    
    Args:
        config_name: Nome da configuração a ser utilizada
        
    Returns:
        Instância da aplicação Flask configurada
    """
    try:
        app = Flask(__name__)
        
        # Carregar configuração
        app.config.from_object(config[config_name])
        _log(f"Configuração carregada: {config_name}")
        
        # Inicializar extensões
        db.init_app(app)
        login_manager.init_app(app)
        migrate.init_app(app, db)
        cors.init_app(app)
        csrf.init_app(app)
        _log("Extensões inicializadas")
        
        # Configurar login
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Por favor, faça login para acessar esta página.'
        login_manager.login_message_category = 'warning'
        
        # Configurar user loader para Supabase
        _setup_user_loader(login_manager)
        _log("User loader configurado")
        
        # Registrar blueprints
        _log("Registrando blueprints...")
        from app.controllers.auth_controller import auth_bp
        from app.controllers.dashboard_controller import dashboard_bp
        from app.controllers.turmas_controller import turmas_bp
        from app.controllers.alunos_controller import alunos_bp
        from app.controllers.professores_controller import professores_bp
        from app.controllers.aulas_controller import aulas_bp
        from app.controllers.calendario_controller import calendario_bp
        from app.controllers.configuracoes_controller import configuracoes_bp
        from app.controllers.analise_controller import analise_bp
        from app.controllers.materias_controller import materias_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(turmas_bp)
        app.register_blueprint(alunos_bp)
        app.register_blueprint(professores_bp)
        app.register_blueprint(aulas_bp)
        app.register_blueprint(calendario_bp)
        app.register_blueprint(configuracoes_bp)
        app.register_blueprint(analise_bp)
        app.register_blueprint(materias_bp)
        _log("Blueprints registrados com sucesso")
        
        # Registrar handlers de erro
        register_error_handlers(app)
        _log("Handlers de erro registrados")
        
        # Criar pasta de uploads (apenas se não for serverless)
        if not is_serverless():
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Criar tabelas do banco de dados (mantido para compatibilidade)
        with app.app_context():
            try:
                db.create_all()
                if not is_serverless():
                    _log("Tabelas do banco de dados criadas/verificadas", "OK")
            except Exception as e:
                if not is_serverless():
                    _log(f"Falha ao criar tabelas: {e}", "AVISO")
        
        _log("Aplicação criada com sucesso", "OK")
        return app
        
    except Exception as e:
        _log(f"ERRO FATAL ao criar aplicação: {e}", "ERRO")
        _log(f"Stack trace:\n{traceback.format_exc()}", "ERRO")
        raise


def _setup_user_loader(login_manager):
    """
    Configura o user loader do Flask-Login para usar SQLAlchemy.
    """
    @login_manager.user_loader
    def load_user(user_id):
        """Carrega usuário para a sessão do Flask-Login."""
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))


def register_error_handlers(app):
    """Registra handlers para erros HTTP."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        try:
            db.session.rollback()
        except:
            pass
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
