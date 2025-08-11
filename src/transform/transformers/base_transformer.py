from abc import ABC, abstractmethod
from typing import Any
from models import ProductModel, TransformationResult


class BaseTransformer(ABC):
    """Clase base abstracta para todos los transformadores de datos"""
    
    @abstractmethod
    def transform_data(self, raw_data: list[dict[str, Any]]) -> TransformationResult:
        """
        Transforma los datos extraídos al formato estándar usando Pydantic
        
        Args:
            raw_data: Datos en formato original del extractor
            
        Returns:
            TransformationResult con productos validados
        """
        pass
    
    @abstractmethod
    def get_transformer_name(self) -> str:
        """Retorna el nombre del transformador"""
        pass
    
    def validate_data(self, data: list[dict[str, Any]]) -> bool:
        """Valida que los datos tengan la estructura esperada"""
        return isinstance(data, list) and len(data) > 0
    
    def create_product_model(self, item_data: dict[str, Any]) -> ProductModel:
        """Crea y valida un modelo de producto usando Pydantic"""
        return ProductModel(**item_data)