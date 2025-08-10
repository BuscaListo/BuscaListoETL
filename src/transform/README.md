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
- [Agregar nuevo transformador](#agregar-nuevo-transformador)
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

## Agregar nuevo transformador

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
from models import TransformationResult
from constants import DataSource

class NuevoTransformer(BaseTransformer):
    def transform_data(self, raw_data):
        valid_products = []
        errors = []
        
        for i, item in enumerate(raw_data):
            try:
                transformed_item = {
                    'source': DataSource.NUEVO,
                    'product_id': item.get('id'),
                    'name': item.get('titulo'),
                    'address': None,
                    'phone': None,
                    'price_type': 'USD',
                    'raw_data': item
                }
                product = self.create_product_model(transformed_item)
                valid_products.append(product)
            except Exception as e:
                errors.append(f"Error en registro {i}: {str(e)}")
        
        return TransformationResult(
            source=DataSource.NUEVO,
            total_records=len(raw_data),
            valid_records=len(valid_products),
            invalid_records=len(raw_data) - len(valid_products),
            products=valid_products,
            errors=errors
        )
    
    def get_transformer_name(self):
        return "Nuevo"
```

3. **Registrar en factory**:

```python
# transformer_factory.py
_transformers = {
    DataSource.DAKA: DakaTransformer,
    DataSource.FARMATODO: FarmatodoTransformer,
    DataSource.NUEVO: NuevoTransformer,  # Agregar aquí
}
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
  - **DIP**: Dependencias invertidas usando servicios
  - **Modular**: Separación clara de responsabilidades
