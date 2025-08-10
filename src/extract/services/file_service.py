import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FileService:
    """Servicio para manejo de archivos (SRP - Single Responsibility Principle)"""
    
    def __init__(self):
        self.project_path = os.getenv('ETL_PROJECT_PATH', os.getcwd())
        self.data_folder = os.getenv('DATA_ETL', 'data')
    
    def save_extracted_data(self, data: list[dict[str, Any]], extractor_name: str) -> str:
        """Guarda los datos extraídos en formato JSON"""
        logger.info(f"DEBUG - ETL_PROJECT_PATH: {self.project_path}")
        logger.info(f"DEBUG - DATA_ETL: {self.data_folder}")
        
        # Construir ruta completa
        data_path = Path(self.project_path) / self.data_folder
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