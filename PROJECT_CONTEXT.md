# 📚 PROJECT_CONTEXT.md - Analitcs School

---

## 🔄 Histórico de Alterações

### 📅 13/04/2026 - Correção: UnboundLocalError (aluno)

#### Erro:
```
UnboundLocalError: local variable 'aluno' referenced before assignment
```

#### Local:
`app/controllers/alunos_controller.py`, linha 255

#### Causa Raiz:
A variável `aluno` era usada dentro do loop `for` antes de ser definida:
```python
# ❌ ERRO: aluno usado na linha 255, mas definido na linha 258
if ano_atual in notas_por_ano:
    for materia_id, dados in notas_por_ano[ano_atual].items():
        ...
        'frequencia': aluno.percentual_frequencia()  # ← ERRO

aluno = AlunoDTO(aluno_data, _repos)  # ← Definido depois do uso
```

#### Solução:
Mover a criação do `AlunoDTO` para **antes** do loop:

```python
# Criar DTO do aluno antes de usar (necessário para calcular frequência)
aluno = AlunoDTO(aluno_data, _repos)

materias_do_aluno = []
ano_atual = date.today().year

if ano_atual in notas_por_ano:
    for materia_id, dados in notas_por_ano[ano_atual].items():
        ...
        'frequencia': aluno.percentual_frequencia()  # ← Agora funciona
```

#### Validação:
- ✅ Sintaxe verificada
- ✅ Código compila sem erros

---

### 📅 13/04/2026 - Correção: Exibição de Matérias do Aluno

#### Problema:
Na aba "Turmas" da página de detalhes do aluno, eram exibidas informações incorretas (turmas em vez de matérias).

#### Solução Aplicada:

**1. Controller atualizado** (`alunos_controller.py`):
- Adicionada variável `materias_do_aluno` para buscar:
  - Código da matéria
  - Nome da matéria
  - Nome do professor responsável
  - Frequência do aluno
  - Média do aluno

```python
# Buscar matérias do aluno (para aba Turmas)
for materia_id, dados in notas_por_ano[ano_atual].items():
    materia = materia_repo.get_by_id(materia_id)
    profes = professor_repo.get_by_materia(materia_id)
    professor_nome = profes[0].get('nome', 'Não atribuído') if profes else 'Não atribuído'
    
    materias_do_aluno.append({
        'codigo': materia.get('codigo', ''),
        'materia_nome': dados['materia_nome'],
        'professor_nome': professor_nome,
        'media': dados.get('media', 0),
        'frequencia': aluno.percentual_frequencia()
    })
```

**2. Template atualizado** (`detalhe.html`):
- Alterado título: "Turmas" → "Matérias"
- Colunas ajustadas:
  - **Código** → código da matéria
  - **Matéria** → nome da matéria
  - **Professor** → nome do professor
  - **Frequência** → frequência do aluno
  - **Média** → média do aluno
- Removida coluna: "Série"

**3. Dados enviados ao template**:
```python
return render_template('alunos/detalhe.html', 
    aluno=aluno, 
    notas_por_ano=notas_por_ano, 
    materias_do_aluno=materias_do_aluno)
```

#### Validação:
- ✅ Template renderiza corretamente
- ✅ Colunas seguem novo padrão

---

### 📅 13/04/2026 - Correção: Exibição de Notas por Matéria

#### Problema:
`materia_id` retornava como `None` ao exibir notas do aluno.

#### Causa Raiz:
O método `Nota.to_dict()` não incluía `materia_id` no dicionário retornado.

#### Solução Aplicada:

**1. Modelo atualizado** (`app/models/nota.py`):
```python
def to_dict(self) -> dict:
    return {
        ...
        'materia_id': self.materia_id,  # ← Adicionado
        ...
    }
```

**2. Controller com fallback** (`alunos_controller.py`):
```python
# Fallback: get materia_id from atividade if not set on nota
if not materia_id and nota.get('atividade_id'):
    atividade = atividade_repo.get_by_id(nota['atividade_id'])
    if atividade:
        materia_id = atividade.get('materia_id')
```

#### Validação:
- ✅ materia_id exibido corretamente nas notas

---

### 📅 13/04/2026 - Correção: Erro em turma_repo.get_all()

