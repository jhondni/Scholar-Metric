#!/usr/bin/env python3
"""
export_to_supabase.py - Exporta banco SQLite para SQL PostgreSQL (Supabase)

Este script lê o banco SQLite local e gera um arquivo SQL completo
compatível com PostgreSQL, pronto para ser executado no SQL Editor do Supabase.

Uso:
    python scripts/export_to_supabase.py

Saída:
    export_supabase.sql - Arquivo SQL pronto para o Supabase
"""

import os
import sys
import sqlite3
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header(title):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_step(step, message):
    """Imprime passo formatado."""
    print(f"[{step}] {message}")


def get_sqlite_connection():
    """
    Obtém conexão com o banco SQLite local.

    Returns:
        sqlite3.Connection: Conexão com o banco
    """
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'instance',
        'analitcs_school.db'
    )

    if not os.path.exists(db_path):
        print(f"[ERRO] Banco SQLite não encontrado em: {db_path}")
        print("[DICA] Execute 'python seed.py' primeiro para criar o banco local")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def sqlite_type_to_postgres(sqlite_type):
    """
    Converte tipo SQLite para tipo PostgreSQL.

    Args:
        sqlite_type: Tipo no SQLite

    Returns:
        str: Tipo correspondente no PostgreSQL
    """
    type_map = {
        'INTEGER': 'INTEGER',
        'INT': 'INTEGER',
        'TINYINT': 'SMALLINT',
        'SMALLINT': 'SMALLINT',
        'BIGINT': 'BIGINT',
        'REAL': 'DOUBLE PRECISION',
        'FLOAT': 'DOUBLE PRECISION',
        'DOUBLE': 'DOUBLE PRECISION',
        'DOUBLE PRECISION': 'DOUBLE PRECISION',
        'NUMERIC': 'NUMERIC',
        'DECIMAL': 'NUMERIC',
        'TEXT': 'TEXT',
        'VARCHAR': 'VARCHAR',
        'CHAR': 'CHAR',
        'BOOLEAN': 'BOOLEAN',
        'BOOL': 'BOOLEAN',
        'DATE': 'DATE',
        'TIME': 'TIME',
        'DATETIME': 'TIMESTAMP',
        'TIMESTAMP': 'TIMESTAMP',
        'BLOB': 'BYTEA',
    }

    # Extrair tamanho de VARCHAR(n)
    if sqlite_type.upper().startswith('VARCHAR('):
        return sqlite_type.upper()

    # Buscar tipo base
    base_type = sqlite_type.upper().split('(')[0].strip()
    return type_map.get(base_type, 'TEXT')


def escape_sql_value(value):
    """
    Escapa valor para uso em SQL INSERT.

    Args:
        value: Valor a ser escapado

    Returns:
        str: Valor formatado para SQL
    """
    if value is None:
        return 'NULL'

    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return str(value)

    if isinstance(value, str):
        # Escapar aspas simples
        escaped = value.replace("'", "''")
        # Escapar barras invertidas
        escaped = escaped.replace("\\", "\\\\")
        return f"'{escaped}'"

    # Para objetos datetime/date/time
    if hasattr(value, 'isoformat'):
        return f"'{value.isoformat()}'"

    # Fallback: converter para string
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def get_table_schema(cursor, table_name):
    """
    Obtém schema completo de uma tabela.

    Args:
        cursor: Cursor SQLite
        table_name: Nome da tabela

    Returns:
        dict: Informações da tabela
    """
    # Colunas
    cursor.execute(f'PRAGMA table_info([{table_name}])')
    columns = cursor.fetchall()

    # Foreign keys
    cursor.execute(f'PRAGMA foreign_key_list([{table_name}])')
    fks = cursor.fetchall()

    # Índices
    cursor.execute(f'PRAGMA index_list([{table_name}])')
    indexes = cursor.fetchall()

    return {
        'columns': columns,
        'foreign_keys': fks,
        'indexes': indexes
    }


