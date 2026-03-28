# app/services/gerador_calendario.py - Serviço de Geração de Calendário Acadêmico
# Módulo avançado para geração automática de calendário escolar

from datetime import date, time, timedelta
from typing import List, Dict, Optional, Tuple
from app import db
from app.models.turma import Turma
from app.models.aula import Aula
from app.models.professor import Professor
from app.models.materia import Materia
from app.models.feriado import Feriado
from app.models.dia_nao_letivo import DiaNaoLetivo


class GeradorCalendarioAcademico:
    """
    Serviço avançado de geração de calendário acadêmico.
    
    Implementa lógica heuristics para distribuição automática de aulas
    considerando professores, turmas, matérias e calendário acadêmico.
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
        if Feriado.is_feriado(data):
            return False
        if DiaNaoLetivo.is_dia_nao_letivo(data):
            return False
        return True
    
    def get_horarios_periodo(self, turno: str) -> List[Tuple[time, time]]:
        """Retorna os horários típicos para um turno."""
        return self.HORARIOS_TURNO.get(turno, self.HORARIOS_TURNO['manha'])
    
    def verificar_conflito_professor(self, professor_id: int, data: date, 
                                     inicio: time, fim: time, turma_id_exclude: Optional[int] = None) -> bool:
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
        conflictos = Aula.query.filter(
            Aula.professor_id == professor_id,
            Aula.data == data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= inicio,
                    Aula.horario_fim > inicio
                ),
                db.and_(
                    Aula.horario_inicio < fim,
                    Aula.horario_fim >= fim
                )
            )
        )
        
        if turma_id_exclude:
            conflictos = conflictos.filter(Aula.turma_id != turma_id_exclude)
        
        return conflictos.first() is not None
    
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
        conflicto = Aula.query.filter(
            Aula.turma_id == turma_id,
            Aula.data == data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= inicio,
                    Aula.horario_fim > inicio
                ),
                db.and_(
                    Aula.horario_inicio < fim,
                    Aula.horario_fim >= fim
                )
            )
        ).first()
        
        return conflicto is not None
    
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
            
        alunos_turma = set(turmas_alunos.get(turma_id, []))
        
        aulas_conflito = Aula.query.filter(
            Aula.turma_id != turma_id,
            Aula.data == data,
            Aula.status != 'cancelada',
            db.or_(
                db.and_(
                    Aula.horario_inicio <= inicio,
                    Aula.horario_fim > inicio
                ),
                db.and_(
                    Aula.horario_inicio < fim,
                    Aula.horario_fim >= fim
                )
            )
        ).all()
        
        for aula in aulas_conflito:
            alunos_aula = set(turmas_alunos.get(aula.turma_id, []))
            if alunos_turma & alunos_aula:  # Interseção
                return True
        
        return False
    
    def professor_pode_lecionar(self, professor: Professor, materia: Materia) -> bool:
        """Verifica se o professor está habilitado para a matéria."""
        return materia in professor.materias
    
    def encontrar_professor_disponivel(self, materia: Materia, data: date, 
                                        horarios: List[Tuple[time, time]], 
                                        turma_id: Optional[int] = None) -> Optional[Professor]:
        """
        Encontra um professor disponível para lecionar a matéria no horário.
        
        Usa abordagem gulosa: tenta encontrar primeiro professor disponível.
        
        Args:
            materia: Matéria a ser lecionada
            data: Data da aula
            horarios: Lista de horários disponíveis
            turma_id: ID da turma (para exclusões)
            
        Returns:
            Professor disponível ou None
        """
        # Filtrar apenas professores ativos que podem lecionar esta matéria
        professores_validos = [p for p in materia.professores if p.ativo]
        
        if not professores_validos:
            return None
        
        # Tentar encontrar professor disponível
        for professor in professores_validos:
            disponivel = True
            for h_inicio, h_fim in horarios:
                if self.verificar_conflito_professor(professor.id, data, h_inicio, h_fim, turma_id):
                    disponivel = False
                    break
            
            if disponivel:
                return professor
        
        return None
    
    def distribuir_aulas_turma(self, turma: Turma, turmas_alunos: Dict[int, List[int]]) -> Dict:
        """
        Distribui as aulas para uma turma respeitando todas as regras.
        
        Args:
            turma: Turma a processar
            turmas_alunos: Dicionário de alunos por turma
            
        Returns:
            Dict: Resultado da operação
        """
        if not turma.ativa:
            return {'success': False, 'error': f'Turma {turma.nome} está inativa'}
        
        if not turma.materias:
            return {'success': False, 'error': f'Turma {turma.nome} não possui matérias cadastradas'}
        
        if not turma.alunos:
            return {'success': False, 'error': f'Turma {turma.nome} não possui alunos matriculados'}
        
        horarios = self.get_horarios_periodo(turma.turno)
        aulas_criadas = 0
        
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
            for materia_idx, materia in enumerate(turma.materias):
                # Encontrar professor disponível para esta matéria neste dia
                # Tentar cada horário até encontrar um disponível
                for horario_idx, (h_inicio, h_fim) in enumerate(horarios):
                    # Verificar se já não existe aula desta matéria neste dia/horário
                    aula_existe = Aula.query.filter_by(
                        turma_id=turma.id,
                        materia=materia.nome,
                        data=data_atual
                    ).first()
                    
                    if aula_existe:
                        continue
                    
                    # Verificar conflito de turma
                    if self.verificar_conflito_turma(turma.id, data_atual, h_inicio, h_fim):
                        continue
                    
                    # Verificar conflitos de alunos com outras turmas
                    if self.verificar_conflito_alunos(turma.id, data_atual, h_inicio, h_fim, turmas_alunos):
                        continue
                    
                    # Encontrar professor disponível
                    professor = self.encontrar_professor_disponivel(
                        materia, data_atual, [(h_inicio, h_fim)], turma.id
                    )
                    
                    if not professor:
                        # Nenhum professor disponível para esta matéria/horário
                        continue
                    
                    # Verificar novamente conflito para o professor específico
                    if self.verificar_conflito_professor(professor.id, data_atual, h_inicio, h_fim, turma.id):
                        continue
                    
                    # Criar a aula
                    aula = Aula(
                        materia=materia.nome,
                        turma_id=turma.id,
                        professor_id=professor.id,
                        data=data_atual,
                        horario_inicio=h_inicio,
                        horario_fim=h_fim,
                        status='agendada'
                    )
                    
                    db.session.add(aula)
                    self.aulas_criadas.append(aula)
                    aulas_criadas += 1
                    
                    # Após criar uma aula, passar para o próximo dia para distribuir melhor
                    break
            
            data_atual += timedelta(days=1)
        
        return {
            'success': True, 
            'aulas_criadas': aulas_criadas,
            'turma': turma.nome
        }
    
    def gerar_para_todas_turmas(self, turma_ids: Optional[List[int]] = None) -> Dict:
        """
        Gera calendário para todas as turmas ativas.
        
        Args:
            turma_ids: IDs específicos de turmas (None = todas ativas)
            
        Returns:
            Dict: Resultado comtotal de aulas criadas
        """
        # Buscar turmas
        if turma_ids:
            turmas = Turma.query.filter(Turma.id.in_(turma_ids), Turma.ativa == True).all()
        else:
            turmas = Turma.query.filter_by(ativa=True).all()
        
        if not turmas:
            return {'success': False, 'error': 'Nenhuma turma ativa encontrada'}
        
        # Coletar alunos de cada turma para verificação de conflitos
        turmas_alunos = {}
        for turma in turmas:
            turmas_alunos[turma.id] = [a.id for a in turma.alunos]
        
        total_aulas = 0
        resultados = []
        
        for turma in turmas:
            resultado = self.distribuir_aulas_turma(turma, turmas_alunos)
            
            if resultado['success']:
                total_aulas += resultado['aulas_criadas']
                resultados.append(f"{resultado['turma']}: {resultado['aulas_criadas']} aulas")
            else:
                resultados.append(f"{resultado.get('turma', 'Desconhecido')}: {resultado.get('error', 'Erro')}")
        
        # Commit de todas as aulas criadas
        if self.aulas_criadas:
            db.session.commit()
        
        return {
            'success': True,
            'total_aulas': total_aulas,
            'detalhes': resultados
        }
    
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
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        
        turma = Turma.query.get(turma_id)
        if not turma:
            return {'success': False, 'error': 'Turma não encontrada'}
        
        # Coletar alunos
        turmas_alunos = {turma.id: [a.id for a in turma.alunos]}
        
        return self.distribuir_aulas_turma(turma, turmas_alunos)


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
    gerador = GeradorCalendarioAcademico(periodo)
    
    if data_inicio and data_fim:
        gerador.data_inicio = data_inicio
        gerador.data_fim = data_fim
    elif turma_id:
        return gerador.gerar_para_periodo_customizado(turma_id, gerador.data_inicio, gerador.data_fim)
    
    return gerador.gerar_para_todas_turmas()