#### Erro:
```
TypeError: TurmaRepository.get_all() got an unexpected keyword argument 'ativa'
```

#### Causa:
O método `get_all()` do `TurmaRepository` não aceitava o parâmetro `ativa` diretamente como argumento, mas utilizava o parâmetro `filters` para filtragem.

As chamadas em `atividades_controller.py` usavam:
```python
turmas = turma_repo.get_all(ativa=True)  # Incorreto
```

#### Solução Aplicada:
Corrigida a chamada para usar o parâmetro `filters`:
```python
turmas = turma_repo.get_all(filters={'ativa': True})  # Correto
```

#### Arquivos Modificados:
- `app/controllers/atividades_controller.py` (linhas 116 e 182)

#### Validação:
- ✅ Página de atividades retorna 200

---

### 📅 13/04/2026 - Correção de UI: Modal de Lançar Notas

#### Problema:
O modal de lançamento de notas não estava centralizado corretamente.

#### Solução Aplicada:
Atualizado o CSS do modal em `lancar_notas.html`:

**Antes:**
```css
.modal { position: fixed; ... }
.modal-content { margin: 10% auto; ... }
```

**Depois:**
```css
.modal {
    position: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.modal-box {
    background: var(--bg-primary);
    border-radius: 8px;
    padding: 20px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

#### Melhorias:
- ✅ Flexbox para centralização
- ✅ Variáveis CSS para cores (compatível com tema)
- ✅ Box-shadow para profundidade
- ✅ Botão de fechar com ícone

#### Validação:
- ✅ Página retorna 200

---

### 📅 13/04/2026 - Correção de UI: Modal de Lançar Notas (v2)

#### Problema:
Modal de notas ainda não estava perfeitamente centralizado e responsivo.

#### Solução Aplicada:
CSS atualizado com melhores práticas:

```css
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(2px);  /* Efeito de desfoque */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
    box-sizing: border-box;
}
.modal-box {
    background: var(--bg-primary);
    border-radius: 8px;
    padding: 24px;
    width: 100%;
    max-width: 400px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    animation: modalFadeIn 0.2s ease-out;
}
@keyframes modalFadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
```

#### Melhorias:
- ✅ `backdrop-filter: blur()` para efeito visual moderno
- ✅ `max-height: 90vh` + `overflow-y: auto` para telas pequenas
- ✅ `padding: 20px` no container para evitar overflow
- ✅ `box-sizing: border-box` para cálculos corretos
- ✅ Animação `modalFadeIn` para transição suave

#### Validação:
- ✅ Status 200

---

### 📅 13/04/2026 - Correção de UI: Modal de Notas (v3 - Final)

#### Problema:
Modal de notas não estava centralizado corretamente em diferentes tamanhos de tela.

#### Solução Aplicada:
CSS com Flexbox + Media Query para responsividade:

```css
.modal {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(2px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
    box-sizing: border-box;
}
.modal-box {
    background: var(--bg-primary);
    border-radius: 8px;
    padding: 24px;
    width: 100%;
    max-width: 400px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    animation: modalFadeIn 0.2s ease-out;
}
/* Responsividade para mobile */
@media (max-width: 480px) {
    .modal-box {
        max-width: 100%;
        padding: 16px;
    }
}
```

#### Melhorias:
- ✅ Flexbox para centralização perfeita
- ✅ `backdrop-filter` para overlay moderno
- ✅ `max-height: 90vh` para telas pequenas
- ✅ Media query `@media (max-width: 480px)` para mobile
- ✅ Animação suave de entrada

#### Validação:
- ✅ Status 200

---

### 📅 13/04/2026 - Correção: Página de Detalhes da Matéria

#### Problema:
A página de detalhes de cada matéria não estava exibindo corretamente:
- Professores que lecionam a matéria
- Turmas que possuem a matéria
- Textos com erros de idioma (russo/francês misturado com português)

#### Causa Raiz:
1. **Controller usava objeto antigo**: O `materias_controller.py` usava `_dict_to_materia_obj()` que criava um objeto artificial sem os relacionamentos
2. **Textos incorretos**: "Turmas que têm Esta Matéria" e "Nenhuma turma associée a esta matéria."

#### Correções Aplicadas:

**1. `materias_controller.py`** - Rota detalhe atualizada:
```python
# Antes (incorreto):
materia_data = materia_repo.get_by_id(id)
materia = _dict_to_materia_obj(materia_data)

# Depois (correto):
from app.models.materia import Materia
materia = Materia.query.get(id)
```

**2. `detalhe.html`** - Textos corrigidos:
- "Turmas que têm Esta Matéria" → "Turmas que possuem esta matéria"
- "Nenhuma turma associée a esta matéria." → "Nenhuma turma associada a esta matéria."

**3. Relacionamentos verificados**:
- `Materia.professores`: Relationship com `professor_materias` ✅
- `Materia.turmas`: Relationship com `turma_materias` ✅
- Dados carregando corretamente: 2 professores, 7 turmas para Matemática

#### Validação:
- ✅ Rota `/materias/1` retorna status 200
- ✅ Professores exibidos na tabela
- ✅ Turmas exibidas na tabela
- ✅ Mensagens amigáveis quando vazio

---

### 📅 13/04/2026 - Correção: Visualização do Calendário (Mês/Semana/Dia)

#### Problema:
Os botões de visualização do calendário (Mês/Semana/Dia) não alternavam corretamente entre os modos.

#### Causa Raiz:
O JavaScript não chamava `renderCalendar()` após alterar o `currentView`, mantendo sempre a visualização mensal.

#### Correções Aplicadas:

**1. `calendario/index.html`** - JavaScript corrigido:
```javascript
// Antes (incorreto):
document.querySelectorAll('.calendar-view-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        currentView = this.dataset.view;
    });
});

