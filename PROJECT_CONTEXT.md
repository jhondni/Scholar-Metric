# 📚 PROJECT_CONTEXT.md - Analitcs School

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
- **Relacionamento**: 1:1 com Usuario, N:N com Turma

#### Turma (turma.py)
- **Responsabilidade**: Agrupar alunos e aulas
- **Atributos**: nome, codigo, serie, turno, capacidade
- **Métodos**: total_alunos(), media_turma(), percentual_frequencia_media()

#### Aula (aula.py)
- **Responsabilidade**: Representar aulas agendadas
- **Atributos**: materia, data, horário, recorrência
- **Métodos**: gerar_datas_recorrencia(), verificar_conflito()
- **Padrão**: Self-referencing (aula_pai → aulas_filhas)

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

### Tabelas de Associação (N:N)
- **alunos_turmas**: alunos ↔ turmas
- **professores_turmas**: professores ↔ turmas

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

### 2. Configurar PostgreSQL
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
```bash
python3 run.py
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

### Versão 1.3.0 (27/03/2026)

#### ✅ Melhorias de Animação - Páginas de Autenticação
- **Animação de background redesenhada**:
  - Movimento flutuante bidimensional (X e Y)
  - 3 variações de animação para movimento mais natural
  - Símbolos incluem: números, símbolos matemáticos, letras (x, y, z, a, b, c)
  - Distribuição aleatória na tela
  - Baixa opacidade (4% a 12%) para não atrapalhar leitura
  
- **Símbolos implementados**:
  - Números: 0-9
  - Operadores: +, −, ×, ÷, =, <, >, ≠, ≈, ±
  - Matemáticos: ∑, √, π, ∞, ∫, ∂, ∇, ∆, ∏, ∪, ∩
  - Grego: α, β, γ, δ, θ, λ, μ, σ, φ, ω, Δ, Σ, Ω
  - Variáveis: x, y, z, a, b, c, n, m, i, f, e
  - Conjuntos: ∈, ∉, ⊂, ⊃, ⊆, ⊇, ∅, ∀, ∃

- **Otimizações de performance**:
  - Uso de `will-change` e `transform` para GPU acceleration
  - Pausa de animação quando aba não está visível
  - Suporte a `prefers-reduced-motion` (movimento reduzido)
  - Animações pausadas quando usuário prefere menos movimento

- **Responsividade**:
  - Funciona em desktop, tablet e mobile
  - Ajuste automático de densidade de símbolos

- **Tema escuro**:
  - Opacidade ajustada para tema escuro
  - Cores adaptadas automaticamente

- **Arquivos modificados**:
  - `app/static/js/auth.js` - JavaScript completamente reescrito
  - `app/static/css/auth.css` - Animações CSS atualizadas

### Versão 1.2.0 (27/03/2026)

#### ✅ Correções de Layout - Páginas de Autenticação
- **Problema corrigido**: Páginas de autenticação ocupando apenas metade da tela
- **Solução aplicada**:
  - Adicionada classe `auth-mode` no `<body>` para páginas não autenticadas
  - CSS do body resetado em modo auth: `display: block` (substituindo `flex`)
  - Dimensões do `.auth-page` ajustadas: `width: 100%` e `height: 100vh`
  - Compatibilidade garantida com todos os navegadores modernos
- **Páginas corrigidas**:
  - Login (`/auth/login`)
  - Registro (`/auth/registro`)
  - Recuperação de senha (`/auth/recuperar-senha`)
- **Responsividade mantida**: Layout funciona corretamente em desktop, tablet e mobile

### Versão 1.1.0 (27/03/2026)

#### ✅ Correções
- **Conexão com banco de dados**: Implementado fallback automático para SQLite quando PostgreSQL não está disponível
- **Mensagens de erro**: Adicionadas mensagens amigáveis para erros de conexão
- **Inicialização**: Verificação automática de conexão antes de iniciar a aplicação

#### ✅ Novas Funcionalidades
- **Script de seed** (`seed.py`): Criação automática de dados de teste
  - Usuário de teste (joao@escola.com / 1234)
  - Professores de exemplo
  - Turmas de exemplo
  - Alunos de exemplo
  - Aulas de exemplo
  - Feriados nacionais

#### ✅ Melhorias de UI/UX - Páginas de Autenticação
- **Layout consistente**: Todas as páginas de auth agora usam o mesmo layout split screen
- **CSS compartilhado** (`auth.css`): Estilos reutilizáveis para login, registro e recuperação
- **JavaScript compartilhado** (`auth.js`): Animações e funcionalidades comuns
- **Responsividade**: Suporte completo a desktop, tablet e mobile
- **Tema escuro**: Suporte a tema escuro em todas as páginas de auth
- **Melhorias visuais**:
  - Animação de entrada suave
  - Toggle de visibilidade de senha
  - Alertas estilizados
  - Botões com efeitos de hover
  - Checkbox customizado
  - Validação visual de campos
  - Links de navegação entre páginas

#### ✅ Melhorias Técnicas
- **Configuração**: Função `check_database_connection()` para verificar conexão
- **Configuração**: Função `get_database_uri()` com fallback automático
- **Factory**: Criação automática de tabelas na inicialização
- **run.py**: Banner de inicialização e tratamento de erros

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
