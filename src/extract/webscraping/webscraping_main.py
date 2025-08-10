import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from dotenv import load_dotenv, find_dotenv
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


def save_extracted_data(data: list[dict[str, Any]], extractor_name: str) -> str:
    """Guarda los datos extraídos en formato JSON con nombre específico"""
    # Obtener variables de entorno
    project_path = os.getenv('ETL_PROJECT_PATH', os.getcwd())
    data_folder = os.getenv('DATA_ETL', 'data')
    
    logger.info(f"DEBUG - ETL_PROJECT_PATH: {project_path}")
    logger.info(f"DEBUG - DATA_ETL: {data_folder}")
    
    # Construir ruta completa
    data_path = Path(project_path) / data_folder
    extract_dir = data_path / 'extract'
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre del archivo con fecha
    today = datetime.now().strftime('%Y_%m_%d')
    filename = f"{extractor_name.lower()}_{today}.json"
    filepath = extract_dir / filename
    
    # Guardar datos
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Datos guardados: {filepath} ({len(data)} registros)")
    return str(filepath)


def extract_from_source(source: str) -> list[dict[str, Any]]:
    """Extrae datos de una fuente específica y los guarda"""
    extractor = ExtractorFactory.create_extractor(source)
    logger.info(f"Iniciando extracción de {extractor.get_extractor_name()}")
    
    data = extractor.extract_data()
    logger.info(f"Extracción completada: {len(data)} registros de {extractor.get_extractor_name()}")
    
    # Guardar datos
    save_extracted_data(data, extractor.get_extractor_name())
    
    return data


def extract_from_all_sources() -> dict[str, list[dict[str, Any]]]:
    """Extrae datos de todas las fuentes disponibles y los guarda"""
    extractors = ExtractorFactory.create_all_extractors()
    results = {}
    
    for name, extractor in extractors.items():
        logger.info(f"Iniciando extracción de {extractor.get_extractor_name()}")
        data = extractor.extract_data()
        results[name] = data
        logger.info(f"Extracción completada: {len(data)} registros de {extractor.get_extractor_name()}")
        
        # Guardar datos
        save_extracted_data(data, extractor.get_extractor_name())
    
    return results


def main():
    """Función principal del proceso de extracción ETL"""
    logger.info("=== PROCESO ETL - FASE DE EXTRACCIÓN ===")
    logger.info(f"Extractores disponibles: {ExtractorFactory.get_available_extractors()}")
    
    # Opción 1: Extraer de todas las fuentes
    all_data = extract_from_all_sources()
    
    # Mostrar resumen
    total_records = sum(len(data) for data in all_data.values())
    logger.info(f"=== RESUMEN: {total_records} registros extraídos ===")
    
    return all_data


if __name__ == '__main__':
    extracted_data = main()
    # extracted_data = extract_from_source('Daka')