-- ============================================================
-- Analitcs School - Exportação para PostgreSQL (Supabase)
-- Gerado em: 2026-03-28 09:57:08
-- Total de tabelas: 15
-- Total de registros: 387
-- ============================================================

-- IMPORTANTE: Execute este arquivo no SQL Editor do Supabase
-- https://supabase.com/dashboard → Seu Projeto → SQL Editor

-- Verificar se está no schema correto
SET search_path TO public;


-- ============================================================
-- LIMPAR TABELAS EXISTENTES (se necessário)
-- ============================================================

DROP TABLE IF EXISTS arquivos CASCADE;
DROP TABLE IF EXISTS notas CASCADE;
DROP TABLE IF EXISTS frequencias CASCADE;
DROP TABLE IF EXISTS aulas CASCADE;
DROP TABLE IF EXISTS turma_materias CASCADE;
DROP TABLE IF EXISTS professor_materias CASCADE;
DROP TABLE IF EXISTS professores_turmas CASCADE;
DROP TABLE IF EXISTS alunos_turmas CASCADE;
DROP TABLE IF EXISTS professores CASCADE;
DROP TABLE IF EXISTS turmas CASCADE;
DROP TABLE IF EXISTS alunos CASCADE;
DROP TABLE IF EXISTS dias_nao_letivos CASCADE;
DROP TABLE IF EXISTS feriados CASCADE;
DROP TABLE IF EXISTS materias CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;


-- ============================================================
-- CRIAR TABELAS
-- ============================================================

-- Tabela: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    senha_hash VARCHAR(256) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    avatar VARCHAR(255),
    telefone VARCHAR(20),
    tema VARCHAR(10),
    ativo BOOLEAN,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    ultimo_acesso TIMESTAMP,
    PRIMARY KEY (id)
);


-- Tabela: materias
CREATE TABLE IF NOT EXISTS materias (
    id SERIAL,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    descricao TEXT,
    carga_horaria INTEGER,
    ativa BOOLEAN,
    PRIMARY KEY (id)
);


-- Tabela: feriados
CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL,
    nome VARCHAR(100) NOT NULL,
    data DATE NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    descricao TEXT,
    recorrente BOOLEAN,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id)
);


-- Tabela: dias_nao_letivos
CREATE TABLE IF NOT EXISTS dias_nao_letivos (
    id SERIAL,
    nome VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id)
);


-- Tabela: alunos
CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(20) NOT NULL,
    data_nascimento DATE,
    cpf VARCHAR(14),
    email VARCHAR(120),
    telefone VARCHAR(20),
    endereco TEXT,
    nome_responsavel VARCHAR(100),
    telefone_responsavel VARCHAR(20),
    email_responsavel VARCHAR(120),
    ano_letivo INTEGER NOT NULL,
    status VARCHAR(20),
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id)
);


-- Tabela: turmas
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL,
    nome VARCHAR(50) NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    serie VARCHAR(30) NOT NULL,
    ano_letivo INTEGER NOT NULL,
    turno VARCHAR(20) NOT NULL,
    capacidade_maxima INTEGER,
    descricao TEXT,
    ativa BOOLEAN,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id)
);


