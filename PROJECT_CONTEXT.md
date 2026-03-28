# 📚 PROJECT_CONTEXT.md - Analitcs School

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

## 🆕 Seed de Dados Expandido (Março/2026)

### Dados Criados
- **Professores**: 11 (incluindo joao@prof.com)
- **Alunos**: 120+
- **Turmas**: 6 (1º ao 3º Ano, Manhã e Tarde)
- **Matérias**: 7 (Matemática, Português, Ciências, etc.)
- **Aulas**: 54 agendadas
- **Feriados**: 10 nacionais brasileiros
- **Associações professor↔matérias**: Cada professor associado à sua especialidade
- **Associações turma↔matérias**: Todas as turmas com todas as matérias configuradas

### Script de Seed
- **Arquivo**: `seed.py`
- **Executar**: `python3 seed.py`
- **Funcionalidades**:
  - Criação automática de turmas equilibradas
  - Distribuição de alunos nas turmas
  - Geração de aulas inteligente
  - Associação de professores às matérias
  - Associação de matérias às turmas com aulas/semana

### Contas para Teste
| Email | Senha | Tipo |
|-------|-------|------|
| joao@escola.com | 1234 | Diretora |
| coordenacao@escola.com | 1234 | Coordenação |
| joao@prof.com | 1234 | Professor |
| maria@escola.com | 1234 | Professor |

---

## 🆕 Atualizações Recentes (Março/2026)

### ✅ Correções de Erros

#### 1. NameError: name 'Nota' is not defined
- **Problema**: Erro ao tentar usar a classe Nota nos modelos
- **Solução**: Adicionado import `from app.models.nota import Nota` no modelo Aluno
- **Arquivo modificado**: `app/models/aluno.py`

#### 2. jinja2.exceptions.UndefinedError: 'csrf_token' is undefined
- **Problema**: Formulários sem proteção CSRF
- **Solução**: 
  - Adicionado Flask-WTF CSRFProtect em `app/__init__.py`
  -Token CSRF adicionado a todos os formuláriosPOST
- **Arquivos modificados**: `app/__init__.py`, múltiplos templates

---

### ✅ Novas Funcionalidades

#### 1. Disponibilidade de Professores (Etapa 3)
- **Modelo novo**: `DisponibilidadeProfessor` em `app/models/especialidade.py`
- **Campos**: dia_semana, horario_inicio, horario_fim
- **Interface**: Página de detalhe do professor com modal para adicionar disponibilidade
- **Arquivos novos**: Rota em `app/controllers/professores_controller.py`

#### 2. Sistema de Frequência (Etapa 4)
- **Modelo**: `Frequencia` em `app/models/frequencia.py` (já existia)
- **Funcionalidade**: Lista todos os alunos da turma, permite marcar Presente/Ausente com justificativa
- **Interface**: Página `aulas/frequencia.html` com formulário completo (@R南通 教育)

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
Requisição HTTP → Flask Router → Controller → Model (DB) → Template (View) → Resposta HTML
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
- Flask + SQLAlchemy + PostgreSQL
- MVC com Blueprints
- Flask-Login para autenticação
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

### 2. Configurar PostgreSQL (opcional - SQLite é usado como fallback)
```bash
# Criar banco de dados
createdb analitcs_school

# Ou via SQL
CREATE DATABASE analitcs_school;
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

## ☁️ Deploy na Vercel

### Pré-requisitos
1. Conta na [Vercel](https://vercel.com)
2. Projeto configurado com PostgreSQL (ex: Supabase, Neon, Railway, Render)
3. Repositório no GitHub/GitLab/Bitbucket

### Passos para Deploy

#### 1. Configurar variáveis de ambiente na Vercel
No painel da Vercel, vá em **Settings → Environment Variables** e adicione:

| Variável | Valor | Obrigatória |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/dbname` | Sim |
| `SECRET_KEY` | Uma string aleatória segura | Sim |
| `FLASK_ENV` | `production` | Não |

#### 2. Conectar repositório
- Clique em "Add New..." → "Project"
- Selecione o repositório
- A Vercel detectará automaticamente o `api/index.py`

#### 3. Deploy
- Clique em "Deploy"
- A Vercel instalará as dependências e fará o deploy

