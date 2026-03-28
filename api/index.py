# api/index.py - Entrypoint para Vercel Serverless Function
#
# Este arquivo é o ponto de entrada para o deploy na Vercel.
# A Vercel usa este arquivo para criar uma serverless function
# que processa todas as requisições HTTP.
#
# Estrutura esperada pela Vercel:
#   api/index.py -> deve exportar um objeto WSGI (app)

import os
import sys

# Adicionar diretório raiz ao path para imports funcionarem
# A Vercel compila o projeto em um diretório diferente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Definir ambiente de produção
os.environ.setdefault('FLASK_ENV', 'production')

# Importar e criar a aplicação Flask
from app import create_app

# Criar instância da aplicação
app = create_app('production')

# A Vercel usa a variável 'app' como handler WSGI