-- Tabela: professores
CREATE TABLE IF NOT EXISTS professores (
    id SERIAL,
    usuario_id INTEGER NOT NULL,
    registro VARCHAR(20) NOT NULL,
    especialidade VARCHAR(100),
    formacao TEXT,
    cpf VARCHAR(14),
    telefone VARCHAR(20),
    endereco TEXT,
    ativo BOOLEAN,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


-- Tabela: alunos_turmas
CREATE TABLE IF NOT EXISTS alunos_turmas (
    aluno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_matricula TIMESTAMP,
    PRIMARY KEY (aluno_id, turma_id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id),
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


-- Tabela: professores_turmas
CREATE TABLE IF NOT EXISTS professores_turmas (
    professor_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_associacao TIMESTAMP,
    PRIMARY KEY (professor_id, turma_id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id),
    FOREIGN KEY (professor_id) REFERENCES professores(id)
);


-- Tabela: professor_materias
CREATE TABLE IF NOT EXISTS professor_materias (
    professor_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    PRIMARY KEY (professor_id, materia_id),
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (professor_id) REFERENCES professores(id)
);


-- Tabela: turma_materias
CREATE TABLE IF NOT EXISTS turma_materias (
    turma_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    PRIMARY KEY (turma_id, materia_id),
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
);


-- Tabela: aulas
CREATE TABLE IF NOT EXISTS aulas (
    id SERIAL,
    materia VARCHAR(100) NOT NULL,
    descricao TEXT,
    turma_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    data DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL,
    recorrente BOOLEAN,
    tipo_recorrencia VARCHAR(20),
    dia_semana INTEGER,
    data_fim_recorrencia DATE,
    aula_pai_id INTEGER,
    status VARCHAR(20),
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (aula_pai_id) REFERENCES aulas(id),
    FOREIGN KEY (professor_id) REFERENCES professores(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
);


-- Tabela: frequencias
CREATE TABLE IF NOT EXISTS frequencias (
    id SERIAL,
    aluno_id INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,
    presente BOOLEAN,
    justificativa TEXT,
    registrado_em TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id),
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


-- Tabela: notas
CREATE TABLE IF NOT EXISTS notas (
    id SERIAL,
    aluno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    aula_id INTEGER,
    tipo_avaliacao VARCHAR(30) NOT NULL,
    descricao VARCHAR(200),
    valor DOUBLE PRECISION NOT NULL,
    valor_maximo DOUBLE PRECISION,
    peso DOUBLE PRECISION,
    bimestre INTEGER,
    registrado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id),
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


-- Tabela: arquivos
CREATE TABLE IF NOT EXISTS arquivos (
    id SERIAL,
    nome_original VARCHAR(255) NOT NULL,
    nome_armazenado VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    tamanho INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (professor_id) REFERENCES professores(id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id)
);


-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE UNIQUE INDEX IF NOT EXISTS ix_alunos_matricula ON alunos (matricula);
CREATE UNIQUE INDEX IF NOT EXISTS ix_alunos_cpf ON alunos (cpf) WHERE cpf IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios (email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_registro ON professores (registro);
CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_cpf ON professores (cpf) WHERE cpf IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_usuario_id ON professores (usuario_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_turmas_codigo ON turmas (codigo);
CREATE UNIQUE INDEX IF NOT EXISTS ix_materias_codigo ON materias (codigo);
CREATE UNIQUE INDEX IF NOT EXISTS ix_materias_nome ON materias (nome);
CREATE UNIQUE INDEX IF NOT EXISTS ix_feriados_data ON feriados (data);


-- ============================================================
-- INSERIR DADOS
-- ============================================================

-- Desabilitar verificação de FKs temporariamente
SET session_replication_role = replica;

-- Dados: usuarios (13 registros)
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('João Silva', 'joao@escola.com', 'scrypt:32768:8:1$9Ur1lFEqUVjIXyiL$ef62da1c59f718ed37992ec17e29281f4b0f3ff106a7ac58a39e4fbfeca714cd7a379413c2d36fc6f19e13920f9ec7293def017db374bc022a7fe90efd721390', 'diretora', NULL, NULL, 'dark', TRUE, '2026-03-27 10:33:51.364935', '2026-03-28 11:03:03.334202', '2026-03-28 11:03:03.332148');
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Maria Santos', 'maria@escola.com', 'scrypt:32768:8:1$2Wg40TNBynd9RhOV$f3f95d85c02deb16498595d22796972e16aba214f0ab000b9aaa66bd33ac35c8ff9d4e283b9b0a2e6b648ff4518e23ece0532c971e4a5f1a1fb9f9057d8b4646', 'professor', NULL, NULL, 'light', TRUE, '2026-03-27 10:33:51.530326', '2026-03-27 10:33:51.530329', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Carlos Oliveira', 'carlos@escola.com', 'scrypt:32768:8:1$N8Wn3eRNHA6VQXql$4cb57ca9640971c081b9b2a38122f9accdd6327f5d56ccd51f5103f48abff288f721465ced048354c976c59ef22b084c6109403478982dbc83f5c233a86ffe91', 'professor', NULL, NULL, 'light', TRUE, '2026-03-27 10:33:51.676950', '2026-03-27 10:33:51.676955', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Ana Costa', 'ana@escola.com', 'scrypt:32768:8:1$CsPeIrgDkmEZV2gZ$9ef909042cf326e2e8f5080684fb08947d3e56125501716d21cd9e98d57ae9ab1bd0439a3b6cc2ed9d8ae84a1ef5880cbc77a8c507aea2923cfe4ae231434455', 'professor', NULL, NULL, 'light', TRUE, '2026-03-27 10:33:51.807693', '2026-03-27 10:33:51.807697', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Paula Mendes', 'coordenacao@escola.com', 'scrypt:32768:8:1$JW7G8983ceI7CYz7$312836eb2bfb27e7ddee8f1172fb09ebe75716dffb26aaa81368017fb2971baf3c5aecbe61b7efeab7448125df6d004a0f6835c044c4d8babeef6ae5f14d8c2c', 'coordenacao', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.135862', '2026-03-28 03:17:20.135865', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Roberto Lima', 'roberto@escola.com', 'scrypt:32768:8:1$NjxGrzsG1N6QlNr9$417ee25943e2b218dc70aa21d50ffffad32633d2a0221c5da9597f00df55f1b92733376faf00e79b14078c2441b763c11d146fd8ed891cc3ee77a9d33e732936', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.311213', '2026-03-28 03:17:20.311216', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Juliana Ferreira', 'juliana@escola.com', 'scrypt:32768:8:1$sa6EboRXfZqmLj6X$4afd1b1c762bfc19f216fc48f8bc41dda23536c06c6d80a543d07be8a1ccb245dd3222c4b1e2409074b4a1205fc4f3335ceb8e3da568501f91a04c445603f0a3', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.454507', '2026-03-28 03:17:20.454512', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Marcos Paulo', 'marcos@escola.com', 'scrypt:32768:8:1$8PyMnGOsCP7cNjpo$9b0625e82d1115f4de84f21d520d0ba8898f4031e712cac8e9791d3f1c9edfc570f64c1af3d079e6dda8e43ee156bd827c1578737e2bedfe75edb1bc43e8ae64', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.581031', '2026-03-28 03:17:20.581034', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Patricia Silva', 'patricia@escola.com', 'scrypt:32768:8:1$1ozwWJ6lPBzDqXQh$ec400ee87fc82e0ca7ebbc889913a9441f4620a02de8d5862ca56eb0a07b9df56b88adc1d6f45999e20b3a3f07b96185a817df3d62b71acd8bd29d2f2da41f40', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.708161', '2026-03-28 03:17:20.708165', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Fernando Alves', 'fernando@escola.com', 'scrypt:32768:8:1$fevCgZtI3pNo7Pll$898c989303397c91955eaf76798a514c71c3b24a664b5eea033fdcc872960fb6ed31351f4f26357a476259baa51d4a28b0fba2ced4eefb0197b9035b73ac2c55', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.833508', '2026-03-28 03:17:20.833511', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Carla Rodrigues', 'carla@escola.com', 'scrypt:32768:8:1$8q3rrJQeTqQn3bVD$87bb7745039710c3644fd1a83a4cb357e17b282c26a000bd6381dda46920b8afc770f5575bdc256a28ed95132761ff365920c2db3ac42fab683403b3a615b137', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:20.966718', '2026-03-28 03:17:20.966721', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('Ricardo Souza', 'ricardo@escola.com', 'scrypt:32768:8:1$bjNIMJdS8kDrbdp2$36133c32827bf81d6187d1eff8aa2dc6dd561edacd75eabe7d0abcdc7cbecdcd54762732e2590821612d240bac6dbf92f3a568f7909cf416736f72ffc97e347a', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:21.112668', '2026-03-28 03:17:21.112672', NULL);
INSERT INTO usuarios (nome, email, senha_hash, tipo, avatar, telefone, tema, ativo, criado_em, atualizado_em, ultimo_acesso) VALUES ('João Professor', 'joao@prof.com', 'scrypt:32768:8:1$SLImIYsBq27YxYU7$30d0c42af72fc8666df5464750266ded5d94deb242ff7456e92b92f50159f0af0dc0e5a314f6b2b5f971aad4319f50adbf4d55b01971acbc6fd2187ab087490c', 'professor', NULL, NULL, 'light', TRUE, '2026-03-28 03:17:21.239716', '2026-03-28 03:28:39.853795', '2026-03-28 03:28:39.853224');

-- Dados: materias (7 registros)
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Matemática', 'MAT', NULL, 200, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Português', 'PORT', NULL, 200, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Ciências', 'CIE', NULL, 100, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('História', 'HIST', NULL, 100, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Geografia', 'GEO', NULL, 100, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Inglês', 'ING', NULL, 80, TRUE);
INSERT INTO materias (nome, codigo, descricao, carga_horaria, ativa) VALUES ('Ed. Física', 'EDFIS', NULL, 80, TRUE);

-- Dados: feriados (10 registros)
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Ano Novo', '2024-01-01', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.979410', '2026-03-27 10:33:51.979414');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Carnaval', '2024-02-12', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.981050', '2026-03-27 10:33:51.981053');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Páscoa', '2024-03-31', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.983699', '2026-03-27 10:33:51.983702');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Tiradentes', '2024-04-21', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.985173', '2026-03-27 10:33:51.985176');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Dia do Trabalho', '2024-05-01', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.986416', '2026-03-27 10:33:51.986418');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Independência', '2024-09-07', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.987485', '2026-03-27 10:33:51.987487');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Nossa Sra. Aparecida', '2024-10-12', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.988563', '2026-03-27 10:33:51.988565');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Finados', '2024-11-02', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.989663', '2026-03-27 10:33:51.989666');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Proclamação da República', '2024-11-15', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.990772', '2026-03-27 10:33:51.990774');
INSERT INTO feriados (nome, data, tipo, descricao, recorrente, criado_em, atualizado_em) VALUES ('Natal', '2024-12-25', 'nacional', NULL, TRUE, '2026-03-27 10:33:51.991643', '2026-03-27 10:33:51.991645');