// Depois (correto):
document.querySelectorAll('.calendar-view-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        currentView = this.dataset.view;
        renderCalendar();  // ← Adicionado
    });
});
```

**2. Implementadas 3 visualizações funcionais**:

| Visualização | Descrição |
|--------------|------------|
| **Mês** | Grade mensal com dias e eventos resumidos |
| **Semana** | Grade semanal com dias e horários (7h-22h) |
| **Dia** | Lista de eventos do dia específico |

**3. Navegação adaptada por visualização**:
- **Mês**: Botões avançam/retrocedem um mês
- **Semana**: Botões avançam/retrocedem uma semana
- **Dia**: Botões avançam/retrocedem um dia

**4. API de eventos adaptada**: O endpoint `/calendario/api/eventos` agora recebe os parâmetros `inicio` e `fim` corretos conforme a visualização.

**5. Estilos CSS adicionados**:
- `.calendar-week-view`: Grade semanal
- `.calendar-day-view`: Visualização diária

#### Validação:
- ✅ Rota `/calendario/` retorna status 200
- ✅ Botões alternam visualização corretamente
- ✅ Navegação funciona para todos os modos
- ✅ Eventos carregados conforme período

---

### 📅 13/04/2026 - Correção: Geração de Calendário Acadêmico

#### Problema:
Erro ao gerar calendário acadêmico. O sistema não criava aulas e retornava `total_aulas: 0`.

#### Causas Raiz Identificadas:

1. **Conversão de data no repositório**: O `AulaRepository.create()` não convertia string de data para objeto date.

2. **Formato dos dados de matéria**: O gerador esperava estrutura aninhada mas repository retorna matéria direta.

3. **Lógica de datas**: As datas não eram passadas corretamente para `gerar_para_periodo_customizado`.

#### Validação:
- ✅ Geração de calendário cria aulas corretamente

---

### 📅 13/04/2026 - Novo Sistema de Notas e Atividades

#### Problema Anterior:
- Notas não organizadas corretamente
- Falta separação por ano e matéria
- Não havia estrutura de atividades

#### Nova Estrutura Implementada:

**1. Modelo `Atividade` (`app/models/atividade.py`)**:
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | PK |
| nome | VARCHAR(100) | Nome da atividade |
| descricao | TEXT | Descrição |
| data | DATE | Data da atividade |
| materia_id | INTEGER | FK matéria |
| turma_id | INTEGER | FK turma |
| professor_id | INTEGER | FK professor |
| tipo | VARCHAR(30) | prova/trabalho/exercicio/participacao/projeto |
| peso | FLOAT | Peso (default 1.0) |
| valor_maximo | FLOAT | Valor máximo (default 10.0) |

**2. Modelo `Nota` atualizado**:
- Adicionado `atividade_id` - FK para Atividade
- Adicionado `ano_letivo` - INTEGER (ano das notas)
- Adicionado `materia_id` - FK matéria

**3. Hierarquia de Exibição**:
```
Ano Letivo (2026)
 └── Matemática
     ├── Atividade 1: Nota 8.0
     ├── Atividade 2: Nota 7.5
     └── Média: 7.75
 └── Português
     └── ...