def generate_create_table_sql(table_name, schema):
    """
    Gera SQL CREATE TABLE para PostgreSQL.

    Args:
        table_name: Nome da tabela
        schema: Schema da tabela (colunas, FKs)

    Returns:
        str: SQL CREATE TABLE
    """
    columns_sql = []
    primary_keys = []

    # Identificar se é tabela de junção (chave composta)
    pk_columns = [col for col in schema['columns'] if col[5]]  # col[5] = pk flag
    is_junction_table = len(pk_columns) > 1

    for col in schema['columns']:
        cid, name, dtype, notnull, default, pk = col

        # Converter tipo
        pg_type = sqlite_type_to_postgres(dtype)

        # Construir definição da coluna
        col_def = f'    {name}'

        if pk:
            if is_junction_table:
                # Tabela de junção: usar INTEGER (não SERIAL)
                col_def += f' {pg_type} NOT NULL'
                primary_keys.append(name)
            elif 'INTEGER' in dtype.upper():
                # Chave simples INTEGER: usar SERIAL
                col_def += ' SERIAL'
                primary_keys.append(name)
            else:
                col_def += f' {pg_type}'
                primary_keys.append(name)
        else:
            col_def += f' {pg_type}'

            if notnull:
                col_def += ' NOT NULL'

            if default is not None:
                # Ajustar defaults do SQLite para PostgreSQL
                default_val = str(default)
                if default_val.upper() == 'CURRENT_TIMESTAMP':
                    col_def += ' DEFAULT NOW()'
                elif default_val.upper() in ('TRUE', 'FALSE', '1', '0'):
                    col_def += f' DEFAULT {default_val}'
                else:
                    col_def += f' DEFAULT {default_val}'

        columns_sql.append(col_def)

    # Primary key constraint - SEMPRE adicionar quando há PKs
    # No PostgreSQL, SERIAL NÃO cria primary key automaticamente
    if primary_keys:
        pk_constraint = f'    PRIMARY KEY ({", ".join(primary_keys)})'
        columns_sql.append(pk_constraint)

    # Foreign keys
    for fk in schema['foreign_keys']:
        fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
        fk_constraint = f'    FOREIGN KEY ({from_col}) REFERENCES {ref_table}({to_col})'
        if on_delete == 'CASCADE':
            fk_constraint += ' ON DELETE CASCADE'
        elif on_delete == 'SET NULL':
            fk_constraint += ' ON DELETE SET NULL'
        columns_sql.append(fk_constraint)

    # Montar SQL final
    columns_str = ',\n'.join(columns_sql)

    sql = f"""-- Tabela: {table_name}
CREATE TABLE IF NOT EXISTS {table_name} (
{columns_str}
);

"""
    return sql


def generate_insert_sql(cursor, table_name):
    """
    Gera SQL INSERT para todos os registros de uma tabela.

    Args:
        cursor: Cursor SQLite
        table_name: Nome da tabela

    Returns:
        str: SQL INSERT statements
    """
    cursor.execute(f'SELECT * FROM [{table_name}]')
    rows = cursor.fetchall()

    if not rows:
        return f'-- Nenhum registro para inserir em {table_name}\n\n'

    # Obter nomes das colunas e informações
    cursor.execute(f'PRAGMA table_info([{table_name}])')
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]

    # Identificar colunas SERIAL (chave simples INTEGER PK)
    # SERIAL só deve ser usado para chaves primárias SIMPLES (não compostas)
    pk_columns = [col for col in columns_info if col[5]]  # col[5] = pk flag
    is_junction_table = len(pk_columns) > 1

    serial_cols = []
    if not is_junction_table and len(pk_columns) == 1:
        pk_col = pk_columns[0]
        if 'INTEGER' in pk_col[2].upper():  # pk_col[2] = dtype
            serial_cols.append(pk_col[1])  # pk_col[1] = name

    # Identificar colunas BOOLEAN (col[2] = dtype)
    boolean_cols = set()
    for col in columns_info:
        col_name = col[1]
        col_type = col[2].upper()
        if 'BOOLEAN' in col_type or 'BOOL' in col_type:
            boolean_cols.add(col_name)

    # Filtrar colunas SERIAL (geradas automaticamente)
    insert_columns = [c for c in column_names if c not in serial_cols]

    sql_lines = []
    sql_lines.append(f'-- Dados: {table_name} ({len(rows)} registros)')

    for row in rows:
        values = []
        for col_name in column_names:
            if col_name in serial_cols:
                continue
            col_idx = column_names.index(col_name)
            value = row[col_idx]

            # Converter valores booleanos (SQLite usa 0/1, PostgreSQL usa TRUE/FALSE)
            if col_name in boolean_cols:
                if value is None:
                    values.append('NULL')
                elif value == 1 or value is True:
                    values.append('TRUE')
                else:
                    values.append('FALSE')
            else:
                values.append(escape_sql_value(value))

        columns_str = ', '.join(insert_columns)
        values_str = ', '.join(values)

        sql_lines.append(f'INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});')

    sql_lines.append('')

    return '\n'.join(sql_lines)


