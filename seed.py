# seed.py - Script de inicialização do banco de dados expandido
# Cria dados de teste completos para o Analitcs School

import os
import sys
from datetime import datetime, date, time, timedelta

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
from app.models.materia import Materia, turma_materias


def seed_usuarios_base():
    """Cria usuários base do sistema (diretora e coordenação)."""
    usuarios_data = [
        {'nome': 'João Silva', 'email': 'joao@escola.com', 'tipo': 'diretora', 'senha': '1234'},
        {'nome': 'Paula Mendes', 'email': 'coordenacao@escola.com', 'tipo': 'coordenacao', 'senha': '1234'},
    ]
    
    for data in usuarios_data:
        usuario = Usuario.query.filter_by(email=data['email']).first()
        if not usuario:
            usuario = Usuario(
                nome=data['nome'],
                email=data['email'],
                tipo=data['tipo'],
                ativo=True
            )
            usuario.set_senha(data['senha'])
            db.session.add(usuario)
    
    db.session.commit()
    print("[OK] Usuários base criados")


def seed_professores():
    """Cria 10+ professores com dados diversos."""
    professores_data = [
        {'nome': 'Maria Santos', 'email': 'maria@escola.com', 'registro': 'PROF001', 'especialidade': 'Matemática'},
        {'nome': 'Carlos Oliveira', 'email': 'carlos@escola.com', 'registro': 'PROF002', 'especialidade': 'Português'},
        {'nome': 'Ana Costa', 'email': 'ana@escola.com', 'registro': 'PROF003', 'especialidade': 'Ciências'},
        {'nome': 'Roberto Lima', 'email': 'roberto@escola.com', 'registro': 'PROF004', 'especialidade': 'História'},
        {'nome': 'Juliana Ferreira', 'email': 'juliana@escola.com', 'registro': 'PROF005', 'especialidade': 'Geografia'},
        {'nome': 'Marcos Paulo', 'email': 'marcos@escola.com', 'registro': 'PROF006', 'especialidade': 'Ed. Física'},
        {'nome': 'Patricia Silva', 'email': 'patricia@escola.com', 'registro': 'PROF007', 'especialidade': 'Inglês'},
        {'nome': 'Fernando Alves', 'email': 'fernando@escola.com', 'registro': 'PROF008', 'especialidade': 'Matemática'},
        {'nome': 'Carla Rodrigues', 'email': 'carla@escola.com', 'registro': 'PROF009', 'especialidade': 'Português'},
        {'nome': 'Ricardo Souza', 'email': 'ricardo@escola.com', 'registro': 'PROF010', 'especialidade': 'Ciências'},
        {'nome': 'João Professor', 'email': 'joao@prof.com', 'registro': 'PROF011', 'especialidade': 'História'},
    ]
    
    professores = []
    for data in professores_data:
        usuario = Usuario.query.filter_by(email=data['email']).first()
        if not usuario:
            usuario = Usuario(
                nome=data['nome'],
                email=data['email'],
                tipo='professor',
                ativo=True
            )
            usuario.set_senha(data.get('senha', '1234'))
            db.session.add(usuario)
            db.session.flush()
        
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


def seed_materias():
    """Cria matérias básicas."""
    materias_data = [
        {'nome': 'Matemática', 'codigo': 'MAT', 'carga_horaria': 200},
        {'nome': 'Português', 'codigo': 'PORT', 'carga_horaria': 200},
        {'nome': 'Ciências', 'codigo': 'CIE', 'carga_horaria': 100},
        {'nome': 'História', 'codigo': 'HIST', 'carga_horaria': 100},
        {'nome': 'Geografia', 'codigo': 'GEO', 'carga_horaria': 100},
        {'nome': 'Inglês', 'codigo': 'ING', 'carga_horaria': 80},
        {'nome': 'Ed. Física', 'codigo': 'EDFIS', 'carga_horaria': 80},
    ]
    
    materias = []
    for mdata in materias_data:
        materia = Materia.query.filter_by(codigo=mdata['codigo']).first()
        if not materia:
            materia = Materia(
                nome=mdata['nome'],
                codigo=mdata['codigo'],
                carga_horaria=mdata['carga_horaria'],
                ativa=True
            )
            db.session.add(materia)
            materias.append(materia)
    
    db.session.commit()
    print(f"[OK] {len(materias)} matérias criadas")
    return materias


