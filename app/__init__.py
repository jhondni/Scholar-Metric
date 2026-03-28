# app/__init__.py - Factory da aplicação Analitcs School

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

from config import config

# Instâncias das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """
    Factory function para criar a aplicação Flask.
    
    Args:
        config_name: Nome da configuração a ser utilizada
        
    Returns:
        Instância da aplicação Flask configurada
    """
    app = Flask(__name__)
    
    # Carregar configuração
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    csrf.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    # Registrar blueprints
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
    
    # Registrar handlers de erro
    register_error_handlers(app)
    
    # Criar pasta de uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Criar tabelas do banco de dados automaticamente
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Tabelas do banco de dados criadas/verificadas")
        except Exception as e:
            print(f"[ERRO] Falha ao criar tabelas: {e}")
    
    return app


def register_error_handlers(app):
    """Registra handlers para erros HTTP."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