def generate_reset_sequences_sql(cursor, tables):
    """
    Gera SQL para resetar sequences (SERIAL) após INSERT.

    Args:
        cursor: Cursor SQLite
        tables: Lista de tabelas

    Returns:
        str: SQL para resetar sequences
    """
    sql_lines = ['-- Resetar sequences para continuar auto-increment corretamente']

    for table in tables:
        cursor.execute(f'PRAGMA table_info([{table}])')
        columns = cursor.fetchall()

        # Verificar se tem coluna ID SERIAL (chave primária simples INTEGER)
        pk_columns = [col for col in columns if col[5]]  # col[5] = pk flag

        # Só resetar sequence se:
        # 1. Tem apenas 1 coluna PK
        # 2. Essa coluna é INTEGER
        if len(pk_columns) == 1:
            col = pk_columns[0]
            cid, name, dtype, notnull, default, pk = col
            if 'INTEGER' in dtype.upper():
                sql_lines.append(
                    f"SELECT setval('{table}_{name}_seq', COALESCE((SELECT MAX({name}) FROM {table}), 1), true);"
                )

    sql_lines.append('')
    return '\n'.join(sql_lines)


def generate_disable_enable_triggers_sql(tables):
    """
    Gera SQL para desabilitar/habilitar triggers (FK checks) durante INSERT.

    Args:
        tables: Lista de tabelas

    Returns:
        tuple: (disable_sql, enable_sql)
    """
    disable_lines = [
        '-- Desabilitar verificação de FKs temporariamente',
        'SET session_replication_role = replica;',
        ''
    ]

    enable_lines = [
        '',
        '-- Reabilitar verificação de FKs',
        'SET session_replication_role = DEFAULT;',
        ''
    ]

    return '\n'.join(disable_lines), '\n'.join(enable_lines)