def seed_turmas():
    """Cria turmas para comportar os alunos."""
    turmas_data = [
        {'nome': '1º Ano A', 'codigo': '1A2024', 'serie': '1º Ano', 'turno': 'manha', 'capacidade': 35},
        {'nome': '1º Ano B', 'codigo': '1B2024', 'serie': '1º Ano', 'turno': 'tarde', 'capacidade': 30},
        {'nome': '2º Ano A', 'codigo': '2A2024', 'serie': '2º Ano', 'turno': 'manha', 'capacidade': 35},
        {'nome': '2º Ano B', 'codigo': '2B2024', 'serie': '2º Ano', 'turno': 'tarde', 'capacidade': 30},
        {'nome': '3º Ano A', 'codigo': '3A2024', 'serie': '3º Ano', 'turno': 'manha', 'capacidade': 35},
        {'nome': '3º Ano B', 'codigo': '3B2024', 'serie': '3º Ano', 'turno': 'tarde', 'capacidade': 30},
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


def seed_alunos():
    """Cria 100+ alunos com dados diversos."""
    
    # Nomes para geração aleatória
    nomes = [
        'Pedro Henrique', 'Julia Oliveira', 'Lucas Silva', 'Mariana Costa', 'Gabriel Santos',
        'Isabela Lima', 'Bruno Almeida', 'Carla Rodrigues', 'Daniel Pereira', 'Eduarda Castro',
        'Felipe Martins', 'Gabriela Nunes', 'Hugo Ferreira', 'Isadora Araujo', 'João Pedro',
        'Karina Tavares', 'Leonardo Campos', 'Marina Dias', 'Nicolas Souza', 'Olivia Lima',
        'Paulo Ricardo', 'Quiteria Santos', 'Rafael Costa', 'Sofia Mendes', 'Thiago Oliveira',
        'Ursula Ferreira', 'Vinícius Silva', 'Wilian Santos', 'Xuxa Rodrigues', 'Yasmin Costa',
        'Zilda Lima', 'André Silva', 'Bruna Oliveira', 'Caio Santos', 'Débora Costa',
        'Eduardo Mendes', 'Fernanda Lima', 'Gustavo Oliveira', 'Helena Santos', 'Igor Costa',
        'Júlia Pereira', 'Kleber Rodrigues', 'Larissa Silva', 'Mateus Oliveira', 'Natália Santos',
        'Otávio Costa', 'Paula Lima', 'Quentinhas Santos', 'Renata Oliveira', 'Samira Costa',
        'Túlio Silva', 'Úrsula Mendes', 'Vagner Oliveira', 'Wellington Santos', 'Xiomara Costa',
        'Yuri Lima', 'Zuleica Oliveira', 'Adriano Santos', 'Bianca Costa', 'Celso Mendes',
        'Daniella Oliveira', 'Evandro Silva', 'Flávia Costa', 'Gilberto Santos', 'Helô Lima',
        'Ivo Oliveira', 'Josiane Santos', 'Karla Costa', 'Leandro Oliveira', 'Miriam Santos',
        'Nelson Costa', 'Osvaldo Lima', 'Pamela Oliveira', 'Queen Santos', 'Rita Costa',
        'Sérgio Lima', 'Terezinha Oliveira', 'Ulisses Santos', 'Valéria Costa', 'Washington Lima',
        'Xenia Oliveira', 'Yago Santos', 'Zilda Maria', 'Albino Costa', 'Berenice Lima',
        'Cláudio Oliveira', 'Denise Santos', 'Elton Costa', 'Fernanda Maria', 'Marcos Vinícius',
    ]
    
    sobrenomes = [
        'Silva', 'Oliveira', 'Santos', 'Costa', 'Lima', 'Mendes', 'Rodrigues', 'Ferreira',
        'Almeida', 'Sousa', 'Gomes', 'Carvalho', 'Martins', 'Rocha', 'Azevedo', 'Pereira',
        'Ribeiro', 'Cardoso', 'Fernandes', 'Barbosa', 'Rosa', 'Correia', 'Dias', 'Castro',
    ]
    
    ano_letivo = 2024
    status_options = ['ativo', 'ativo', 'ativo', 'ativo', 'inativo']  # Maioria ativo
    
    alunos = []
    for i in range(120):  # Criar 120 alunos
        nome = f"{nomes[i % len(nomes)]} {sobrenomes[i % len(sobrenomes)]}"
        matricula = f"ALU{i+1:05d}"
        email = f"aluno{i+1}@email.com"
        
        # Verificar se aluno já existe
        aluno = Aluno.query.filter_by(matricula=matricula).first()
        if not aluno:
            aluno = Aluno(
                nome=nome,
                matricula=matricula,
                email=email,
                ano_letivo=ano_letivo,
                status=status_options[i % len(status_options)],
                telefone=f"99999-{1000+i:04d}"
            )
            db.session.add(aluno)
            alunos.append(aluno)
    
    db.session.commit()
    print(f"[OK] {len(alunos)} alunos criados")
    return alunos


def seed_turmas_alunos(turmas, alunos):
    """Associa alunos às turmas de forma equilibrada."""
    if not turmas or not alunos:
        return
    
    # Cada turma recebe aproximadamente 20 alunos
    alunos_por_turma = len(alunos) // len(turmas)
    
    for idx, turma in enumerate(turmas):
        inicio = idx * alunos_por_turma
        fim = inicio + alunos_por_turma
        
        if idx == len(turmas) - 1:
            fim = len(alunos)  # Ultima turma pega o resto
        
        turma_alunos = alunos[inicio:fim]
        
        for aluno in turma_alunos:
            if aluno not in turma.alunos:
                turma.alunos.append(aluno)
    
    db.session.commit()
    print("[OK] Alunos distribuídos nas turmas")


def seed_aulas(turmas, professores):
    """Cria aulas básicas parademo."""
    if not turmas or not professores:
        return
    
    materias = ['Matemática', 'Português', 'Ciências', 'História', 'Geografia']
    hoje = date.today()
    
    aulas_criadas = 0
    for i in range(10):  # Próximos 10 dias úteis
        data_aula = hoje + timedelta(days=i)
        
        if data_aula.weekday() >= 5:  # Pular fim de semana
            continue
        
        for turma in turmas[:3]:  # Primeiras 3 turmas
            for materia in materias[:3]:  # Primeiras 3 matérias
                professor = professores[i % len(professores)]
                
                # Criar aula
                aula = Aula(
                    materia=materia,
                    turma_id=turma.id,
                    professor_id=professor.id,
                    data=data_aula,
                    horario_inicio=time(7 + i % 4, 0),
                    horario_fim=time(7 + i % 4, 50),
                    status='agendada'
                )
                db.session.add(aula)
                aulas_criadas += 1
    
    db.session.commit()
    print(f"[OK] {aulas_criadas} aulas criadas")


def seed_feriados():
    """Cria feriados brasileiros."""
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
    
    db.session.commit()
    print("[OK] Feriados criados")


def seed_professor_materias(professores, materias):
    """Associa professores às matérias que podem lecionar."""
    if not professores or not materias:
        return
    
    # Mapear especialidade para matéria
    especialidade_para_materia = {
        'Matemática': 'MAT',
        'Português': 'PORT',
        'Ciências': 'CIE',
        'História': 'HIST',
        'Geografia': 'GEO',
        'Inglês': 'ING',
        'Ed. Física': 'EDFIS'
    }
    
    materias_por_codigo = {m.codigo: m for m in materias}
    
    associacoes = 0
    for professor in professores:
        # Associar pela especialidade
        codigo_materia = especialidade_para_materia.get(professor.especialidade)
        if codigo_materia and codigo_materia in materias_por_codigo:
            materia = materias_por_codigo[codigo_materia]
            if materia not in professor.materias:
                professor.materias.append(materia)
                associacoes += 1
        
        # Alguns professores podem lecionar mais de uma matéria
        # Ex: Matemática e Ciências
        if professor.especialidade == 'Matemática' and 'CIE' in materias_por_codigo:
            extra = materias_por_codigo['CIE']
            if extra not in professor.materias:
                professor.materias.append(extra)
                associacoes += 1
    
    db.session.commit()
    print(f"[OK] {associacoes} associações professor-matéria criadas")


def seed_turma_materias(turmas, materias):
    """Associa matérias às turmas com aulas por período."""
    if not turmas or not materias:
        return
    
    # Configuração de aulas por semana para cada matéria
    aulas_por_materia = {
        'MAT': 4,    # Matemática - 4 aulas/semana
        'PORT': 4,   # Português - 4 aulas/semana
        'CIE': 2,    # Ciências - 2 aulas/semana
        'HIST': 2,   # História - 2 aulas/semana
        'GEO': 2,    # Geografia - 2 aulas/semana
        'ING': 2,    # Inglês - 2 aulas/semana
        'EDFIS': 2   # Ed. Física - 2 aulas/semana
    }
    
    materias_por_codigo = {m.codigo: m for m in materias}
    
    associacoes = 0
    for turma in turmas:
        for codigo, materia in materias_por_codigo.items():
            # Verificar se já existe
            existing = db.session.query(turma_materias).filter_by(
                turma_id=turma.id, materia_id=materia.id
            ).first()
            
            if not existing:
                aulas = aulas_por_materia.get(codigo, 2)
                db.session.execute(
                    turma_materias.insert().values(
                        turma_id=turma.id,
                        materia_id=materia.id,
                        aulas_por_periodo=aulas
                    )
                )
                associacoes += 1
    
    db.session.commit()
    print(f"[OK] {associacoes} associações turma-matéria criadas")


def run_seed():
    """Executa toda a seed de dados."""
    print("\n" + "="*50)
    print("  SEED DE DADOS EXPANDIDO - ANALITCS SCHOOL")
    print("="*50 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Etapa 1: Usuários base
            print("[1/8] Criando usuários base...")
            seed_usuarios_base()
            
            # Etapa 2: Professores
            print("\n[2/8] Criando professores...")
            professores = seed_professores()
            
            # Etapa 3: Matérias
            print("\n[3/8] Criando matérias...")
            materias = seed_materias()
            
            # Etapa 4: Turmas
            print("\n[4/8] Criando turmas...")
            turmas = seed_turmas()
            
            # Etapa 5: Alunos
            print("\n[5/8] Criando alunos...")
            alunos = seed_alunos()
            
            # Etapa 6: Associar alunos às turmas
            print("\n[6/8] Associando alunos às turmas...")
            seed_turmas_alunos(turmas, alunos)
            
            # Etapa 7: Associar professores às matérias
            print("\n[7/8] Associando professores às matérias...")
            seed_professor_materias(professores, materias)
            
            # Etapa 8: Associar matérias às turmas
            print("\n[8/8] Associando matérias às turmas...")
            seed_turma_materias(turmas, materias)
            
            # aulas
            seed_aulas(turmas, professores)
            
            # Feriados
            seed_feriados()
            
            print("\n" + "="*50)
            print("  SEED CONCLUÍDA COM SUCESSO!")
            print("="*50)
            print("\n📋 RESUMO:")
            print(f"  - Professores: {len(professores)}")
            print(f"  - Turmas: {len(turmas)}")
            print(f"  - Alunos: {len(alunos)}")
            print(f"  - Matérias: {len(materias)}")
            print("\n📝 CONTAS PARA TESTE:")
            print("  | Email           | Senha | Tipo        |")
            print("  |-----------------|-------|------------|")
            print("  | joao@escola.com | 1234  | Diretora   |")
            print("  | coordenacao@... | 1234  | Coordenação|")
            print("  | joao@prof.com   | 1234  | Professor  |")
            print("  | maria@escola... | 1234  | Professor  |")
            print("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"\n[ERRO] Falha na seed: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    run_seed()