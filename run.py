# run.py - Ponto de entrada do Analitcs School

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def print_banner():
    """Exibe banner de inicialização."""
    print("""
    ╔═══════════════════════════════════════════╗
    ║        ANALITCS SCHOOL                    ║
    ║        Sistema de Gestão Escolar          ║
    ╚═══════════════════════════════════════════╝
    """)


def main():
    """Função principal."""
    print_banner()
    
    try:
        from app import create_app
        
        # Criar aplicação
        config_name = os.environ.get('FLASK_ENV', 'development')
        print(f"[INFO] Configuração: {config_name}")
        
        app = create_app(config_name)
        
        print("[OK] Aplicação iniciada com sucesso!")
        print("[INFO] Acesse: http://localhost:5000")
        print("[INFO] Para encerrar: Ctrl+C")
        print("-" * 45)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"[ERRO] Dependência não encontrada: {e}")
        print("[DICA] Execute: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] Falha ao iniciar aplicação: {e}")
        print("[DICA] Verifique a configuração do banco de dados")
        sys.exit(1)


if __name__ == '__main__':
    main()
