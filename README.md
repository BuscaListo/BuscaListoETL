# ETL BuscaListo

Sistema ETL (Extract, Transform, Load) para la extracción, transformación y carga de datos de productos desde API proporcionadas o datos suministrados.

## Índice

- [ETL BuscaListo](#etl-buscalisto)
- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Procesos](#procesos)
- [Configuración](#configuración)
- [Uso](#uso)

## Descripción

BuscaListo ETL es un pipeline de datos diseñado para extraer información de ciertos productos, transformar los datos al formato de análisis y cargarlos hacía la base de datos.

## Estructura del Proyecto

``` bash
BuscaListoETL/
├── src/                   # Código fuente de los procesos ETL
│   ├── extract/           # Módulo de extracción de datos
│   │   ├── webscraping/   # Web scraping components
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── transform/         # Módulo de transformación de datos
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── load/              # Módulo de carga de datos
│       ├── Dockerfile
│       └── requirements.txt
├── data/                  # Datos procesados por etapa
│   ├── extract/           # Datos extraídos
│   ├── transform/         # Datos transformados
│   └── load/              # Datos cargados
├── docker-compose.yml     # Configuración de contenedores
├── .env.example           # Variables de entorno ejemplo
└── README.md              # Este archivo
```

## Procesos

### Extract

Carpeta **[src/extract](/src/extract/)**

- Extracción de datos mediante web scraping o consulta de API publicas
- Soporte para múltiples sitios web
- Configuración modular por extractor

### Transform

Carpeta **[src/transform](/src/transform/)**

- Limpieza y normalización de datos
- Validación de información
- Enriquecimiento de datos

### Load

Carpeta **[src/load](/src/load/)**

- Carga de datos al sistema destino
- Gestión de duplicados
- Logging y monitoreo

## Configuración

1. Copiar `.env.example` a `.env`
2. Configurar las variables de entorno necesarias

## Uso

```bash
# Ejecutar todo el pipeline ETL
docker-compose up

# Ejecutar servicios individuales
docker-compose up extractor
docker-compose up transformer
docker-compose up loader
```
