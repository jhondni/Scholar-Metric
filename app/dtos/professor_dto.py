"""
app/dtos/professor_dto.py - DTO de Professor

Encapsula dados do professor do Supabase e fornece a mesma interface
que o modelo SQLAlchemy Professor.
"""

from datetime import datetime, time as time_class
from app.dtos.base_dto import BaseDTO


class ProfessorDTO(BaseDTO):
    """
    Data Transfer Object para Professor.
    
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
        self.usuario_id = data.get('usuario_id')
        self.registro = data.get('registro', '')
        self.especialidade = data.get('especialidade', '')
        self.formacao = data.get('formacao', '')
        self.cpf = data.get('cpf', '')
        self.telefone = data.get('telefone', '')
        self.endereco = data.get('endereco', '')
        self.ativo = self.parse_bool(data.get('ativo', True))
        self.criado_em = self.parse_datetime(data.get('criado_em'))
        self.atualizado_em = self.parse_datetime(data.get('atualizado_em'))
        
        # Repositórios para consultas
        self._repos = repos or {}
        self._usuario = None
        self._turmas = None
        self._materias = None
        self._aulas_count = None
        self._disponibilidades = None
    
    @property
    def usuario(self):
        """
        Retorna o objeto UsuarioDTO associado.
        
        Returns:
            UsuarioDTO: Objeto do usuário
        """
        if self._usuario is not None:
            return self._usuario
        
        from app.repositories import UsuarioRepository
        from app.dtos.usuario_dto import UsuarioDTO
        
        usuario_repo = self._repos.get('usuario') or UsuarioRepository()
        usuario_data = usuario_repo.get_by_id(self.usuario_id)
        
        if usuario_data:
            self._usuario = UsuarioDTO(usuario_data)
        else:
            # Criar objeto vazio para evitar erros
            self._usuario = UsuarioDTO({'nome': 'N/A', 'email': 'N/A'})
        
        return self._usuario
    
    def total_aulas(self, periodo: tuple = None) -> int:
        """
        Retorna o total de aulas do professor.
        
        Args:
            periodo: Tupla com (data_inicio, data_fim) para filtrar
            
        Returns:
            int: Número de aulas
        """
        from app.repositories import AulaRepository
        
        aula_repo = self._repos.get('aula') or AulaRepository()
        
        if periodo:
            aulas = aula_repo.get_by_date_range(periodo[0], periodo[1])
            aulas = [a for a in aulas if a.get('professor_id') == self.id]
        else:
            aulas = aula_repo.get_by_professor(self.id)
        
        return len(aulas)
    
    @property
    def turmas(self) -> list:
        """
        Retorna as turmas do professor.
        
        Returns:
            list: Lista de TurmaDTO
        """
        if self._turmas is not None:
            return self._turmas
        
        from app.repositories import ProfessorRepository, TurmaRepository
        from app.dtos.turma_dto import TurmaDTO
        
        professor_repo = self._repos.get('professor') or ProfessorRepository()
        
        turmas_raw = professor_repo.get_by_turma(self.id)
        # get_by_turma na verdade busca professores de uma turma
        # Precisamos buscar as turmas do professor
        
        from app.services.supabase_client import get_supabase_client
        try:
            client = get_supabase_client()
            result = client.table('professores_turmas').select('turma_id').eq('professor_id', self.id).execute()
            
            turma_repo = self._repos.get('turma') or TurmaRepository()
            self._turmas = []
            
            for item in (result.data or []):
                turma_data = turma_repo.get_by_id(item.get('turma_id'))
                if turma_data:
                    self._turmas.append(TurmaDTO(turma_data, self._repos))
        except Exception as e:
            print(f"[ERRO] ProfessorDTO.turmas: {e}")
            self._turmas = []
        
        return self._turmas
    
    @property
    def materias(self) -> list:
        """
        Retorna as matérias que o professor pode lecionar.
        
        Returns:
            list: Lista de MateriaDTO
        """
        if self._materias is not None:
            return self._materias
        
        from app.repositories import ProfessorRepository
        from app.dtos.materia_dto import MateriaDTO
        
        professor_repo = self._repos.get('professor') or ProfessorRepository()
        
        materias_raw = professor_repo.get_materias(self.id)
        self._materias = [MateriaDTO(m, self._repos) for m in materias_raw]
        
        return self._materias
    
    @property
    def disponibilidades(self) -> list:
        """
        Retorna as disponibilidades do professor.
        
        Returns:
            list: Lista de objetos de disponibilidade
        """
        if self._disponibilidades is not None:
            return self._disponibilidades
        
        from app.services.supabase_client import get_supabase_client
        try:
            client = get_supabase_client()
            result = client.table('disponibilidade_professores').select('*')
            result = result.eq('professor_id', self.id).eq('ativo', True)
            result = result.order('dia_semana').execute()
            
            self._disponibilidades = []
            for disp in (result.data or []):
                disp_obj = type('Disponibilidade', (), {
                    'id': disp.get('id'),
                    'professor_id': disp.get('professor_id'),
                    'dia_semana': disp.get('dia_semana'),
                    'horario_inicio': self.parse_time(disp.get('horario_inicio')),
                    'horario_fim': self.parse_time(disp.get('horario_fim')),
                    'ativo': self.parse_bool(disp.get('ativo', True)),
                    'get_dia_label': lambda ds: self._get_dia_label(ds)
                })()
                self._disponibilidades.append(disp_obj)
        except Exception as e:
            # Tabela pode não existir no Supabase
            if 'PGRST205' in str(e) or 'Could not find the table' in str(e):
                pass  # Tabela não existe ainda
            else:
                print(f"[ERRO] ProfessorDTO.disponibilidades: {e}")
            self._disponibilidades = []
        
        return self._disponibilidades
    
    @staticmethod
    def _get_dia_label(dia_semana: int) -> str:
        """Retorna label do dia da semana."""
        dias = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        return dias.get(dia_semana, '')
    
    def __repr__(self):
        return f'<ProfessorDTO {self.registro}>'