```

**4. Repositório `AtividadeRepository`**:
- `get_by_turma()` - Buscar atividades por turma
- `get_by_turma_materia()` - Buscar por turma e matéria
- `get_by_professor()` - Atividades do professor
- `create()`, `update()`, `delete()` - CRUD completo

**5. Controller de Atividades**:
- `GET /atividades/turma/<id>` - Lista atividades
- `GET /atividades/turma/<id>/novo` - Criar atividade
- `GET /atividades/<id>/lancar-notas` - Lançar notas
- `POST /atividades/<id>/lancar-notas` - Salvar nota (API)

**6. Interface de Turmas**:
- Botão "Cadastrar Atividade" 
- Botão "Ver Atividades"

**7. Interface de Alunos**:
- Exibição de notas organizada por:
  - Ano letivo
  - Matéria
  - Lista de atividades com notas
  - Média calculada por matéria

#### Validação:
- ✅ Página de atividades retorna 200
- ✅ Página de detalhe do aluno retorna 200
- ✅ Banco atualizado com novas colunas

---

#### Problema:
A página de detalhes do professor não estava exibindo corretamente:
- Disponibilidades não eram carregadas
- Turmas não eram exibidas

#### Causa Raiz:
1. **Bug no `ProfessorDTO.turmas`**: O método chamava `get_by_turma()` passando `professor_id`, mas esse método espera `turma_id` (era a relação inversa)

2. **Bug no `DisponibilidadeObj`**: A classe interna não tinha acesso ao método `parse_time()` herdado de `BaseDTO`

3. **Repository incompleto**: Faltava método `get_turmas()` para buscar turmas de um professor

#### Correções Aplicadas:

**1. `professor_repository.py`** - Adicionado novo método:
```python
def get_turmas(self, professor_id: int) -> List[Dict]:
    """Retorna as turmas de um professor."""
    professor = Professor.query.get(professor_id)
    if professor:
        return [t.to_dict() for t in professor.turmas]
    return []
```

**2. `professor_dto.py`** - Corrigido `turmas` property:
```python
@property
def turmas(self) -> list:
    # Antes (incorreto): usava get_by_turma
    # Depois (correto): usa get_turmas
    turmas_raw = professor_repo.get_turmas(self.id)
    self._turmas = [TurmaDTO(t, self._repos) for t in turmas_raw]
```

**3. `professor_dto.py`** - Corrigido `DisponibilidadeObj._parse_time()`:
```python
@staticmethod
def _parse_time(value):
    """Parse time from string or return None."""
    if value is None:
        return None
    if hasattr(value, 'strftime'):
        return value
    from datetime import time
    if isinstance(value, str):
        parts = value.split(':')
        return time(int(parts[0]), int(parts[1]))
    return value
