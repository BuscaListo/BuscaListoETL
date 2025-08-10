import logging
from typing import Any
from webscraping.extractors.extractor_factory import ExtractorFactory
from services.file_service import FileService

logger = logging.getLogger(__name__)


class ExtractionService:
    """Servicio para orquestar extracciones (SRP - Single Responsibility Principle)"""
    
    def __init__(self):
        self.file_service = FileService()
    
    def extract_from_source(self, source: str) -> list[dict[str, Any]]:
        """Extrae datos de una fuente específica"""
        extractor = ExtractorFactory.create_extractor(source)
        logger.info(f"Iniciando extracción de {extractor.get_extractor_name()}")
        
        data = extractor.extract_data()
        logger.info(f"Extracción completada: {len(data)} registros de {extractor.get_extractor_name()}")
        
        # Guardar datos
        self.file_service.save_extracted_data(data, extractor.get_extractor_name())
        
        return data
    
    def extract_from_all_sources(self) -> dict[str, list[dict[str, Any]]]:
        """Extrae datos de todas las fuentes disponibles"""
        extractors = ExtractorFactory.create_all_extractors()
        results = {}
        
        for name, extractor in extractors.items():
            logger.info(f"Iniciando extracción de {extractor.get_extractor_name()}")
            data = extractor.extract_data()
            results[name] = data
            logger.info(f"Extracción completada: {len(data)} registros de {extractor.get_extractor_name()}")
            
            # Guardar datos
            self.file_service.save_extracted_data(data, extractor.get_extractor_name())
        
        return results