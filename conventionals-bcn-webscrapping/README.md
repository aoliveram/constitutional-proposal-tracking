# Web Scraping de Convencionales Constituyentes (BCN)

Este módulo contiene las herramientas necesarias para la recopilación y sistematización de los perfiles biográficos de los Convencionales Constituyentes que participaron en la Convención Constitucional de Chile (2021-2022).

## Objetivo
El objetivo de este sub-proyecto es enriquecer la base de datos de convencionales con información personal, profesional y política relevante extraída directamente desde la **Biblioteca del Congreso Nacional (BCN)**.

## Progreso Actual

### 1. Extracción de Datos Crudos (`conventional-profiles-raw.json`)
Se ha implementado un scraper robusto (`fetch_convencionales.py`) que realiza las siguientes tareas:
- **Matching Inteligente:** Mapea los nombres listados en el archivo maestro `convention_members.json` con las URLs canónicas de las fichas biográficas en el portal de la BCN.
- **Extracción de Variables:** Se capturan de forma estructurada los siguientes campos:
    - **Introducción:** Resumen biográfico (`intro_wiki`).
    - **Biografía Detallada:** Secciones de familia, juventud, estudios, trayectoria política y propuestas Constitucionales.
    - **Datos Personales:** Nombre completo, fecha y lugar de nacimiento, profesión y grado académico.
    - **Representación:** Distrito y afiliación política (militancia o independencia).

### 2. Archivos Generados
- `fetch_convencionales.py`: Script principal de Python para ejecutar el scraping.
- `conventional-profiles-raw.json`: Base de datos cruda con la información textual completa de 147 convencionales.
- `reporte_scraping_bcn.md`: Documentación técnica sobre la arquitectura original del scraper.

## Próximos Pasos
El siguiente hito del proyecto es la creación de **`conventional-profiles.json`**. Este nuevo archivo será una versión procesada y acotada del archivo "raw", enfocada en:
1. **Normalización de Fechas:** Estandarizar las fechas de nacimiento a formato ISO (YYYY-MM-DD).
2. **Categorización Política:** Simplificar las afiliaciones en categorías analíticas.
3. **Análisis de Experiencia:** Identificar de forma booleana si el convencional poseía cargos políticos previos basándose en el análisis de su biografía textual.

## Instrucciones de Uso

Para ejecutar el scraper desde la raíz del proyecto:

```bash
source conventionals-bcn-webscrapping/venv/bin/activate
python conventionals-bcn-webscrapping/fetch_convencionales.py
```

---
*Este proyecto forma parte del seguimiento de propuestas constitucionales del Doctorado.*
