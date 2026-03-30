"""
app/dtos/base_dto.py - DTO Base

Classe base para todos os DTOs do sistema.
Fornece funcionalidades comuns de conversão de dados.
"""

from datetime import datetime, date, time


class BaseDTO:
    """
    DTO Base com funcionalidades comuns.
    
    Todos os DTOs herdam desta classe.
    """
    
    def __eq__(self, other):
        """
        Compara dois DTOs pelo ID.
        
        Args:
            other: Outro objeto para comparar
            
        Returns:
            bool: True se os IDs são iguais
        """
        if not isinstance(other, self.__class__):
            return False
        return getattr(self, 'id', None) == getattr(other, 'id', None)
    
    def __hash__(self):
        """
        Retorna hash baseado no ID para uso em sets e dicts.
        
        Returns:
            int: Hash do objeto
        """
        return hash(getattr(self, 'id', None))
    
    @staticmethod
    def parse_date(value):
        """Converte string para date."""
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            # Remover parte de tempo se existir
            date_str = value.split('T')[0].split(' ')[0]
            for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def parse_time(value):
        """Converte string para time."""
        if value is None:
            return None
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            # Remover timezone e microsegundos se existirem
            time_str = value.split('+')[0].split('-')[0].split('.')[0].strip()
            for fmt in ['%H:%M:%S', '%H:%M']:
                try:
                    return datetime.strptime(time_str, fmt).time()
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def parse_datetime(value):
        """Converte string para datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in [
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def parse_bool(value):
        """Converte valor para boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'sim')
        return False
