# seed.py - Script de inicialização do banco de dados
# Cria dados de teste para o Analitcs School

import os
import sys
from datetime import datetime, date, time, timedelta

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.aula import Aula
from app.models.feriado import Feriado


def criar_usuario_teste():
    """Cria o usuário de teste principal."""
    email = 'joao@escola.com'
    
    # Verificar se já existe
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        print(f"[INFO] Usuário de teste já existe: {email}")
        return usuario
    
    # Criar novo usuário
    usuario = Usuario(
        nome='João Silva',
        email=email,
        tipo='diretora',
        ativo=True,
        tema='light'
    )
    usuario.set_senha('1234')
    
    db.session.add(usuario)
    db.session.commit()
    
    print(f"[OK] Usuário de teste criado: {email} / senha: 1234")
    return usuario


def criar_professores():
    """Cria professores de teste."""
    professores_data = [
        {'nome': 'Maria Santos', 'email': 'maria@escola.com', 'registro': 'PROF001', 'especialidade': 'Matemática'},
        {'nome': 'Carlos Oliveira', 'email': 'carlos@escola.com', 'registro': 'PROF002', 'especialidade': 'Português'},
        {'nome': 'Ana Costa', 'email': 'ana@escola.com', 'registro': 'PROF003', 'especialidade': 'Ciências'},
    ]
    
    professores = []
    for data in professores_data:
        # Criar usuário
        usuario = Usuario.query.filter_by(email=data['email']).first()
        if not usuario:
            usuario = Usuario(
                nome=data['nome'],
                email=data['email'],
                tipo='professor',
                ativo=True
            )
            usuario.set_senha('1234')
            db.session.add(usuario)
            db.session.flush()
        
        # Criar professor
        professor = Professor.query.filter_by(registro=data['registro']).first()
        if not professor:
            professor = Professor(
                usuario_id=usuario.id,
                registro=data['registro'],
                especialidade=data['especialidade'],
                ativo=True
            )
            db.session.add(professor)
            professores.append(professor)
    
    db.session.commit()
    print(f"[OK] {len(professores)} professores criados")
    return professores


def criar_turmas():
    """Cria turmas de teste."""
    turmas_data = [
        {'nome': '1º Ano A', 'codigo': '1A2024', 'serie': '1º Ano', 'turno': 'manha', 'capacidade': 35},
        {'nome': '2º Ano B', 'codigo': '2B2024', 'serie': '2º Ano', 'turno': 'tarde', 'capacidade': 30},
        {'nome': '3º Ano C', 'codigo': '3C2024', 'serie': '3º Ano', 'turno': 'manha', 'capacidade': 40},
    ]
    
    turmas = []
    for data in turmas_data:
        turma = Turma.query.filter_by(codigo=data['codigo']).first()
        if not turma:
            turma = Turma(
                nome=data['nome'],
                codigo=data['codigo'],
                serie=data['serie'],
                ano_letivo=2024,
                turno=data['turno'],
                capacidade_maxima=data['capacidade'],
                ativa=True
            )
            db.session.add(turma)
            turmas.append(turma)
    
    db.session.commit()
    print(f"[OK] {len(turmas)} turmas criadas")
    return turmas


def criar_alunos():
    """Cria alunos de teste."""
    alunos_data = [
        {'nome': 'Pedro Henrique', 'matricula': 'ALU001', 'email': 'pedro@email.com'},
        {'nome': 'Julia Oliveira', 'matricula': 'ALU002', 'email': 'julia@email.com'},
        {'nome': 'Lucas Silva', 'matricula': 'ALU003', 'email': 'lucas@email.com'},
        {'nome': 'Mariana Costa', 'matricula': 'ALU004', 'email': 'mariana@email.com'},
        {'nome': 'Gabriel Santos', 'matricula': 'ALU005', 'email': 'gabriel@email.com'},
        {'nome': 'Isabela Lima', 'matricula': 'ALU006', 'email': 'isabela@email.com'},
    ]
    
    alunos = []
    for data in alunos_data:
        aluno = Aluno.query.filter_by(matricula=data['matricula']).first()
        if not aluno:
            aluno = Aluno(
                nome=data['nome'],
                matricula=data['matricula'],
                email=data['email'],
                ano_letivo=2024,
                status='ativo'
            )
            db.session.add(aluno)
            alunos.append(aluno)
    
    db.session.commit()
    print(f"[OK] {len(alunos)} alunos criados")
    return alunos


