-- SQL Script para criação do banco de dados Analitcs School
-- PostgreSQL

-- Criar banco de dados
-- CREATE DATABASE analitcs_school;

-- Executar como superusuário do PostgreSQL

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha_hash VARCHAR(256) NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'professor',
    avatar VARCHAR(255),
    telefone VARCHAR(20),
    tema VARCHAR(10) DEFAULT 'light',
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP
);

-- Tabela de Alunos
CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    data_nascimento DATE,
    cpf VARCHAR(14) UNIQUE,
    email VARCHAR(120),
    telefone VARCHAR(20),
    endereco TEXT,
    nome_responsavel VARCHAR(100),
    telefone_responsavel VARCHAR(20),
    email_responsavel VARCHAR(120),
    ano_letivo INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Professores
CREATE TABLE IF NOT EXISTS professores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    registro VARCHAR(20) UNIQUE NOT NULL,
    especialidade VARCHAR(100),
    formacao TEXT,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20),
    endereco TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Turmas
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    serie VARCHAR(30) NOT NULL,
    ano_letivo INTEGER NOT NULL,
    turno VARCHAR(20) NOT NULL,
    capacidade_maxima INTEGER DEFAULT 40,
    descricao TEXT,
    ativa BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Aulas
CREATE TABLE IF NOT EXISTS aulas (
    id SERIAL PRIMARY KEY,
    materia VARCHAR(100) NOT NULL,
    descricao TEXT,
    turma_id INTEGER NOT NULL REFERENCES turmas(id),
    professor_id INTEGER NOT NULL REFERENCES professores(id),
    data DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL,
    recorrente BOOLEAN DEFAULT FALSE,
    tipo_recorrencia VARCHAR(20),
    dia_semana INTEGER,
    data_fim_recorrencia DATE,
    aula_pai_id INTEGER REFERENCES aulas(id),
    status VARCHAR(20) DEFAULT 'agendada',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Frequências
CREATE TABLE IF NOT EXISTS frequencias (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id),
    aula_id INTEGER NOT NULL REFERENCES aulas(id),
    presente BOOLEAN DEFAULT TRUE,
    justificativa TEXT,
    registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(aluno_id, aula_id)
);

-- Tabela de Notas
CREATE TABLE IF NOT EXISTS notas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id),
    turma_id INTEGER NOT NULL REFERENCES turmas(id),
    aula_id INTEGER REFERENCES aulas(id),
    tipo_avaliacao VARCHAR(30) NOT NULL,
    descricao VARCHAR(200),
    valor FLOAT NOT NULL,
    valor_maximo FLOAT DEFAULT 10.0,
    peso FLOAT DEFAULT 1.0,
    bimestre INTEGER,
    registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Arquivos
