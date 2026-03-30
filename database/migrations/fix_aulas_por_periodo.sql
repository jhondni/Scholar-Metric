-- ============================================================
-- CORREÇÃO: Adicionar coluna aulas_por_periodo em turma_materias
-- ============================================================
-- Data: 2026-03-30
-- Erro corrigido: ERROR: 42703: column "aulas_por_periodo" 
--                 of relation "turma_materias" does not exist
-- ============================================================
-- Execute este SQL no SQL Editor do Supabase
-- URL: https://supabase.com/dashboard → Projeto → SQL Editor
-- ============================================================

-- Verificar se a tabela existe e adicionar a coluna se necessário
DO $$ 
BEGIN
    -- Verificar se a tabela turma_materias existe
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'turma_materias'
    ) THEN
        -- Verificar se a coluna aulas_por_periodo existe
        IF NOT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'turma_materias' 
            AND column_name = 'aulas_por_periodo'
        ) THEN
            -- Adicionar a coluna
            ALTER TABLE turma_materias 
            ADD COLUMN aulas_por_periodo INTEGER DEFAULT 2;
            
            RAISE NOTICE 'Coluna aulas_por_periodo adicionada com sucesso!';
        ELSE
            RAISE NOTICE 'Coluna aulas_por_periodo já existe.';
        END IF;
    ELSE
        RAISE NOTICE 'Tabela turma_materias não existe. Crie-a primeiro usando supabase_schema.sql';
    END IF;
END $$;

-- Adicionar comentário na coluna
COMMENT ON COLUMN turma_materias.aulas_por_periodo IS 'Quantidade de aulas da matéria por período (semana)';

-- ============================================================
-- FIM DA CORREÇÃO
-- ============================================================
