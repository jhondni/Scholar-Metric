"""
app/dtos/aula_dto.py - DTO de Aula

Encapsula dados da aula do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Aula.
"""

from datetime import datetime, date, time as time_class, timedelta
from app.dtos.base_dto import BaseDTO


class AulaDTO(BaseDTO):
    """
    Data Transfer Object para Aula.
    
    Fornece todos os atributos e métodos esperados pelos templates.
    """
    
    def __init__(self, data: dict, repos: dict = None):
        """
        Inicializa o DTO a partir de dados do Supabase.
        
        Args:
            data: Dicionário com dados do Supabase
            repos: Dicionário com repositórios para consultas
        """
        self.id = data.get('id')
        self.materia = data.get('materia', '')
        self.descricao = data.get('descricao', '')
        self.turma_id = data.get('turma_id')
        self.professor_id = data.get('professor_id')
        self.data = self.parse_date(data.get('data'))
        self.horario_inicio = self.parse_time(data.get('horario_inicio'))
        self.horario_fim = self.parse_time(data.get('horario_fim'))
        self.recorrente = self.parse_bool(data.get('recorrente'))
        self.tipo_recorrencia = data.get('tipo_recorrencia')
        self.dia_semana = data.get('dia_semana')
        self.data_fim_recorrencia = self.parse_date(data.get('data_fim_recorrencia'))
        self.aula_pai_id = data.get('aula_pai_id')
        self.status = data.get('status', 'agendada')
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._turma = None
        self._professor = None
        self._frequencias = None
        self._aulas_filhas = None
    
    @property
    def turma(self):
        """
        Retorna o objeto TurmaDTO associado.
        
        Returns:
            TurmaDTO: Objeto da turma
        """
        if self._turma is not None:
            return self._turma
        
        from app.repositories import TurmaRepository
        from app.dtos.turma_dto import TurmaDTO
        
        turma_repo = self._repos.get('turma') or TurmaRepository()
        turma_data = turma_repo.get_by_id(self.turma_id)
        
        if turma_data:
            self._turma = TurmaDTO(turma_data, self._repos)
        else:
            self._turma = type('Turma', (), {'id': None, 'nome': 'N/A', 'codigo': 'N/A'})()
        
        return self._turma
    
    @property
    def professor(self):
        """
        Retorna o objeto ProfessorDTO associado.
        
        Returns:
            ProfessorDTO: Objeto do professor
        """
        if self._professor is not None:
            return self._professor
        
        from app.repositories import ProfessorRepository
        from app.dtos.professor_dto import ProfessorDTO
        
        professor_repo = self._repos.get('professor') or ProfessorRepository()
        professor_data = professor_repo.get_by_id(self.professor_id)
        
        if professor_data:
            self._professor = ProfessorDTO(professor_data, self._repos)
        else:
            self._professor = type('Professor', (), {
                'id': None,
                'usuario': type('Usuario', (), {'nome': 'N/A'})()
            })()
        
        return self._professor
    
    @property
    def frequencias(self):
        """
        Retorna as frequências da aula.
        
        Returns:
            list: Lista de FrequenciaDTO
        """
        if self._frequencias is not None:
            return self._frequencias
        
        from app.repositories import FrequenciaRepository, AlunoRepository
        from app.dtos.frequencia_dto import FrequenciaDTO
        
        freq_repo = self._repos.get('frequencia') or FrequenciaRepository()
        
        freqs_raw = freq_repo.get_by_aula(self.id)
        
        # Enriquecer com dados do aluno
        aluno_repo = self._repos.get('aluno') or AlunoRepository()
        
        self._frequencias = []
        for freq in freqs_raw:
            aluno_data = aluno_repo.get_by_id(freq.get('aluno_id'))
            freq['aluno'] = aluno_data or {'nome': 'N/A'}
            self._frequencias.append(FrequenciaDTO(freq, self._repos))
        
        return self._frequencias
    
    def count_frequencias(self) -> int:
        """
        Retorna o número de frequências registradas.
        
        Returns:
            int: Número de frequências
        """
        from app.repositories import FrequenciaRepository
        
        freq_repo = self._repos.get('frequencia') or FrequenciaRepository()
        freqs = freq_repo.get_by_aula(self.id)
        return len(freqs)
    
    @staticmethod
    def gerar_datas_recorrencia(data_inicio: date, tipo_recorrencia: str, 
                                data_fim: date) -> list:
        """
        Gera datas para aulas recorrentes.
        
        Args:
            data_inicio: Data inicial
            tipo_recorrencia: Tipo de recorrência
            data_fim: Data final
            
        Returns:
            list: Lista de datas
        """
        datas = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            datas.append(data_atual)
            
            if tipo_recorrencia == 'semanal':
                data_atual += timedelta(weeks=1)
            elif tipo_recorrencia == 'mensal':
                data_atual += timedelta(days=30)
            elif tipo_recorrencia == 'bimestral':
                data_atual += timedelta(days=60)
            elif tipo_recorrencia == 'trimestral':
                data_atual += timedelta(days=90)
            elif tipo_recorrencia == 'semestral':
                data_atual += timedelta(days=180)
            elif tipo_recorrencia == 'anual':
                data_atual += timedelta(days=365)
            else:
                break
        
        return datas
    
    def __repr__(self):
        return f'<AulaDTO {self.materia} - {self.data}>'
