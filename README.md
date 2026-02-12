# Constitutional Proposal Tracking

## Descripción
Herramienta de IA para rastrear la genealogía de normas constitucionales desde su iniciativa original hasta el borrador final, aplicando indicaciones de votación. Este proyecto utiliza Modelos de Lenguaje (LLMs) para reconstruir la historia fidedigna del proceso constituyente chileno.

## Estructura del Proyecto

- **`scripts/`**: Contiene los scripts de procesamiento de datos en Python.
    - `06_apply_indications_ai_v3.py`: Script principal para aplicar indicaciones.
    - `02_map_initiatives.py`: Mapeo de iniciativas a artículos.
    - `04_extract_indications.py`: Extracción de indicaciones desde PDFs.
- **`comision-*/`**: Carpetas de datos por comisión (1-7).
    - `genesis-extracted/`: Datos base de las propuestas originales.
    - `indicaciones-universal-extracted/`: Datos de las votaciones e indicaciones extraídos.
- **`reports/`**: Reportes de estado y análisis de calidad de datos.

## Setup

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar API Key:**
    Este proyecto requiere acceso a Google Gemini API. Configura tu variable de entorno:
    ```bash
    export GOOGLE_API_KEY="tu_api_key_aqui"
    ```

## Uso

El script principal procesa las indicaciones y genera el borrador evolutivo:

```bash
python scripts/06_apply_indications_ai_v3.py
```

## Estado
El proyecto se encuentra actualmente en fase de **Revisión de Calidad de Datos**. Consulta la carpeta `reports/` para más detalles sobre el progreso de extracción por comisión.
