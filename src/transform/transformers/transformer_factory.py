from typing import Type
from transformers.base_transformer import BaseTransformer
from transformers.transformer_daka import DakaTransformer
from transformers.transformer_farmatodo import FarmatodoTransformer
from constants import DataSource


class TransformerFactory:
    """Factory para crear transformadores de datos"""
    
    _transformers: dict[str, Type[BaseTransformer]] = {
        DataSource.DAKA: DakaTransformer,
        DataSource.FARMATODO: FarmatodoTransformer,
    }
    
    @classmethod
    def create_transformer(cls, transformer_type: str) -> BaseTransformer:
        """Crea una instancia del transformador especificado"""
        transformer_class = cls._transformers.get(transformer_type.lower())
        
        if not transformer_class:
            available = ', '.join(cls._transformers.keys())
            raise ValueError(f"Transformador '{transformer_type}' no encontrado. Disponibles: {available}")
        
        return transformer_class()
    
    @classmethod
    def get_available_transformers(cls) -> list:
        """Retorna la lista de transformadores disponibles"""
        return list(cls._transformers.keys())
    
    @classmethod
    def create_all_transformers(cls) -> dict[str, BaseTransformer]:
        """Crea instancias de todos los transformadores disponibles"""
        return {name: cls.create_transformer(name) for name in cls._transformers.keys()}