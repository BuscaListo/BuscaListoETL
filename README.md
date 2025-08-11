# ETL BuscaListo

Sistema ETL (Extract, Transform, Load) para la extracción, transformación y carga de datos de productos desde API proporcionadas o datos suministrados.

## Índice

- [ETL BuscaListo](#etl-buscalisto)
- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Procesos](#procesos)
- [Configuración](#configuración)
- [Uso con Docker Compose](#uso-con-docker-compose)
- [Mejoras Implementadas](#mejoras-implementadas)

## Descripción

BuscaListo ETL es un pipeline de datos diseñado para extraer información de productos, transformar los datos al formato de análisis y cargarlos hacia la base de datos.

**Características principales:**
- **Arquitectura de microservicios** con Docker
- **Principios SOLID** aplicados en todos los módulos
- **Validación automática** con Pydantic
- **Múltiples formatos** de entrada (JSON, CSV, Excel)
- **Salidas optimizadas** (JSON completo + CSV para analistas)

## Estructura del Proyecto

``` bash
BuscaListoETL/
├── src/                   # Código fuente de los procesos ETL
│   ├── extract/           # Módulo de extracción de datos
│   │   ├── webscraping/   # Extractores y configuración
│   │   ├── services/      # Servicios (SRP)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── transform/         # Módulo de transformación de datos
│   │   ├── transformers/  # Transformadores y factory
│   │   ├── services/      # Servicios (SRP)
│   │   ├── models.py      # Modelos Pydantic
│   │   ├── constants.py   # Enums y constantes
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── load/              # Módulo de carga de datos
│       ├── Dockerfile
│       └── requirements.txt
├── data/                  # Datos procesados por etapa
│   ├── extract/           # Datos extraídos (JSON)
│   ├── transform/         # Datos transformados (JSON + CSV)
│   └── load/              # Datos cargados
├── docker-compose.yml     # Configuración de contenedores
├── .env.example           # Variables de entorno ejemplo
└── README.md              # Este archivo
```

## Procesos

### Extract

Carpeta **[src/extract](/src/extract/)**

- **Extracción de datos** mediante APIs públicas
- **Factory Pattern** para múltiples extractores
- **Servicios SOLID** (FileService, ExtractionService)
- **Salida**: JSON con datos crudos
- **Fuentes actuales**: Daka

### Transform

Carpeta **[src/transform](/src/transform/)**

- **Validación automática** con modelos Pydantic
- **Múltiples formatos** de entrada (JSON, CSV, Excel)
- **Enums y constantes** centralizadas
- **Servicios SOLID** (FileService, TransformationService)
- **Salidas duales**:
  - JSON completo con métricas
  - CSV limpio para analistas (sin raw_data)
- **Fuentes actuales**: Daka, Farmatodo

### Load

Carpeta **[src/load](/src/load/)**

- Carga de datos al sistema destino
- Gestión de duplicados
- Logging y monitoreo

## Configuración

### Variables de Entorno

1. Copiar `.env.example` a `.env`
2. Configurar las variables necesarias:

```bash
# Rutas del proyecto
ETL_PROJECT_PATH=/ruta/al/proyecto
DATA_ETL=data

# Configuración Docker
DOCKER_ENV=true
```

### Estructura de Datos

El sistema creará automáticamente:

```bash
data/
├── extract/
│   ├── daka_2025_01_09.json
│   └── farmatodo_2025_01_09.json
├── transform/
│   ├── daka_transformed_2025_01_09.json      # JSON completo
│   ├── daka_products_2025_01_09.csv          # CSV para analistas
│   ├── farmatodo_transformed_2025_01_09.json
│   └── farmatodo_products_2025_01_09.csv
└── load/
    └── (archivos de carga)
```

## Uso con Docker Compose

### Pipeline Completo (Recomendado)

```bash
# Ejecutar todo el pipeline ETL secuencialmente
docker-compose up
```

**Orden de ejecución:**
1. `extractor` → Extrae datos de APIs
2. `transformer` → Transforma y valida datos (depende de extractor)
3. `loader` → Carga datos finales (depende de transformer)

### Servicios Individuales

```bash
# Solo extracción
docker-compose up extractor

# Solo transformación (requiere datos extraídos)
docker-compose up transformer

# Solo carga (requiere datos transformados)
docker-compose up loader
```

### Reconstruir Contenedores

```bash
# Reconstruir sin cache (cuando hay cambios en el código)
docker-compose build --no-cache

# Reconstruir y ejecutar
docker-compose up --build

# Reconstruir servicio específico
docker-compose build --no-cache transformer
```

### Comandos Útiles

```bash
# Ver logs de un servicio
docker-compose logs transformer

# Ejecutar en segundo plano
docker-compose up -d

# Detener todos los servicios
docker-compose down

# Limpiar volúmenes y contenedores
docker-compose down -v --remove-orphans
```

## Mejoras Implementadas

### Principios SOLID
- **SRP**: Servicios con responsabilidades únicas
- **DIP**: Dependencias invertidas usando servicios
- **Factory Pattern**: Creación de extractores/transformadores

### Validación y Calidad
- **Pydantic Models**: Validación automática de datos
- **Enums centralizados**: Constantes y tipos de datos
- **Métricas detalladas**: Conteo de registros válidos/inválidos

### Formatos y Compatibilidad
- **Múltiples entradas**: JSON, CSV, Excel
- **Salidas optimizadas**: JSON completo + CSV limpio
- **Tipos modernos**: Python 3.9+ (list, dict nativos)

### Monitoreo y Logs
- **Logging estructurado**: Información detallada del proceso
- **Manejo de errores**: Captura y reporte de problemas
- **Métricas de procesamiento**: Resumen de resultados