```

**4. `professores_controller.py`** - Adicionado repo ao dicionário:
```python
_repos = {
    'professor': _professor_repo,
    'materia': _materia_repo,
    'usuario': _usuario_repo,
    'disponibilidade': _disponibilidade_repo  # Adicionado
}
```

#### Verificação:
- ✅ Nome do professor: Maria Santos
- ✅ Email: maria@escola.com
- ✅ Materias: 1 (Matemática)
- ✅ Disponibilidades: 10 entries (dias e horários)
- ✅ Turmas: Carregadas corretamente via relationship

---

### 📅 13/04/2026 - Correção de Layout: Professor Detail Page

#### Problema:
Na página de detalhes do professor (`professores/detalhe.html`), os elementos "Disponibilidade" e "Turmas" estavam ordenados incorretamente.

#### Ordem Anterior (incorreta):
1. Matérias que Pode Lecionar
2. Turmas
3. Disponibilidade

#### Nova Ordem (corrigida):
1. Matérias que Pode Lecionar
2. Disponibilidade (mover antes de Turmas - disponibilidade determina quais turmas o professor pode lecionar)
3. Turmas

#### Alteração:
- Seção "Disponibilidade" movida para antes de "Turmas" para manter lógica de negócio
- Botão "Adicionar" movido para o header do card para melhor UX

---

### 📅 13/04/2026 - Correção: Matérias não aparecem na turma

#### Problema:
A página de detalhes da turma (`turmas/detalhe.html`) mostrava "Nenhuma matéria cadastrada" mesmo após a migração para SQLAlchemy.

#### Causa Raiz:
A tabela `turma_materias` existia no banco de dados mas **não tinha associações**. A seed script não criava os registros corretamente.

#### Solução Aplicada:
1. Executado script para popular `turma_materias`:
   - 7 turmas × 7 matérias = **49 associações criadas**
   - Cada matéria associada com `aulas_por_periodo` baseado na carga horária:
     - Matemática: 4 aulas/semana
     - Português: 4 aulas/semana
     - Ciências: 2 aulas/semana
     - História: 2 aulas/semana
     - Geografia: 2 aulas/semana
     - Inglês: 2 aulas/semana
     - Ed. Física: 2 aulas/semana

2. Executado script para popular `professor_materias`:
   - 11 associações criadas (cada professor à sua especialidade)

#### Verificação:
- ✅ `turma.materias` retorna 7 matérias
- ✅ `turma.get_aulas_por_periodo(materia_id)` retorna valor correto
- ✅ `materia.professores.filter_by(ativo=True)` retorna professores

#### Fluxo verificado:
```
TurmaDTO.materias → TurmaRepository.get_materias() → turma.materias (relationship)
                                                      ↓
                                              materia.to_dict()
                                              ↓
                                         MateriaDTO(data)
```

---

### 📅 13/04/2026 - Correção ImportError (turma_materias)

#### Problema:
```
ImportError: cannot import name 'turma_materias' from 'app.models.turma'
```

#### Causa Raiz:
A tabela `turma_materias` estava definida em `app/models/materia.py`, mas alguns arquivos tentavam importar de `app/models/turma.py`:

```python
# ❌ INCORRETO - tentou importar de turma.py
from app.models.turma import turma_materias

# ✅ CORRETO - está definido em materia.py
from app.models.materia import turma_materias
```

#### Arquivos Corrigidos:

| Arquivo | Linha | Correção |
|---------|-------|----------|
| `app/controllers/turmas_controller.py` | 269 | `app.models.turma` → `app.models.materia` |
| `app/repositories/materia_repository.py` | 186, 214 | `app.models.turma` → `app.models.materia` |

#### Estrutura Correta:
```
app/models/
├── materia.py          # Define: turma_materias, professor_materias
│   └── turma_materias = db.Table('turma_materias', ...)
│
└── turma.py           # Usa: secondary='turma_materias' no relationship
    └── materias = relationship('Materia', secondary='turma_materias', ...)
