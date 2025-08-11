import json
import logging
import os
from pathlib import Path
from typing import Any
import pandas as pd
from constants import FileExtension

logger = logging.getLogger(__name__)


class FileService:
    """Servicio para manejo de archivos (SRP - Single Responsibility Principle)"""
    
    def __init__(self):
        self.project_path = os.getenv('ETL_PROJECT_PATH', os.getcwd())
        self.data_folder = os.getenv('DATA_ETL', 'data')
    
    def find_latest_file(self, source: str, folder: str = 'extract') -> Path:
        """Encuentra el archivo más reciente para una fuente"""
        extract_dir = Path(self.project_path) / self.data_folder / folder
        supported_extensions = ['json', 'csv', 'xlsx', 'xls']
        
        all_files = []
        for ext in supported_extensions:
            pattern = f"{source.lower()}_*.{ext}"
            all_files.extend(extract_dir.glob(pattern))
        
        if not all_files:
            logger.warning(f"No se encontraron archivos para {source} en {extract_dir}")
            logger.info(f"Archivos disponibles: {list(extract_dir.glob('*'))}")
            return None
        
        return max(all_files, key=lambda f: f.stat().st_mtime)
    
    def load_file_by_extension(self, filepath: Path) -> list[dict[str, Any]]:
        """Carga archivo según su extensión"""
        extension = filepath.suffix.lower()
        
        try:
            if extension == FileExtension.JSON:
                return self._load_json(filepath)
            elif extension == FileExtension.CSV:
                return self._load_csv(filepath)
            elif extension in ['.xlsx', '.xls']:
                return self._load_excel(filepath)
            else:
                logger.error(f"Formato de archivo no soportado: {extension}")
                return []
        except Exception as e:
            logger.error(f"Error cargando archivo {filepath}: {str(e)}")
            return []
    
    def _load_json(self, filepath: Path) -> list[dict[str, Any]]:
        """Carga archivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    
    def _load_csv(self, filepath: Path) -> list[dict[str, Any]]:
        """Carga archivo CSV"""
        df = pd.read_csv(filepath)
        return df.to_dict('records')
    
    def _load_excel(self, filepath: Path) -> list[dict[str, Any]]:
        """Carga archivo Excel"""
        df = pd.read_excel(filepath)
        return df.to_dict('records')
    
    def save_json(self, data: Any, filename: str, folder: str = 'transform') -> str:
        """Guarda datos en formato JSON"""
        output_dir = Path(self.project_path) / self.data_folder / folder
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)
    
    def save_csv(self, data: list[dict[str, Any]], filename: str, folder: str = 'transform') -> str:
        """Guarda datos en formato CSV"""
        output_dir = Path(self.project_path) / self.data_folder / folder
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return str(filepath)