-- Nenhum registro para inserir em dias_nao_letivos


-- Dados: alunos (126 registros)
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Pedro Henrique', 'ALU001', NULL, NULL, 'pedro@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.865164', '2026-03-27 10:33:51.865167');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Julia Oliveira', 'ALU002', NULL, NULL, 'julia@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.866758', '2026-03-27 10:33:51.866760');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Lucas Silva', 'ALU003', NULL, NULL, 'lucas@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.867920', '2026-03-27 10:33:51.867922');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Mariana Costa', 'ALU004', NULL, NULL, 'mariana@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.868916', '2026-03-27 10:33:51.868918');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gabriel Santos', 'ALU005', NULL, NULL, 'gabriel@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.869954', '2026-03-27 10:33:51.869956');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Isabela Lima', 'ALU006', NULL, NULL, 'isabela@email.com', NULL, NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-27 10:33:51.870897', '2026-03-27 10:33:51.870899');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Pedro Henrique Silva', 'ALU00001', NULL, NULL, 'aluno1@email.com', '99999-1000', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.333265', '2026-03-28 03:17:21.333269');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Julia Oliveira Oliveira', 'ALU00002', NULL, NULL, 'aluno2@email.com', '99999-1001', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.335698', '2026-03-28 03:17:21.335701');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Lucas Silva Santos', 'ALU00003', NULL, NULL, 'aluno3@email.com', '99999-1002', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.337166', '2026-03-28 03:17:21.337168');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Mariana Costa Costa', 'ALU00004', NULL, NULL, 'aluno4@email.com', '99999-1003', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.338623', '2026-03-28 03:17:21.338627');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gabriel Santos Lima', 'ALU00005', NULL, NULL, 'aluno5@email.com', '99999-1004', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.339997', '2026-03-28 03:17:21.339999');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Isabela Lima Mendes', 'ALU00006', NULL, NULL, 'aluno6@email.com', '99999-1005', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.341343', '2026-03-28 03:17:21.341345');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Bruno Almeida Rodrigues', 'ALU00007', NULL, NULL, 'aluno7@email.com', '99999-1006', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.342762', '2026-03-28 03:17:21.342764');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Carla Rodrigues Ferreira', 'ALU00008', NULL, NULL, 'aluno8@email.com', '99999-1007', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.344220', '2026-03-28 03:17:21.344222');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Daniel Pereira Almeida', 'ALU00009', NULL, NULL, 'aluno9@email.com', '99999-1008', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.345591', '2026-03-28 03:17:21.345594');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Eduarda Castro Sousa', 'ALU00010', NULL, NULL, 'aluno10@email.com', '99999-1009', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.346860', '2026-03-28 03:17:21.346862');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Felipe Martins Gomes', 'ALU00011', NULL, NULL, 'aluno11@email.com', '99999-1010', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.348109', '2026-03-28 03:17:21.348111');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gabriela Nunes Carvalho', 'ALU00012', NULL, NULL, 'aluno12@email.com', '99999-1011', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.349379', '2026-03-28 03:17:21.349381');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Hugo Ferreira Martins', 'ALU00013', NULL, NULL, 'aluno13@email.com', '99999-1012', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.350580', '2026-03-28 03:17:21.350581');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Isadora Araujo Rocha', 'ALU00014', NULL, NULL, 'aluno14@email.com', '99999-1013', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.351750', '2026-03-28 03:17:21.351751');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('João Pedro Azevedo', 'ALU00015', NULL, NULL, 'aluno15@email.com', '99999-1014', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.352875', '2026-03-28 03:17:21.352877');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Karina Tavares Pereira', 'ALU00016', NULL, NULL, 'aluno16@email.com', '99999-1015', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.353989', '2026-03-28 03:17:21.353991');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Leonardo Campos Ribeiro', 'ALU00017', NULL, NULL, 'aluno17@email.com', '99999-1016', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.355104', '2026-03-28 03:17:21.355106');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Marina Dias Cardoso', 'ALU00018', NULL, NULL, 'aluno18@email.com', '99999-1017', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.356187', '2026-03-28 03:17:21.356189');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Nicolas Souza Fernandes', 'ALU00019', NULL, NULL, 'aluno19@email.com', '99999-1018', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.357269', '2026-03-28 03:17:21.357271');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Olivia Lima Barbosa', 'ALU00020', NULL, NULL, 'aluno20@email.com', '99999-1019', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.358352', '2026-03-28 03:17:21.358360');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Paulo Ricardo Rosa', 'ALU00021', NULL, NULL, 'aluno21@email.com', '99999-1020', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.359397', '2026-03-28 03:17:21.359399');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Quiteria Santos Correia', 'ALU00022', NULL, NULL, 'aluno22@email.com', '99999-1021', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.360443', '2026-03-28 03:17:21.360444');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Rafael Costa Dias', 'ALU00023', NULL, NULL, 'aluno23@email.com', '99999-1022', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.361860', '2026-03-28 03:17:21.361863');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Sofia Mendes Castro', 'ALU00024', NULL, NULL, 'aluno24@email.com', '99999-1023', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.363400', '2026-03-28 03:17:21.363402');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Thiago Oliveira Silva', 'ALU00025', NULL, NULL, 'aluno25@email.com', '99999-1024', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.364911', '2026-03-28 03:17:21.364913');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Ursula Ferreira Oliveira', 'ALU00026', NULL, NULL, 'aluno26@email.com', '99999-1025', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.366015', '2026-03-28 03:17:21.366017');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Vinícius Silva Santos', 'ALU00027', NULL, NULL, 'aluno27@email.com', '99999-1026', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.367273', '2026-03-28 03:17:21.367274');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Wilian Santos Costa', 'ALU00028', NULL, NULL, 'aluno28@email.com', '99999-1027', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.368301', '2026-03-28 03:17:21.368302');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Xuxa Rodrigues Lima', 'ALU00029', NULL, NULL, 'aluno29@email.com', '99999-1028', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.369332', '2026-03-28 03:17:21.369334');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Yasmin Costa Mendes', 'ALU00030', NULL, NULL, 'aluno30@email.com', '99999-1029', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.370340', '2026-03-28 03:17:21.370341');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Zilda Lima Rodrigues', 'ALU00031', NULL, NULL, 'aluno31@email.com', '99999-1030', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.371377', '2026-03-28 03:17:21.371379');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('André Silva Ferreira', 'ALU00032', NULL, NULL, 'aluno32@email.com', '99999-1031', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.372519', '2026-03-28 03:17:21.372520');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Bruna Oliveira Almeida', 'ALU00033', NULL, NULL, 'aluno33@email.com', '99999-1032', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.373585', '2026-03-28 03:17:21.373587');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Caio Santos Sousa', 'ALU00034', NULL, NULL, 'aluno34@email.com', '99999-1033', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.374632', '2026-03-28 03:17:21.374633');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Débora Costa Gomes', 'ALU00035', NULL, NULL, 'aluno35@email.com', '99999-1034', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.375705', '2026-03-28 03:17:21.375707');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Eduardo Mendes Carvalho', 'ALU00036', NULL, NULL, 'aluno36@email.com', '99999-1035', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.376973', '2026-03-28 03:17:21.376975');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Fernanda Lima Martins', 'ALU00037', NULL, NULL, 'aluno37@email.com', '99999-1036', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.378259', '2026-03-28 03:17:21.378260');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gustavo Oliveira Rocha', 'ALU00038', NULL, NULL, 'aluno38@email.com', '99999-1037', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.379473', '2026-03-28 03:17:21.379474');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Helena Santos Azevedo', 'ALU00039', NULL, NULL, 'aluno39@email.com', '99999-1038', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.380549', '2026-03-28 03:17:21.380551');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Igor Costa Pereira', 'ALU00040', NULL, NULL, 'aluno40@email.com', '99999-1039', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.381668', '2026-03-28 03:17:21.381670');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Júlia Pereira Ribeiro', 'ALU00041', NULL, NULL, 'aluno41@email.com', '99999-1040', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.382788', '2026-03-28 03:17:21.382789');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Kleber Rodrigues Cardoso', 'ALU00042', NULL, NULL, 'aluno42@email.com', '99999-1041', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.384093', '2026-03-28 03:17:21.384095');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Larissa Silva Fernandes', 'ALU00043', NULL, NULL, 'aluno43@email.com', '99999-1042', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.385223', '2026-03-28 03:17:21.385224');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Mateus Oliveira Barbosa', 'ALU00044', NULL, NULL, 'aluno44@email.com', '99999-1043', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.386433', '2026-03-28 03:17:21.386435');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Natália Santos Rosa', 'ALU00045', NULL, NULL, 'aluno45@email.com', '99999-1044', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.387548', '2026-03-28 03:17:21.387549');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Otávio Costa Correia', 'ALU00046', NULL, NULL, 'aluno46@email.com', '99999-1045', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.388721', '2026-03-28 03:17:21.388723');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Paula Lima Dias', 'ALU00047', NULL, NULL, 'aluno47@email.com', '99999-1046', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.389844', '2026-03-28 03:17:21.389846');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Quentinhas Santos Castro', 'ALU00048', NULL, NULL, 'aluno48@email.com', '99999-1047', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.390933', '2026-03-28 03:17:21.390935');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Renata Oliveira Silva', 'ALU00049', NULL, NULL, 'aluno49@email.com', '99999-1048', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.392123', '2026-03-28 03:17:21.392125');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Samira Costa Oliveira', 'ALU00050', NULL, NULL, 'aluno50@email.com', '99999-1049', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.393256', '2026-03-28 03:17:21.393257');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Túlio Silva Santos', 'ALU00051', NULL, NULL, 'aluno51@email.com', '99999-1050', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.394756', '2026-03-28 03:17:21.394758');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Úrsula Mendes Costa', 'ALU00052', NULL, NULL, 'aluno52@email.com', '99999-1051', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.396285', '2026-03-28 03:17:21.396287');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Vagner Oliveira Lima', 'ALU00053', NULL, NULL, 'aluno53@email.com', '99999-1052', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.397733', '2026-03-28 03:17:21.397734');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Wellington Santos Mendes', 'ALU00054', NULL, NULL, 'aluno54@email.com', '99999-1053', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.398876', '2026-03-28 03:17:21.398878');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Xiomara Costa Rodrigues', 'ALU00055', NULL, NULL, 'aluno55@email.com', '99999-1054', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.399985', '2026-03-28 03:17:21.399987');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Yuri Lima Ferreira', 'ALU00056', NULL, NULL, 'aluno56@email.com', '99999-1055', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.401066', '2026-03-28 03:17:21.401068');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Zuleica Oliveira Almeida', 'ALU00057', NULL, NULL, 'aluno57@email.com', '99999-1056', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.402107', '2026-03-28 03:17:21.402109');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Adriano Santos Sousa', 'ALU00058', NULL, NULL, 'aluno58@email.com', '99999-1057', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.403177', '2026-03-28 03:17:21.403178');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Bianca Costa Gomes', 'ALU00059', NULL, NULL, 'aluno59@email.com', '99999-1058', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.404268', '2026-03-28 03:17:21.404269');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Celso Mendes Carvalho', 'ALU00060', NULL, NULL, 'aluno60@email.com', '99999-1059', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.405558', '2026-03-28 03:17:21.405560');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Daniella Oliveira Martins', 'ALU00061', NULL, NULL, 'aluno61@email.com', '99999-1060', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.406624', '2026-03-28 03:17:21.406625');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Evandro Silva Rocha', 'ALU00062', NULL, NULL, 'aluno62@email.com', '99999-1061', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.407562', '2026-03-28 03:17:21.407564');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Flávia Costa Azevedo', 'ALU00063', NULL, NULL, 'aluno63@email.com', '99999-1062', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.408496', '2026-03-28 03:17:21.408498');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gilberto Santos Pereira', 'ALU00064', NULL, NULL, 'aluno64@email.com', '99999-1063', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.409538', '2026-03-28 03:17:21.409539');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Helô Lima Ribeiro', 'ALU00065', NULL, NULL, 'aluno65@email.com', '99999-1064', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.410619', '2026-03-28 03:17:21.410621');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Ivo Oliveira Cardoso', 'ALU00066', NULL, NULL, 'aluno66@email.com', '99999-1065', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.411603', '2026-03-28 03:17:21.411605');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Josiane Santos Fernandes', 'ALU00067', NULL, NULL, 'aluno67@email.com', '99999-1066', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.412597', '2026-03-28 03:17:21.412599');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Karla Costa Barbosa', 'ALU00068', NULL, NULL, 'aluno68@email.com', '99999-1067', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.413612', '2026-03-28 03:17:21.413614');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Leandro Oliveira Rosa', 'ALU00069', NULL, NULL, 'aluno69@email.com', '99999-1068', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.414910', '2026-03-28 03:17:21.414912');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Miriam Santos Correia', 'ALU00070', NULL, NULL, 'aluno70@email.com', '99999-1069', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.416074', '2026-03-28 03:17:21.416075');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Nelson Costa Dias', 'ALU00071', NULL, NULL, 'aluno71@email.com', '99999-1070', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.417149', '2026-03-28 03:17:21.417150');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Osvaldo Lima Castro', 'ALU00072', NULL, NULL, 'aluno72@email.com', '99999-1071', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.418192', '2026-03-28 03:17:21.418194');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Pamela Oliveira Silva', 'ALU00073', NULL, NULL, 'aluno73@email.com', '99999-1072', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.419292', '2026-03-28 03:17:21.419293');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Queen Santos Oliveira', 'ALU00074', NULL, NULL, 'aluno74@email.com', '99999-1073', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.420284', '2026-03-28 03:17:21.420285');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Rita Costa Santos', 'ALU00075', NULL, NULL, 'aluno75@email.com', '99999-1074', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.421220', '2026-03-28 03:17:21.421222');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Sérgio Lima Costa', 'ALU00076', NULL, NULL, 'aluno76@email.com', '99999-1075', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.422191', '2026-03-28 03:17:21.422193');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Terezinha Oliveira Lima', 'ALU00077', NULL, NULL, 'aluno77@email.com', '99999-1076', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.423222', '2026-03-28 03:17:21.423223');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Ulisses Santos Mendes', 'ALU00078', NULL, NULL, 'aluno78@email.com', '99999-1077', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.424261', '2026-03-28 03:17:21.424263');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Valéria Costa Rodrigues', 'ALU00079', NULL, NULL, 'aluno79@email.com', '99999-1078', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.425196', '2026-03-28 03:17:21.425198');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Washington Lima Ferreira', 'ALU00080', NULL, NULL, 'aluno80@email.com', '99999-1079', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.426200', '2026-03-28 03:17:21.426202');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Xenia Oliveira Almeida', 'ALU00081', NULL, NULL, 'aluno81@email.com', '99999-1080', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.427277', '2026-03-28 03:17:21.427279');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Yago Santos Sousa', 'ALU00082', NULL, NULL, 'aluno82@email.com', '99999-1081', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.428354', '2026-03-28 03:17:21.428355');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Zilda Maria Gomes', 'ALU00083', NULL, NULL, 'aluno83@email.com', '99999-1082', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.429303', '2026-03-28 03:17:21.429305');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Albino Costa Carvalho', 'ALU00084', NULL, NULL, 'aluno84@email.com', '99999-1083', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.430229', '2026-03-28 03:17:21.430231');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Berenice Lima Martins', 'ALU00085', NULL, NULL, 'aluno85@email.com', '99999-1084', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.431237', '2026-03-28 03:17:21.431239');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Cláudio Oliveira Rocha', 'ALU00086', NULL, NULL, 'aluno86@email.com', '99999-1085', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.432282', '2026-03-28 03:17:21.432284');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Denise Santos Azevedo', 'ALU00087', NULL, NULL, 'aluno87@email.com', '99999-1086', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.433348', '2026-03-28 03:17:21.433349');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Elton Costa Pereira', 'ALU00088', NULL, NULL, 'aluno88@email.com', '99999-1087', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.434313', '2026-03-28 03:17:21.434315');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Fernanda Maria Ribeiro', 'ALU00089', NULL, NULL, 'aluno89@email.com', '99999-1088', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.435309', '2026-03-28 03:17:21.435311');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Marcos Vinícius Cardoso', 'ALU00090', NULL, NULL, 'aluno90@email.com', '99999-1089', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.436305', '2026-03-28 03:17:21.436307');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Pedro Henrique Fernandes', 'ALU00091', NULL, NULL, 'aluno91@email.com', '99999-1090', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.437402', '2026-03-28 03:17:21.437404');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Julia Oliveira Barbosa', 'ALU00092', NULL, NULL, 'aluno92@email.com', '99999-1091', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.438383', '2026-03-28 03:17:21.438384');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Lucas Silva Rosa', 'ALU00093', NULL, NULL, 'aluno93@email.com', '99999-1092', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.439441', '2026-03-28 03:17:21.439443');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Mariana Costa Correia', 'ALU00094', NULL, NULL, 'aluno94@email.com', '99999-1093', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.440581', '2026-03-28 03:17:21.440583');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gabriel Santos Dias', 'ALU00095', NULL, NULL, 'aluno95@email.com', '99999-1094', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.441656', '2026-03-28 03:17:21.441657');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Isabela Lima Castro', 'ALU00096', NULL, NULL, 'aluno96@email.com', '99999-1095', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.442748', '2026-03-28 03:17:21.442749');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Bruno Almeida Silva', 'ALU00097', NULL, NULL, 'aluno97@email.com', '99999-1096', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.443903', '2026-03-28 03:17:21.443905');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Carla Rodrigues Oliveira', 'ALU00098', NULL, NULL, 'aluno98@email.com', '99999-1097', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.445060', '2026-03-28 03:17:21.445062');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Daniel Pereira Santos', 'ALU00099', NULL, NULL, 'aluno99@email.com', '99999-1098', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.446098', '2026-03-28 03:17:21.446100');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Eduarda Castro Costa', 'ALU00100', NULL, NULL, 'aluno100@email.com', '99999-1099', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.447196', '2026-03-28 03:17:21.447198');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Felipe Martins Lima', 'ALU00101', NULL, NULL, 'aluno101@email.com', '99999-1100', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.448291', '2026-03-28 03:17:21.448293');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Gabriela Nunes Mendes', 'ALU00102', NULL, NULL, 'aluno102@email.com', '99999-1101', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.449415', '2026-03-28 03:17:21.449417');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Hugo Ferreira Rodrigues', 'ALU00103', NULL, NULL, 'aluno103@email.com', '99999-1102', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.450491', '2026-03-28 03:17:21.450493');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Isadora Araujo Ferreira', 'ALU00104', NULL, NULL, 'aluno104@email.com', '99999-1103', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.451600', '2026-03-28 03:17:21.451601');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('João Pedro Almeida', 'ALU00105', NULL, NULL, 'aluno105@email.com', '99999-1104', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.452648', '2026-03-28 03:17:21.452650');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Karina Tavares Sousa', 'ALU00106', NULL, NULL, 'aluno106@email.com', '99999-1105', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.453805', '2026-03-28 03:17:21.453806');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Leonardo Campos Gomes', 'ALU00107', NULL, NULL, 'aluno107@email.com', '99999-1106', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.455117', '2026-03-28 03:17:21.455118');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Marina Dias Carvalho', 'ALU00108', NULL, NULL, 'aluno108@email.com', '99999-1107', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.456213', '2026-03-28 03:17:21.456215');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Nicolas Souza Martins', 'ALU00109', NULL, NULL, 'aluno109@email.com', '99999-1108', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.457342', '2026-03-28 03:17:21.457343');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Olivia Lima Rocha', 'ALU00110', NULL, NULL, 'aluno110@email.com', '99999-1109', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.458471', '2026-03-28 03:17:21.458472');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Paulo Ricardo Azevedo', 'ALU00111', NULL, NULL, 'aluno111@email.com', '99999-1110', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.459651', '2026-03-28 03:17:21.459653');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Quiteria Santos Pereira', 'ALU00112', NULL, NULL, 'aluno112@email.com', '99999-1111', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.461045', '2026-03-28 03:17:21.461048');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Rafael Costa Ribeiro', 'ALU00113', NULL, NULL, 'aluno113@email.com', '99999-1112', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.462344', '2026-03-28 03:17:21.462345');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Sofia Mendes Cardoso', 'ALU00114', NULL, NULL, 'aluno114@email.com', '99999-1113', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.463387', '2026-03-28 03:17:21.463389');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Thiago Oliveira Fernandes', 'ALU00115', NULL, NULL, 'aluno115@email.com', '99999-1114', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.464494', '2026-03-28 03:17:21.464495');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Ursula Ferreira Barbosa', 'ALU00116', NULL, NULL, 'aluno116@email.com', '99999-1115', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.465700', '2026-03-28 03:17:21.465703');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Vinícius Silva Rosa', 'ALU00117', NULL, NULL, 'aluno117@email.com', '99999-1116', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.466754', '2026-03-28 03:17:21.466755');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Wilian Santos Correia', 'ALU00118', NULL, NULL, 'aluno118@email.com', '99999-1117', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.467767', '2026-03-28 03:17:21.467769');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Xuxa Rodrigues Dias', 'ALU00119', NULL, NULL, 'aluno119@email.com', '99999-1118', NULL, NULL, NULL, NULL, 2024, 'ativo', '2026-03-28 03:17:21.468819', '2026-03-28 03:17:21.468821');
INSERT INTO alunos (nome, matricula, data_nascimento, cpf, email, telefone, endereco, nome_responsavel, telefone_responsavel, email_responsavel, ano_letivo, status, criado_em, atualizado_em) VALUES ('Yasmin Costa Castro', 'ALU00120', NULL, NULL, 'aluno120@email.com', '99999-1119', NULL, NULL, NULL, NULL, 2024, 'inativo', '2026-03-28 03:17:21.469668', '2026-03-28 03:17:21.469669');

