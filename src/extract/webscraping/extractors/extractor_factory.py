from typing import Type
from webscraping.extractors.base_extractor import BaseExtractor
from webscraping.models_config import ConfigFactory


class ExtractorFactory:
    """Factory para crear extractores de APIs"""
    
    _extractors: dict[str, Type[BaseExtractor]] = ConfigFactory.extractors
    
    @classmethod
    def create_extractor(cls, extractor_type: str) -> BaseExtractor:
        """Crea una instancia del extractor especificado"""
        extractor_class = cls._extractors.get(extractor_type.lower())
        
        if not extractor_class:
            available = ', '.join(cls._extractors.keys())
            raise ValueError(f"Extractor '{extractor_type}' no encontrado. Disponibles: {available}")
        
        return extractor_class()
    
    @classmethod
    def get_available_extractors(cls) -> list:
        """Retorna la lista de extractores disponibles"""
        return list(cls._extractors.keys())
    
    @classmethod
    def create_all_extractors(cls) -> dict[str, BaseExtractor]:
        """Crea instancias de todos los extractores disponibles"""
        return {name: cls.create_extractor(name) for name in cls._extractors.keys()}