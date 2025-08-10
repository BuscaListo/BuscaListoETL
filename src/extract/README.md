# Módulo de Extracción ETL

Proceso de extracción y filtrado de datos según los campos necesarios para su debida transformación en el proceso **[transform](/transform/)**

## Indice

- [Módulo de Extracción ETL](#módulo-de-extracción-etl)
- [Extract - Webscraping - Factory Pattern](#extract---webscraping---factory-pattern)
- [Estructura](#estructura)
- [Uso Factory Pattern](#uso-factory-pattern)
- [Agregar nuevo extractor](#agregar-nuevo-extractor)
- [Ejecutar](#ejecutar)
- [Microservicio](#microservicio)

## Extract - Webscraping - Factory Pattern

### Estructura

```bash
extract
├── webscraping/
│    ├── __init__.py
│    ├── extractors/
│    │   ├── __init__.py      
│    │   ├── base_extractor.py          # Clase abstracta base
│    │   ├── extractor_factory.py       # Factory para crear extractores
│    │   ├── extractor_daka.py          # Extractor API Daka
│    ├── models_config.py               # Configuración de extractores
│    ├── models_enum.py                 # Enums de configuración
│    └── webscraping_main.py            # Orquestador principal (DIP)
├── services/
│   ├── __init__.py
│   ├── file_service.py              # Servicio de manejo de archivos (SRP)
│   └── extraction_service.py        # Servicio de extracción (SRP)
├── .dockerignore
├── Dockerfile
├── README.md
└── requirements.txt
```

### Uso Factory Pattern

```python
from webscraping.extractors.extractor_factory import ExtractorFactory

# Extraer de una fuente específica
extractor = ExtractorFactory.create_extractor('daka')
data = extractor.extract_data()

# Extraer de todas las fuentes
extractors = ExtractorFactory.create_all_extractors()
```

### Agregar nuevo extractor

1. Crear clase heredando de `BaseExtractor`
2. Implementar métodos `extract_data()` y `get_extractor_name()`
3. Registrar en `ExtractorFactory._extractors`

### Ejecutar

#### Local

Es necesario ubicarse dentro de la carpeta **[src/extract](/src/extract)** y ejecutar:

```bash
python -m webscraping.webscraping_main
```

#### Docker

**Variables de entorno requeridas:**

- `ETL_PROJECT_PATH`: Ruta principal del proyecto ETL
- `DATA_ETL`: Carpeta donde se guardarán los datos (relativa al proyecto)

#### **Opción 1: Con docker-compose (recomendado)**

Desde la raíz del proyecto [BuscaListoETL](/), se ejecuta el siguiente comando desde la consola

```bash
docker-compose up extractor
```

#### **Opción 2: Docker standalone**

```bash
# Construir imagen
docker build -t busca-listo-extractor .

# Opción 2a: Con archivo .env (recomendado)
docker run --name extractor \
  --env-file ../../.env \
  -v $(pwd)/../../data:/app/data \
  busca-listo-extractor

# Opción 2b: Con variables manuales
docker run --name extractor \
  -e ETL_PROJECT_PATH=/app \
  -e DATA_ETL=data \
  -v $(pwd)/../../data:/app/data \
  busca-listo-extractor
```

**Salida de datos:**
Los datos extraídos se guardan en formato JSON:

- Ubicación: `{ETL_PROJECT_PATH}/{DATA_ETL}/extract/`
- Formato: `{extractor}_{YYYY_MM_DD}.json`
- Ejemplo: `daka_2025_01_09.json`

### Microservicio

- **Proceso batch**: Extracción de datos de APIs
- **Imagen**: Python 3.11-slim optimizada
- **SOLID**: Principios de diseño aplicados para mejor mantenibilidad
  - **SRP**: Cada clase tiene una sola responsabilidad
  - **DIP**: Dependencias invertidas usando servicios
  - **Modular**: Separación clara de responsabilidades
