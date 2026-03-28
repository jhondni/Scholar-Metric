# app.py - Entrypoint principal do Analitcs School
#
# Este arquivo serve como ponto de entrada para:
# - flask run (CLI do Flask)
# - Gunicorn / uWSGI (servidores de produção)
# - python app.py (execução direta)
#
# Mantém a arquitetura MVC intacta usando a factory function create_app()

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente ANTES de tudo
load_dotenv()

# Criar instância da aplicação usando factory pattern
from app import create_app

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# Execução direta via python app.py
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    ║        ANALITCS SCHOOL                    ║
    ║        Sistema de Gestão Escolar          ║
    ╚═══════════════════════════════════════════╝
    """)
    print(f"[INFO] Configuração: {config_name}")
    print("[OK] Aplicação iniciada com sucesso!")
    print("[INFO] Acesse: http://localhost:5000")
    print("[INFO] Para encerrar: Ctrl+C")
    print("-" * 45)
    app.run(host='0.0.0.0', port=5000, debug=True)
