# Constitutional Proposal Tracking

## Descripción
Conjunto de scripts (varios de ellos usando API Gemini) para rastrear la genealogía del de iniciativas e indicaciones de votación de la Convención Constitucional Chile 2021-2022, desde su iniciativa original hasta el borrador final.

## Estructura del Proyecto

- **`scripts/`**: Contiene los scripts de procesamiento de datos en Python.
    - `06_apply_indications_ai_v3.py`: Script principal para aplicar indicaciones.
    - `02_map_initiatives.py`: Mapeo de iniciativas a artículos.
    - `04_extract_indications.py`: Extracción de indicaciones desde PDFs.
- **`comision-*/`**: Carpetas de datos por comisión (1-7).
    - `genesis-extracted/`: Datos base de las propuestas originales.
    - `indicaciones-universal-extracted/`: Datos de las votaciones e indicaciones extraídos.
- **`reports/`**: Reportes de estado y análisis de calidad de datos.

## Perfiles de Extracción por Comisión

El archivo `constitutional_proposal_tracking/config/commission_profiles.py` define la estrategia de extracción para cada comisión, adaptándose a la estructura variable de sus documentos originales (PDFs de "Génesis" y "Votación").

### Tipos de Perfil
*   **NARRATIVE (Narrativo):** Documentos de texto continuo donde los artículos e indicaciones se identifican por patrones de lenguaje natural y palabras clave (ej: "Artículo 1...").
*   **TABULAR (Tabular):** Documentos estructurados en tablas de dos columnas (ej: columna izquierda para ID de iniciativa, derecha para texto del artículo).
*   **CUSTOM_COMPLEX:** Lógica ad-hoc para casos con formatos irregulares.

### Asignación Actual por Comisión

| Comisión | Perfil Génesis | Perfil Votación |
| :--- | :--- | :--- |
| **1 (Sistema Político)** | NARRATIVE | NARRATIVE |
| **2 (Principios)** | NARRATIVE | CUSTOM_COMPLEX |
| **3 (Forma de Estado)** | TABULAR | TABULAR |
| **4 (Derechos Fund.)** | CUSTOM_COMPLEX | NARRATIVE |
| **5 (Medio Ambiente)** | TABULAR | NARRATIVE |
| **6 (Sistemas de Justicia)** | TABULAR | NARRATIVE |
| **7 (Sistemas de Conoc.)** | NARRATIVE | NARRATIVE |

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