CREATE TABLE IF NOT EXISTS arquivos (
    id SERIAL PRIMARY KEY,
    nome_original VARCHAR(255) NOT NULL,
    nome_armazenado VARCHAR(255) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    tamanho INTEGER NOT NULL,
    aula_id INTEGER NOT NULL REFERENCES aulas(id),
    professor_id INTEGER NOT NULL REFERENCES professores(id),
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Feriados
CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data DATE UNIQUE NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'nacional',
    descricao TEXT,
    recorrente BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Dias Não Letivos
CREATE TABLE IF NOT EXISTS dias_nao_letivos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    tipo VARCHAR(30) NOT NULL DEFAULT 'recesso',
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Disponibilidade de Professores
-- Define os dias e horários disponíveis de cada professor para lecionar
CREATE TABLE IF NOT EXISTS disponibilidade_professores (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER NOT NULL REFERENCES professores(id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana >= 0 AND dia_semana <= 6),
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: horário de fim deve ser maior que horário de início
    CONSTRAINT chk_horario_valido CHECK (horario_fim > horario_inicio),
    
    -- Constraint: evitar duplicatas para mesmo professor, dia e horário
    CONSTRAINT uq_professor_dia_horario UNIQUE (professor_id, dia_semana, horario_inicio, horario_fim)
);

-- Tabela de Associação: Alunos <-> Turmas
CREATE TABLE IF NOT EXISTS alunos_turmas (
    aluno_id INTEGER NOT NULL REFERENCES alunos(id),
    turma_id INTEGER NOT NULL REFERENCES turmas(id),
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(aluno_id, turma_id)
);

-- Tabela de Associação: Professores <-> Turmas
CREATE TABLE IF NOT EXISTS professores_turmas (
    professor_id INTEGER NOT NULL REFERENCES professores(id),
    turma_id INTEGER NOT NULL REFERENCES turmas(id),
    data_associacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(professor_id, turma_id)
);

-- Tabela de Associação: Turmas <-> Matérias
-- Define quais matérias cada turma tem e quantas aulas por período (semana)
CREATE TABLE IF NOT EXISTS turma_materias (
    turma_id INTEGER NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
    materia_id INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    aulas_por_periodo INTEGER DEFAULT 2,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(turma_id, materia_id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_alunos_matricula ON alunos(matricula);
CREATE INDEX IF NOT EXISTS idx_professores_registro ON professores(registro);
CREATE INDEX IF NOT EXISTS idx_turmas_codigo ON turmas(codigo);
CREATE INDEX IF NOT EXISTS idx_aulas_data ON aulas(data);
CREATE INDEX IF NOT EXISTS idx_aulas_turma ON aulas(turma_id);
CREATE INDEX IF NOT EXISTS idx_aulas_professor ON aulas(professor_id);
CREATE INDEX IF NOT EXISTS idx_frequencias_aluno ON frequencias(aluno_id);
CREATE INDEX IF NOT EXISTS idx_frequencias_aula ON frequencias(aula_id);
CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id);
CREATE INDEX IF NOT EXISTS idx_notas_turma ON notas(turma_id);
CREATE INDEX IF NOT EXISTS idx_feriodos_data ON feriados(data);
CREATE INDEX IF NOT EXISTS idx_dias_nao_letivos_periodo ON dias_nao_letivos(data_inicio, data_fim);
CREATE INDEX IF NOT EXISTS idx_disp_professor_id ON disponibilidade_professores(professor_id);
CREATE INDEX IF NOT EXISTS idx_disp_dia_semana ON disponibilidade_professores(dia_semana);
CREATE INDEX IF NOT EXISTS idx_disp_ativo ON disponibilidade_professores(ativo);
CREATE INDEX IF NOT EXISTS idx_turma_materias_turma ON turma_materias(turma_id);
CREATE INDEX IF NOT EXISTS idx_turma_materias_materia ON turma_materias(materia_id);

-- Comentários nas tabelas
COMMENT ON TABLE usuarios IS 'Tabela de usuários do sistema para autenticação';
COMMENT ON TABLE alunos IS 'Tabela de alunos matriculados';
COMMENT ON TABLE professores IS 'Tabela de professores/docentes';
COMMENT ON TABLE turmas IS 'Tabela de turmas escolares';
COMMENT ON TABLE aulas IS 'Tabela de aulas agendadas (suporta recorrência)';
COMMENT ON TABLE frequencias IS 'Tabela de registro de frequência dos alunos';
COMMENT ON TABLE notas IS 'Tabela de notas e avaliações';
COMMENT ON TABLE arquivos IS 'Tabela de arquivos/materiais didáticos';
COMMENT ON TABLE feriados IS 'Tabela de feriados (nacionais, estaduais, municipais)';
COMMENT ON TABLE dias_nao_letivos IS 'Tabela de dias não letivos (recessos, eventos)';
COMMENT ON TABLE disponibilidade_professores IS 'Armazena os dias e horários disponíveis de cada professor para lecionar';
COMMENT ON COLUMN disponibilidade_professores.dia_semana IS 'Dia da semana (0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo)';
COMMENT ON TABLE turma_materias IS 'Associação entre turmas e matérias com quantidade de aulas por período';
COMMENT ON COLUMN turma_materias.aulas_por_periodo IS 'Quantidade de aulas da matéria por período (semana)';
