import logging
from datetime import datetime
from typing import Any
from transformers.transformer_factory import TransformerFactory
from models import TransformationResult
from services.file_service import FileService

logger = logging.getLogger(__name__)


class TransformationService:
    """Servicio para orquestar transformaciones (SRP - Single Responsibility Principle)"""
    
    def __init__(self):
        self.file_service = FileService()
    
    def transform_source(self, source: str) -> TransformationResult:
        """Transforma datos de una fuente específica"""
        # Cargar datos
        raw_data = self._load_source_data(source)
        if not raw_data:
            return self._create_empty_result(source)
        
        # Transformar datos
        transformer = TransformerFactory.create_transformer(source)
        logger.info(f"Iniciando transformación de {transformer.get_transformer_name()}")
        
        result = transformer.transform_data(raw_data)
        logger.info(f"Transformación completada: {result.valid_records} registros válidos de {transformer.get_transformer_name()}")
        
        # Guardar resultados
        self._save_transformation_result(result, source)
        
        return result
    
    def transform_all_sources(self) -> dict[str, TransformationResult]:
        """Transforma datos de todas las fuentes disponibles"""
        transformers = TransformerFactory.get_available_transformers()
        results = {}
        
        for source in transformers:
            source_name = source.value if hasattr(source, 'value') else str(source)
            logger.info(f"Procesando fuente: {source_name}")
            result = self.transform_source(source_name)
            results[source_name] = result
        
        return results
    
    def _load_source_data(self, source: str) -> list[dict[str, Any]]:
        """Carga datos de una fuente"""
        latest_file = self.file_service.find_latest_file(source)
        if not latest_file:
            logger.warning(f"No hay datos para transformar de {source}")
            return []
        
        logger.info(f"Cargando datos desde: {latest_file}")
        return self.file_service.load_file_by_extension(latest_file)
    
    def _create_empty_result(self, source: str) -> TransformationResult:
        """Crea un resultado vacío para fuentes sin datos"""
        return TransformationResult(
            source=source,
            total_records=0,
            valid_records=0,
            invalid_records=0,
            products=[],
            errors=["No hay datos para procesar"]
        )
    
    def _save_transformation_result(self, result: TransformationResult, source: str):
        """Guarda los resultados de la transformación"""
        today = datetime.now().strftime('%Y_%m_%d')
        
        # Guardar JSON completo
        json_filename = f"{source.lower()}_transformed_{today}.json"
        data_to_save = result.model_dump() if hasattr(result, 'model_dump') else result
        json_path = self.file_service.save_json(data_to_save, json_filename)
        
        logger.info(f"Datos transformados guardados: {json_path} ({result.valid_records} registros válidos)")
        
        # Guardar CSV para analistas (sin raw_data)
        if result.products:
            csv_filename = f"{source.lower()}_products_{today}.csv"
            products_data = self._prepare_csv_data(result.products)
            csv_path = self.file_service.save_csv(products_data, csv_filename)
            logger.info(f"CSV para analistas guardado: {csv_path} ({len(products_data)} productos)")
        else:
            logger.warning(f"No se generó CSV - no hay productos válidos para {source}")
    
    def _prepare_csv_data(self, products: list) -> list[dict[str, Any]]:
        """Prepara datos para CSV excluyendo raw_data"""
        products_data = []
        for product in products:
            product_dict = product.model_dump() if hasattr(product, 'model_dump') else product
            # Remover raw_data para el CSV
            product_dict.pop('raw_data', None)
            products_data.append(product_dict)
        return products_data