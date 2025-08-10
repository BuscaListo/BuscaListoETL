from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from constants import DataSource, ValidationError, PriceType


class ProductModel(BaseModel):
    """Modelo Pydantic para productos estandarizados"""
    
    source: str = Field(..., description="Fuente de los datos")
    product_id: str = Field(..., description="Identificador único del producto")
    name: str = Field(..., description="Nombre/descripción del producto")
    category: Optional[str] = Field(None, description="Categoría del producto")
    price: Optional[float] = Field(None, ge=0, description="Precio del producto")
    brand: Optional[str] = Field(None, description="Marca del producto")
    image_url: Optional[str] = Field(None, description="URL de la imagen del producto")
    is_promotion: bool = Field(default=False, description="Indica si está en promoción")
    family: Optional[str] = Field(None, description="Familia/departamento del producto")
    is_visible: bool = Field(default=True, description="Indica si el producto está visible")
    address: Optional[str] = Field(None, description="Dirección de la tienda/sucursal")
    phone: Optional[str] = Field(None, description="Teléfono de contacto")
    price_type: Optional[str] = Field(None, description="Tipo de precio: USD o VES")
    raw_data: dict[str, Any] = Field(..., description="Datos originales sin transformar")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación del registro")
    
    @validator('source')
    def validate_source(cls, v):
        """Valida que la fuente sea válida"""
        if not DataSource.is_valid_source(v):
            raise ValueError(f'Fuente debe ser una de: {DataSource.get_all_values()}')
        return v.lower()
    
    @validator('product_id')
    def validate_product_id(cls, v):
        """Valida que el product_id no esté vacío"""
        if not v or not v.strip():
            raise ValueError(ValidationError.EMPTY_PRODUCT_ID)
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError(ValidationError.EMPTY_NAME)
        return v.strip()
    
    @validator('price')
    def validate_price(cls, v):
        """Valida que el precio sea válido"""
        if v is not None and v < 0:
            raise ValueError(ValidationError.NEGATIVE_PRICE)
        return v
    
    @validator('price_type')
    def validate_price_type(cls, v):
        """Valida que el tipo de precio sea válido"""
        if v is not None:
            # Convertir a mayúsculas para validación
            v_upper = v.upper()
            if v_upper not in PriceType.get_all_values():
                raise ValueError(f'{ValidationError.INVALID_PRICE_TYPE}. Debe ser uno de: {PriceType.get_all_values()}')
            return v_upper
        return v
    
    class Config:
        """Configuración del modelo"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "source": DataSource.DAKA,
                "product_id": "LB-00001632",
                "name": "MICROONDA 1.1 PIE CNEGRO WM1711D WHIRLPOOL",
                "category": "MICROONDAS",
                "price": 250.0,
                "brand": "WHIRLPOOL",
                "image_url": "https://www.tiendasdaka.com/img/producto/LB-00001632.webp",
                "is_promotion": False,
                "family": "Linea Blanca",
                "is_visible": True,
                "address": "Av. Principal, Centro Comercial XYZ",
                "phone": "+58-212-1234567",
                "price_type": PriceType.USD,
                "raw_data": {},
                "created_at": "2025-01-09T10:30:00"
            }
        }


class TransformationResult(BaseModel):
    """Modelo para el resultado de la transformación"""
    
    source: str = Field(..., description="Fuente de los datos")
    total_records: int = Field(..., ge=0, description="Total de registros procesados")
    valid_records: int = Field(..., ge=0, description="Registros válidos")
    invalid_records: int = Field(..., ge=0, description="Registros inválidos")
    products: list[ProductModel] = Field(..., description="Lista de productos válidos")
    errors: list[str] = Field(default_factory=list, description="Lista de errores encontrados")
    processed_at: datetime = Field(default_factory=datetime.now, description="Fecha de procesamiento")
    
    @validator('valid_records', 'invalid_records')
    def validate_record_counts(cls, v, values):
        """Valida que los conteos sean consistentes"""
        if 'total_records' in values:
            total = values['total_records']
            if v > total:
                raise ValueError('Los conteos no pueden ser mayores al total')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }