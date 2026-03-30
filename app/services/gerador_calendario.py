# app/services/gerador_calendario.py - Serviço de Geração de Calendário Acadêmico
# Módulo avançado para geração automática de calendário escolar
#
# ATUALIZADO: Usa Supabase REST API via repositórios (compatível com Vercel Serverless)
# ANTERIOR: Usava SQLAlchemy ORM (incompatível com ambiente serverless)

from datetime import date, time, timedelta
from typing import List, Dict, Optional, Tuple

from app.repositories import (
    AulaRepository,
    TurmaRepository,
    ProfessorRepository,
    FeriadoRepository,
    DiaNaoLetivoRepository
)


class GeradorCalendarioAcademico:
    """
    Serviço avançado de geração de calendário acadêmico.
    
    Implementa lógica heurística para distribuição automática de aulas
    considerando professores, turmas, matérias e calendário acadêmico.
    
    Usa Supabase REST API via repositórios para compatibilidade com
    ambiente serverless (Vercel).
    """
    
    # Duração padrão de cada aula em minutos
    DURACAO_AULA = 50
    
    # Definição de turnos e seus horários
    HORARIOS_TURNO = {
        'manha': [
            (time(7, 0), time(7, 50)),
            (time(8, 0), time(8, 50)),
            (time(9, 0), time(9, 50)),
            (time(10, 0), time(10, 50)),
            (time(11, 0), time(11, 50))
        ],
        'tarde': [
            (time(13, 0), time(13, 50)),
            (time(14, 0), time(14, 50)),
            (time(15, 0), time(15, 50)),
            (time(16, 0), time(16, 50)),
            (time(17, 0), time(17, 50))
        ],
        'noite': [
            (time(19, 0), time(19, 50)),
            (time(20, 0), time(20, 50)),
            (time(21, 0), time(21, 50))
        ]
    }
    
    def __init__(self, periodo: str = 'trimestral'):
        """
        Inicializa o gerador de calendário.
        
        Args:
            periodo: Período para geração ('trimestral', 'semestral', 'anual')
        """
        self.periodo = periodo
        self.aulas_criadas = []
        self.conflitos = []
        self.errors = []
        
        # Inicializar repositórios
        self._aula_repo = AulaRepository()
        self._turma_repo = TurmaRepository()
        self._professor_repo = ProfessorRepository()
        self._feriado_repo = FeriadoRepository()
        self._dia_nao_letivo_repo = DiaNaoLetivoRepository()
        
        self._definir_periodo_datas()
    
    def _definir_periodo_datas(self):
        """Define as datas de início e fim baseado no período."""
        hoje = date.today()
        
        if self.periodo == 'trimestral':
            self.data_fim = hoje + timedelta(days=90)
        elif self.periodo == 'semestral':
            self.data_fim = hoje + timedelta(days=180)
        elif self.periodo == 'anual':
            self.data_fim = hoje + timedelta(days=365)
        else:
            self.data_fim = hoje + timedelta(days=90)  # Default trimestral
        
        self.data_inicio = hoje
    
    def verificar_dia_letivo(self, data: date) -> bool:
        """
        Verifica se um dia é letivo (não é feriado nem dia não letivo).
        
        Args:
            data: Data a verificar
            
        Returns:
            bool: True se for dia letivo
        """
        try:
            if self._feriado_repo.is_feriado(data):
                return False
            if self._dia_nao_letivo_repo.is_dia_nao_letivo(data):
                return False
            return True
        except Exception as e:
            print(f"[ERRO] verificar_dia_letivo: {e}")
            return True  # Em caso de erro, considerar dia letivo
    
    def get_horarios_periodo(self, turno: str) -> List[Tuple[time, time]]:
        """Retorna os horários típicos para um turno."""
        return self.HORARIOS_TURNO.get(turno, self.HORARIOS_TURNO['manha'])
    
    def verificar_conflito_professor(self, professor_id: int, data: date, 
                                     inicio: time, fim: time, 
                                     turma_id_exclude: Optional[int] = None) -> bool:
        """
        Verifica se o professor tem conflito de horário.
        
        Args:
            professor_id: ID do professor
            data: Data da aula
            inicio: Horário de início
            fim: Horário de fim
            turma_id_exclude: ID de turma a excluir (para UPDATE)
            
        Returns:
            bool: True se há conflito
        """
        try:
            aulas_professor = self._aula_repo.get_by_professor(professor_id)
            data_str = str(data)
            inicio_str = str(inicio)
            fim_str = str(fim)
            
            for aula in aulas_professor:
                if aula.get('data') != data_str:
                    continue
                if aula.get('status') == 'cancelada':
                    continue
                if turma_id_exclude and aula.get('turma_id') == turma_id_exclude:
                    continue
                
                aula_inicio = aula.get('horario_inicio', '')
                aula_fim = aula.get('horario_fim', '')
                
                # Verificar sobreposição de horários
                if aula_inicio < fim_str and aula_fim > inicio_str:
                    return True
            
            return False
        except Exception as e:
            print(f"[ERRO] verificar_conflito_professor: {e}")
            return False
    
    def verificar_conflito_turma(self, turma_id: int, data: date, 
                                 inicio: time, fim: time) -> bool:
        """
        Verifica se a turma tem conflito de horário.
        
        Args:
            turma_id: ID da turma
            data: Data da aula
            inicio: Horário de início
            fim: Horário de fim
            
        Returns:
            bool: True se há conflito
        """
        try:
            aulas_turma = self._aula_repo.get_by_turma(turma_id)
            data_str = str(data)
            inicio_str = str(inicio)
            fim_str = str(fim)
            
            for aula in aulas_turma:
                if aula.get('data') != data_str:
                    continue
                if aula.get('status') == 'cancelada':
                    continue
                
                aula_inicio = aula.get('horario_inicio', '')
                aula_fim = aula.get('horario_fim', '')
                
                # Verificar sobreposição de horários
                if aula_inicio < fim_str and aula_fim > inicio_str:
                    return True
            
            return False
        except Exception as e:
            print(f"[ERRO] verificar_conflito_turma: {e}")
            return False
    
    def verificar_conflito_alunos(self, turma_id: int, data: date, 
                                   inicio: time, fim: time, 
                                   turmas_alunos: Dict[int, List[int]]) -> bool:
        """
        Verifica se alunos de outra turma terão aula no mesmo horário.
        
        Args:
            turma_id: ID da turma atual
            data: Data da aula
            inicio: Horário de início
            fim: Horário de fim
            turmas_alunos: Dicionário de IDs de alunos por turma
            
        Returns:
            bool: True se há conflito de alunos
        """
        if not turmas_alunos or turma_id not in turmas_alunos:
            return False
        
        try:
            alunos_turma = set(turmas_alunos.get(turma_id, []))
            data_str = str(data)
            inicio_str = str(inicio)
            fim_str = str(fim)
            
            # Buscar todas as aulas do dia
            aulas_dia = self._aula_repo.get_by_date(data)
            
            for aula in aulas_dia:
                if aula.get('turma_id') == turma_id:
                    continue
                if aula.get('status') == 'cancelada':
                    continue
                
                aula_inicio = aula.get('horario_inicio', '')
                aula_fim = aula.get('horario_fim', '')
                
                # Verificar sobreposição de horários
                if aula_inicio < fim_str and aula_fim > inicio_str:
                    aula_turma_id = aula.get('turma_id')
                    alunos_aula = set(turmas_alunos.get(aula_turma_id, []))
                    if alunos_turma & alunos_aula:  # Interseção
                        return True
            
            return False
        except Exception as e:
            print(f"[ERRO] verificar_conflito_alunos: {e}")
            return False
    
    def professor_pode_lecionar(self, professor_id: int, materia_id: int) -> bool:
        """
        Verifica se o professor está habilitado para a matéria.
        
        Args:
            professor_id: ID do professor
            materia_id: ID da matéria
            
        Returns:
            bool: True se pode lecionar
        """
        try:
            materias_professor = self._professor_repo.get_materias(professor_id)
            return any(m.get('id') == materia_id for m in materias_professor)
        except Exception as e:
            print(f"[ERRO] professor_pode_lecionar: {e}")
            return False
    
    def encontrar_professor_disponivel(self, materia_id: int, materia_nome: str,
                                        data: date, horarios: List[Tuple[time, time]], 
                                        turma_id: Optional[int] = None) -> Optional[Dict]:
        """
        Encontra um professor disponível para lecionar a matéria no horário.
        
        Usa abordagem gulosa: tenta encontrar primeiro professor disponível.
        
        Args:
            materia_id: ID da matéria a ser lecionada
            materia_nome: Nome da matéria
            data: Data da aula
            horarios: Lista de horários disponíveis
            turma_id: ID da turma (para exclusões)
            
        Returns:
            Dict do professor disponível ou None
        """
        try:
            # Buscar professores que podem lecionar esta matéria
            professores_validos = self._professor_repo.get_by_materia(materia_id)
            professores_ativos = [p for p in professores_validos if p.get('ativo', True)]
            
            if not professores_ativos:
                return None
            
            # Tentar encontrar professor disponível
            for professor in professores_ativos:
                disponivel = True
                for h_inicio, h_fim in horarios:
                    if self.verificar_conflito_professor(
                        professor.get('id'), data, h_inicio, h_fim, turma_id
                    ):
                        disponivel = False
                        break
                
                if disponivel:
                    return professor
            
            return None
        except Exception as e:
            print(f"[ERRO] encontrar_professor_disponivel: {e}")
            return None
    
    def distribuir_aulas_turma(self, turma: Dict, turmas_alunos: Dict[int, List[int]]) -> Dict:
        """
        Distribui as aulas para uma turma respeitando todas as regras.
        
        Args:
            turma: Dicionário com dados da turma
            turmas_alunos: Dicionário de alunos por turma
            
        Returns:
            Dict: Resultado da operação
        """
        turma_id = turma.get('id')
        turma_nome = turma.get('nome', 'Desconhecida')
        
        if not turma.get('ativa', True):
            return {'success': False, 'error': f'Turma {turma_nome} está inativa'}
        
        # Buscar matérias da turma
        materias_data = self._turma_repo.get_materias(turma_id)
        if not materias_data:
            return {'success': False, 'error': f'Turma {turma_nome} não possui matérias cadastradas'}
        
        # Buscar alunos da turma
        alunos = self._turma_repo.get_alunos(turma_id)
        if not alunos:
            return {'success': False, 'error': f'Turma {turma_nome} não possui alunos matriculados'}
        
        horarios = self.get_horarios_periodo(turma.get('turno', 'manha'))
        aulas_criadas_count = 0
        
        # Processar cada dia do período
        data_atual = self.data_inicio
        while data_atual <= self.data_fim:
            # Pular dias não letivos (feriados, dias especiais)
            if not self.verificar_dia_letivo(data_atual):
                data_atual += timedelta(days=1)
                continue
            
            # Pular fins de semana (0=Segunda, 6=Domingo)
            if data_atual.weekday() >= 5:
                data_atual += timedelta(days=1)
                continue
            
            # Para cada matéria da turma
            for materia_info in materias_data:
                materia = materia_info.get('materias', {})
                materia_id = materia.get('id')
                materia_nome = materia.get('nome', 'N/A')
                
                if not materia_id:
                    continue
                
                # Verificar se já existe aula desta matéria neste dia
                aulas_existentes = self._aula_repo.get_by_date(data_atual, turma_id)
                ja_existe = any(
                    a.get('materia') == materia_nome 
                    for a in aulas_existentes
                    if a.get('status') != 'cancelada'
                )
                
                if ja_existe:
                    continue
                
                # Tentar cada horário até encontrar um disponível
                for h_inicio, h_fim in horarios:
                    # Verificar conflito de turma
                    if self.verificar_conflito_turma(turma_id, data_atual, h_inicio, h_fim):
                        continue
                    
                    # Verificar conflitos de alunos com outras turmas
                    if self.verificar_conflito_alunos(turma_id, data_atual, h_inicio, h_fim, turmas_alunos):
                        continue
                    
                    # Encontrar professor disponível
                    professor = self.encontrar_professor_disponivel(
                        materia_id, materia_nome, data_atual, [(h_inicio, h_fim)], turma_id
                    )
                    
                    if not professor:
                        # Nenhum professor disponível para esta matéria/horário
                        continue
                    
                    # Verificar novamente conflito para o professor específico
                    if self.verificar_conflito_professor(
                        professor.get('id'), data_atual, h_inicio, h_fim, turma_id
                    ):
                        continue
                    
                    # Criar a aula via Supabase
                    aula_data = {
                        'materia': materia_nome,
                        'turma_id': turma_id,
                        'professor_id': professor.get('id'),
                        'data': str(data_atual),
                        'horario_inicio': str(h_inicio),
                        'horario_fim': str(h_fim),
                        'status': 'agendada',
                        'recorrente': False
                    }
                    
                    resultado = self._aula_repo.create(aula_data)
                    if resultado:
                        self.aulas_criadas.append(resultado)
                        aulas_criadas_count += 1
                    
                    # Após criar uma aula, passar para o próximo dia para distribuir melhor
                    break
            
            data_atual += timedelta(days=1)
        
        return {
            'success': True, 
            'aulas_criadas': aulas_criadas_count,
            'turma': turma_nome
        }
    
    def gerar_para_todas_turmas(self, turma_ids: Optional[List[int]] = None) -> Dict:
        """
        Gera calendário para todas as turmas ativas.
        
        Args:
            turma_ids: IDs específicos de turmas (None = todas ativas)
            
        Returns:
            Dict: Resultado com total de aulas criadas
        """
        try:
            # Buscar turmas
            if turma_ids:
                todas_turmas = self._turma_repo.get_active_turmas()
                turmas = [t for t in todas_turmas if t.get('id') in turma_ids]
            else:
                turmas = self._turma_repo.get_active_turmas()
            
            if not turmas:
                return {'success': False, 'error': 'Nenhuma turma ativa encontrada'}
            
            # Coletar alunos de cada turma para verificação de conflitos
            turmas_alunos = {}
            for turma in turmas:
                turma_id = turma.get('id')
                alunos = self._turma_repo.get_alunos(turma_id)
                turmas_alunos[turma_id] = [a.get('id') for a in alunos]
            
            total_aulas = 0
            resultados = []
            
            for turma in turmas:
                resultado = self.distribuir_aulas_turma(turma, turmas_alunos)
                
                if resultado['success']:
                    total_aulas += resultado['aulas_criadas']
                    resultados.append(f"{resultado['turma']}: {resultado['aulas_criadas']} aulas")
                else:
                    resultados.append(f"{resultado.get('turma', 'Desconhecido')}: {resultado.get('error', 'Erro')}")
            
            return {
                'success': True,
                'total_aulas': total_aulas,
                'detalhes': resultados
            }
        except Exception as e:
            print(f"[ERRO] gerar_para_todas_turmas: {e}")
            return {'success': False, 'error': str(e)}
    
    def gerar_para_periodo_customizado(self, turma_id: int, data_inicio: date, 
                                        data_fim: date) -> Dict:
        """
        Gera calendário para uma turma específica em período customizado.
        
        Args:
            turma_id: ID da turma
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            Dict: Resultado da geração
        """
        try:
            self.data_inicio = data_inicio
            self.data_fim = data_fim
            
            turma = self._turma_repo.get_by_id(turma_id)
            if not turma:
                return {'success': False, 'error': 'Turma não encontrada'}
            
            # Coletar alunos
            alunos = self._turma_repo.get_alunos(turma_id)
            turmas_alunos = {turma_id: [a.get('id') for a in alunos]}
            
            return self.distribuir_aulas_turma(turma, turmas_alunos)
        except Exception as e:
            print(f"[ERRO] gerar_para_periodo_customizado: {e}")
            return {'success': False, 'error': str(e)}


def gerar_calendario_avancado(turma_id: Optional[int] = None, 
                               data_inicio: Optional[date] = None,
                               data_fim: Optional[date] = None,
                               periodo: str = 'trimestral') -> Dict:
    """
    Função principal para geração avançada de calendário acadêmico.
    
    Args:
        turma_id: ID da turma específica (None = todas as turmas)
        data_inicio: Data de início customizada
        data_fim: Data de fim customizada
        periodo: Período padrão se datas não definidas
        
    Returns:
        Dict: Resultado da operação
    """
    try:
        gerador = GeradorCalendarioAcademico(periodo)
        
        if data_inicio and data_fim:
            gerador.data_inicio = data_inicio
            gerador.data_fim = data_fim
        elif turma_id:
            return gerador.gerar_para_periodo_customizado(turma_id, gerador.data_inicio, gerador.data_fim)
        
        return gerador.gerar_para_todas_turmas()
    except Exception as e:
        print(f"[ERRO] gerar_calendario_avancado: {e}")
        return {'success': False, 'error': str(e)}