def main():
    """Função principal do script de exportação."""
    print_header("EXPORTAÇÃO SQLite → PostgreSQL (Supabase)")

    # Passo 1: Conectar ao SQLite
    print_step(1, "Conectando ao SQLite...")
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    print("[OK] Conectado ao SQLite")

    # Passo 2: Obter lista de tabelas na ordem correta (dependências)
    print_step(2, "Identificando tabelas...")

    # Ordem de criação (respeitando dependências de FK)
    tables_order = [
        'usuarios',           # Sem dependências
        'materias',           # Sem dependências
        'feriados',           # Sem dependências
        'dias_nao_letivos',   # Sem dependências
        'alunos',             # Sem dependências
        'turmas',             # Sem dependências
        'professores',        # Depende de usuarios
        'alunos_turmas',      # Depende de alunos, turmas
        'professores_turmas', # Depende de professores, turmas
        'professor_materias', # Depende de professores, materias
        'turma_materias',     # Depende de turmas, materias
        'aulas',              # Depende de turmas, professores
        'frequencias',        # Depende de alunos, aulas
        'notas',              # Depende de alunos, turmas, aulas
        'arquivos',           # Depende de aulas, professores
    ]

    # Verificar quais tabelas existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    existing_tables = [t[0] for t in cursor.fetchall() if not t[0].startswith('sqlite_')]

    # Filtrar apenas tabelas que existem
    tables = [t for t in tables_order if t in existing_tables]
    # Adicionar tabelas não listadas (fallback)
    for t in existing_tables:
        if t not in tables:
            tables.append(t)

    print(f"[OK] {len(tables)} tabelas encontradas")

    # Passo 3: Coletar schemas
    print_step(3, "Coletando schemas...")
    schemas = {}
    total_records = 0

    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM [{table}]')
        count = cursor.fetchone()[0]
        total_records += count
        schemas[table] = get_table_schema(cursor, table)
        print(f"    - {table}: {count} registros")

    print(f"[OK] {total_records} registros totais")

    # Passo 4: Gerar SQL
    print_step(4, "Gerando SQL para PostgreSQL...")

    sql_parts = []

    # Cabeçalho
    sql_parts.append(f"""-- ============================================================
-- Analitcs School - Exportação para PostgreSQL (Supabase)
-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Total de tabelas: {len(tables)}
-- Total de registros: {total_records}
-- ============================================================

-- IMPORTANTE: Execute este arquivo no SQL Editor do Supabase
-- https://supabase.com/dashboard → Seu Projeto → SQL Editor

-- Verificar se está no schema correto
SET search_path TO public;

""")

    # Drop tables (para re-execução)
    sql_parts.append("-- ============================================================")
    sql_parts.append("-- LIMPAR TABELAS EXISTENTES (se necessário)")
    sql_parts.append("-- ============================================================\n")

    for table in reversed(tables):
        sql_parts.append(f'DROP TABLE IF EXISTS {table} CASCADE;')
    sql_parts.append('\n')

    # Create tables
    sql_parts.append("-- ============================================================")
    sql_parts.append("-- CRIAR TABELAS")
    sql_parts.append("-- ============================================================\n")

    for table in tables:
        sql_parts.append(generate_create_table_sql(table, schemas[table]))

    # Índices únicos
    sql_parts.append("-- ============================================================")
    sql_parts.append("-- ÍNDICES")
    sql_parts.append("-- ============================================================\n")

    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_alunos_matricula ON alunos (matricula);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_alunos_cpf ON alunos (cpf) WHERE cpf IS NOT NULL;')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios (email);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_registro ON professores (registro);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_cpf ON professores (cpf) WHERE cpf IS NOT NULL;')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_usuario_id ON professores (usuario_id);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_turmas_codigo ON turmas (codigo);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_materias_codigo ON materias (codigo);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_materias_nome ON materias (nome);')
    sql_parts.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_feriados_data ON feriados (data);')
    sql_parts.append('\n')

    # Inserir dados
    sql_parts.append("-- ============================================================")
    sql_parts.append("-- INSERIR DADOS")
    sql_parts.append("-- ============================================================\n")

    # Desabilitar triggers temporariamente
    disable_sql, enable_sql = generate_disable_enable_triggers_sql(tables)
    sql_parts.append(disable_sql)

    for table in tables:
        sql_parts.append(generate_insert_sql(cursor, table))

    # Reabilitar triggers
    sql_parts.append(enable_sql)

    # Resetar sequences
    sql_parts.append("-- ============================================================")
    sql_parts.append("-- RESETAR SEQUENCES")
    sql_parts.append("-- ============================================================\n")

    sql_parts.append(generate_reset_sequences_sql(cursor, tables))

    # Rodapé
    sql_parts.append(f"""
-- ============================================================
-- FIM DA EXPORTAÇÃO
-- Total: {total_records} registros em {len(tables)} tabelas
-- ============================================================

-- Verificar dados importados
-- SELECT 'usuarios' as tabela, COUNT(*) as registros FROM usuarios
-- UNION ALL SELECT 'alunos', COUNT(*) FROM alunos
-- UNION ALL SELECT 'professores', COUNT(*) FROM professores
-- UNION ALL SELECT 'turmas', COUNT(*) FROM turmas
-- UNION ALL SELECT 'aulas', COUNT(*) FROM aulas;
""")

    # Juntar todas as partes
    full_sql = '\n'.join(sql_parts)

    # Passo 5: Salvar arquivo
    print_step(5, "Salvando arquivo...")

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'export_supabase.sql'
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_sql)

    file_size = os.path.getsize(output_path)
    print(f"[OK] Arquivo salvo: {output_path}")
    print(f"[OK] Tamanho: {file_size / 1024:.1f} KB")

    # Passo 6: Validar
    print_step(6, "Validando SQL gerado...")

    # Contar INSERTs gerados
    insert_count = full_sql.count('INSERT INTO')
    create_count = full_sql.count('CREATE TABLE')

    print(f"[OK] {create_count} CREATE TABLE gerados")
    print(f"[OK] {insert_count} INSERT INTO gerados")

    # Resultado
    print_header("EXPORTAÇÃO CONCLUÍDA")

    print(f"""
Arquivo gerado: {output_path}
Tamanho: {file_size / 1024:.1f} KB
Tabelas: {create_count}
Registros: {insert_count}

PRÓXIMOS PASSOS:
1. Acesse https://supabase.com/dashboard
2. Selecione seu projeto
3. Vá em SQL Editor
4. Clique em "New Query"
5. Cole o conteúdo de export_supabase.sql
6. Clique em "Run"

Ou use o comando:
    cat export_supabase.sql | pbcopy  (macOS)
    cat export_supabase.sql | xclip   (Linux)
""")

    conn.close()


if __name__ == '__main__':
    main()
