from typing import Any
from pydantic import ValidationError
from transformers.base_transformer import BaseTransformer
from models import TransformationResult
from constants import DataSource


class DakaTransformer(BaseTransformer):
    """Transformador para datos de Daka"""
    
    def transform_data(self, raw_data: list[dict[str, Any]]) -> TransformationResult:
        """Transforma datos de Daka al formato estándar usando Pydantic"""
        if not self.validate_data(raw_data):
            return TransformationResult(
                source=DataSource.DAKA,
                total_records=0,
                valid_records=0,
                invalid_records=0,
                products=[],
                errors=["No hay datos válidos para procesar"]
            )
        
        valid_products = []
        errors = []
        
        for i, item in enumerate(raw_data):
            try:
                transformed_item = {
                    'source': DataSource.DAKA,
                    'product_id': item.get('sap'),
                    'name': item.get('descripcion'),
                    'category': item.get('categoria'),
                    'price': item.get('precio'),
                    'brand': item.get('marca'),
                    'image_url': item.get('image'),
                    'is_promotion': item.get('promo', False),
                    'family': item.get('familia'),
                    'is_visible': item.get('view', True),
                    'address': None,  # A futuro se agregará
                    'phone': None,    # A futuro se agregará
                    'price_type': 'USD',  # Daka maneja precios en USD
                    'raw_data': item
                }
                
                # Crear y validar modelo Pydantic
                product = self.create_product_model(transformed_item)
                valid_products.append(product)
                
            except ValidationError as e:
                error_msg = f"Error en registro {i}: {str(e)}"
                errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error inesperado en registro {i}: {str(e)}"
                errors.append(error_msg)
        
        return TransformationResult(
            source=DataSource.DAKA,
            total_records=len(raw_data),
            valid_records=len(valid_products),
            invalid_records=len(raw_data) - len(valid_products),
            products=valid_products,
            errors=errors
        )
    
    def get_transformer_name(self) -> str:
        return "Daka"