-- Dados: turmas (7 registros)
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('1º Ano A', '1A2024', '1º Ano', 2024, 'manha', 35, NULL, TRUE, '2026-03-27 10:33:51.836261', '2026-03-27 10:33:51.836274');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('2º Ano B', '2B2024', '2º Ano', 2024, 'tarde', 30, NULL, TRUE, '2026-03-27 10:33:51.837882', '2026-03-27 10:33:51.837884');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('3º Ano C', '3C2024', '3º Ano', 2024, 'manha', 40, NULL, TRUE, '2026-03-27 10:33:51.838753', '2026-03-27 10:33:51.838755');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('1º Ano B', '1B2024', '1º Ano', 2024, 'tarde', 30, NULL, TRUE, '2026-03-28 03:17:21.298596', '2026-03-28 03:17:21.298600');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('2º Ano A', '2A2024', '2º Ano', 2024, 'manha', 35, NULL, TRUE, '2026-03-28 03:17:21.300201', '2026-03-28 03:17:21.300203');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('3º Ano A', '3A2024', '3º Ano', 2024, 'manha', 35, NULL, TRUE, '2026-03-28 03:17:21.301860', '2026-03-28 03:17:21.301862');
INSERT INTO turmas (nome, codigo, serie, ano_letivo, turno, capacidade_maxima, descricao, ativa, criado_em, atualizado_em) VALUES ('3º Ano B', '3B2024', '3º Ano', 2024, 'tarde', 30, NULL, TRUE, '2026-03-28 03:17:21.302830', '2026-03-28 03:17:21.302832');