#### 4. Verificar
- Acesse a URL fornecida pela Vercel
- Verifique se `/auth/login` funciona

### Estrutura de Deploy na Vercel

```
projeto/
├── api/
│   └── index.py          ← Entrypoint serverless
├── app/
│   ├── static/           ← Servido estaticamente
│   ├── templates/
│   ├── controllers/
│   └── models/
├── vercel.json           ← Configuração de roteamento
├── .vercelignore         ← Arquivos excluídos
├── runtime.txt           ← Versão Python
└── requirements.txt      ← Dependências
```

### Variáveis de Ambiente por Ambiente

| Ambiente | `DATABASE_URL` | `FLASK_ENV` | `SECRET_KEY` |
|----------|---------------|-------------|--------------|
| Local (dev) | PostgreSQL ou SQLite | `development` | Qualquer |
| Vercel (prod) | PostgreSQL obrigatório | `production` | Segura e única |

### Provedores de PostgreSQL Recomendados (Gratuitos)
- [Supabase](https://supabase.com) - 500MB gratuito
- [Neon](https://neon.tech) - 512MB gratuito
- [Railway](https://railway.app) - 5$/mês (trial grátis)
- [Render](https://render.com) - 90 dias gratuito

---

## 🐞 Resolução de Problemas

### Erro: "No flask entrypoint found"

#### Causa
O erro ocorre quando o Flask CLI (`flask run`) não consegue encontrar a instância da aplicação Flask. Isso acontece porque:

1. Não existe arquivo `app.py` na raiz do projeto
2. A variável de ambiente `FLASK_APP` não está configurada corretamente
3. A variável `app` está encapsulada dentro de uma função (não acessível no escopo global)

#### Solução Aplicada

**Arquivo `app.py` (Entrypoint Principal):**
```python
# app.py cria a instância 'app' no escopo global
from app import create_app
app = create_app('development')
```

**Arquivo `.flaskenv` (Configuração Automática):**
```bash
FLASK_APP=app.py
FLASK_ENV=development
```

**Arquivo `pyproject.toml` (Scripts de Projeto):**
```toml
[project.scripts]
analitcs-school = "app:app.run"
```

#### Como Funciona

| Método | Arquivo | Variável `app` | Funciona com `flask run` |
|--------|---------|----------------|--------------------------|
| `app.py` | Raiz | Global | ✅ Sim |
| `.flaskenv` | Config | Define `FLASK_APP` | ✅ Sim |
| `pyproject.toml` | Config | Script registrado | ✅ Sim |
| `run.py` | Raiz | Dentro de função | ❌ Não (apenas `python run.py`) |

#### Prevenção Futura

1. Sempre manter `app.py` na raiz do projeto Flask
2. Manter `.flaskenv` com `FLASK_APP=app.py`
3. Usar factory pattern mas expor `app` no módulo principal
4. Testar com `flask routes` após mudanças

---

### Erro: "500 INTERNAL_SERVER_ERROR - FUNCTION_INVOCATION_FAILED" (Vercel)

#### Causa
Este erro ocorre quando a Serverless Function da Vercel falha durante a inicialização. Causas principais:

1. **Sem `vercel.json`** - Vercel não sabe como rotear requisições
2. **Sem entrypoint serverless** - Falta `api/index.py` para Vercel
3. **Timeout de conexão ao banco** - `config.py` tenta conectar ao PostgreSQL durante importação
4. **SQLite em diretório read-only** - Vercel só permite escrita em `/tmp`
5. **SESSION_TYPE = 'filesystem'** - Filesystem é read-only em serverless

#### Solução Aplicada

**1. Arquivo `vercel.json` (Roteamento):**
```json
{
  "version": 2,
  "builds": [
    {"src": "api/index.py", "use": "@vercel/python"},
    {"src": "app/static/**", "use": "@vercel/static"}
  ],
  "routes": [
    {"src": "/static/(.*)", "dest": "/app/static/$1"},
    {"src": "/(.*)", "dest": "api/index.py"}
  ]
}
```

**2. Arquivo `api/index.py` (Entrypoint Serverless):**
```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('FLASK_ENV', 'production')
from app import create_app
app = create_app('production')
```

**3. Refatoração de `config.py`:**
- Adicionada função `is_serverless()` para detectar ambiente Vercel
- `get_database_uri()` agora NÃO testa conexão em serverless
- SQLite fallback usa `/tmp` em serverless
- Suporte a `postgres://` → `postgresql://` (Render/Railway)

**4. Correção em `app/__init__.py`:**
- `db.create_all()` não falha silenciosamente em serverless
- Upload folder não é criado em serverless

**5. Arquivo `.vercelignore`:**
- Exclui `.env`, `.venv`, `__pycache__`, `instance/` do deploy

**6. Arquivo `runtime.txt`:**
- Especifica Python 3.11.6

#### Variáveis de Ambiente na Vercel

Configure no painel da Vercel (Settings → Environment Variables):

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | URI do PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Chave secreta do Flask | `sua-chave-secreta-aqui` |
| `FLASK_ENV` | Ambiente | `production` |

#### Estrutura de Deploy

```
projeto/
├── api/
│   └── index.py          # Entrypoint serverless (Vercel)
├── app/
│   ├── __init__.py       # Factory Flask
│   ├── controllers/      # Blueprints
│   ├── models/           # SQLAlchemy
│   ├── templates/        # Jinja2
│   └── static/           # CSS/JS/Images
├── app.py                # Entrypoint local (flask run)
├── config.py             # Configurações (detecta serverless)
├── vercel.json           # Configuração Vercel
├── .vercelignore         # Arquivos excluídos do deploy
├── runtime.txt           # Versão do Python
└── requirements.txt      # Dependências
```

#### Prevenção Futura

1. Sempre testar com `FLASK_ENV=production` localmente antes de deploy
2. Usar `is_serverless()` para lógica condicional
3. Nunca fazer I/O de filesystem em serverless (exceto `/tmp`)
4. Usar PostgreSQL em produção (não SQLite)
5. Configurar variáveis de ambiente na Vercel antes do deploy

---

## 📝 Notas Técnicas

### Segurança
- Senhas com hash (Werkzeug)
- CSRF Protection (Flask-WTF)
- Validação de formulários
- Controle de acesso por tipo de usuário

### Performance
- Índices em campos de busca
- Paginação de listas
- Lazy loading de relacionamentos
- CSS e JS minificados em produção

### Extensibilidade
- Fácil adição de novos módulos
- Sistema de plugins via Blueprints
- Templates herdados para consistência
- API REST para integrações futuras

---

## 📋 Changelog

### Versão 2.0.2 (28/03/2026)

#### 🐞 Correção de Deploy na Vercel (Serverless)
- **Problema**: Erro `500: FUNCTION_INVOCATION_FAILED` ao acessar a aplicação na Vercel
- **Causas identificadas**:
  - Ausência de `vercel.json` para roteamento
  - Ausência de `api/index.py` como entrypoint serverless
  - `config.py` tentava conectar ao PostgreSQL durante importação (timeout)
  - SQLite fallback gravava em diretório read-only
  - `SESSION_TYPE = 'filesystem'` incompatível com serverless
- **Solução**:
  - Criado `vercel.json` com configuração de builds e routes
  - Criado `api/index.py` como entrypoint para Vercel
  - Refatorado `config.py` com detecção de ambiente serverless (`is_serverless()`)
  - Corrigido `get_database_uri()` para não testar conexão em serverless
  - SQLite fallback usa `/tmp` em ambiente serverless
  - `ProductionConfig` usa sessão via cookies (não filesystem)
  - Criado `.vercelignore` para excluir arquivos desnecessários
  - Criado `runtime.txt` especificando Python 3.11.6
  - Atualizado `requirements.txt` com gunicorn
- **Arquivos criados**:
  - `vercel.json` - Configuração de deploy Vercel
  - `api/index.py` - Entrypoint serverless
  - `.vercelignore` - Arquivos excluídos do deploy
  - `runtime.txt` - Versão Python
- **Arquivos modificados**:
  - `config.py` - Detecção de ambiente serverless, lógica de DB resiliente
  - `app/__init__.py` - Tratamento de erros em serverless
  - `requirements.txt` - Adicionado gunicorn

#### Variáveis de Ambiente Necessárias na Vercel
| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | Sim | URI PostgreSQL (ex: `postgresql://user:pass@host:5432/db`) |
| `SECRET_KEY` | Sim | Chave secreta do Flask |
| `FLASK_ENV` | Não | Padrão: `production` |

### Versão 2.0.1 (28/03/2026)

#### 🐞 Correção de Entrypoint Flask
- **Problema**: Erro "No flask entrypoint found" ao executar `flask run`
- **Causa**: A variável `app` estava encapsulada em função `main()` em `run.py`
- **Solução**:
  - Criado `app.py` como entrypoint principal com `app` no escopo global
  - Criado `.flaskenv` com configurações automáticas do Flask CLI
  - Criado `pyproject.toml` com definição de scripts
  - Atualizado `.env.example` com `FLASK_APP=app.py`
  - Atualizado `run.py` com documentação de compatibilidade
- **Arquivos criados**:
  - `app.py` - Entrypoint principal
  - `.flaskenv` - Variáveis de ambiente Flask
  - `pyproject.toml` - Configuração do projeto
- **Arquivos modificados**:
  - `.env.example` - FLASK_APP corrigido
  - `run.py` - Documentação atualizada

### Versão 2.0.0 (28/03/2026)

#### ✅ Gestão Avançada de Turmas
- **Matérias por Turma**: Definir matérias e aulas/semana para cada turma
- **Página dedicada**: `/turmas/<id>/materias` com interface completa
- **Validação**: Mostra professores disponíveis por matéria
- **Tabela de associação**: `turma_materias` com campo `aulas_por_periodo`

#### ✅ Professores e Matérias
- **Matérias por Professor**: Cada professor tem lista de matérias que pode lecionar
- **Exibição**: Página de detalhe mostra matérias como badges
- **Gerenciamento**: Página dedicada `/professores/<id>/materias` com checkboxes
- **API**: Rotas para adicionar/remover matérias via AJAX
- **Tabela de associação**: `professor_materias`

#### ✅ Geração Automática de Calendário
- **Serviço**: `GeradorCalendarioAcademico` em `app/services/gerador_calendario.py`
- **Algoritmo**: Heurístico guloso para distribuição de aulas
- **Restrições**: Sem conflitos de professor, turma ou alunos
- **Períodos**: Semestral ou Anual
- **Interface**: Botão "Gerar Calendário Semanal" na página de turma
- **Geração em lote**: Botão "Gerar Calendário Geral" na lista de turmas

#### ✅ Integração
- Link "Matérias" adicionado ao sidebar
- Coluna "Matérias" na tabela de turmas
- Ícone de livro para acessar matérias da turma na tabela

#### ✅ Controle de Acesso
- Edição de matérias: apenas Diretora e Coordenação
- Geração de calendário: apenas Diretora e Coordenação

#### ✅ Seed Atualizado
- Associações automáticas de professores às suas especialidades
- Todas as turmas com todas as matérias configuradas
- Aulas por semana: Matemática (4), Português (4), outras (2)

#### ✅ Documentação
- PROJECT_CONTEXT.md atualizado com novas funcionalidades
- Modelagem de dados atualizada
- Sistema de calendário documentado

### Versão 1.4.0 (27/03/2026)

#### ✅ Consistência de UI - Sidebar e Header
- **Problema corrigido**: Altura inconsistente entre `.sidebar-header` e `.header`
- **Solução aplicada**:
  - `.sidebar-header` agora usa `height: var(--header-height)` (mesma variável do `.header`)
  - Padding alterado de `1.5rem` (todos os lados) para `0 1.5rem` (apenas horizontal)
  - Ambos os elementos compartilham a mesma variável CSS `--header-height`
- **Responsividade**: Alterações se adaptam automaticamente via variável CSS (64px desktop, 56px mobile)
- **Boas práticas**:
  - Zero código duplicado
  - Variáveis CSS reutilizáveis
  - Sem impacto em outros componentes
- **Arquivo modificado**: `app/static/css/main.css`

### Versão 1.0.0 (26/03/2026)
- Versão inicial do sistema
- Estrutura MVC completa
- Todos os módulos implementados