```

#### Testes Realizados:
- ✅ Imports funcionando
- ✅ App criada com sucesso
- ✅ Blueprint registrado
- ✅ Matérias: 7 encontradas
- ✅ Turmas: 7 encontradas
- ✅ Servidor funcionando

---

### 📅 13/04/2026 - Correção ModuleNotFoundError (Imports Remanescentes do Supabase)

#### Problema:
```
ModuleNotFoundError: No module named 'app.services.supabase_client'
```

#### Causa Raiz:
Após remover o arquivo `supabase_client.py`, havia **8 arquivos** que ainda importavam dele:

1. `app/controllers/professores_controller.py` (2 imports)
2. `app/dtos/professor_dto.py` (2 imports)
3. `app/controllers/configuracoes_controller.py` (1 import)
4. `app/controllers/turmas_controller.py` (1 import)
5. `app/dtos/turma_dto.py` (1 import)
6. `app/dtos/aluno_dto.py` (1 import)

#### Solução Aplicada:

**1. Criado novo Repository:**
- `app/repositories/disponibilidade_repository.py`: Repository para `DisponibilidadeProfessor`

**2. Atualizado Modelo:**
- `app/models/especialidade.py`: Adicionado método `to_dict()` ao `DisponibilidadeProfessor`

**3. Atualizado `__init__.py` dos Models:**
- Adicionado `DisponibilidadeProfessor` ao exports

**4. Atualizado `__init__.py` dos Repositories:**
- Adicionado `DisponibilidadeRepository` ao exports

**5. Corrigidos Controllers:**
- `professores_controller.py`: Removidos imports do Supabase, usa SQLAlchemy
- `turmas_controller.py`: Removido import do Supabase, usa SQLAlchemy
- `configuracoes_controller.py`: Reescrito `verificar_banco()` para usar SQLAlchemy

**6. Corrigidos DTOs:**
- `professor_dto.py`: Removidos imports do Supabase
- `turma_dto.py`: `get_aulas_por_periodo()` usa SQLAlchemy
- `aluno_dto.py`: Propriedade `turmas` usa SQLAlchemy

#### Boas Práticas para Evitar Este Erro:
- **Remover imports órfãos** quando um módulo é removido
- **Verificar todos os arquivos** que usam um módulo antes de removê-lo
- **Usar grep** para encontrar imports relacionados
- **Testar incrementalmente** após cada mudança

#### Testes Realizados:
- Todos os imports: ✅ Sucesso
- App criação: ✅ Sucesso
- Blueprint registro: ✅ Sucesso
- Tabelas no banco: 18 tabelas
- Servidor Flask: ✅ Funcionando

---

### 📅 13/04/2026 - Correção do Erro NoInspectionAvailable

#### Problema:
```
sqlalchemy.exc.NoInspectionAvailable: No inspection system is available for object of type <class 'str'>
```

#### Causa Raiz:
No arquivo `app/repositories/aluno_repository.py`, linha 74, havia:
```python
turma = db.session.get('Turma', turma_id)  # ❌ String ao invés do modelo
```

O SQLAlchemy esperava um **modelo/classe** (`Turma`), mas recebeu uma **string** (`'Turma'`).

#### Solução Aplicada:
1. Adicionado import do modelo `Turma` no arquivo
2. Substituído `db.session.get('Turma', turma_id)` por `Turma.query.get(turma_id)`

```python
# Antes (INCORRETO):
turma = db.session.get('Turma', turma_id)

# Depois (CORRETO):
from app.models.turma import Turma  # Linha 10
turma = Turma.query.get(turma_id)
```

#### Boas Práticas para Evitar Este Erro:
- **Sempre usar modelos/classe** ao invés de strings para operações ORM
- **Usar `Model.query.get(id)`** para buscar por ID
- **Usar `db.session.get(Model, id)`** passando o modelo, nunca uma string
- **Importar modelos** explicitamente no início do arquivo

#### Testes Realizados:
- `get_by_turma(1)`: ✅ Sucesso - retornou 2 alunos
- `get_all()`: ✅ Sucesso - retornou 126 alunos
- `search("Maria")`: ✅ Sucesso - retornou 5 resultados
- Todos os repositories testados: ✅ Passaram

---

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

### 📅 13/04/2026 - Correção de UI: Modal de Notas (v4 - Final)

#### Problema:
Modal de notas não estava centralizado corretamente e faltavam funcionalidades de usabilidade.

#### Solução Aplicada:

**1. Centralização com Flexbox:**
```css
.modal {
    position: fixed;
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
```

**2. Fechar ao clicar fora:**
```html
<div id="notaModal" onclick="fecharModalOutside(event)">
    <div class="modal-box" onclick="event.stopPropagation()">
```

```javascript
function fecharModalOutside(event) {
    if (event.target.id === 'notaModal') {
        fecharModal();
    }
}
```

**3. Acessibilidade:**
```html
<button class="modal-close" onclick="fecharModal()" aria-label="Fechar">
```

#### Melhorias:
- ✅ Flexbox com `height: 100vh` para centralização perfeita
- ✅ Fechar ao clicar no overlay (fora do modal)
- ✅ `event.stopPropagation()` impede cierre ao clicar no conteúdo
- ✅ `aria-label` para acessibilidade
- ✅ Botão de fechar com ícone

#### Validação:
- ✅ Todas as checagens passaram

---
