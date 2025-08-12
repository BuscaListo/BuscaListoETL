import logging
from datetime import datetime
from typing import Any
from transformers.transformer_factory import TransformerFactory
from formatters.formatter_factory import FormatterFactory
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
        """Guarda los resultados de la transformación usando formatters"""
        today = datetime.now().strftime('%Y_%m_%d')
        
        # Crear formatter para productos
        formatter = FormatterFactory.create_formatter('product')
        
        # Preparar datos de productos para formateo
        products_data = []
        for product in result.products:
            product_dict = product.model_dump() if hasattr(product, 'model_dump') else product
            products_data.append(product_dict)
        
        # Guardar JSON completo usando formatter
        json_filename = f"{source.lower()}_transformed_{today}.json"
        formatted_json = formatter.format_to_json(products_data)
        
        # Añadir metadatos de transformación al JSON
        complete_data = {
            "transformation_metadata": {
                "source": result.source,
                "total_records": result.total_records,
                "valid_records": result.valid_records,
                "invalid_records": result.invalid_records,
                "errors": result.errors,
                "processed_at": result.processed_at.isoformat() if hasattr(result.processed_at, 'isoformat') else str(result.processed_at)
            },
            "formatted_data": formatted_json
        }
        
        json_path = self.file_service.save_json(complete_data, json_filename)
        logger.info(f"Datos transformados guardados: {json_path} ({result.valid_records} registros válidos)")
        
        # Guardar CSV para analistas usando formatter
        if result.products:
            csv_filename = f"{source.lower()}_products_{today}.csv"
            csv_data = formatter.format_to_csv(products_data)
            csv_path = self.file_service.save_csv(csv_data, csv_filename)
            logger.info(f"CSV para analistas guardado: {csv_path} ({len(csv_data)} productos)")
        else:
            logger.warning(f"No se generó CSV - no hay productos válidos para {source}")
    
