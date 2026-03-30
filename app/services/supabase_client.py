"""
app/services/supabase_client.py - Cliente Supabase para Analitcs School

Este módulo inicializa e gerencia a conexão com o Supabase via REST API.
Todas as operações de banco de dados passam por esta camada.

Segurança:
    - Usa variáveis de ambiente (SUPABASE_URL, SUPABASE_ANON_KEY)
    - NUNCA expõe credenciais no código
    - A anon key é segura para uso no frontend (RLS protege os dados)

Uso:
    from app.services.supabase_client import get_supabase_client
    client = get_supabase_client()
    result = client.table('usuarios').select('*').execute()
"""

import os
from supabase import create_client, Client
from functools import lru_cache


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Retorna instância singleton do cliente Supabase.
    
    Returns:
        Client: Instância do cliente Supabase
        
    Raises:
        ValueError: Se as variáveis de ambiente não estiverem configuradas
    """
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL e SUPABASE_ANON_KEY devem estar configuradas no .env"
        )
    
    return create_client(url, key)


def test_connection() -> dict:
    """
    Testa a conexão com o Supabase.
    
    Returns:
        dict: {'success': bool, 'message': str, 'error': str|None}
    """
    try:
        client = get_supabase_client()
        # Tenta fazer uma consulta simples
        result = client.table('usuarios').select('id').limit(1).execute()
        return {
            'success': True,
            'message': 'Conexão com Supabase estabelecida com sucesso',
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'message': 'Falha na conexão com Supabase',
            'error': str(e)
        }


def is_supabase_configured() -> bool:
    """
    Verifica se o Supabase está configurado.
    
    Returns:
        bool: True se as variáveis de ambiente estiverem configuradas
    """
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')
    return bool(url and key)


def verify_required_tables() -> dict:
    """
    Verifica se todas as tabelas necessárias existem no Supabase.
    
    Returns:
        dict: {'success': bool, 'missing_tables': list, 'message': str}
    """
    required_tables = [
        'usuarios',
        'alunos',
        'professores',
        'turmas',
        'aulas',
        'frequencias',
        'notas',
        'feriados',
        'dias_nao_letivos',
        'disponibilidade_professores',
        'professores_turmas',
        'alunos_turmas',
        'professor_materias',
        'turma_materias'
    ]
    
    if not is_supabase_configured():
        return {
            'success': False,
            'missing_tables': [],
            'message': 'Supabase não configurado. Configure SUPABASE_URL e SUPABASE_ANON_KEY.'
        }
    
    try:
        client = get_supabase_client()
        missing_tables = []
        
        for table in required_tables:
            try:
                # Tenta fazer uma consulta simples na tabela
                client.table(table).select('id').limit(1).execute()
            except Exception as e:
                error_msg = str(e)
                if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
                    missing_tables.append(table)
        
        if missing_tables:
            return {
                'success': False,
                'missing_tables': missing_tables,
                'message': f'Tabelas não encontradas no Supabase: {", ".join(missing_tables)}. '
                          f'Execute o script de migração SQL correspondente.'
            }
        
        return {
            'success': True,
            'missing_tables': [],
            'message': 'Todas as tabelas necessárias estão presentes no Supabase.'
        }
    except Exception as e:
        return {
            'success': False,
            'missing_tables': [],
            'message': f'Erro ao verificar tabelas: {str(e)}'
        }
