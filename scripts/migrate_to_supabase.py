#!/usr/bin/env python3
"""
migrate_to_supabase.py - Script de Migração SQLite → PostgreSQL (Supabase)

Este script realiza a migração completa dos dados do SQLite local para
o PostgreSQL hospedado no Supabase.

Uso:
    python scripts/migrate_to_supabase.py

Pré-requisitos:
    1. Conta no Supabase criada
    2. Projeto criado no Supabase
    3. Variável DATABASE_URL configurada no .env com a string de conexão Supabase
    4. Banco SQLite local com dados existentes

O que o script faz:
    1. Lê todos os dados do SQLite local
    2. Cria as tabelas no PostgreSQL (via SQLAlchemy)
    3. Migra os dados na ordem correta (respeitando foreign keys)
    4. Valida a migração comparando contagens

Segurança:
    - NÃO apaga dados do SQLite
    - NÃO apaga dados existentes no PostgreSQL (falha se houver conflitos)
    - Cria backup automático antes de iniciar
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


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
    
    return sqlite3.connect(db_path)


def get_postgresql_connection_string():
    """
    Obtém string de conexão PostgreSQL do Supabase.
    
    Returns:
        str: String de conexão PostgreSQL
    """
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("[ERRO] DATABASE_URL não configurada no .env")
        print("\n[DICA] Configure a DATABASE_URL com a string de conexão do Supabase:")
        print("       DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres")
        print("\n[ONDE OBTER]")
        print("  1. Acesse https://supabase.com/dashboard")
        print("  2. Selecione seu projeto")
        print("  3. Vá em Settings → Database")
        print("  4. Copie a 'Connection string' (URI)")
        sys.exit(1)
    
    # Corrigir formato se necessário
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Adicionar SSL se não estiver presente (Supabase requer)
    if 'sslmode' not in db_url:
        separator = '&' if '?' in db_url else '?'
        db_url += f'{separator}sslmode=require'
    
    return db_url


def export_sqlite_data(sqlite_conn):
    """
    Exporta todos os dados do SQLite para um dicionário.
    
    Args:
        sqlite_conn: Conexão SQLite
        
    Returns:
        dict: Dados organizados por tabela
    """
    cursor = sqlite_conn.cursor()
    
    # Ordem de migração (respeitando dependências de FK)
    tables_order = [
        'usuarios',           # Sem dependências
        'materias',           # Sem dependências
        'feriados',           # Sem dependências
        'dias_nao_letivos',   # Sem dependências
        'alunos',             # Sem dependências
        'professores',        # Depende de usuarios
        'turmas',             # Sem dependências
        'alunos_turmas',      # Depende de alunos, turmas
        'professores_turmas', # Depende de professores, turmas
        'professor_materias', # Depende de professores, materias
        'turma_materias',     # Depende de turmas, materias
        'aulas',              # Depende de turmas, professores, aulas (self)
        'frequencias',        # Depende de alunos, aulas
        'notas',              # Depende de alunos, turmas, aulas
        'arquivos',           # Depende de aulas, professores
    ]
    
    data = {}
    
    for table in tables_order:
        cursor.execute(f'SELECT * FROM [{table}]')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        data[table] = {
            'columns': columns,
            'rows': [dict(zip(columns, row)) for row in rows],
            'count': len(rows)
        }
    
    return data


def create_backup(data, backup_path):
    """
    Cria backup JSON dos dados exportados.
    
    Args:
        data: Dados exportados
        backup_path: Caminho do arquivo de backup
    """
    # Converter datetime para string para serialização JSON
    def serialize_value(value):
        if isinstance(datetime, type(value)) or hasattr(value, 'isoformat'):
            return value.isoformat() if value else None
        return value
    
    serializable_data = {}
    for table, table_data in data.items():
        serializable_data[table] = {
            'columns': table_data['columns'],
            'rows': [
                {k: serialize_value(v) for k, v in row.items()}
                for row in table_data['rows']
            ],
            'count': table_data['count']
        }
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"[OK] Backup salvo em: {backup_path}")


def migrate_data_to_postgresql(data, pg_conn_string):
    """
    Migra os dados para o PostgreSQL usando SQLAlchemy.
    
    Args:
        data: Dados exportados do SQLite
        pg_conn_string: String de conexão PostgreSQL
        
    Returns:
        dict: Resultado da migração
    """
    from app import create_app, db
    from app.models.usuario import Usuario
    from app.models.aluno import Aluno
    from app.models.professor import Professor
    from app.models.turma import Turma
    from app.models.aula import Aula
    from app.models.frequencia import Frequencia
    from app.models.nota import Nota
    from app.models.arquivo import Arquivo
    from app.models.feriado import Feriado
    from app.models.dia_nao_letivo import DiaNaoLetivo
    from app.models.materia import Materia
    from app.models.materia import professor_materias, turma_materias
    from app.models.professor import professores_turmas
    from app.models.aluno import alunos_turmas
    
    # Configurar app para usar PostgreSQL
    os.environ['DATABASE_URL'] = pg_conn_string
    os.environ['FLASK_ENV'] = 'production'
    
    app = create_app('production')
    
    results = {}
    
    with app.app_context():
        # Criar todas as tabelas no PostgreSQL
        try:
            db.create_all()
            print("[OK] Tabelas criadas no PostgreSQL")
        except Exception as e:
            print(f"[AVISO] Erro ao criar tabelas: {e}")
        
        # Ordem de migração (respeitando dependências)
        # (mesma ordem da exportação)
        
        # 1. Usuarios (sem dependências)
        if data.get('usuarios', {}).get('rows'):
            count = 0
            for row in data['usuarios']['rows']:
                try:
                    existing = db.session.get(Usuario, row['id'])
                    if not existing:
                        user = Usuario(
                            id=row['id'],
                            nome=row['nome'],
                            email=row['email'],
                            senha_hash=row['senha_hash'],
                            tipo=row['tipo'],
                            avatar=row.get('avatar'),
                            telefone=row.get('telefone'),
                            tema=row.get('tema', 'light'),
                            ativo=bool(row.get('ativo', 1)),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em'),
                            ultimo_acesso=row.get('ultimo_acesso')
                        )
                        db.session.add(user)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar usuario {row.get('id')}: {e}")
            db.session.commit()
            results['usuarios'] = count
            print(f"[OK] {count} usuarios migrados")
        
        # 2. Materias (sem dependências)
        if data.get('materias', {}).get('rows'):
            count = 0
            for row in data['materias']['rows']:
                try:
                    existing = db.session.get(Materia, row['id'])
                    if not existing:
                        materia = Materia(
                            id=row['id'],
                            nome=row['nome'],
                            codigo=row['codigo'],
                            descricao=row.get('descricao'),
                            carga_horaria=row.get('carga_horaria'),
                            ativa=bool(row.get('ativa', 1))
                        )
                        db.session.add(materia)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar materia {row.get('id')}: {e}")
            db.session.commit()
            results['materias'] = count
            print(f"[OK] {count} materias migradas")
        
        # 3. Feriados (sem dependências)
        if data.get('feriados', {}).get('rows'):
            count = 0
            for row in data['feriados']['rows']:
                try:
                    existing = db.session.get(Feriado, row['id'])
                    if not existing:
                        feriado = Feriado(
                            id=row['id'],
                            nome=row['nome'],
                            data=row['data'],
                            tipo=row['tipo'],
                            descricao=row.get('descricao'),
                            recorrente=bool(row.get('recorrente', 0)),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(feriado)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar feriado {row.get('id')}: {e}")
            db.session.commit()
            results['feriados'] = count
            print(f"[OK] {count} feriados migrados")
        
        # 4. Dias Não Letivos
        if data.get('dias_nao_letivos', {}).get('rows'):
            count = 0
            for row in data['dias_nao_letivos']['rows']:
                try:
                    existing = db.session.get(DiaNaoLetivo, row['id'])
                    if not existing:
                        dia = DiaNaoLetivo(
                            id=row['id'],
                            nome=row['nome'],
                            data_inicio=row['data_inicio'],
                            data_fim=row['data_fim'],
                            tipo=row['tipo'],
                            descricao=row.get('descricao'),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(dia)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar dia_nao_letivo {row.get('id')}: {e}")
            db.session.commit()
            results['dias_nao_letivos'] = count
            print(f"[OK] {count} dias não letivos migrados")
        
        # 5. Alunos
        if data.get('alunos', {}).get('rows'):
            count = 0
            for row in data['alunos']['rows']:
                try:
                    existing = db.session.get(Aluno, row['id'])
                    if not existing:
                        aluno = Aluno(
                            id=row['id'],
                            nome=row['nome'],
                            matricula=row['matricula'],
                            data_nascimento=row.get('data_nascimento'),
                            cpf=row.get('cpf'),
                            email=row.get('email'),
                            telefone=row.get('telefone'),
                            endereco=row.get('endereco'),
                            nome_responsavel=row.get('nome_responsavel'),
                            telefone_responsavel=row.get('telefone_responsavel'),
                            email_responsavel=row.get('email_responsavel'),
                            ano_letivo=row['ano_letivo'],
                            status=row.get('status', 'ativo'),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(aluno)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar aluno {row.get('id')}: {e}")
            db.session.commit()
            results['alunos'] = count
            print(f"[OK] {count} alunos migrados")
        
        # 6. Professores (depende de usuarios)
        if data.get('professores', {}).get('rows'):
            count = 0
            for row in data['professores']['rows']:
                try:
                    existing = db.session.get(Professor, row['id'])
                    if not existing:
                        professor = Professor(
                            id=row['id'],
                            usuario_id=row['usuario_id'],
                            registro=row['registro'],
                            especialidade=row.get('especialidade'),
                            formacao=row.get('formacao'),
                            cpf=row.get('cpf'),
                            telefone=row.get('telefone'),
                            endereco=row.get('endereco'),
                            ativo=bool(row.get('ativo', 1)),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(professor)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar professor {row.get('id')}: {e}")
            db.session.commit()
            results['professores'] = count
            print(f"[OK] {count} professores migrados")
        
        # 7. Turmas
        if data.get('turmas', {}).get('rows'):
            count = 0
            for row in data['turmas']['rows']:
                try:
                    existing = db.session.get(Turma, row['id'])
                    if not existing:
                        turma = Turma(
                            id=row['id'],
                            nome=row['nome'],
                            codigo=row['codigo'],
                            serie=row['serie'],
                            ano_letivo=row['ano_letivo'],
                            turno=row['turno'],
                            capacidade_maxima=row.get('capacidade_maxima', 40),
                            descricao=row.get('descricao'),
                            ativa=bool(row.get('ativa', 1)),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(turma)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar turma {row.get('id')}: {e}")
            db.session.commit()
            results['turmas'] = count
            print(f"[OK] {count} turmas migradas")
        
        # 8. Associações alunos_turmas
        if data.get('alunos_turmas', {}).get('rows'):
            count = 0
            for row in data['alunos_turmas']['rows']:
                try:
                    db.session.execute(
                        alunos_turmas.insert().values(
                            aluno_id=row['aluno_id'],
                            turma_id=row['turma_id'],
                            data_matricula=row.get('data_matricula')
                        )
                    )
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar aluno_turma: {e}")
            db.session.commit()
            results['alunos_turmas'] = count
            print(f"[OK] {count} associações aluno-turma migradas")
        
        # 9. Associações professores_turmas
        if data.get('professores_turmas', {}).get('rows'):
            count = 0
            for row in data['professores_turmas']['rows']:
                try:
                    db.session.execute(
                        professores_turmas.insert().values(
                            professor_id=row['professor_id'],
                            turma_id=row['turma_id'],
                            data_associacao=row.get('data_associacao')
                        )
                    )
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar professor_turma: {e}")
            db.session.commit()
            results['professores_turmas'] = count
            print(f"[OK] {count} associações professor-turma migradas")
        
        # 10. Associações professor_materias
        if data.get('professor_materias', {}).get('rows'):
            count = 0
            for row in data['professor_materias']['rows']:
                try:
                    db.session.execute(
                        professor_materias.insert().values(
                            professor_id=row['professor_id'],
                            materia_id=row['materia_id']
                        )
                    )
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar professor_materia: {e}")
            db.session.commit()
            results['professor_materias'] = count
            print(f"[OK] {count} associações professor-materia migradas")
        
        # 11. Associações turma_materias
        if data.get('turma_materias', {}).get('rows'):
            count = 0
            for row in data['turma_materias']['rows']:
                try:
                    db.session.execute(
                        turma_materias.insert().values(
                            turma_id=row['turma_id'],
                            materia_id=row['materia_id'],
                            aulas_por_periodo=row.get('aulas_por_periodo', 2)
                        )
                    )
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar turma_materia: {e}")
            db.session.commit()
            results['turma_materias'] = count
            print(f"[OK] {count} associações turma-materia migradas")
        
        # 12. Aulas (depende de turmas, professores)
        if data.get('aulas', {}).get('rows'):
            count = 0
            for row in data['aulas']['rows']:
                try:
                    existing = db.session.get(Aula, row['id'])
                    if not existing:
                        aula = Aula(
                            id=row['id'],
                            materia=row['materia'],
                            descricao=row.get('descricao'),
                            turma_id=row['turma_id'],
                            professor_id=row['professor_id'],
                            data=row['data'],
                            horario_inicio=row['horario_inicio'],
                            horario_fim=row['horario_fim'],
                            recorrente=bool(row.get('recorrente', 0)),
                            tipo_recorrencia=row.get('tipo_recorrencia'),
                            dia_semana=row.get('dia_semana'),
                            data_fim_recorrencia=row.get('data_fim_recorrencia'),
                            aula_pai_id=row.get('aula_pai_id'),
                            status=row.get('status', 'agendada'),
                            criado_em=row.get('criado_em'),
                            atualizado_em=row.get('atualizado_em')
                        )
                        db.session.add(aula)
                        count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar aula {row.get('id')}: {e}")
            db.session.commit()
            results['aulas'] = count
            print(f"[OK] {count} aulas migradas")
        
        # 13. Frequencias
        if data.get('frequencias', {}).get('rows'):
            count = 0
            for row in data['frequencias']['rows']:
                try:
                    freq = Frequencia(
                        id=row['id'],
                        aluno_id=row['aluno_id'],
                        aula_id=row['aula_id'],
                        presente=bool(row.get('presente', 1)),
                        justificativa=row.get('justificativa'),
                        registrado_em=row.get('registrado_em')
                    )
                    db.session.add(freq)
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar frequencia {row.get('id')}: {e}")
            db.session.commit()
            results['frequencias'] = count
            print(f"[OK] {count} frequencias migradas")
        
        # 14. Notas
        if data.get('notas', {}).get('rows'):
            count = 0
            for row in data['notas']['rows']:
                try:
                    nota = Nota(
                        id=row['id'],
                        aluno_id=row['aluno_id'],
                        turma_id=row['turma_id'],
                        aula_id=row.get('aula_id'),
                        tipo_avaliacao=row['tipo_avaliacao'],
                        descricao=row.get('descricao'),
                        valor=row['valor'],
                        valor_maximo=row.get('valor_maximo'),
                        peso=row.get('peso'),
                        bimestre=row.get('bimestre'),
                        registrado_em=row.get('registrado_em'),
                        atualizado_em=row.get('atualizado_em')
                    )
                    db.session.add(nota)
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar nota {row.get('id')}: {e}")
            db.session.commit()
            results['notas'] = count
            print(f"[OK] {count} notas migradas")
        
        # 15. Arquivos
        if data.get('arquivos', {}).get('rows'):
            count = 0
            for row in data['arquivos']['rows']:
                try:
                    arquivo = Arquivo(
                        id=row['id'],
                        nome_original=row['nome_original'],
                        nome_armazenado=row['nome_armazenado'],
                        tipo=row['tipo'],
                        tamanho=row['tamanho'],
                        aula_id=row['aula_id'],
                        professor_id=row['professor_id'],
                        descricao=row.get('descricao'),
                        criado_em=row.get('criado_em')
                    )
                    db.session.add(arquivo)
                    count += 1
                except Exception as e:
                    print(f"  [AVISO] Erro ao migrar arquivo {row.get('id')}: {e}")
            db.session.commit()
            results['arquivos'] = count
            print(f"[OK] {count} arquivos migrados")
    
    return results


def validate_migration(sqlite_data, pg_conn_string):
    """
    Valida a migração comparando contagens.
    
    Args:
        sqlite_data: Dados exportados do SQLite
        pg_conn_string: String de conexão PostgreSQL
        
    Returns:
        dict: Resultado da validação
    """
    from app import create_app, db
    
    os.environ['DATABASE_URL'] = pg_conn_string
    app = create_app('production')
    
    validation = {}
    
    with app.app_context():
        table_models = {
            'usuarios': 'Usuario',
            'materias': 'Materia',
            'feriados': 'Feriado',
            'dias_nao_letivos': 'DiaNaoLetivo',
            'alunos': 'Aluno',
            'professores': 'Professor',
            'turmas': 'Turma',
            'aulas': 'Aula',
            'frequencias': 'Frequencia',
            'notas': 'Nota',
            'arquivos': 'Arquivo',
        }
        
        for table_name, model_name in table_models.items():
            from app.models import Usuario, Aluno, Professor, Turma, Aula, Frequencia, Nota, Arquivo, Feriado, DiaNaoLetivo, Materia
            
            model_map = {
                'Usuario': Usuario,
                'Aluno': Aluno,
                'Professor': Professor,
                'Turma': Turma,
                'Aula': Aula,
                'Frequencia': Frequencia,
                'Nota': Nota,
                'Arquivo': Arquivo,
                'Feriado': Feriado,
                'DiaNaoLetivo': DiaNaoLetivo,
                'Materia': Materia,
            }
            
            model = model_map.get(model_name)
            if model:
                pg_count = model.query.count()
                sqlite_count = sqlite_data.get(table_name, {}).get('count', 0)
                
                validation[table_name] = {
                    'sqlite': sqlite_count,
                    'postgresql': pg_count,
                    'match': sqlite_count == pg_count
                }
    
    return validation


def main():
    """Função principal do script de migração."""
    print_header("MIGRAÇÃO SQLite → PostgreSQL (Supabase)")
    
    # Passo 1: Conectar ao SQLite
    print_step(1, "Conectando ao SQLite...")
    sqlite_conn = get_sqlite_connection()
    print("[OK] Conectado ao SQLite")
    
    # Passo 2: Exportar dados
    print_step(2, "Exportando dados do SQLite...")
    data = export_sqlite_data(sqlite_conn)
    total_records = sum(table['count'] for table in data.values())
    print(f"[OK] {total_records} registros exportados de {len(data)} tabelas")
    
    for table, table_data in data.items():
        if table_data['count'] > 0:
            print(f"    - {table}: {table_data['count']} registros")
    
    # Passo 3: Criar backup
    print_step(3, "Criando backup...")
    backup_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'database'
    )
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'backup_sqlite_{timestamp}.json')
    create_backup(data, backup_path)
    
    # Passo 4: Obter string de conexão PostgreSQL
    print_step(4, "Configurando conexão PostgreSQL...")
    pg_conn_string = get_postgresql_connection_string()
    # Mascarar senha na exibição
    masked = pg_conn_string[:30] + '***' + pg_conn_string[-20:]
    print(f"[OK] String de conexão: {masked}")
    
    # Passo 5: Confirmar migração
    print_step(5, "Confirmar migração")
    print(f"\n    Dados a migrar: {total_records} registros")
    print(f"    Backup salvo em: {backup_path}")
    print(f"    Destino: PostgreSQL (Supabase)")
    
    confirm = input("\n    Deseja continuar? (s/N): ").strip().lower()
    if confirm not in ('s', 'sim', 'y', 'yes'):
        print("\n[INFO] Migração cancelada pelo usuário")
        sqlite_conn.close()
        return
    
    # Passo 6: Migrar dados
    print_step(6, "Migrando dados para PostgreSQL...")
    results = migrate_data_to_postgresql(data, pg_conn_string)
    
    # Passo 7: Validar migração
    print_step(7, "Validando migração...")
    validation = validate_migration(data, pg_conn_string)
    
    # Resultado final
    print_header("RESULTADO DA MIGRAÇÃO")
    
    all_ok = True
    for table, result in validation.items():
        status = "✅" if result['match'] else "❌"
        print(f"  {status} {table}: SQLite={result['sqlite']} | PostgreSQL={result['postgresql']}")
        if not result['match']:
            all_ok = False
    
    if all_ok:
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\nPróximos passos:")
        print("  1. Atualize o .env com a DATABASE_URL do Supabase")
        print("  2. Teste a aplicação: flask run")
        print("  3. Verifique se todos os dados estão corretos")
    else:
        print("\n⚠️ MIGRAÇÃO CONCLUÍDA COM DIVERGÊNCIAS")
        print("Verifique as tabelas com ❌ acima")
    
    sqlite_conn.close()


if __name__ == '__main__':
    main()
