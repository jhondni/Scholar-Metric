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
    
    @staticmethod
    def parse_date(value):
        """Converte string para date."""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return None
        return None
    
    @staticmethod
    def parse_time(value):
        """Converte string para time."""
        if value is None:
            return None
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            for fmt in ['%H:%M:%S', '%H:%M']:
                try:
                    return datetime.strptime(value, fmt).time()
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
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
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
