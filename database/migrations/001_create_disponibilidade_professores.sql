-- Migration 001: Criar tabela disponibilidade_professores
-- Data: 2026-03-30
-- Objetivo: Criar tabela de disponibilidade de professores no Supabase PostgreSQL
--
-- INSTRUÇÕES DE EXECUÇÃO:
-- 1. Acesse o painel do Supabase (https://supabase.com/dashboard)
-- 2. Selecione o projeto
-- 3. Vá em SQL Editor
-- 4. Cole este script e execute
--
-- OU use o comando via terminal:
-- psql "postgresql://postgres:PASSWORD@HOST:PORT/postgres" -f 001_create_disponibilidade_professores.sql

-- Criar tabela de disponibilidade de professores
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

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_disp_professor_id ON disponibilidade_professores(professor_id);
CREATE INDEX IF NOT EXISTS idx_disp_dia_semana ON disponibilidade_professores(dia_semana);
CREATE INDEX IF NOT EXISTS idx_disp_ativo ON disponibilidade_professores(ativo);

-- Adicionar comentário na tabela
COMMENT ON TABLE disponibilidade_professores IS 'Armazena os dias e horários disponíveis de cada professor para lecionar';

-- Adicionar comentários nas colunas
COMMENT ON COLUMN disponibilidade_professores.dia_semana IS 'Dia da semana (0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo)';
COMMENT ON COLUMN disponibilidade_professores.horario_inicio IS 'Horário de início da disponibilidade';
COMMENT ON COLUMN disponibilidade_professores.horario_fim IS 'Horário de fim da disponibilidade';
COMMENT ON COLUMN disponibilidade_professores.ativo IS 'Se a disponibilidade está ativa (TRUE) ou desativada (FALSE)';

-- Trigger para atualizar atualizado_em automaticamente
CREATE OR REPLACE FUNCTION update_disponibilidade_professores_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_disponibilidade_professores
    BEFORE UPDATE ON disponibilidade_professores
    FOR EACH ROW
    EXECUTE FUNCTION update_disponibilidade_professores_timestamp();
