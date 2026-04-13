# 📚 PROJECT_CONTEXT.md - Analitcs School

---

## 🔄 Histórico de Alterações

### 📅 13/04/2026 - Remoção do Supabase e Migração para PostgreSQL

#### Alterações Realizadas:

**1. Remoção do Supabase:**
- Removido arquivo `app/services/supabase_client.py`
- Removido arquivo `app/services/supabase_auth.py`
- Removidos scripts `scripts/export_to_supabase.py` e `scripts/migrate_to_supabase.py`
- Removida dependência `supabase>=2.28.0` do `requirements.txt`
- Removidas variáveis `SUPABASE_URL` e `SUPABASE_ANON_KEY` do `.env`

**2. Refatoração de Repositories:**
- `base_repository.py`: Migrado de Supabase REST API para SQLAlchemy ORM
- `usuario_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `aluno_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `professor_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `turma_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `aula_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `materia_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `frequencia_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `nota_repository.py`: Reescrito para usar SQLAlchemy diretamente
- `feriado_repository.py`: Reescrito para usar SQLAlchemy diretamente (inclui DiaNaoLetivoRepository)

**3. Atualização de Models:**
- Adicionado método `to_dict()` aos modelos:
  - `Usuario`
  - `Aluno`
  - `Professor`
  - `Turma`
  - `Aula`
  - `Materia`
  - `Feriado`
  - `DiaNaoLetivo`
  - `Frequencia`
  - `Nota`

**4. Atualização de Controllers:**
- `auth_controller.py`: Atualizado para usar modelo `Usuario` diretamente (sem SupabaseUser)
- `app/__init__.py`: User loader simplificado para usar SQLAlchemy diretamente

**5. Atualização de Configuração:**
- `config.py`: Removidas variáveis SUPABASE_URL e SUPABASE_ANON_KEY
- `.env`: Configurado para PostgreSQL (DATABASE_URL)
- `.env.example`: Atualizado para PostgreSQL

**6. Padrão de Acesso a Dados:**
Antes (Supabase REST API):
```
Controller → Repository → Supabase Client → REST API → Supabase DB
```

Depois (SQLAlchemy ORM):
```
Controller → Repository → SQLAlchemy ORM → Database (PostgreSQL/SQLite)
```

#### Benefícios:
- **Performance**: Conexão direta ao banco, sem overhead de API REST
- **Consistência**: Usa SQLAlchemy ORM em toda a aplicação
- **Simplicidade**: Menos dependências externas
- **Portabilidade**: Funciona com PostgreSQL ou SQLite (fallback)
- **Manutenção**: Código mais simples e manutenível

#### Banco de Dados:
- **PostgreSQL**: Recomendado para produção
- **SQLite**: Fallback automático para desenvolvimento local
- **Configuração**: Via variável `DATABASE_URL` no `.env`

---

## 🆕 Funcionalidades Avançadas - Gestão de Turmas e Calendário (Março/2026)

### ✅ Gestão de Matérias por Professor
- **Página**: Detalhe do professor mostra matérias que pode lecionar
- **Gerenciamento**: Botão "Gerenciar Matérias" leva a página dedicada
- **API**: Rotas para adicionar/remover matérias via AJAX
- **Rotas novas**:
  - `GET /professores/<id>/materias` - Página de gerenciamento
  - `POST /professores/<id>/materias` - Salvar matérias (form)
  - `POST /professores/<id>/materias/adicionar` - API adicionar matéria
  - `DELETE /professores/<id>/materias/<materia_id>` - API remover matéria

### ✅ Gestão de Matérias por Turma com Aulas por Período
- **Página dedicada**: `/turmas/<id>/materias`
- **Funcionalidade**: Selecionar matérias e definir aulas/semana
- **Exemplo**: Matemática → 4 aulas/semana, Português → 3 aulas/semana
- **Validação**: Mostra quantos professores estão disponíveis para cada matéria
- **Rotas novas**:
  - `GET /turmas/<id>/materias` - Página de gerenciamento
  - `POST /turmas/<id>/materias` - Salvar matérias (form)
  - `POST /turmas/<id>/materias/adicionar` - API adicionar matéria
  - `DELETE /turmas/<id>/materias/<materia_id>` - API remover matéria

### ✅ Geração Automática de Calendário
- **Serviço**: `app/services/gerador_calendario.py` - `GeradorCalendarioAcademico`
- **Algoritmo**: Heurístico guloso que distribui aulas considerando:
  - Matérias da turma e aulas por período
  - Professores disponíveis para cada matéria
  - Conflito de horário (mesma turma)
  - Conflito de professor (mesmo professor em duas turmas)
  - Conflito de alunos (alunos com aulas simultâneas)
  - Feriados e dias não letivos
  - Horários de turno (manhã/tarde/noite)
- **Períodos suportados**: Semestral (6 meses) ou Anual (12 meses)
- **Rotas novas**:
  - `POST /turmas/<id>/gerar-calendario` - Gerar para uma turma
  - `POST /turmas/gerar-calendario-todas` - Gerar para todas as turmas
- **Interface**: Botão "Gerar Calendário Semanal" na página de detalhe da turma
- **Restrições respeitadas**:
  - ❌ Não permite conflito de horários do professor
  - ❌ Não permite aulas simultâneas para alunos da mesma turma
  - ❌ Pula feriados e dias não letivos
  - ❌ Pula fins de semana

### ✅ Integração com Sistema
- Calendário gerado aparece automaticamente no:
  - Calendário geral (`/calendario`)
  - Página de aulas (`/aulas`)
- Aulas são editáveis individualmente após geração
- Link de "Matérias" adicionado ao sidebar

### ✅ Controle de Acesso
- Apenas **Diretora** e **Coordenação** podem:
  - Editar matérias de turmas
  - Editar matérias de professores
  - Gerar calendário automático
- Professores podem apenas visualizar

### 📊 Modelagem de Dados Atualizada

#### Tabela: turma_materias (N:N com campo extra)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| turma_id | INTEGER (FK) | Referência à turma |
| materia_id | INTEGER (FK) | Referência à matéria |
| aulas_por_periodo | INTEGER | Quantidade de aulas por semana |

#### Tabela: professor_materias (N:N)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| professor_id | INTEGER (FK) | Referência ao professor |
| materia_id | INTEGER (FK) | Referência à matéria |

#### Novos Relacionamentos
- **Professor ↔ Matéria**: N:N via `professor_materias`
  - Professor pode lecionar múltiplas matérias
  - Matéria pode ser lecionada por múltiplos professores
- **Turma ↔ Matéria**: N:N via `turma_materias` (com `aulas_por_periodo`)
  - Turma tem múltiplas matérias
  - Matéria pode estar em múltiplas turmas
  - Cada associação define quantas aulas/semana

---


## 📌 Visão Geral do Sistema

### Objetivo
O **Analitcs School** é um sistema web de gestão escolar inteligente que permite gerenciar turmas, alunos, professores, aulas, calendário acadêmico e oferece módulo de análise de desempenho.

### Público-alvo
- Diretoras e coordenadores de escolas
- Professores
- Equipe administrativa escolar

### Problema que resolve
- Desorganização na gestão de turmas e aulas
- Falta de controle sobre frequência e desempenho
- Dificuldade em identificar alunos em risco de evasão
- Necessidade de um sistema centralizado para gestão escolar

---

## 🏗️ Arquitetura do Projeto

### Estrutura de Pastas

```
projeto/
├── app/
│   ├── __init__.py              # Factory da aplicação Flask
│   ├── models/                  # Modelos ORM (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── usuario.py           # Modelo de Usuário
│   │   ├── aluno.py             # Modelo de Aluno
│   │   ├── professor.py         # Modelo de Professor
│   │   ├── turma.py             # Modelo de Turma
│   │   ├── aula.py              # Modelo de Aula
│   │   ├── frequencia.py        # Modelo de Frequência
│   │   ├── nota.py              # Modelo de Nota
│   │   ├── arquivo.py           # Modelo de Arquivo
│   │   ├── feriado.py           # Modelo de Feriado
│   │   └── dia_nao_letivo.py    # Modelo de Dia Não Letivo
│   ├── controllers/             # Controllers (Rotas e Lógica)
│   │   ├── __init__.py
│   │   ├── auth_controller.py   # Autenticação
│   │   ├── dashboard_controller.py
│   │   ├── turmas_controller.py
│   │   ├── alunos_controller.py
│   │   ├── professores_controller.py
│   │   ├── aulas_controller.py
│   │   ├── calendario_controller.py
│   │   ├── configuracoes_controller.py
│   │   └── analise_controller.py
│   ├── repositories/            # Camada de Acesso a Dados (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base_repository.py   # CRUD genérico
│   │   ├── usuario_repository.py
│   │   ├── aluno_repository.py
│   │   ├── professor_repository.py
│   │   ├── turma_repository.py
│   │   ├── aula_repository.py
│   │   ├── materia_repository.py
│   │   ├── frequencia_repository.py
│   │   ├── nota_repository.py
│   │   ├── feriado_repository.py
│   │   └── escola_repository.py
│   ├── services/                # Serviços de Negócio
│   │   └── gerador_calendario.py
│   ├── views/                   # Views (Helpers/Utilitários)
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css         # Estilos principais + Variáveis de tema
│   │   │   ├── components.css   # Componentes específicos
│   │   │   └── responsive.css   # Media queries
│   │   ├── js/
│   │   │   ├── main.js          # JavaScript principal
│   │   │   └── theme.js         # Gerenciamento de tema
│   │   ├── images/
│   │   └── uploads/             # Arquivos enviados
│   └── templates/
│       ├── base.html            # Template base (layout)
│       ├── auth/                # Templates de autenticação
│       ├── dashboard/           # Dashboard
│       ├── turmas/              # Gestão de turmas
│       ├── alunos/              # Gestão de alunos
│       ├── professores/         # Gestão de professores
│       ├── aulas/               # Gestão de aulas
│       ├── calendario/          # Calendário
│       ├── configuracoes/       # Configurações
│       ├── analise/             # Módulo de análise
│       ├── components/          # Componentes reutilizáveis
│       └── errors/              # Páginas de erro
├── config.py                    # Configurações da aplicação
├── run.py                       # Ponto de entrada
├── requirements.txt             # Dependências Python
├── .env.example                 # Exemplo de variáveis de ambiente
└── PROJECT_CONTEXT.md           # Este arquivo
```

### Padrão MVC

O projeto segue o padrão **Model-View-Controller (MVC)**:

- **Models** (`app/models/`): Definição das entidades do banco de dados usando SQLAlchemy ORM
- **Views** (`app/templates/`): Templates HTML renderizados com Jinja2
- **Controllers** (`app/controllers/`): Lógica de negócio, rotas e manipulação de requisições

### Fluxo de Requisições

```
Requisição HTTP → Flask Router → Controller → Repository → SQLAlchemy ORM → Database
                                    ↓
                              Flask-Login User (Usuario model)
