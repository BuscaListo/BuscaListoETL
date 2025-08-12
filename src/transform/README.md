# Módulo de Transformación ETL

Proceso de transformación de datos extraídos al formato estándar para su posterior carga en el proceso **[load](/src/load/)**

## Índice

- [Módulo de Transformación ETL](#módulo-de-transformación-etl)
- [Transform - Factory Pattern](#transform---factory-pattern)
- [Estructura](#estructura)
- [Modelos de Datos con Pydantic](#modelos-de-datos-con-pydantic)
- [Constantes y Enums](#constantes-y-enums)
- [Validaciones Automáticas](#validaciones-automáticas)
- [Formatos de Archivo Soportados](#formatos-de-archivo-soportados)
- [Uso Factory Pattern](#uso-factory-pattern)
- [Sistema de Formatters](#sistema-de-formatters)
- [Extensibilidad](#extensibilidad)
- [Ejecutar](#ejecutar)
- [Microservicio](#microservicio)

## Transform - Factory Pattern

### Estructura

```bash
transform/
├── transformers/
│   ├── __init__.py
│   ├── base_transformer.py          # Clase abstracta base
│   ├── transformer_factory.py       # Factory para crear transformadores
│   ├── transformer_daka.py          # Transformador para Daka
│   └── transformer_farmatodo.py     # Transformador para Farmatodo
├── formatters/
│   ├── __init__.py
│   ├── base_formatter.py            # Clase abstracta base (SRP)
│   ├── formatter_factory.py         # Factory para crear formatters (OCP)
│   └── product_formatter.py         # Formatter para ProductModel
├── services/
│   ├── __init__.py
│   ├── file_service.py              # Servicio de manejo de archivos (SRP)
│   └── transformation_service.py    # Servicio de transformación (SRP)
├── models.py                        # Modelos Pydantic
├── constants.py                     # Enums y constantes
├── transform_main.py                # Orquestador principal (DIP)
├── Dockerfile
├── requirements.txt
└── README.md
```

## Modelos de Datos con Pydantic

### ProductModel

Todos los transformadores usan modelos Pydantic para validación automática:

```json
{
  "source": "daka|farmatodo",
  "product_id": "string",
  "name": "string",
  "category": "string",
  "price": "number",
  "brand": "string",
  "image_url": "string",
  "is_promotion": "boolean",
  "family": "string",
  "is_visible": "boolean",
  "address": "string",
  "phone": "string",
  "price_type": "USD|VES",
  "raw_data": "object",
  "created_at": "datetime"
}
```

### TransformationResult

Resultado del proceso de transformación:

```json
{
  "source": "string",
  "total_records": "number",
  "valid_records": "number",
  "invalid_records": "number",
  "products": ["ProductModel"],
  "errors": ["string"],
  "processed_at": "datetime"
}
```

## Constantes y Enums

### DataSource

Fuentes de datos disponibles:

```python
from constants import DataSource

DataSource.DAKA          # "daka"
DataSource.FARMATODO     # "farmatodo"
DataSource.get_all_values()  # ["daka", "farmatodo"]
```

### ValidationError

Mensajes de error estandarizados:

```python
ValidationError.EMPTY_PRODUCT_ID    # "product_id no puede estar vacío"
ValidationError.EMPTY_NAME          # "name no puede estar vacío"
ValidationError.NEGATIVE_PRICE      # "price no puede ser negativo"
ValidationError.INVALID_PRICE_TYPE  # "tipo de precio no válido"
```

### PriceType

Tipos de precio soportados:

```python
PriceType.USD                       # "USD" (Dólares)
PriceType.VES                       # "VES" (Bolívares)
PriceType.get_all_values()          # ["USD", "VES"]
```

### FileExtension

Extensiones de archivos soportadas:

```python
FileExtension.JSON       # ".json"
FileExtension.CSV        # ".csv"
FileExtension.XLSX       # ".xlsx"
FileExtension.XLS        # ".xls"
FileExtension.get_supported_formats()  # [".json", ".csv", ".xlsx", ".xls"]
```

## Validaciones Automáticas

- **Campos obligatorios**: source, product_id, name
- **Validación de tipos**: Automática con Pydantic
- **Precios**: No pueden ser negativos
- **Fuentes**: Solo valores válidos del enum DataSource
- **Tipos de precio**: Solo valores válidos del enum PriceType (USD, VES) en mayúsculas
- **Conteos**: Registros válidos + inválidos = total
- **Formatos**: Detección automática por extensión de archivo

## Formatos de Archivo Soportados

- **JSON**: Formato nativo, soporta arrays y objetos
- **CSV**: Convertido automáticamente a diccionarios
- **Excel**: Soporta .xlsx y .xls, lee la primera hoja
- **Detección automática**: Por extensión de archivo
- **Normalización**: Todos los formatos se convierten a List[Dict]

## Uso Factory Pattern

### Transformadores (por fuente de datos)

```python
from transformers.transformer_factory import TransformerFactory
from constants import DataSource

# Transformar datos de una fuente específica
transformer = TransformerFactory.create_transformer(DataSource.DAKA)
result = transformer.transform_data(raw_data)

# Acceder a productos validados
valid_products = result.products
print(f"Procesados: {result.total_records}")
print(f"Válidos: {result.valid_records}")
print(f"Errores: {result.errors}")

# Obtener todos los transformadores
transformers = TransformerFactory.create_all_transformers()
```

## Sistema de Formatters

El sistema de formatters separa la lógica de formateo de datos por modelo de salida, siguiendo el principio de responsabilidad única (SRP) y permitiendo extensibilidad futura.

### Uso Básico

```python
from formatters.formatter_factory import FormatterFactory

# Crear formatter para modelo específico
formatter = FormatterFactory.create_formatter('product')

# Formatear datos a JSON con metadatos
products_data = [product.model_dump() for product in result.products]
json_output = formatter.format_to_json(products_data)

# Formatear datos a CSV para analistas (sin raw_data)
csv_output = formatter.format_to_csv(products_data)

print(f"JSON generado con {json_output['total_products']} productos")
print(f"CSV generado con {len(csv_output)} registros")
```

### Verificar Modelos Disponibles

```python
# Obtener lista de modelos soportados
available_models = FormatterFactory.get_available_models()
print(f"Modelos disponibles: {available_models}")

# Verificar si un modelo está soportado
if FormatterFactory.is_model_supported('product'):
    formatter = FormatterFactory.create_formatter('product')
```

### Crear Todos los Formatters

```python
# Útil para procesamiento batch o inicialización
all_formatters = FormatterFactory.create_all_formatters()

for model_name, formatter in all_formatters.items():
    print(f"Formatter {formatter.get_formatter_name()} para modelo {model_name}")
```

### Estructura de Salida

#### JSON Formateado
```json
{
  "model": "ProductModel",
  "total_products": 35,
  "products": [
    {
      "source": "daka",
      "product_id": "LB-00001632",
      "name": "MICROONDA 1.1 PIE CNEGRO WM1711D WHIRLPOOL",
      "price": 250.0,
      "price_type": "USD"
    }
  ],
  "metadata": {
    "format": "json",
    "version": "1.0",
    "fields": ["source", "product_id", "name", ...]
  }
}
```

#### CSV Formateado
- Excluye automáticamente el campo `raw_data`
- Mantiene todos los demás campos del modelo
- Optimizado para análisis en Excel/Google Sheets

### Manejo de Errores

```python
try:
    formatter = FormatterFactory.create_formatter('modelo_inexistente')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Formatter for model 'modelo_inexistente' not found. 
    #         Available models: product, productmodel
```

## Extensibilidad

### Agregar nuevo transformador (por fuente)

1. **Agregar fuente al enum**:
```python
# constants.py
class DataSource(str, Enum):
    DAKA = "daka"
    FARMATODO = "farmatodo"
    NUEVO = "nuevo"  # Agregar aquí
```

2. **Crear clase transformador**:
```python
from transformers.base_transformer import BaseTransformer

class NuevoTransformer(BaseTransformer):
    def transform_data(self, raw_data):
        # Lógica de transformación específica por fuente
        pass
    
    def get_transformer_name(self):
        return "Nuevo"
```

3. **Registrar en factory**:
```python
# transformer_factory.py
_transformers[DataSource.NUEVO] = NuevoTransformer
```

### Agregar nuevo formatter (por modelo)

1. **Crear clase formatter**:
```python
from formatters.base_formatter import BaseFormatter

class InventoryFormatter(BaseFormatter):
    """
    Formatter para modelo de inventario.
    
    Maneja formateo de datos de inventario a diferentes
    formatos de salida (JSON, CSV, etc.).
    """
    
    def __init__(self) -> None:
        """Inicializar InventoryFormatter."""
        super().__init__("InventoryModel")
    
    def format_to_json(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Formatear datos de inventario a JSON."""
        return {
            "model": self.model_name,
            "total_items": len(data),
            "inventory_items": data,
            "metadata": {
                "format": "json",
                "version": "1.0",
                "fields": ["item_id", "quantity", "location"]
            }
        }
    
    def format_to_csv(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Formatear datos de inventario a CSV."""
        # Remover campos complejos para CSV
        csv_data = []
        for item in data:
            csv_item = {k: v for k, v in item.items() if k != 'metadata'}
            csv_data.append(csv_item)
        return csv_data
    
    def get_formatter_name(self) -> str:
        """Obtener nombre del formatter."""
        return "InventoryFormatter"
```

2. **Registrar dinámicamente (Open/Closed Principle)**:
```python
# Registro dinámico - no requiere modificar FormatterFactory
FormatterFactory.register_formatter('inventory', InventoryFormatter)

# Verificar registro exitoso
if FormatterFactory.is_model_supported('inventory'):
    inventory_formatter = FormatterFactory.create_formatter('inventory')
    print(f"Formatter registrado: {inventory_formatter.get_formatter_name()}")
```

3. **Uso del nuevo formatter**:
```python
# Crear formatter para inventario
inventory_formatter = FormatterFactory.create_formatter('inventory')

# Formatear datos
inventory_data = [{"item_id": "INV001", "quantity": 100, "location": "A1"}]
json_output = inventory_formatter.format_to_json(inventory_data)
csv_output = inventory_formatter.format_to_csv(inventory_data)
```

### Ejemplo Completo de Extensión

```python
# 1. Definir nuevo modelo Pydantic
class InventoryModel(BaseModel):
    item_id: str
    quantity: int
    location: str
    last_updated: datetime = Field(default_factory=datetime.now)

# 2. Crear formatter personalizado
class InventoryFormatter(BaseFormatter):
    # ... implementación completa arriba ...

# 3. Registrar y usar
FormatterFactory.register_formatter('inventory', InventoryFormatter)
formatter = FormatterFactory.create_formatter('inventory')

# 4. Integrar en el pipeline ETL
class InventoryTransformationService(TransformationService):
    def _save_transformation_result(self, result, source):
        # Usar formatter específico según el tipo de datos
        if source == 'inventory_source':
            formatter = FormatterFactory.create_formatter('inventory')
        else:
            formatter = FormatterFactory.create_formatter('product')
        
        # Continuar con lógica de guardado...
```

## Ejecutar

### Local

Es necesario ubicarse dentro de la carpeta **[src/transform](/src/transform)** y ejecutar:

```bash
python -m transform_main
```

### Docker

**Variables de entorno requeridas:**

- `ETL_PROJECT_PATH`: Ruta principal del proyecto ETL
- `DATA_ETL`: Carpeta donde se guardan los datos

**Opción 1: Con docker-compose (recomendado)**

Desde la raíz del proyecto:

```bash
docker-compose up transformer
```

**Opción 2: Docker standalone**

```bash
# Construir imagen
docker build -t busca-listo-transformer .

# Ejecutar con variables de entorno
docker run --name transformer \
  -e ETL_PROJECT_PATH=/app \
  -e DATA_ETL=data \
  -v $(pwd)/../../data:/app/data \
  busca-listo-transformer
```

### Entrada y Salida de datos

**Entrada:**

- Lee archivos de: `{ETL_PROJECT_PATH}/{DATA_ETL}/extract/`
- **Formatos soportados**: JSON, CSV, Excel (.xlsx, .xls)
- Formato de nombre: `{source}_YYYY_MM_DD.{extension}`
- Ejemplos:
  - `daka_2025_01_09.json`
  - `farmatodo_2025_01_09.csv`
  - `nueva_fuente_2025_01_09.xlsx`

**Salida:**

- **JSON completo**: `{ETL_PROJECT_PATH}/{DATA_ETL}/transform/`
  - Formato: `{source}_transformed_YYYY_MM_DD.json`
  - Ejemplo: `daka_transformed_2025_01_09.json`
  - Contenido: TransformationResult con productos validados y métricas

- **CSV para analistas**: `{ETL_PROJECT_PATH}/{DATA_ETL}/transform/`
  - Formato: `{source}_products_YYYY_MM_DD.csv`
  - Ejemplo: `daka_products_2025_01_09.csv`
  - Contenido: Solo productos sin campo `raw_data`
  - Uso: Análisis de datos, reportes, visualizaciones

## Microservicio

- **Proceso batch**: Transformación de datos extraídos
- **Imagen**: Python 3.11-slim optimizada
- **Dependencia**: Requiere que el proceso extract haya completado
- **Validación**: Pydantic para validación automática de datos
- **Escalable**: Fácil agregar nuevas fuentes usando Enums
- **Trazabilidad**: Métricas detalladas de procesamiento y errores
- **Consistencia**: Constantes centralizadas para mantenimiento
- **SOLID**: Principios de diseño aplicados para mejor mantenibilidad
  - **SRP**: Cada clase tiene una sola responsabilidad
  - **OCP**: Abierto para extensión, cerrado para modificación
  - **DIP**: Dependencias invertidas usando servicios
  - **Factory Pattern**: Creación centralizada de transformadores y formatters
- **PEP 8**: Estándares de codificación Python aplicados
- **Documentación**: Docstrings completos siguiendo estándares Python
- **Extensibilidad**: Sistema preparado para múltiples modelos y formatos