-- Dados: professores (11 registros)
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (2, 'PROF001', 'Matemática', NULL, NULL, NULL, NULL, TRUE, '2026-03-27 10:33:51.535452', '2026-03-27 10:33:51.535454');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (3, 'PROF002', 'Português', NULL, NULL, NULL, NULL, TRUE, '2026-03-27 10:33:51.678560', '2026-03-27 10:33:51.678562');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (4, 'PROF003', 'Ciências', NULL, NULL, NULL, NULL, TRUE, '2026-03-27 10:33:51.808958', '2026-03-27 10:33:51.808960');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (6, 'PROF004', 'História', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.314068', '2026-03-28 03:17:20.314070');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (7, 'PROF005', 'Geografia', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.456199', '2026-03-28 03:17:20.456202');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (8, 'PROF006', 'Ed. Física', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.582649', '2026-03-28 03:17:20.582651');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (9, 'PROF007', 'Inglês', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.709604', '2026-03-28 03:17:20.709606');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (10, 'PROF008', 'Matemática', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.834949', '2026-03-28 03:17:20.834951');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (11, 'PROF009', 'Português', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:20.968258', '2026-03-28 03:17:20.968260');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (12, 'PROF010', 'Ciências', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:21.114275', '2026-03-28 03:17:21.114276');
INSERT INTO professores (usuario_id, registro, especialidade, formacao, cpf, telefone, endereco, ativo, criado_em, atualizado_em) VALUES (13, 'PROF011', 'História', NULL, NULL, NULL, NULL, TRUE, '2026-03-28 03:17:21.241326', '2026-03-28 03:17:21.241328');

-- Dados: alunos_turmas (126 registros)
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (1, 1, '2026-03-27 10:33:51.902449');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (2, 2, '2026-03-27 10:33:51.906013');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (3, 3, '2026-03-27 10:33:51.909001');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (4, 1, '2026-03-27 10:33:51.911465');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (5, 2, '2026-03-27 10:33:51.913835');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (6, 3, '2026-03-27 10:33:51.916678');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (7, 4, '2026-03-28 03:17:21.502586');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (8, 4, '2026-03-28 03:17:21.505320');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (9, 4, '2026-03-28 03:17:21.507755');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (10, 4, '2026-03-28 03:17:21.510156');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (11, 4, '2026-03-28 03:17:21.512920');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (12, 4, '2026-03-28 03:17:21.515960');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (13, 4, '2026-03-28 03:17:21.518352');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (14, 4, '2026-03-28 03:17:21.520804');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (15, 4, '2026-03-28 03:17:21.523239');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (16, 4, '2026-03-28 03:17:21.525781');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (17, 4, '2026-03-28 03:17:21.528325');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (18, 4, '2026-03-28 03:17:21.531277');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (19, 4, '2026-03-28 03:17:21.533763');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (20, 4, '2026-03-28 03:17:21.536215');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (21, 4, '2026-03-28 03:17:21.538741');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (22, 4, '2026-03-28 03:17:21.541038');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (23, 4, '2026-03-28 03:17:21.543616');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (24, 4, '2026-03-28 03:17:21.546255');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (25, 4, '2026-03-28 03:17:21.548764');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (26, 4, '2026-03-28 03:17:21.551163');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (27, 4, '2026-03-28 03:17:21.553645');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (28, 4, '2026-03-28 03:17:21.556230');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (29, 4, '2026-03-28 03:17:21.559298');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (30, 4, '2026-03-28 03:17:21.561896');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (31, 4, '2026-03-28 03:17:21.564503');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (32, 4, '2026-03-28 03:17:21.567268');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (33, 4, '2026-03-28 03:17:21.569983');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (34, 4, '2026-03-28 03:17:21.572587');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (35, 4, '2026-03-28 03:17:21.575274');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (36, 4, '2026-03-28 03:17:21.578039');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (37, 5, '2026-03-28 03:17:21.581237');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (38, 5, '2026-03-28 03:17:21.583382');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (39, 5, '2026-03-28 03:17:21.585658');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (40, 5, '2026-03-28 03:17:21.587855');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (41, 5, '2026-03-28 03:17:21.590072');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (42, 5, '2026-03-28 03:17:21.592337');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (43, 5, '2026-03-28 03:17:21.594550');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (44, 5, '2026-03-28 03:17:21.596765');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (45, 5, '2026-03-28 03:17:21.599267');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (46, 5, '2026-03-28 03:17:21.601496');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (47, 5, '2026-03-28 03:17:21.603802');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (48, 5, '2026-03-28 03:17:21.606224');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (49, 5, '2026-03-28 03:17:21.608471');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (50, 5, '2026-03-28 03:17:21.610822');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (51, 5, '2026-03-28 03:17:21.613603');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (52, 5, '2026-03-28 03:17:21.615974');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (53, 5, '2026-03-28 03:17:21.618383');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (54, 5, '2026-03-28 03:17:21.620781');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (55, 5, '2026-03-28 03:17:21.623326');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (56, 5, '2026-03-28 03:17:21.625967');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (57, 5, '2026-03-28 03:17:21.628406');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (58, 5, '2026-03-28 03:17:21.631073');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (59, 5, '2026-03-28 03:17:21.633809');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (60, 5, '2026-03-28 03:17:21.636787');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (61, 5, '2026-03-28 03:17:21.639292');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (62, 5, '2026-03-28 03:17:21.641790');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (63, 5, '2026-03-28 03:17:21.644271');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (64, 5, '2026-03-28 03:17:21.646761');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (65, 5, '2026-03-28 03:17:21.649409');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (66, 5, '2026-03-28 03:17:21.651940');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (67, 6, '2026-03-28 03:17:21.654595');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (68, 6, '2026-03-28 03:17:21.656762');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (69, 6, '2026-03-28 03:17:21.659328');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (70, 6, '2026-03-28 03:17:21.661698');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (71, 6, '2026-03-28 03:17:21.664298');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (72, 6, '2026-03-28 03:17:21.666572');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (73, 6, '2026-03-28 03:17:21.668924');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (74, 6, '2026-03-28 03:17:21.671189');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (75, 6, '2026-03-28 03:17:21.673640');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (76, 6, '2026-03-28 03:17:21.676429');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (77, 6, '2026-03-28 03:17:21.678846');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (78, 6, '2026-03-28 03:17:21.681272');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (79, 6, '2026-03-28 03:17:21.683783');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (80, 6, '2026-03-28 03:17:21.686624');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (81, 6, '2026-03-28 03:17:21.689048');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (82, 6, '2026-03-28 03:17:21.691335');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (83, 6, '2026-03-28 03:17:21.693833');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (84, 6, '2026-03-28 03:17:21.696117');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (85, 6, '2026-03-28 03:17:21.698405');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (86, 6, '2026-03-28 03:17:21.700717');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (87, 6, '2026-03-28 03:17:21.703034');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (88, 6, '2026-03-28 03:17:21.705359');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (89, 6, '2026-03-28 03:17:21.707745');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (90, 6, '2026-03-28 03:17:21.710119');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (91, 6, '2026-03-28 03:17:21.712476');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (92, 6, '2026-03-28 03:17:21.714873');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (93, 6, '2026-03-28 03:17:21.717294');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (94, 6, '2026-03-28 03:17:21.720077');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (95, 6, '2026-03-28 03:17:21.722577');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (96, 6, '2026-03-28 03:17:21.725167');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (97, 7, '2026-03-28 03:17:21.727697');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (98, 7, '2026-03-28 03:17:21.729805');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (99, 7, '2026-03-28 03:17:21.732295');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (100, 7, '2026-03-28 03:17:21.734479');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (101, 7, '2026-03-28 03:17:21.736666');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (102, 7, '2026-03-28 03:17:21.738879');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (103, 7, '2026-03-28 03:17:21.741089');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (104, 7, '2026-03-28 03:17:21.743332');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (105, 7, '2026-03-28 03:17:21.745965');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (106, 7, '2026-03-28 03:17:21.748215');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (107, 7, '2026-03-28 03:17:21.750455');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (108, 7, '2026-03-28 03:17:21.752690');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (109, 7, '2026-03-28 03:17:21.754960');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (110, 7, '2026-03-28 03:17:21.757263');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (111, 7, '2026-03-28 03:17:21.759800');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (112, 7, '2026-03-28 03:17:21.762302');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (113, 7, '2026-03-28 03:17:21.764595');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (114, 7, '2026-03-28 03:17:21.766917');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (115, 7, '2026-03-28 03:17:21.769311');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (116, 7, '2026-03-28 03:17:21.771610');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (117, 7, '2026-03-28 03:17:21.773968');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (118, 7, '2026-03-28 03:17:21.776336');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (119, 7, '2026-03-28 03:17:21.778692');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (120, 7, '2026-03-28 03:17:21.781051');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (121, 7, '2026-03-28 03:17:21.783427');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (122, 7, '2026-03-28 03:17:21.785828');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (123, 7, '2026-03-28 03:17:21.788213');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (124, 7, '2026-03-28 03:17:21.790807');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (125, 7, '2026-03-28 03:17:21.793232');
INSERT INTO alunos_turmas (aluno_id, turma_id, data_matricula) VALUES (126, 7, '2026-03-28 03:17:21.795512');

-- Nenhum registro para inserir em professores_turmas


-- Nenhum registro para inserir em professor_materias


-- Nenhum registro para inserir em turma_materias


-- Dados: aulas (57 registros)
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 1, 1, '2026-03-27', '08:00:00.000000', '09:30:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-27 10:33:51.948141', '2026-03-27 10:33:51.948144');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('História', NULL, 1, 1, '2026-03-30', '08:00:00.000000', '09:30:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-27 10:33:51.950231', '2026-03-27 10:33:51.950234');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Geografia', NULL, 2, 2, '2026-03-31', '08:00:00.000000', '09:30:00.000000', FALSE, NULL, NULL, NULL, NULL, 'realizada', '2026-03-27 10:33:51.953369', '2026-03-28 03:06:42.493573');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.828274', '2026-03-28 03:17:21.828277');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.828277', '2026-03-28 03:17:21.828278');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.828278', '2026-03-28 03:17:21.828279');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.830523', '2026-03-28 03:17:21.830524');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.830525', '2026-03-28 03:17:21.830526');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.830526', '2026-03-28 03:17:21.830527');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.832345', '2026-03-28 03:17:21.832347');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.832348', '2026-03-28 03:17:21.832348');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 6, '2026-03-30', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.832349', '2026-03-28 03:17:21.832349');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834861', '2026-03-28 03:17:21.834863');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834864', '2026-03-28 03:17:21.834865');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834865', '2026-03-28 03:17:21.834866');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834866', '2026-03-28 03:17:21.834867');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834867', '2026-03-28 03:17:21.834868');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834869', '2026-03-28 03:17:21.834869');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834870', '2026-03-28 03:17:21.834870');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834871', '2026-03-28 03:17:21.834871');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 7, '2026-03-31', '10:00:00.000000', '10:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.834872', '2026-03-28 03:17:21.834872');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837474', '2026-03-28 03:17:21.837476');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837477', '2026-03-28 03:17:21.837477');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837478', '2026-03-28 03:17:21.837478');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837479', '2026-03-28 03:17:21.837479');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837480', '2026-03-28 03:17:21.837480');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837481', '2026-03-28 03:17:21.837481');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837482', '2026-03-28 03:17:21.837482');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837482', '2026-03-28 03:17:21.837483');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 8, '2026-04-01', '07:00:00.000000', '07:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.837483', '2026-03-28 03:17:21.837484');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840062', '2026-03-28 03:17:21.840063');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840064', '2026-03-28 03:17:21.840064');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840065', '2026-03-28 03:17:21.840065');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840066', '2026-03-28 03:17:21.840066');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840067', '2026-03-28 03:17:21.840067');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840068', '2026-03-28 03:17:21.840068');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840068', '2026-03-28 03:17:21.840069');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840069', '2026-03-28 03:17:21.840070');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 9, '2026-04-02', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.840070', '2026-03-28 03:17:21.840071');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842960', '2026-03-28 03:17:21.842962');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842963', '2026-03-28 03:17:21.842963');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842964', '2026-03-28 03:17:21.842964');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842965', '2026-03-28 03:17:21.842966');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842966', '2026-03-28 03:17:21.842967');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842967', '2026-03-28 03:17:21.842978');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842978', '2026-03-28 03:17:21.842979');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842979', '2026-03-28 03:17:21.842980');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 10, '2026-04-03', '09:00:00.000000', '09:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.842980', '2026-03-28 03:17:21.842981');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 4, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845441', '2026-03-28 03:17:21.845442');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 4, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845443', '2026-03-28 03:17:21.845443');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 4, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845444', '2026-03-28 03:17:21.845444');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 5, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845445', '2026-03-28 03:17:21.845445');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 5, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845446', '2026-03-28 03:17:21.845446');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 5, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845447', '2026-03-28 03:17:21.845447');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Matemática', NULL, 6, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845448', '2026-03-28 03:17:21.845448');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Português', NULL, 6, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845449', '2026-03-28 03:17:21.845449');
INSERT INTO aulas (materia, descricao, turma_id, professor_id, data, horario_inicio, horario_fim, recorrente, tipo_recorrencia, dia_semana, data_fim_recorrencia, aula_pai_id, status, criado_em, atualizado_em) VALUES ('Ciências', NULL, 6, 5, '2026-04-06', '08:00:00.000000', '08:50:00.000000', FALSE, NULL, NULL, NULL, NULL, 'agendada', '2026-03-28 03:17:21.845450', '2026-03-28 03:17:21.845450');