```

**Fluxo SQLAlchemy (atual):**
```
Requisição → Controller → Repository → SQLAlchemy ORM → PostgreSQL/SQLite → Resposta
                                    ↓
                              Usuario Model (Flask-Login)
```

---

## 🧠 Arquitetura Orientada a Objetos

### Classes Principais

#### Usuário (usuario.py)
- **Responsabilidade**: Autenticação e controle de acesso
- **Atributos**: nome, email, senha_hash, tipo, tema
- **Métodos**: set_senha(), verificar_senha(), tem_permissao()
- **Herança**: UserMixin (Flask-Login)

#### Aluno (aluno.py)
- **Responsabilidade**: Representar estudantes
- **Atributos**: nome, matricula, dados pessoais, responsável
- **Métodos**: media_notas(), percentual_frequencia()
- **Relacionamento**: N:N com Turma

#### Professor (professor.py)
- **Responsabilidade**: Representar docentes
- **Atributos**: registro, especialidade, formação
- **Métodos**: total_aulas(), turmas_ativas()
- **Relacionamento**: 1:1 com Usuario, N:N com Turma, N:N com Matéria

#### Turma (turma.py)
- **Responsabilidade**: Agrupar alunos e aulas
- **Atributos**: nome, codigo, serie, turno, capacidade
- **Métodos**: total_alunos(), media_turma(), percentual_frequencia_media(), get_aulas_por_periodo(), set_aulas_por_periodo()
- **Relacionamento**: N:N com Aluno, N:N com Professor, N:N com Matéria (com aulas_por_periodo)

#### Aula (aula.py)
- **Responsabilidade**: Representar aulas agendadas
- **Atributos**: materia, data, horário, recorrência
- **Métodos**: gerar_datas_recorrencia(), verificar_conflito()
- **Padrão**: Self-referencing (aula_pai → aulas_filhas)

#### Matéria (materia.py)
- **Responsabilidade**: Representar disciplinas lecionadas
- **Atributos**: nome, codigo, descricao, carga_horaria, ativa
- **Relacionamento**: N:N com Professor (professor_materias), N:N com Turma (turma_materias com aulas_por_periodo)

### Boas Práticas Aplicadas
- **Single Responsibility**: Cada classe tem uma responsabilidade bem definida
- **Encapsulation**: Atributos privados com getters/setters onde necessário
- **Factory Pattern**: create_app() para criação da aplicação
- **Blueprint Pattern**: Organização modular dos controllers

---

## 🗄️ Arquitetura de Dados

### Modelagem

#### Tabela: usuarios
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(100) | Nome completo |
| email | VARCHAR(120) | E-mail único |
| senha_hash | VARCHAR(256) | Hash da senha |
| tipo | VARCHAR(20) | diretora/coordenacao/professor |
| tema | VARCHAR(10) | light/dark |
| ativo | BOOLEAN | Status da conta |

#### Tabela: alunos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(100) | Nome completo |
| matricula | VARCHAR(20) | Matrícula única |
| data_nascimento | DATE | Data de nascimento |
| cpf | VARCHAR(14) | CPF único |
| email | VARCHAR(120) | E-mail |
| telefone | VARCHAR(20) | Telefone |
| endereco | TEXT | Endereço |
| nome_responsavel | VARCHAR(100) | Nome do responsável |
| telefone_responsavel | VARCHAR(20) | Telefone do responsável |
| email_responsavel | VARCHAR(120) | E-mail do responsável |
| ano_letivo | INTEGER | Ano letivo |
| status | VARCHAR(20) | ativo/inativo/transferido/evadido |

#### Tabela: professores
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| usuario_id | INTEGER (FK) | Referência ao usuário |
| registro | VARCHAR(20) | Registro profissional único |
| especialidade | VARCHAR(100) | Especialidade |
| formacao | TEXT | Formação acadêmica |
| cpf | VARCHAR(14) | CPF |
| telefone | VARCHAR(20) | Telefone |
| ativo | BOOLEAN | Status |

#### Tabela: turmas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(50) | Nome da turma |
| codigo | VARCHAR(20) | Código único |
| serie | VARCHAR(30) | Série |
| ano_letivo | INTEGER | Ano letivo |
| turno | VARCHAR(20) | manha/tarde/noite |
| capacidade_maxima | INTEGER | Capacidade máxima |
| ativa | BOOLEAN | Status |

#### Tabela: aulas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| materia | VARCHAR(100) | Nome da matéria |
| turma_id | INTEGER (FK) | Referência à turma |
| professor_id | INTEGER (FK) | Referência ao professor |
| data | DATE | Data da aula |
| horario_inicio | TIME | Hora de início |
| horario_fim | TIME | Hora de término |
| recorrente | BOOLEAN | Se é recorrente |
| tipo_recorrencia | VARCHAR(20) | Tipo de recorrência |
| dia_semana | INTEGER | Dia da semana (0-6) |
| data_fim_recorrencia | DATE | Data fim da recorrência |
| aula_pai_id | INTEGER (FK) | Referência à aula pai |
| status | VARCHAR(20) | agendada/realizada/cancelada |

#### Tabela: frequencias
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| aluno_id | INTEGER (FK) | Referência ao aluno |
| aula_id | INTEGER (FK) | Referência à aula |
| presente | BOOLEAN | Presença |
| justificativa | TEXT | Justificativa de falta |

#### Tabela: notas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| aluno_id | INTEGER (FK) | Referência ao aluno |
| turma_id | INTEGER (FK) | Referência à turma |
| aula_id | INTEGER (FK) | Referência à aula |
| tipo_avaliacao | VARCHAR(30) | Tipo de avaliação |
| valor | FLOAT | Valor da nota |
| valor_maximo | FLOAT | Valor máximo |
| peso | FLOAT | Peso da nota |
| bimestre | INTEGER | Bimestre |

#### Tabela: arquivos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome_original | VARCHAR(255) | Nome original |
| nome_armazenado | VARCHAR(255) | Nome no servidor |
| tipo | VARCHAR(50) | Tipo MIME |
| tamanho | INTEGER | Tamanho em bytes |
| aula_id | INTEGER (FK) | Referência à aula |
| professor_id | INTEGER (FK) | Referência ao professor |

#### Tabela: feriados
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(100) | Nome do feriado |
| data | DATE | Data do feriado |
| tipo | VARCHAR(20) | nacional/estadual/municipal |
| recorrente | BOOLEAN | Repete todo ano |

#### Tabela: dias_nao_letivos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(100) | Nome/descrição |
| data_inicio | DATE | Data de início |
| data_fim | DATE | Data de fim |
| tipo | VARCHAR(30) | Tipo |

#### Tabela: materias
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | Identificador único |
| nome | VARCHAR(100) | Nome da matéria (único) |
| codigo | VARCHAR(20) | Código único |
| descricao | TEXT | Descrição |
| carga_horaria | INTEGER | Carga horária total |
| ativa | BOOLEAN | Status |

### Tabelas de Associação (N:N)
- **alunos_turmas**: alunos ↔ turmas
- **professores_turmas**: professores ↔ turmas
- **professor_materias**: professores ↔ matérias
- **turma_materias**: turmas ↔ matérias (com aulas_por_periodo INTEGER default 2)

### Justificativa das Decisões
- **PostgreSQL**: Robusto, suporta transações e índices avançados
- **SQLAlchemy ORM**: Abstração do banco, migrations automáticas
- **Chaves estrangeiras**: Integridade referencial
- **Índices**: Campos de busca frequente (email, matricula, registro)

---

## 🔐 Controle de Acesso

### Estrutura de Permissões

| Tipo | Acesso |
|------|--------|
| **Diretora** | Acesso total ao sistema |
| **Coordenação** | Gestão de cadastros, turmas, alunos, professores |
| **Professor** | Acesso restrito às suas aulas e turmas |

### Regras de Autorização
- Login obrigatório para todas as rotas (exceto auth)
- Verificação de permissão via `current_user.tem_permissao()`
- Professores só editam suas próprias aulas
- Controllers verificam permissão antes de operações sensíveis

---

## 📊 Regras de Negócio

### Conflito de Horários
- Um aluno NÃO pode ter duas aulas no mesmo horário
- Validação no controller de aulas antes de salvar
- Retorna erro claro em caso de conflito

### Feriados e Dias Não Letivos
- Sistema NÃO permite agendamento de aulas nesses dias
- Para aulas recorrentes: datas são automaticamente puladas
- Verificação feita em `verificar_dia_letivo()`

### Lógica de Recorrência
- Aula principal criada com `recorrente=True`
- Aulas filhas geradas automaticamente
- Cada aula filha tem `aula_pai_id` referenciando a principal
- Datas são geradas por `Aula.gerar_datas_recorrencia()`

---

## 🔄 Fluxos do Sistema

### Login
1. Usuário acessa `/auth/login`
2. Preenche email e senha
3. Sistema valida credenciais
4. Cria sessão com Flask-Login
5. Redireciona para Dashboard

### Cadastro de Aluno
1. Usuário acessa `/alunos/novo`
2. Preenche formulário
3. Sistema valida dados
4. Salva no banco
5. Redireciona para lista

### Criação de Aula
1. Usuário acessa `/aulas/novo`
2. Seleciona turma, professor, data, horário
3. Se recorrente, define tipo e data fim
4. Sistema verifica:
   - Conflito de horário
   - Dia letivo (feriado/não letivo)
5. Cria aula principal
6. Se recorrente, gera aulas filhas
7. Redireciona para lista

---

## 📅 Sistema de Calendário

### Funcionalidade
- Visualização em mês, semana e dia
- Integração com aulas, feriados e dias não letivos
- API REST para eventos (`/calendario/api/eventos`)
- Cores diferenciadas por tipo de evento

### Geração Automática de Calendário
- **Serviço**: `app/services/gerador_calendario.py`
- **Classe**: `GeradorCalendarioAcademico`
- **Algoritmo**: Heurístico guloso

#### Entradas:
- Matérias da turma com aulas por período (semana)
- Professores disponíveis para cada matéria
- Horários do turno da turma
- Feriados e dias não letivos

#### Restrições respeitadas:
- Sem conflito de horário do professor (mesmo professor em duas turmas simultâneas)
- Sem conflito de alunos (alunos não podem ter aulas simultâneas)
- Respeito a feriados e dias não letivos
- Pulados fins de semana

#### Períodos suportados:
- **Semestral**: Gera aulas para 6 meses a partir de hoje
- **Anual**: Gera aulas para 12 meses a partir de hoje

#### Lógica de distribuição:
1. Para cada dia letivo do período
2. Para cada matéria da turma
3. Tenta alocar em cada horário disponível do turno
4. Encontra professor disponível sem conflito
5. Cria a aula se não houver conflito
6. Avança para próxima matéria/dia

### Integração
- Aulas aparecem automaticamente no calendário
- Feriados e dias não letivos destacados
- Impedimento de agendamento em datas bloqueadas

---

## 📈 Sistema de Análise

### Métricas
- **Frequência**: Percentual de presença por aluno/turma
- **Desempenho**: Média de notas por aluno/turma
- **Risco de Evasão**: Baseado em frequência (<75%) e média (<5)

### Gráficos (Chart.js)
- Distribuição de alunos por turma (Doughnut)
- Aulas por mês (Bar)
- Desempenho das turmas (Bar)

### Como interpretar
- **Risco Alto**: Frequência < 75% OU Média < 5
- **Risco Médio**: Frequência < 85% OU Média < 7
- **Risco Baixo**: Acima dos limites

---

## 🎨 Interface e UX

### Tema Claro
- Primary: `#4f46e5` (Índigo)
- Secondary: `#06b6d4` (Ciano)
- Background: `#ffffff`
- Text: `#1e293b`

