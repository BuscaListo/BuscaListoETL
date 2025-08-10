from enum import Enum


class DataSource(str, Enum):
    """Enum para las fuentes de datos disponibles"""
    DAKA = "daka"
    FARMATODO = "farmatodo"
    
    @classmethod
    def get_all_values(cls) -> list[str]:
        """Retorna todos los valores del enum como lista"""
        return [source.value for source in cls]
    
    @classmethod
    def is_valid_source(cls, source: str) -> bool:
        """Verifica si una fuente es válida"""
        return source.lower() in cls.get_all_values()


class FileExtension(str, Enum):
    """Enum para extensiones de archivos"""
    JSON = ".json"
    CSV = ".csv"
    XLSX = ".xlsx"
    XLS = ".xls"
    PARQUET = ".parquet"
    
    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Retorna formatos soportados para lectura"""
        return [cls.JSON, cls.CSV, cls.XLSX, cls.XLS]


class ProcessStatus(str, Enum):
    """Enum para estados de procesamiento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PriceType(str, Enum):
    """Enum para tipos de precio"""
    USD = "USD"
    VES = "VES"  # Bolívares venezolanos
    
    @classmethod
    def get_all_values(cls) -> list[str]:
        """Retorna todos los valores del enum como lista"""
        return [price_type.value for price_type in cls]


class ValidationError(str, Enum):
    """Enum para tipos de errores de validación"""
    EMPTY_PRODUCT_ID = "product_id no puede estar vacío"
    EMPTY_NAME = "name no puede estar vacío"
    NEGATIVE_PRICE = "price no puede ser negativo"
    INVALID_SOURCE = "fuente no válida"
    INVALID_PRICE_TYPE = "tipo de precio no válido"
    MISSING_REQUIRED_FIELD = "campo requerido faltante"