def associar_alunos_turmas(alunos, turmas):
    """Associa alunos às turmas."""
    if not alunos or not turmas:
        return
    
    # Distribuir alunos nas turmas
    for i, aluno in enumerate(alunos):
        turma = turmas[i % len(turmas)]
        if aluno not in turma.alunos:
            turma.alunos.append(aluno)
    
    db.session.commit()
    print("[OK] Alunos associados às turmas")


def criar_aulas(turmas, professores):
    """Cria aulas de teste."""
    if not turmas or not professores:
        return
    
    hoje = date.today()
    materias = ['Matemática', 'Português', 'Ciências', 'História', 'Geografia']
    
    aulas_criadas = 0
    for i in range(5):  # 5 aulas de exemplo
        data_aula = hoje + timedelta(days=i)
        
        # Pular fins de semana
        if data_aula.weekday() >= 5:
            continue
        
        turma = turmas[i % len(turmas)]
        professor = professores[i % len(professores)]
        materia = materias[i % len(materias)]
        
        # Verificar se já existe
        aula_existente = Aula.query.filter_by(
            turma_id=turma.id,
            data=data_aula,
            horario_inicio=time(8, 0)
        ).first()
        
        if not aula_existente:
            aula = Aula(
                materia=materia,
                turma_id=turma.id,
                professor_id=professor.id,
                data=data_aula,
                horario_inicio=time(8, 0),
                horario_fim=time(9, 30),
                recorrente=False,
                status='agendada'
            )
            db.session.add(aula)
            aulas_criadas += 1
    
    db.session.commit()
    print(f"[OK] {aulas_criadas} aulas criadas")


def criar_feriados():
    """Cria feriados de teste."""
    feriados_data = [
        {'nome': 'Ano Novo', 'data': date(2024, 1, 1), 'tipo': 'nacional'},
        {'nome': 'Carnaval', 'data': date(2024, 2, 12), 'tipo': 'nacional'},
        {'nome': 'Páscoa', 'data': date(2024, 3, 31), 'tipo': 'nacional'},
        {'nome': 'Tiradentes', 'data': date(2024, 4, 21), 'tipo': 'nacional'},
        {'nome': 'Dia do Trabalho', 'data': date(2024, 5, 1), 'tipo': 'nacional'},
        {'nome': 'Independência', 'data': date(2024, 9, 7), 'tipo': 'nacional'},
        {'nome': 'Nossa Sra. Aparecida', 'data': date(2024, 10, 12), 'tipo': 'nacional'},
        {'nome': 'Finados', 'data': date(2024, 11, 2), 'tipo': 'nacional'},
        {'nome': 'Proclamação da República', 'data': date(2024, 11, 15), 'tipo': 'nacional'},
        {'nome': 'Natal', 'data': date(2024, 12, 25), 'tipo': 'nacional'},
    ]
    
    criados = 0
    for data in feriados_data:
        feriado = Feriado.query.filter_by(data=data['data']).first()
        if not feriado:
            feriado = Feriado(
                nome=data['nome'],
                data=data['data'],
                tipo=data['tipo'],
                recorrente=True
            )
            db.session.add(feriado)
            criados += 1
    
    db.session.commit()
    print(f"[OK] {criados} feriados criados")


def seed_database():
    """Função principal de seed."""
    print("\n" + "=" * 45)
    print("  INICIALIZAÇÃO DO BANCO DE DADOS")
    print("=" * 45 + "\n")
    
    # Criar aplicação
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Criar dados
            usuario_teste = criar_usuario_teste()
            professores = criar_professores()
            turmas = criar_turmas()
            alunos = criar_alunos()
            associar_alunos_turmas(alunos, turmas)
            criar_aulas(turmas, professores)
            criar_feriados()
            
            print("\n" + "=" * 45)
            print("  BANCO DE DADOS INICIALIZADO COM SUCESSO!")
            print("=" * 45)
            print(f"\n  Usuário de teste:")
            print(f"  Email: joao@escola.com")
            print(f"  Senha: 1234")
            print(f"  Tipo: diretora (acesso total)")
            print("\n" + "=" * 45 + "\n")
            
        except Exception as e:
            print(f"\n[ERRO] Falha na inicialização: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    seed_database()