-- Dados: frequencias (30 registros)
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (7, 49, TRUE, '', '2026-03-28 03:30:34.913624');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (8, 49, TRUE, '', '2026-03-28 03:30:34.916004');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (9, 49, TRUE, '', '2026-03-28 03:30:34.917541');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (10, 49, TRUE, '', '2026-03-28 03:30:34.919150');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (11, 49, TRUE, '', '2026-03-28 03:30:34.920631');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (12, 49, TRUE, '', '2026-03-28 03:30:34.922130');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (13, 49, TRUE, '', '2026-03-28 03:30:34.923609');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (14, 49, TRUE, '', '2026-03-28 03:30:34.925077');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (15, 49, TRUE, '', '2026-03-28 03:30:34.926496');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (16, 49, TRUE, '', '2026-03-28 03:30:34.927906');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (17, 49, TRUE, '', '2026-03-28 03:30:34.929256');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (18, 49, TRUE, '', '2026-03-28 03:30:34.930584');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (19, 49, TRUE, '', '2026-03-28 03:30:34.931922');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (20, 49, TRUE, '', '2026-03-28 03:30:34.933240');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (21, 49, TRUE, '', '2026-03-28 03:30:34.934546');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (22, 49, TRUE, '', '2026-03-28 03:30:34.935888');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (23, 49, TRUE, '', '2026-03-28 03:30:34.937130');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (24, 49, TRUE, '', '2026-03-28 03:30:34.938355');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (25, 49, TRUE, '', '2026-03-28 03:30:34.939576');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (26, 49, TRUE, '', '2026-03-28 03:30:34.940820');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (27, 49, TRUE, '', '2026-03-28 03:30:34.942060');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (28, 49, TRUE, '', '2026-03-28 03:30:34.943283');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (29, 49, TRUE, '', '2026-03-28 03:30:34.944510');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (30, 49, TRUE, '', '2026-03-28 03:30:34.945758');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (31, 49, TRUE, '', '2026-03-28 03:30:34.946966');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (32, 49, TRUE, '', '2026-03-28 03:30:34.948167');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (33, 49, TRUE, '', '2026-03-28 03:30:34.949370');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (34, 49, TRUE, '', '2026-03-28 03:30:34.950568');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (35, 49, TRUE, '', '2026-03-28 03:30:34.951825');
INSERT INTO frequencias (aluno_id, aula_id, presente, justificativa, registrado_em) VALUES (36, 49, TRUE, '', '2026-03-28 03:30:34.952822');

