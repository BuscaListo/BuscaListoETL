import logging
import os
from dotenv import load_dotenv, find_dotenv
from services.extraction_service import ExtractionService
from webscraping.extractors.extractor_factory import ExtractorFactory

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno solo en desarrollo local
if not os.getenv('DOCKER_ENV'):
    load_dotenv(find_dotenv())
    logger.info("Variables cargadas desde archivo .env")
else:
    logger.info("Usando variables de entorno del contenedor")


class ETLExtractionOrchestrator:
    """Orquestador principal del proceso ETL Extract (SRP + DIP)"""
    
    def __init__(self):
        self.extraction_service = ExtractionService()
    
    def run_extraction_process(self):
        """Ejecuta el proceso completo de extracción"""
        logger.info("=== PROCESO ETL - FASE DE EXTRACCIÓN ===")
        logger.info(f"Extractores disponibles: {ExtractorFactory.get_available_extractors()}")
        
        # Extraer de todas las fuentes
        all_data = self.extraction_service.extract_from_all_sources()
        
        # Mostrar resumen
        total_records = sum(len(data) for data in all_data.values())
        logger.info(f"=== RESUMEN: {total_records} registros extraídos ===")
        
        return all_data


def main():
    """Función principal del proceso de extracción ETL"""
    orchestrator = ETLExtractionOrchestrator()
    return orchestrator.run_extraction_process()


if __name__ == '__main__':
    main()