### Tema Escuro
- Primary: `#818cf8` (Índigo claro)
- Background: `#0f172a` (Azul escuro)
- Text: `#f1f5f9`

### Responsividade
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px
- Sidebar colapsável em mobile

---

## 🚀 Guia para IA

### Como reutilizar este projeto
1. **Estrutura**: Seguir organização MVC
2. **Models**: Usar SQLAlchemy ORM com padrão existente
3. **Controllers**: Criar Blueprints, usar decorators de permissão
4. **Templates**: Herdar de `base.html`, usar componentes CSS existentes
5. **Autenticação**: Usar `@login_required` e `tem_permissao()`
6. **Tema**: Respeitar variáveis CSS do sistema de temas

### Contexto Resumido
- Flask + SQLAlchemy ORM
- MVC com Blueprints + Camada de Repositório
- Flask-Login com Usuario model
- PostgreSQL (produção) / SQLite (fallback)
- WTForms para formulários
- Chart.js para gráficos
- CSS Variables para temas
- Design responsivo mobile-first

---

## 🚀 Instruções de Execução

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar PostgreSQL
```bash
# Criar banco de dados
createdb analitcs_school

# Ou via SQL
CREATE DATABASE analitcs_school;

# Configurar usuário (se necessário)
psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres';"
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 4. Inicializar banco de dados
```bash
# Método 1: Usando o script de seed (RECOMENDADO)
python3 seed.py

# Método 2: Usando Flask-Migrate
flask db init
flask db migrate -m "Migração inicial"
flask db upgrade
```

### 5. Executar aplicação

#### Método A: Flask CLI (RECOMENDADO)
```bash
# O .flaskenv já configura FLASK_APP automaticamente
flask run
```

#### Método B: Execução direta via app.py
```bash
python app.py
```

#### Método C: Execução via run.py (legado)
```bash
python run.py
```

### 6. Acessar
```
http://localhost:5000
```

### 7. Credenciais de teste
```
Email: joao@escola.com
Senha: 1234
Tipo: diretora (acesso total)
```

---