-- Nenhum registro para inserir em notas


-- Nenhum registro para inserir em arquivos



-- Reabilitar verificação de FKs
SET session_replication_role = DEFAULT;

-- ============================================================
-- RESETAR SEQUENCES
-- ============================================================

-- Resetar sequences para continuar auto-increment corretamente
SELECT setval('usuarios_id_seq', COALESCE((SELECT MAX(id) FROM usuarios), 1), true);
SELECT setval('materias_id_seq', COALESCE((SELECT MAX(id) FROM materias), 1), true);
SELECT setval('feriados_id_seq', COALESCE((SELECT MAX(id) FROM feriados), 1), true);
SELECT setval('dias_nao_letivos_id_seq', COALESCE((SELECT MAX(id) FROM dias_nao_letivos), 1), true);
SELECT setval('alunos_id_seq', COALESCE((SELECT MAX(id) FROM alunos), 1), true);
SELECT setval('turmas_id_seq', COALESCE((SELECT MAX(id) FROM turmas), 1), true);
SELECT setval('professores_id_seq', COALESCE((SELECT MAX(id) FROM professores), 1), true);
SELECT setval('aulas_id_seq', COALESCE((SELECT MAX(id) FROM aulas), 1), true);
SELECT setval('frequencias_id_seq', COALESCE((SELECT MAX(id) FROM frequencias), 1), true);
SELECT setval('notas_id_seq', COALESCE((SELECT MAX(id) FROM notas), 1), true);
SELECT setval('arquivos_id_seq', COALESCE((SELECT MAX(id) FROM arquivos), 1), true);


-- ============================================================
-- FIM DA EXPORTAÇÃO
-- Total: 387 registros em 15 tabelas
-- ============================================================

-- Verificar dados importados
-- SELECT 'usuarios' as tabela, COUNT(*) as registros FROM usuarios
-- UNION ALL SELECT 'alunos', COUNT(*) FROM alunos
-- UNION ALL SELECT 'professores', COUNT(*) FROM professores
-- UNION ALL SELECT 'turmas', COUNT(*) FROM turmas
-- UNION ALL SELECT 'aulas', COUNT(*) FROM aulas;
