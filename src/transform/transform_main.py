import logging
import os
from dotenv import load_dotenv, find_dotenv
from services.transformation_service import TransformationService
from transformers.transformer_factory import TransformerFactory

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno solo en desarrollo local
if not os.getenv('DOCKER_ENV'):
    load_dotenv(find_dotenv())
    logger.info("Variables cargadas desde archivo .env")
else:
    logger.info("Usando variables de entorno del contenedor")


class ETLTransformationOrchestrator:
    """Orquestador principal del proceso ETL Transform (SRP + DIP)"""
    
    def __init__(self):
        self.transformation_service = TransformationService()
    
    def run_transformation_process(self):
        """Ejecuta el proceso completo de transformación"""
        logger.info("=== PROCESO ETL - FASE DE TRANSFORMACIÓN ===")
        logger.info(f"Transformadores disponibles: {TransformerFactory.get_available_transformers()}")
        
        # Transformar todas las fuentes
        all_data = self.transformation_service.transform_all_sources()
        
        # Mostrar resumen
        total_records = sum(result.valid_records for result in all_data.values())
        logger.info(f"=== RESUMEN: {total_records} registros transformados ===")
        
        return all_data


def main():
    """Función principal del proceso de transformación ETL"""
    orchestrator = ETLTransformationOrchestrator()
    return orchestrator.run_transformation_process()


if __name__ == '__main__':
    main()